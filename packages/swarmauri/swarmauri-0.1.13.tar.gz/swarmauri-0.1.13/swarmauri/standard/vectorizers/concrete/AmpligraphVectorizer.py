from typing import List, Union, Any
from ampligraph.latent_features import ScoringBasedEmbeddingModel
from swarmauri.core.vectorizers.IVectorize import IVectorize
from swarmauri.core.vectorizers.IFeature import IFeature
from swarmauri.core.vectors.IVector import IVector
from swarmauri.standard.vectors.concrete.SimpleVector import SimpleVector

class AmpligraphVectorizer(IVectorize, IFeature):
    def __init__(self, model: Union[str, EmbeddingModel]):
        """
        Initialize the AmpligraphVectorizer.

        Parameters:
        - model (Union[str, EmbeddingModel]): Either the path to a saved model or an instance of an EmbeddingModel.
        """
        self.model = ScoringBasedEmbeddingModel(k=150,
                                   eta=10,
                                   scoring_type='ComplEx',
                                   seed=0)

    def extract_features(self) -> List[str]:
        raise NotImplementedError("AmpligraphVectorizer does not support feature extraction.")

    def fit(self, data: Union[str, Any]) -> List[IVector]:
        optim = tf.keras.optimizers.Adam(learning_rate=1e-3)
        loss = get_loss('pairwise', {'margin': 0.5})
        regularizer = get_regularizer('LP', {'p': 2, 'lambda': 1e-5})
        self.model.compile(optimizer=optim, loss=loss, entity_relation_regularizer=regularizer)
        # Fit the model on training and validation set
        model.fit(X['train'],
                  batch_size=int(X['train'].shape[0] / 10),
                  epochs=20,                    # Number of training epochs
                  validation_freq=20,           # Epochs between successive validation
                  validation_burn_in=100,       # Epoch to start validation
                  validation_data=X['valid'],   # Validation data
                  validation_filter=filter,     # Filter positives from validation corruptions
                  callbacks=[checkpoint],       # Early stopping callback (more from tf.keras.callbacks are supported)
                  verbose=True                  # Enable stdout messages
                  )


    def transform(self, data: Union[str, Any]) -> List[IVector]:
        raise NotImplementedError("AmpligraphVectorizer transform method is not implemented. Please use infer_vector instead.")

    def infer_vector(self, data: Union[str, Any]) -> IVector:
        """
        Generates an embedding for the input data.

        Parameters:
        - data (Union[str, Any]): The input data, expected to be a textual representation of an RDF triple
                                  or a list of textual representations if batching.

        Returns:
        - IVector: An instance of IVector containing the generated embedding.
        """
        if isinstance(data, str):
            data = [data.split()]
        elif isinstance(data, list):
            data = [d.split() for d in data]
        else:
            raise TypeError("Data must be a string or a list of strings.")

        # Generate embeddings
        embeddings = self.model.predict(data)
        return SimpleVector(embeddings[0] if embeddings.ndim == 1 else embeddings.mean(axis=0))