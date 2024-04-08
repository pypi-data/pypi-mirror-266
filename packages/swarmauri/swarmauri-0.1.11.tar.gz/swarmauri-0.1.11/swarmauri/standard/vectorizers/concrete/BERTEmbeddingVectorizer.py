from typing import List
from transformers import BertModel, BertTokenizer
import torch
from swarmauri.core.vectors.IVector import IVector
from swarmauri.standard.vectors.concrete.SimpleVector import SimpleVector

class BERTEmbeddingVectorizer:
    def __init__(self, model_name: str = 'bert-base-uncased'):
        self.tokenizer = BertTokenizer.from_pretrained(model_name)
        self.model = BertModel.from_pretrained(model_name)
        self.model.eval()

    def fit(self, documents: List[str], labels=None) -> None:
        raise NotImplementedError('Fit not yet implemented on BERTEmbeddingVectorizer class.')

    def transform(self, documents: List[str], labels=None) -> None:
        raise NotImplementedError('Fit not yet implemented on BERTEmbeddingVectorizer class.')

    def infer_vector(self, document: str) -> IVector:
        """
        Function to infer a BERT embedding for a single document, intended for inference.
        Wrap the forward pass in torch.no_grad() as gradients are not needed.
        """
        self.model.eval()  # Set the model to evaluation mode
        with torch.no_grad():
            inputs = self.tokenizer([document], return_tensors='pt', padding=True, truncation=True, max_length=512)
            outputs = self.model(**inputs)
            embeddings = outputs.last_hidden_state.mean(dim=1)

            return SimpleVector(embeddings.detach().numpy().tolist())  # Convert to SimpleVector and return