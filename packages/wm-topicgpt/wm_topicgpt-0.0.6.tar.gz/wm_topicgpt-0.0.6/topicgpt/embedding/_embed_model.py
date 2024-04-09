import math
from tqdm import tqdm
from langchain_community.embeddings import HuggingFaceBgeEmbeddings


class BGEEmbedModel:

    def __init__(self, batch_size=500, device="cpu", model_name="BAAI/bge-small-en-v1.5"):
        self.batch_size = batch_size
        self.model = HuggingFaceBgeEmbeddings(
            model_name=model_name, model_kwargs={"device": device}, encode_kwargs={"normalize_embeddings": True}
        )

    def embed_documents(self, documents):
        embeddings = []
        num_batch = math.ceil(len(documents) / self.batch_size)
        for idx in tqdm(range(0, len(documents), self.batch_size), total=num_batch):
            batch_documents = documents[idx: idx+self.batch_size]
            batch_embeddings = self.model.embed_documents(batch_documents)
            embeddings.extend(batch_embeddings)
        return embeddings
    
    def embed_query(self, document):
        return self.model.embed_query(document)