# TopicGPT package

## How to install this package?
```python
pip install wm_topicgpt==0.06
```

## How to use this package?

### Step 1: Set up global parameters
```python
from topicgpt import config

# For NameFilter
config.azure_key = ""
config.azure_endpoint = ""

# For GPT3.5 or GPT4 or Ada-002
config.consumer_id = ""
config.private_key_path = ""
config.mso_llm_env = ""
```

### Step 2: Load your dataset
Replace *dataset.csv* with your own dataset and replace *Content* with your text column name.
```python
import pandas as pd

data = pd.read_csv("dataset.csv")

# drop NA data
data = data.dropna(subset=["Content"])
# make sure data are text
data['Content'] = data['Content'].astype(str)
# convert to list
data = data['Content'].tolist()
```


### Step 3: Preprocessing the texts
This function only keeps the texts which include 1 - 1000 words.
```python
from topicgpt.preprocessing import MinMaxLengthFilter

filter = MinMaxLengthFilter(words_range=(1, 1000))
texts = filter.transform(data)
```

To protect the privacy, this function replaces the names in the texts with word "PersonName".
```python
from topicgpt.preprocessing import NameFilter

filter = NameFilter()
texts = filter.transform(texts)
```

### Step 4: Embedding the texts
You may choose one of them to embed your texts.
```python
# Option 1: use OpenAI model
from topicgpt.walmart_llm import AdaEmbedModel
llm = AdaEmbedModel(batch_size=500)
embedding = llm.embed_documents(texts)

# Option 2: use BGE model
from topicgpt.embedding import BGEEmbedModel
# llm = BGEEmbedModel(batch_size=500, device="cpu")
llm = BGEEmbedModel(batch_size=500, device="mps")
embedding = llm.embed_documents(texts)
```

### Step 5: Build topics from texts
This function is used to generate topic taxonomy from the texts.
```python
from topicgpt.topic import HDBSCANTopicGenerator
model = HDBSCANTopicGenerator(reduced_dim=10, n_neighbors=10, min_cluster_percent=0.02, topk=5)
root = model.predict(texts, embedding)
```
