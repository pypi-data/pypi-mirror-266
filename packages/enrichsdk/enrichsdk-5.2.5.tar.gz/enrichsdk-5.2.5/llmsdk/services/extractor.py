from ..agents.extractor import *

import json

def get_contract_profilespec():

    import json

    # example of how to write methods to modify
    # profilespec queries
    def mod_query_duration(query, params):
        """
        modify the duration query based on the value
        populated in the billing frequency column
        """
        freqs = {
            "daily": "days",
            "weekly": "weeks",
            "monthly": "months",
            "quarterly": "months",
            "semi-annually": "months",
            "annually": "years",
            "yearly": "years",
        }

        # get the inputs we need
        billing_freq = params.get("billing_freq")
        # check if we have them and can proceed
        if not billing_freq:
            return query

        # modify the duration query
        billing_freq = billing_freq.lower()
        freq = freqs.get(billing_freq)
        if freq:
            query = f"{query} in {freq}?"

        return query

    # example of how to write methods to post-process LLM response
    def pp_companies(answer):
        """
        post-process the answer for the
        queries on parties involved
        """
        try:
            answer = json.loads(answer)
        except:
            pass
        return answer

    query_spec = {
        "name": "acme",
        "query_set": [
            {
                "name": "industry",
                "query": "what industry vertical does the contract deal with? respond with only the type of industry",
                "query_alts": [
                    "what industry is mentioned? respond with only the type of industry"
                ],
                "use_alts": "on-fail",
                "postprocess": None,
                "fill_columns": ["industry_vertical"]
            },
            {
                "name": "companies",
                "query": "which two companies is this contract between? format your response as a json list",
                "postprocess": pp_companies,
                "fill_columns": ["company_1", "company_2"]
            },
            {
                "name": "contract type",
                "query": "what type of contract does the document represent? choose from one of the following options: service agreement, master services agreement, purchase order, change order, subscription, saas services agreement, ammendment",
                "postprocess": None,
                "fill_columns": ["contract_type"]
            },
            {
                "name": "start date",
                "query": "what is the start date of the contract? respond with only a date.",
                "query_alts": [
                    "what is the effective date of the contract? respond with only a date"
                ],
                "use_alts": "on-fail",
                "postprocess": None,
                "fill_columns": ["commencement_date"]
            },
            {
                "name": "end date",
                "query": "what is the end date of the contract? respond with only a date.",
                "postprocess": None,
                "fill_columns": ["termination_date"]
            },
            {
                "name": "billing frequency",
                "query": "what is the billing frequency mentioned in the contract? choose from one of the following options: daily, weekly, monthly, quarterly, semi-annually, annually, adhoc",
                "postprocess": None,
                "fill_columns": ["billing_freq"]
            },
            {
                "name": "duration",
                "query": "what is the duration of the contract",
                "query_mod": {
                    "method": mod_query_duration,
                    "inputs": ["billing_freq"],
                    "apply_to": "first"
                },
                "query_alts": [
                    "what is the duration of the contract?"
                ],
                "use_alts": "always",
                "postprocess": None,
                "fill_columns": ["duration"]
            },
            {
                "name": "billing currency",
                "query": "what is the billing currency for the contract? respond with only the currency code",
                "query_alts": [
                    "what cuurency is the cost mentioned in? respond only with the code"
                ],
                "use_alts": "on-fail",
                "postprocess": None,
                "fill_columns": ["billing_currency"]
            },
            {
                "name": "billable amount",
                "query": "what is the total billable value of the contract?",
                "query_alts": [
                    "what is the cost mentioned?"
                ],
                "use_alts": "on-fail",
                "postprocess": None,
                "fill_columns": ["billable_amount"]
            }
        ]
    }

    return query_spec

def contract_query(profilespec, filename, cred=None):

    name = profilespec['name']
    persist_directory = "chromadb123"

    # create an agent
    agent = LLMQuerierExtractor(name=f"{name}_contract_agent", cred=cred)

    # point it to a document to read
    if filename.endswith("pdf"):
        agent.read_document(source="pdf",
                            content=filename,
                            persist_directory=persist_directory)
    elif filename.endswith("txt"):
        agent.read_document(source="str",
                            content=open(filename).read(),
                            metadata={
                                "source": filename,
                            },
                            persist_directory=persist_directory)
    else:
        raise Exception("Unsupported input file. Only pdf/txt are supported")

    # run it against the profilespec
    result = agent.process_spec(profilespec)

    return result, agent.get_metadata()
