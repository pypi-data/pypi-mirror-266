import sys
sys.path.append("..")

#-------- Add Config ------------
from topicgpt import config

config.azure_key = "6ea086b8344b41338f484502e3f77cd9"
config.azure_endpoint = "https://my-assistant-text-analyzer-dev-66b3fa72-cognitive.cognitiveservices.azure.com/"

config.consumer_id = "719f6b98-cfb3-4048-9bd0-095b57b3257a"
config.private_key_path = "private_key.pem"
config.mso_llm_env = "stage"

# --------- Load data ------------------
import pandas as pd
data = pd.read_csv("20230725-20240315.csv")
data = data#.sample(n=10000)
data = data.dropna(subset=['userInput'])
texts = data['userInput'].tolist()

# --------- Preprocessing ---------------
from topicgpt.preprocessing import MinMaxLengthFilter

filter = MinMaxLengthFilter((1, 1000))
texts = filter.transform(texts)
print(len(texts))

# -------- Embedding data -----------
from topicgpt.embedding import BGEEmbedModel

llm = BGEEmbedModel(batch_size=500, device="mps")
embeddings = llm.embed_documents(texts)

# -------- Extract Keywords ----------
from topicgpt.feature_extraction import LlmKeywordsExtractor

llm = LlmKeywordsExtractor()
keywords = llm.transform(texts)
breakpoint()

# --------- HDBSCAN -----------------
from topicgpt.topic import HDBSCANTopicGenerator

generator = HDBSCANTopicGenerator(reduced_dim=10, n_neighbors=10, min_cluster_size=50)

# one stop
root = generator.predict(texts, embeddings)

# step by step
# root = generator.build_cluster_tree(texts, embeddings)
# generator.fill_cluster_tree(root)
# generator.plot_cluster_tree(root)