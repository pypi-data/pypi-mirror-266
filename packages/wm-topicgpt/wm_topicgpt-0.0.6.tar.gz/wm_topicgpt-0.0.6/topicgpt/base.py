import abc


class TransformerMixin(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def transform(self, texts, **params):
        pass


class GeneratorMixin(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def predict(self, texts, embeddings, **params):
        pass