import re
import sys
import math
import asyncio
from tqdm import tqdm
from azure.ai.textanalytics.aio import TextAnalyticsClient
from azure.ai.textanalytics import PiiEntityCategory
from azure.core.credentials import AzureKeyCredential
from .. import config
from ..base import TransformerMixin


class MinMaxLengthFilter(TransformerMixin):

    def __init__(self, words_range=(0, -1)):
        self.words_range = words_range
        
    def transform(self, texts, labels=None):
        min_words = self.words_range[0]
        max_words = self.words_range[1] if self.words_range[1] != -1 else sys.maxsize
        texts_tr, labels_tr = [], []
        for idx in range(len(texts)):
            words = str(texts[idx]).strip().split()
            if min_words <= len(words) <= max_words:
                texts_tr.append(texts[idx])
                if labels:
                    labels_tr.append(labels[idx])
        if labels:
            return texts_tr, labels_tr
        else:
            return texts_tr
        

class NameFilter(TransformerMixin):

    batch_size = 5

    def __init__(self):
        self._test_config()

    def _test_config(self):
        if config.azure_key is None:
            raise ValueError("Please set up `config.azure_key`!")
        if config.azure_endpoint is None:
            raise ValueError("Please set up `config.azure_endpoint`!")

    async def _name_filter(self, texts):
        client = TextAnalyticsClient(
            endpoint=config.azure_endpoint,
            credential=AzureKeyCredential(config.azure_key),
        )
        async with client:
            response = await client.recognize_pii_entities(documents=texts, language="en", categories_filter = [PiiEntityCategory.PERSON], verify_ssl=False)
            filtered_texts = [re.sub(r'[*]+', 'PersonName', doc.redacted_text) for doc in response if not doc.is_error]
        await client.close()
        return filtered_texts

    def transform(self, texts):
        texts_tr = []
        num_batch = math.ceil(len(texts) / self.batch_size)
        for idx in tqdm(range(0, len(texts), self.batch_size), total=num_batch):
            texts_tr.extend(asyncio.run(self._name_filter(texts[idx: idx+self.batch_size])))
        return texts_tr