from typing import List, Union
from swarmauri.core.documents.IDocument import IDocument
from swarmauri.core.document_stores.IDocumentStore import IDocumentStore
from swarmauri.core.retrievers.IRetriever import IRetriever
from swarmauri.standard.vectorizers.concrete.Doc2VecVectorizer import Doc2VecVectorizer
from swarmauri.standard.vector_stores.concrete.CosineDistance import CosineDistance

class Doc2VecDocumentStore(IDocumentStore, IRetriever):
    def __init__(self):
        self.vectorizer = Doc2VecVectorizer()
        self.metric = CosineDistance()
        self.documents = []      

    def add_document(self, document: IDocument) -> None:
        self.documents.append(document)
        # Recalculate document embeddings for the current set of documents
        self.vectorizer.fit([doc.content for doc in self.documents if doc.content])

    def add_documents(self, documents: List[IDocument]) -> None:
        self.documents.extend(documents)
        # Recalculate document embeddings for the current set of documents
        self.vectorizer.fit([doc.content for doc in self.documents if doc.content])

    def get_document(self, doc_id: str) -> Union[IDocument, None]:
        for document in self.documents:
            if document.id == doc_id:
                return document
        return None

    def get_all_documents(self) -> List[IDocument]:
        return self.documents

    def delete_document(self, doc_id: str) -> None:
        self.documents = [doc for doc in self.documents if doc.id != doc_id]
        # Recalculate document embeddings for the current set of documents
        self.vectorizer.fit([doc.content for doc in self.documents if doc.content])

    def update_document(self, doc_id: str, updated_document: IDocument) -> None:
        for i, document in enumerate(self.documents):
            if document.id == doc_id:
                self.documents[i] = updated_document
                break
        # Recalculate document embeddings for the current set of documents
        self.vectorizer.fit([doc.content for doc in self.documents if doc.content])

    def retrieve(self, query: str, top_k: int = 5) -> List[IDocument]:
        query_vector = self.vectorizer.infer_vector(query)
        document_vectors = self.vectorizer.transform([doc.content for doc in self.documents if doc.content])

        distances = self.metric.distances(query_vector, document_vectors)

        # Get the indices of the top_k least distant (most similar) documents
        top_k_indices = sorted(range(len(distances)), key=lambda i: distances[i])[:top_k]
        
        return [self.documents[i] for i in top_k_indices]

    def document_count(self):
        return len(self.documents)