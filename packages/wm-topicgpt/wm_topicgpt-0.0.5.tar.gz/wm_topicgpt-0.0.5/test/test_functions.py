import sys
sys.path.append("..")

#-------- Test Config ------------
from topicgpt import config

config.azure_key = "6ea086b8344b41338f484502e3f77cd9"
config.azure_endpoint = "https://my-assistant-text-analyzer-dev-66b3fa72-cognitive.cognitiveservices.azure.com/"

config.consumer_id = "719f6b98-cfb3-4048-9bd0-095b57b3257a"
config.private_key_path = "private_key.pem"
config.mso_llm_env = "stage"

#------- Test ChatModel ----------
# from topicgpt.walmart_llm import ChatModel
# llm = ChatModel(model_name="gpt-35-turbo", temperature=0.1, batch_size=500)

# message = "Who is American's president?"
# response = llm.retry_completion(message)

# message = "Question: Who is American's president? Answere in the json format as follows: {'Question': [put quesiont here], 'Answer': [put answer here]}"
# response = llm.retry_json_completeion(message, ['Question', 'Answer'])

# messages = ["Who is American's president?"] * 100000
# response = llm.batch_completion(messages)
# print(len(response))

#------- Test EmbedModel---------
# from topicgpt.walmart_llm import EmbedModel
# from topicgpt.embedding import BGEEmbedModel
# llm = BGEEmbedModel(batch_size=500, device="mps")
# llm = EmbedModel(model_name="text-embedding-ada-002", batch_size=500)

# message = "Who is American's president?"
# response = llm.embed_query(message)

# message = ["Who is American's president?"] * 10000
# response = llm.embed_documents(message)
# print(len(response))


# message = "Who is American's resident?"
# response = llm.embed_query(message)


#------- Test preprocessing -----------
# from topicgpt.preprocessing import MinMaxLengthFilter, NameFilter

# texts = ["I'm Alex", "You are good girl, please don't talk"] * 100

# filter = MinMaxLengthFilter(words_range=(0, -1))
# texts1 = filter.transform(texts)
# print(texts1)

# filter = NameFilter()
# texts2 = filter.transform(texts1)
# print(texts2)

#-------- Test feature_extraction ---------
# from topicgpt.feature_extraction import TfidifKeywordsExtractor, LlmKeywordsExtractor
# texts = ["I'm Alex", "You are good girl, please don't talk", "401k"] * 100

# extractor = TfidifKeywordsExtractor()
# r_text, r_label = extractor.transform(texts)
# print(len(r_text), len(r_label))

# extractor = LlmKeywordsExtractor()
# r_text = extractor.transform(texts)
# breakpoint()