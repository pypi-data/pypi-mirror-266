from sklearn.feature_extraction.text import TfidfVectorizer
from ..base import TransformerMixin
from ..walmart_llm import ChatModel


class TfidifKeywordsExtractor(TransformerMixin):

    def __init__(self, ngram_range=(1, 2), topk=10):
        self.ngram_range = ngram_range
        self.topk = topk

    def transform(self, texts, labels=None, **params):
        if labels is None:
            labels = list(range(len(texts)))
        
        # build corpus
        uni_labels = list(set(labels))
        n_classes = len(uni_labels)
        corpus = [""] * n_classes
        for text, label in zip(texts, labels):
            corpus[uni_labels.index(label)] += (" " + str(text))

        vectorizer = TfidfVectorizer(ngram_range=self.ngram_range, stop_words='english')
        tfidf = vectorizer.fit_transform(corpus)

        # extract keywords
        keywords = []
        feature_names = vectorizer.get_feature_names_out()
        for idx in range(n_classes):
            tfidf_values = tfidf[idx].toarray().flatten()
            sorted_indices = tfidf_values.argsort()[::-1]
            top_keywords_indices = sorted_indices[:self.topk]
            top_keywords = [feature_names[idx] for idx in top_keywords_indices]
            keywords.append(top_keywords)
        
        return keywords, labels


class LlmKeywordsExtractor(TransformerMixin):

    def __init__(self, topk=10, model_name="gpt-35-turbo", temperature=0., batch_size=500):
        self.topk = topk
        self.template = "Extract at most {topk} keywords: {text}"
        self.model = ChatModel(model_name=model_name, temperature=temperature, batch_size=batch_size)
    
    def transform(self, texts, **params):
        prompts = [self.template.format(topk=self.topk, text=text) for text in texts]
        keywords = self.model.batch_completion(prompts)
        return keywords