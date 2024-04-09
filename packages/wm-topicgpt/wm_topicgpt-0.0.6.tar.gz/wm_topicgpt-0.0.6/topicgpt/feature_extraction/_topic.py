import tiktoken
from ..base import TransformerMixin
from ..walmart_llm import ChatModel


class TopicGenerator(TransformerMixin):

    def __init__(self, model_name="gpt-35-turbo", temperature=0.):
        self.model_name = model_name
        self.model = ChatModel(model_name=model_name, temperature=temperature)
        self.encoding = tiktoken.encoding_for_model(model_name=model_name)

    def _generate_topic_and_description_for_cluster(self, cluster):
        prefix = """You are a good editor. Given some requirements and sentences, you need to summarize the main topic of those sentences and give a simple description of this topic according to those requirements. 
        Here are some requirements you MUST follow:
        1. The topic should reflect the main intent of those prompts.
        2. The topic should be less than 10 words.
        3. The description should be less than 30 words.

        Here are the sentences you need to consider all:
        {user_input}
        """
        suffix = """
        The output should be in the json format:
        {"topic": <summarize the main topic of those sentence>, "description": <output a discription for this topic>}
        """
        user_input = ""
        for i, text in enumerate([cluster.texts[idx] for idx in cluster.closest], start=1):
            if (self.model_name == "gpt-35-turbo" and len(self.encoding.encode(user_input)) < 4000) or \
               (self.model_name == "gpt-4" and len(self.encoding.encode(user_input)) < 7000):
                user_input += f"sentence {i}: {str(text).strip()}\n"
        prompt = prefix.format(user_input=user_input) + suffix
        try:
            return self.model.retry_json_completeion(prompt, keys=['topic', 'description'])
        except Exception as e:
            breakpoint()
            raise ValueError(f"Exception: {e}")
         
    def transform(self, cluster):
        return self._generate_topic_and_description_for_cluster(cluster)