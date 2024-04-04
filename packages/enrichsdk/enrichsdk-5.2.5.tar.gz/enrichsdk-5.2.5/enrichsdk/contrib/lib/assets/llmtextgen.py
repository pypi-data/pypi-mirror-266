import openai
from enrichsdk.lib import get_credentials_by_name

__all__ = [
    'LLMTextGenerator'
]
class LLMTextGenerator(object):

    def __init__(self, cred, *args, **kwargs):
        """
        default
        """
        # vars
        self.available_models = {
            "completion": [
                    "text-davinci-003",
                    "text-curie-001",
                    "text-babbage-001",
                    "text-ada-001",
                    "code-davinci-002",
                    "code-cushman-001"
                ],
            "embedding": [
                    "text-embedding-ada-002"
                ]
        }
        self.default_code_model = "code-davinci-002"
        self.default_text_model = "text-davinci-003"
        self.default_embedding_model = "text-embedding-ada-002"

        # setup defaults
        # use a valid model
        model = kwargs.pop('model', "")
        available_models = []
        for task, models in self.available_models.items():
            available_models += models
        if model not in available_models:
            model = self.default_text_model
        self.model = model

        # setup the api key
        self.cred = cred
        self.api_key = self.get_api_key(self.cred)

        super().__init__(*args, **kwargs)

    def get_api_key(self, cred):
        """
        get the API key from the cred
        """
        api_key = None
        if isinstance(cred, str):
            api_key = cred
        if isinstance(cred, dict) and 'apikey' in cred:
            api_key = cred['apikey']
        return api_key

    def set_model(self, task, model):
        """
        set the model to use for text completion
        """
        available_models = self.available_models.get(task, [])
        if model not in available_models:
            return False

        self.model = model
        return True

    def get_model(self):
        """
        get the model to use for text completion
        """
        return self.model

    def generate_text(self, **kwargs):
        """
        generate a text completion given a prompt
        """
        kwargs['model'] = self.default_text_model
        return self.generate_common(task='completion', **kwargs)

    def generate_code(self, **kwargs):
        """
        generate a code completion given a prompt
        """
        kwargs['model'] = self.default_code_model
        return self.generate_common(task='completion', **kwargs)

    def generate_embedding(self, **kwargs):
        """
        generate an embedding vector given some text
        """
        kwargs['model'] = self.default_embedding_model
        return self.generate_common(task='embedding', **kwargs)

    def generate_common(self, task, **kwargs):
        """
        generate a completion given a prompt
        """
        # default, override if successful
        result = {"success": False}

        # check if we have all the required params
        if self.api_key == None:
            result['msg'] = "No API key available"
            return result

        prompt = kwargs.get('prompt')
        if prompt == None:
            result['msg'] = "No valid input data specified"
            return result

        model = kwargs.get('model')
        if model == None:
            result['msg'] = "No valid model specified"
            return result
        else:
            success = self.set_model(task, model)
            if success:
                model = self.get_model()
            else:
                result['msg'] = "No valid model specified"
                return result

        # call OpenAI API
        try:
            if task == 'completion':
                result['text'] = self.call_completion_api(prompt, model)
                result['success'] = True
            elif task == 'embedding':
                result['embedding'] = self.call_embedding_api(prompt, model)
                result['success'] = True
            else:
                result['msg'] = "Unknown task specified, cannot proceed"
        except:
            result['msg'] = "Something went wrong when calling the API"

        return result

    def call_completion_api(self, prompt, model):
        """
        Make a call to OpenAI API to get the text completion
        """
        openai.api_key = self.api_key

        max_tokens = round(len(prompt)*1.5)
        if model == self.default_code_model:
            max_tokens = 2047

        response = openai.Completion.create(
          model=model,
          prompt=prompt,
          temperature=0,
          max_tokens=max_tokens,
          top_p=1.0,
          frequency_penalty=0.0,
          presence_penalty=0.0,
          stop=["#", ";"]
        )

        text = response.choices[0]['text']

        return text

    def call_embedding_api(self, prompt, model):
        """
        Make a call to OpenAI API to get the embedding
        """
        openai.api_key = self.api_key

        response = openai.Embedding.create(
          model=model,
          input=prompt
        )

        embedding = response['data'][0]['embedding']

        return embedding


if __name__ == "__main__":

    cred = get_credentials_by_name('openai-api')

    prompt1 = "test"
    prompt2 = "Create a SQL request to find all users who live in California and have over 1000 credits"
    prompt3 = """### Postgres SQL tables, with their properties:
#
# Employee(id, name, department_id)
# Department(id, name, address)
# Salary_Payments(id, employee_id, amount, date)
#
### A query to list the names of the departments which employed more than 10 employees in the last 3 months"""

    generator = LLMTextGenerator(cred)
    result = generator.generate_embedding(prompt=prompt3)

    if result['success'] == True:
        print (result['embedding'])
    else:
        print (result['msg'])
