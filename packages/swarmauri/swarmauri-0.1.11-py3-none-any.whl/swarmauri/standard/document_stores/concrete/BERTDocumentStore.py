from typing import List, Union, Optional
from swarmauri.core.documents.IDocument import IDocument
from swarmauri.core.document_stores.IDocumentStore import IDocumentStore
from swarmauri.core.retrievers.IRetriever import IRetriever
from swarmauri.standard.documents.concrete.EmbeddedDocument import EmbeddedDocument
from swarmauri.standard.vectorizers.concrete.BERTEmbeddingVectorizer import BERTEmbeddingVectorizer
from swarmauri.standard.vector_stores.concrete.CosineDistance import CosineDistance

class BERTDocumentStore(IDocumentStore, IRetriever):
    def __init__(self):
        self.documents: List[EmbeddedDocument] = []
        self.vectorizer = BERTEmbeddingVectorizer()  # Assuming this is already implemented
        self.metric = CosineDistance()

    def add_document(self, document: IDocument) -> None:
        embeddings = self.vectorizer.infer_vector(document.content)
        embedded_document = EmbeddedDocument(doc_id=document.id, content=document.content, metadata=document.metadata, embedding=embeddings)
        self.documents.append(embedded_document)

    def add_documents(self, documents: List[IDocument]) -> None:
        for doc in documents:
            self.add_document(doc)

    def get_document(self, doc_id: str) -> Union[EmbeddedDocument, None]:
        for document in self.documents:
            if document.id == doc_id:
                return document
        return None
        
    def get_all_documents(self) -> List[EmbeddedDocument]:
        return self.documents

    def delete_document(self, doc_id: str) -> None:
        self.documents = [doc for doc in self.documents if doc.id != doc_id]

    def update_document(self, doc_id: str) -> None:
        pass
        
    def retrieve(self, query: str, top_k: int = 5) -> List[IDocument]:
        query_vector = self.vectorizer.infer_vector(query)
        embeddings = [doc.embedding for doc in self.documents]
        similarities = self.metric.similarities(query_vector, embeddings)
    
        top_k_indices = sorted(range(len(self.documents)), key=lambda i: similarities[i])[:top_k]
        return [self.documents[i] for i in top_k_indices]