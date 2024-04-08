from sklearn.feature_extraction.text import TfidfVectorizer as SklearnTfidfVectorizer
from typing import List, Union, Any
from swarmauri.core.vectorizers.IVectorize import IVectorize
from swarmauri.core.vectors.IVector import IVector
from swarmauri.standard.vectors.concrete.SimpleVector import SimpleVector

class TFIDFVectorizer(IVectorize):
    def __init__(self):
        # Using scikit-learn's TfidfVectorizer as the underlying mechanism
        self.tfidf_vectorizer = SklearnTfidfVectorizer()
        super().__init__()
        
    def extract_features(self):
        return self.tfidf_vectorizer.get_feature_names_out()

    def fit(self, data: Union[str, Any]) -> List[IVector]:
        """
        Vectorizes the input data using the TF-IDF scheme.

        Parameters:
        - data (Union[str, Any]): The input data to be vectorized. Expected to be a single string (document)
                                  or a list of strings (corpus).

        Returns:
        - List[IVector]: A list containing IVector instances, each representing a document's TF-IDF vector.
        """
        if isinstance(data, str):
            data = [data]  # Convert a single string into a list for the vectorizer
        
        tfidf_matrix = self.tfidf_vectorizer.fit_transform(data)

        # Convert the sparse matrix rows into SimpleVector instances
        vectors = [SimpleVector(vector.toarray().flatten()) for vector in tfidf_matrix]

        return vectors
    
    def transform(self, data: Union[str, Any]) -> List[IVector]:
        """
        Vectorizes the input data using the TF-IDF scheme.

        Parameters:
        - data (Union[str, Any]): The input data to be vectorized. Expected to be a single string (document)
                                  or a list of strings (corpus).

        Returns:
        - List[IVector]: A list containing IVector instances, each representing a document's TF-IDF vector.
        """
        if isinstance(data, str):
            data = [data]  # Convert a single string into a list for the vectorizer
        
        tfidf_matrix = self.tfidf_vectorizer.fit_transform(data)

        # Convert the sparse matrix rows into SimpleVector instances
        vectors = [SimpleVector(vector.toarray().flatten()) for vector in tfidf_matrix]

        return vectors