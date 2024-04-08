from typing import List, Union, Any

import torch
from transformers import BertModel, BertTokenizer

from swarmauri.core.vectorizers.IVectorize import IVectorize
from swarmauri.core.vectors.IVector import IVector

from swarmauri.standard.vectors.concrete.SimpleVector import SimpleVector

class BERTEmbeddingVectorizer(IVectorize):
    """
    A vectorizer that generates embeddings for input text using a BERT model.
    """
    
    def __init__(self, model_name: str = 'bert-base-uncased'):
        """
        Initializes the BERTEmbeddingVectorizer with a specified BERT model.
        
        Parameters:
        - model_name (str): The name of the pre-trained BERT model to use.
        """
        self.tokenizer = BertTokenizer.from_pretrained(model_name)
        self.model = BertModel.from_pretrained(model_name)
        self.model.eval()  # Set model to evaluation mode for inference
    

    
    def fit(self, data: Union[str, Any]) -> List[IVector]:
        """
        Vectorizes input data using the BERT model to generate embeddings.

        Parameters:
        - data (Union[str, Any]): The input data to be vectorized, expected to be text.

        Returns:
        - List[IVector]: A list of IVector instances representing the generated BERT embeddings.
        """
        # Tokenization
        inputs = self.tokenizer(data, return_tensors='pt', padding=True, truncation=True, max_length=512)

        # Generate embeddings
        with torch.no_grad():
            outputs = self.model(**inputs)

        # Use the last hidden state as the embeddings (batch_size, sequence_length, hidden_size)
        embeddings = outputs.last_hidden_state

        # Convert embeddings to SimpleVector instances
        vectorized_data = []
        for embedding in embeddings:
            # Flatten the embeddings or take mean/max pooling across the sequence_length dimension if needed
            vector = SimpleVector(embedding.mean(dim=0).cpu().numpy().tolist())  # Taking mean across the token embeddings
            vectorized_data.append(vector)

        return vectorized_data
    
    def transform(self):
        raise NotImplementedError('Transform not yet implemented on BERTEmbeddingVectorizer class.')