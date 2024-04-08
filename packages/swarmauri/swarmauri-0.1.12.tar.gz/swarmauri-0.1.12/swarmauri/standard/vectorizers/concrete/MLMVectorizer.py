from typing import List, Union, Any
import torch
import numpy as np
from torch.utils.data import TensorDataset, DataLoader
from torch.optim import AdamW
from transformers import AutoModelForMaskedLM, AutoTokenizer
from sklearn.model_selection import train_test_split
from torch.utils.data import Dataset
from swarmauri.core.vectorizers.IVectorize import IVectorize
from swarmauri.core.vectors.IVector import IVector
from swarmauri.standard.vectors.concrete.SimpleVector import SimpleVector


class MLMVectorizer(IVectorize):
    """
    IVectorize implementation that fine-tunes a Masked Language Model (MLM).
    """

    def __init__(self, model_name='bert-base-uncased', masking_ratio: float = 0.15, randomness_ratio: float = 0.10):
        """
        Initializes the vectorizer with a pre-trained MLM model and tokenizer for fine-tuning.
        
        Parameters:
        - model_name (str): Identifier for the pre-trained model and tokenizer.
        """
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForMaskedLM.from_pretrained(model_name)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        self.masking_ratio = masking_ratio
        self.randomness_ratio = randomness_ratio
        self.mask_token_id = self.tokenizer.convert_tokens_to_ids([self.tokenizer.mask_token])[0]

    def extract_features(self):
        raise NotImplementedError('Extract_features not implemented on MLMVectorizer.')

    def _mask_tokens(self, encodings):
        """
        Masks tokens according to the masking ratio.

        Parameters:
        - encodings: Tokenized inputs (output of tokenizer's encode_plus or batch_encode_plus).

        Returns:
        - input_ids (torch.Tensor): Tensor of token IDs to be fed to the model.
        - attention_mask (torch.Tensor): Tensor denoting which tokens should be attended to by the model.
        - labels (torch.Tensor): Tensor with the original token IDs (with other tokens set to -100 for ignoring in loss computation).
        """
        # Convert lists to PyTorch tensors
        input_ids = encodings.input_ids
        attention_mask =encodings.attention_mask

        # Create a copy of input_ids to be used as labels
        labels = input_ids.detach().clone()

        # Determine which tokens to mask for MLM objective
        # We don't mask special tokens ([CLS], [SEP]) hence set their probability to 0
        probability_matrix = torch.full(labels.shape, self.masking_ratio)
        special_tokens_mask = [
            self.tokenizer.get_special_tokens_mask(val, already_has_special_tokens=True) for val in labels.tolist()
        ]
        probability_matrix.masked_fill_(torch.tensor(special_tokens_mask, dtype=torch.bool), value=0.0)
        masked_indices = torch.bernoulli(probability_matrix).bool()

        # Apply the masking: for MLM, 80% MASK, 10% random, 10% original token
        labels[~masked_indices] = -100  # We only compute loss on masked tokens
        
        # % of the time, we replace masked input tokens with tokenizer.mask_token ([MASK])
        indices_replaced = torch.bernoulli(torch.full(labels.shape, self.masking_ratio)).bool() & masked_indices
        input_ids[indices_replaced] = self.mask_token_id

        # % of the time, we replace masked input tokens with random word
        indices_random = torch.bernoulli(torch.full(labels.shape, self.randomness_ratio)).bool() & masked_indices & ~indices_replaced
        random_words = torch.randint(len(self.tokenizer), labels.shape, dtype=torch.long)
        input_ids[indices_random] = random_words[indices_random]

        # The rest of the time  we keep the masked input tokens unchanged

        return input_ids, attention_mask, labels

    # work on this
    def fit(self, documents, epochs=1, batch_size=8, learning_rate=5e-5):
        encodings = self.tokenizer(documents, return_tensors='pt', padding=True, truncation=True, max_length=512).to(self.device)
        input_ids, attention_mask, labels = self._mask_tokens(encodings)       
        optimizer = AdamW(self.model.parameters(), lr=learning_rate)
        dataset = TensorDataset(input_ids, attention_mask, labels)
        data_loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

        self.model.train()

        for epoch in range(epochs):
            for batch in data_loader:
                # Move batch to the correct device
                batch = {k: v.to(self.device) for k, v in zip(['input_ids', 'attention_mask', 'labels'], batch)}
                
                outputs = self.model(**batch)
                loss = outputs.loss

                # Backpropagation
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

            print(f"Epoch {epoch+1}: Loss {loss.item()}")

        print("MLMVectorizer training completed.")



    def transform(self, documents: List[Union[str, Any]]) -> List[IVector]:
        """
        Generates embeddings for a list of documents using the fine-tuned MLM.
        """
        list_of_embeddings = []
        
        for document in documents:
            inputs = self.tokenizer(document, return_tensors='pt', padding=True, truncation=True, max_length=512)
            with torch.no_grad():
                outputs = self.model(**inputs)
            # Extract embedding (for simplicity, averaging the last hidden states)
            if hasattr(outputs, 'last_hidden_state'):
                embedding = outputs.last_hidden_state.mean(1)
            else:
                # Fallback or corrected attribute access
                embedding = outputs['logits'].mean(1)
            list_of_embeddings.append(SimpleVector(embedding.squeeze().tolist()))

        return list_of_embeddings

    def fit_transform(self, documents: List[Union[str, Any]], **kwargs) -> List[IVector]:
        """
        Fine-tunes the MLM and generates embeddings for the provided documents.
        """
        self.fit(documents, **kwargs)
        return self.transform(documents)

    def infer_vector(self, document):
        inputs = self.tokenizer(document, return_tensors="pt", padding=True, truncation=True, max_length=512)
            
        # Existing preprocessing
        with torch.no_grad():
            outputs = self.model(**inputs)
            # Adjusted to correctly access embeddings
            if hasattr(outputs, 'last_hidden_state'):
                embedding = outputs.last_hidden_state.mean(1)
            else:
                # Fallback or corrected attribute access
                embedding = outputs['logits'].mean(1)
            return SimpleVector(embedding.squeeze().tolist())
        
