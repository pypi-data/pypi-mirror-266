from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from typing import List, Union, Any
from swarmauri.core.vectorizers.IVectorize import IVectorize
from swarmauri.core.vectors.IVector import IVector
from swarmauri.standard.vectors.concrete.SimpleVector import SimpleVector

class Doc2VecVectorizer(IVectorize):
    def __init__(self):
        self.model = Doc2Vec(vector_size=2000, window=10, min_count=1, workers=5)

    def extract_features(self):
        return list(self.model.wv.key_to_index.keys())

    def fit(self, documents: List[str], labels=None) -> None:
        tagged_data = [TaggedDocument(words=_d.split(), 
            tags=[str(i)]) for i, _d in enumerate(documents)]

        self.model.build_vocab(tagged_data)
        self.model.train(tagged_data, total_examples=self.model.corpus_count, epochs=self.model.epochs)

    def transform(self, documents: List[str]) -> List[IVector]:
        vectors = [self.model.infer_vector(doc.split()) for doc in documents]
        return [SimpleVector(vector) for vector in vectors]

    def infer_vector(self, data: str) -> IVector:
        vector = self.model.infer_vector(data.split())
        return SimpleVector(vector)