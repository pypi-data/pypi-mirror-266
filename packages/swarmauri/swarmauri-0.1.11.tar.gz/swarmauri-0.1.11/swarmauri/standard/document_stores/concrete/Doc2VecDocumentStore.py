from typing import List, Union, Optional
import numpy as np
from gensim.models.doc2vec import TaggedDocument, Doc2Vec
from swarmauri.core.document_stores.IDocumentStore import IDocumentStore
from swarmauri.core.retrievers.IRetriever import IRetriever
from swarmauri.core.documents.IDocument import IDocument
from swarmauri.standard.vector_stores.concrete.CosineDistance import CosineDistance
from swarmauri.standard.vectors.concrete.SimpleVector import SimpleVector
#import gensim.downloader as api

class Doc2VecDocumentStore(IDocumentStore, IRetriever):
    def __init__(self):
        self.model = Doc2Vec(vector_size=2000, window=10, min_count=1, workers=5)  # Example parameters; adjust as needed
        self.documents = []
        self.metric = CosineDistance()

    def add_document(self, document: IDocument) -> None:
        self.documents.append(document)
        self._train()
        
    def add_documents(self, documents: List[IDocument]) -> None:
        self.documents.extend(documents)
        self._train()
        
    def get_document(self, doc_id: str) -> Union[IDocument, None]:
        for document in self.documents:
            if document.id == doc_id:
                return document
        return None
        
    def get_all_documents(self) -> List[IDocument]:
        return self.documents
        
    def delete_document(self, doc_id: str) -> None:
        self.documents = [doc for doc in self.documents if doc.id != doc_id]

    def update_document(self, doc_id: str, updated_document: IDocument) -> None:
        for i, document in enumerate(self.documents):
            if document.id == doc_id:
                self.documents[i] = updated_document
                break
        self._train()

    def retrieve(self, query: str, top_k: int = 5) -> List[IDocument]:
        """
        Retrieve documents similar to the query string based on Word2Vec embeddings.
        """
        query_vector = self.model.infer_vector(query.split())

        similarities = self.model.dv.most_similar([query_vector], topn=self.model.corpus_count)
        top_k_indices = sorted(range(len(similarities)), key=lambda i: similarities[i], reverse=True)[:top_k]
        return [self.documents[i] for i in top_k_indices]

    def _train(self):
        tagged_data = [TaggedDocument(words=_d.content.split(), tags=[str(i)]) for i, _d in enumerate(self.documents) if _d.content]
        self.model.build_vocab(tagged_data)
        self.model.train(tagged_data, total_examples=self.model.corpus_count, epochs=self.model.epochs)

    def extract_features(self):
        return list(self.model.wv.key_to_index.keys())