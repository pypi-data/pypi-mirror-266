import os
import json
import pandas as pd
from langchain.llms import OpenAI
from langchain import PromptTemplate

__all__ = ['SADLClassifier']

class SADLClassifier(object):
    """
    Class to take in a dataframe and create a data dictionary for it
    """

    def __init__(self,
                 cred,
                 df,
                 context="",
                 entities=None):
        """
        init SADL object
        cred: credentials object
        df: dataframe
        context: any useful context when doing the labelling
                    usually, this will include keywords that identify
                    the industry/domain that the dataframe is from
        entities: path to a json spec with any additional entity mappings
                    needed by the labeller
        """

        # init
        self.cred = cred
        self.df = df
        self.context = context
        self.model = "openai"

        # init the base entity map
        self.entity_map = {
            "person": ["id", "name", "gender", "occupation", "nationality", "age", "marital status", "education level", "salutation", "job title", "relationship", "other"],
            "location": ["id", "city", "state", "province", "country", "address", "postal code", "latitude and longitude", "landmark", "neighborhood", "region", "time zone", "other"],
            "organization": ["id", "type", "industry", "other"],
            "event": ["id", "type", "theme", "other"],
            "product": ["id", "category", "brand", "model", "feature", "other"],
            "service": ["id", "category", "cost", "feature", "other"],
            "date/time": ["id", "date", "day", "month", "year", "timestamp", "time zone", "duration", "other"],
            "identifier": ["id"],
            "metric": ["revenue", "size", "volume", "sales", "measurement", "price", "other"],
            "contact": ["website", "email", "phone number", "social link"]
        }

        # init the base industry list
        self.industries = ["Business", "Technology",
                           "Finance", "Healthcare",
                           "Manufacturing", "Retail",
                           "Government", "eCommerce",
                           "Education", "Logistics"]

        # load additional entities if needed
        if entities:
            self.entity_map = self.load_entities(entities)

        # get the LLM obj
        self.llm = self._get_llm_objs(model=self.model,
                                      cred=self.cred)


    ## helper functions

    def _get_llm_objs(self, model, cred):
        """
        setup the LLM
        """
        # get the api key from creds
        api_key = self._get_api_key(cred)

        # init the model
        if model == "openai":
            # get the llm object
            llm = OpenAI(temperature=0,
                         max_tokens=1024,
                         openai_api_key=api_key)
        else:
            llm = None

        return llm

    def _get_api_key(self, cred):
        """
        get the API key from the cred
        """
        api_key = None
        if isinstance(cred, str):
            api_key = cred
        if isinstance(cred, dict) and 'apikey' in cred:
            api_key = cred['apikey']
        return api_key


    ## interfaces

    def load_entities(self, entities):
        """
        load any additional entity mappings and add them to the
        base entity map
        entities: path to entity mappings
        """

        # get the base entity map
        entity_map = self.entity_map

        # check path
        if os.path.exists(entities) and entities.endswith(".json"):
            with open(entities, "r") as fd:
                addl_emap = json.load(fd)
            if isinstance(addl_emap, dict):
                for  e, se in addl_emap.items():
                    # lowercase everything
                    e = e.lower()
                    # we need lists
                    if isinstance(se, str):
                        se = [se.lower()]
                    # lowercase everything
                    if isinstance(se, list):
                        se = [i.lower() for i in se]
                    else:
                        # we cannot add this item, move on
                        continue
                    # we can now add this mapping to the base map
                    entity_map[e].extend(se)
                    # make sure we remove duplicates
                    entity_map[e] = list(set(entity_map[e]))
            # done, we have the updated map
            self.entity_map = entity_map
        else:
            pass

        return self.entity_map


    def generate_prompt_columns(self, df, context=""):
        """
        generate a prompt for labelling a dataframe given some context
        """

        def construct_promptpartial_from_map(entity_map):
            """
            Take an entity map and construct the entity mapping partial
            that goes into the prompt for the LLM
            """
            # first the entities
            entities = ", ".join(list(entity_map.keys()))
            partial_e = f"Assume the entities available for classification are as follows: \n{entities}"

            # then for the sub-entities
            partial_se = ""
            for e, se in entity_map.items():
                p_se = f"Assume the following are the sub entities for {e}: \n{', '.join(se)}"
                partial_se = f"{partial_se}\n\n{p_se}"

            partial = f"{partial_e}{partial_se}"

            return partial

        def construct_promptpartial_outputformat():
            """
            Construct the output format structure
            for the response from the LLM
            """
            column_label = "column_name"
            label_fields = ['datatype', 'entity', 'sub_entity', 'pii', 'description']

            p = ", ".join([f'"{f}": {f}' for f in label_fields])
            op_format = "{" + column_label + ": {" + p + "}}"

            return op_format


        # construct the prompt partial for the entity mappings
        map_partial = construct_promptpartial_from_map(self.entity_map)

        # get the input column name labels
        labels = ", ".join(list(df.columns))

        # output format
        output_format = construct_promptpartial_outputformat()

        # setup the prompt
        template = """You are a data entry operator.
Your task is to construct a data dictionary for a set of database column names given to you.
The database is from a company in {context} industry.

{map_partial}

Classify the following column names into entity and sub_entity using the above mentioned details.
Also provide the following for each column:
- datatype
- true/false indicating whether the column could contain personally identifiable information (PII)
- description

Format your output as a nested json dictionary as follows:
{output_format}

Here are the input column names:
{labels}"""

        prompt = PromptTemplate(
            input_variables=["context", "map_partial", "labels", "output_format"],
            template=template
        )

        return prompt.format(context=context, map_partial=map_partial, labels=labels, output_format=output_format)

    def generate_prompt_industry(self, df):
        """
        generate a prompt for identifying the industry of a dataframe given some context
        """
        # get the input labels
        labels = ", ".join(list(df.columns))

        # setup the prompt
        template = """You are a data entry operator.
Assume you have a list of industries:
{industries}

Your task is to identify what industry a dataset belongs to given the columns in the dataset.
Respond with EXACTLY one option from the list of industries.

Here are the columns in the dataset:
{labels}"""

        prompt = PromptTemplate(
            input_variables=["labels", "industries"],
            template=template
        )

        return prompt.format(labels=labels, industries=self.industries)


    def classify_columns(self, context=""):
        """
        label the columns in the dataframe
        """

        # get the dataframe
        df = self.df

        # set the context for this labelling attempt
        context = self.context if context=="" else context

        # get the prompt for the LLM
        prompt = self.generate_prompt_columns(df, context)

        # prompt the LLM
        response = self.llm(prompt)

        try:
            result = json.loads(response.lower().strip())
            result_type = 'json'
        except:
            result = response.strip()
            result_type = 'str'

        # process the response
        return result, result_type

    def classify_industry(self):
        """
        figure out what industry the dataframe is from
        """

        # get the dataframe
        df = self.df

        # get the prompt for the LLM
        prompt = self.generate_prompt_industry(df)

        # prompt the LLM and get the response
        response = self.llm(prompt)
        result = response.lower().strip()

        # process the response
        return result



if __name__ == "__main__":

    cred = get_credentials_by_name('openai-api')

    # Sample file
    csv_path = "revenue.dashboard_market.csv"
    emap_file = "emap.json"

    # Access other data from here and specify local path
    #s3path      = "s3://scribble-demodata/sadl/demo-server/sadl-demo/sadl-llm"
    #csv_file    = f"{s3path}/revenue.dashboard_market.csv"
    #emap_file   = f"{s3path}/emap.json"

    # load csv and make df
    df = pd.read_csv(csv_file)

    # add two new dummy columns
    # only to show off SADL capabilities
    df['txn_id']            = df.index
    df['sender_fullname']   = "dummy"

    # get a SADL agent
    labeller = SADLClassifier(cred=cred,
                                df=df,
                                entities=emap_file)

    # -- optional step --
    # get a label for possible industry
    # not needed if context param is specified when creating a new SADL object
    industry = labeller.classify_industry()

    # classify the column labels
    result, result_type = labeller.classify_columns(context=industry)
    if result_type=='json':
        print (json.dumps(result, indent=4))
    else:
        print (result)
