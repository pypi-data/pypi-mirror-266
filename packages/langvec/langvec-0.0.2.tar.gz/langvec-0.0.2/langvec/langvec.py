import os
import tempfile
import zipfile
from typing import List, Tuple

import numpy as np

from .constants import LEXICON, MAX_SAMPLES, BATCH_SIZE

os.environ["OMP_NUM_THREADS"] = "12"


class LangVec:
    def __init__(self, lexicon: List[str] = LEXICON, chunk_size: int = 3):
        self.lexicon = lexicon
        self.lexicon_size = len(lexicon)
        self._lexicon_distribution = self._initialize_lexicon_distribution()
        self.chunk_size = chunk_size
        self.percentiles = None

    def _initialize_lexicon_distribution(self) -> Tuple[float, ...]:
        """
        Initialize the lexicon distribution based on the lexicon size.
        Returns:
            Tuple[float, ...]: A tuple of floats representing the lexicon distribution.
        """
        if self.lexicon_size <= 1:
            return (50,)  # Default to median if only one word
        return tuple(np.linspace(0, 100, self.lexicon_size + 1)[1:-1])

    def _calculate_percentiles(self, data: np.ndarray) -> None:
        """
        Calculate percentiles from the input data using the lexicon distribution.
        Args:
            data (np.ndarray): The input data as a NumPy array.
        """
        self.percentiles = np.percentile(data, self._lexicon_distribution)

    def _validate_input(self, X: List[np.ndarray]):
        """
        Validate the input data as a list of 1-dimensional NumPy arrays.
        Args:
            X (List[np.ndarray]): The input data as a list of NumPy arrays.
        Returns:
            List[np.ndarray]: The validated input data.
        Raises:
            TypeError: If the input data is not a list of NumPy arrays.
            ValueError: If the input NumPy arrays are not 1-dimensional.
        """
        if not (isinstance(X, list) or isinstance(X, np.ndarray)):
            raise TypeError("❌ Input data must be provided as a list of numpy arrays.")

        if not all(isinstance(x, np.ndarray) for x in X):
            raise TypeError("❌ Each element of the input list must be a numpy array.")

        if any(x.ndim != 1 for x in X):
            raise ValueError(
                "❌ Each numpy array in the input list must be 1-dimensional."
            )

        return X

    def fit(
        self,
        X: List[np.ndarray],
        max_samples: int = MAX_SAMPLES,
        batch_size: int = BATCH_SIZE,
    ):
        """
        Fit the LangVec model to the input data using batch processing.
        Args:
            X (List[np.ndarray]): The input data as a list of NumPy arrays.
            max_samples (int, optional): The maximum number of samples to use for fitting.
            batch_size (int, optional): The size of the batch or chunk to process at a time.
        Raises:
            ValueError: If there is an error in fitting the data.
        """
        self._validate_input(X)

        try:
            num_batches = (len(X) + batch_size - 1) // batch_size
            combined_percentiles = None

            for batch_idx in range(num_batches):
                start = batch_idx * batch_size
                end = start + batch_size
                batch_data = X[start:end]

                # Process the batch data
                elements = np.concatenate(batch_data)
                if elements.shape[0] > max_samples:
                    sample_indices = np.random.choice(
                        elements.shape[0], size=max_samples, replace=False
                    )
                    elements = elements[sample_indices]

                batch_percentiles = np.percentile(elements, self._lexicon_distribution)

                # Combine the batch percentiles with the previous percentiles
                if combined_percentiles is None:
                    combined_percentiles = batch_percentiles
                else:
                    combined_percentiles = np.concatenate(
                        (combined_percentiles, batch_percentiles)
                    )

            self._calculate_percentiles(combined_percentiles)

        except ValueError as e:
            raise ValueError(f"❌ Error in fitting data: {e}")

    def predict(
        self,
        input_vector: np.ndarray,
        chunk_size: int = 3,
        summarized: bool = False,
        padding: bool = True,
    ) -> List[str]:
        """
        Predict words from the input vector based on the learned distribution.
        Args:
            input_vector (np.ndarray): The input vector as a 1-dimensional NumPy array.
            chunk_size (int, optional): The size of the chunks to split the input vector into.
            summarized (bool, optional): Whether to summarize the predicted words if their count exceeds 6.
            padding (bool, optional): Whether to pad the last chunk with zeros if it has fewer elements than chunk_size.
        Returns:
            List[str]: A list of predicted words.
        Raises:
            ValueError: If the model is not fitted or loaded, if the input vector is not 1-dimensional, or if the chunk size is invalid.
        """
        if not isinstance(self.percentiles, np.ndarray) or len(self.percentiles) == 0:
            raise ValueError(
                "❌ Model not fitted or loaded. Call 'fit' or 'load' with appropriate data before prediction."
            )

        if not isinstance(input_vector, np.ndarray) or input_vector.ndim != 1:
            raise ValueError("❌ Input vector must be a 1-dimensional numpy array.")

        if not isinstance(chunk_size, int) or chunk_size <= 0:
            raise ValueError("❌ Chunk size must be a positive integer.")

        if self.lexicon_size - 1 != len(self.percentiles):
            raise ValueError(
                "❌ Lexicon size does not match learned distribution. Maybe you used different lexicon on training?"
            )

        words_for_vector = []
        for i in range(0, len(input_vector), chunk_size):
            chunk = input_vector[i : i + chunk_size]
            if len(chunk) < chunk_size:
                if padding:
                    # Pad the last chunk with zeros if it has fewer elements than chunk_size
                    chunk = np.pad(chunk, (0, chunk_size - len(chunk)), mode="constant")
                else:
                    # Trim the last chunk if padding is not desired
                    continue
            word_index = sum(np.mean(chunk) > self.percentiles)
            words_for_vector.append(self.lexicon[word_index])

        if summarized and len(words_for_vector) > 6:
            return words_for_vector[:3] + ["....."] + words_for_vector[-3:]
        return words_for_vector

    def save(self, filepath: str) -> None:
        """
        Save the LangVec model to a file.
        Args:
            filepath (str): The path to save the model to.
        Raises:
            ValueError: If the model is not fitted.
        """
        if self.percentiles is None:
            raise ValueError("❌ Model not fitted. Call 'fit' before saving.")

        # Create a temporary directory to store the model artifacts
        with tempfile.TemporaryDirectory() as tmp_dir:
            percentiles_filepath = os.path.join(tmp_dir, "percentiles.npy")
            np.save(percentiles_filepath, self.percentiles)

            # Create a zip file and add the model artifacts
            with zipfile.ZipFile(filepath, "w") as zipf:
                zipf.write(percentiles_filepath, arcname="percentiles.npy")

    def load(self, filepath: str) -> None:
        """
        Load a LangVec model from a file.
        Args:
            filepath (str): The path to load the model from.
        """
        with zipfile.ZipFile(filepath, "r") as zipf:
            # Extract the model artifacts to a temporary directory
            with tempfile.TemporaryDirectory() as tmp_dir:
                zipf.extractall(tmp_dir)
                percentiles_filepath = os.path.join(tmp_dir, "percentiles.npy")

                # Load the percentiles from the extracted file
                self.percentiles = np.load(percentiles_filepath)

    def update(self, X: List[np.ndarray], max_samples: int = MAX_SAMPLES) -> None:
        """
        Update the LangVec model with new data.
        Args:
            X (List[np.ndarray]): The new data as a list of NumPy arrays.
            max_samples (int, optional): The maximum number of samples to use for updating.
        Raises:
            ValueError: If there is an error in updating the data.
        """
        self._validate_input(X)

        try:
            elements = np.concatenate(X)
            if elements.shape[0] > max_samples:
                # Perform random sampling if the number of elements exceeds max_samples
                sample_indices = np.random.choice(
                    elements.shape[0], size=max_samples, replace=False
                )
                elements = elements[sample_indices]

            # Calculate percentiles for the new data
            new_percentiles = np.percentile(elements, self._lexicon_distribution)

            # Combine the new percentiles with the existing percentiles
            if self.percentiles is not None:
                combined_percentiles = np.concatenate(
                    (self.percentiles, new_percentiles)
                )
            else:
                combined_percentiles = new_percentiles

            # Recalculate the percentiles using the combined percentiles
            self.percentiles = np.percentile(
                combined_percentiles, self._lexicon_distribution
            )

        except ValueError as e:
            raise ValueError(f"❌ Error in updating data: {e}")

    def info(self) -> None:
        print("📦LangVec model info:")
        print(f"✔ Lexicon size: {self.lexicon_size}")
        print(f"✔ Chunk size: {self.chunk_size}")
        percentiles_count = len(self.percentiles) if self.percentiles is not None else 0
        model_fitted = "yes" if self.percentiles is not None else "no"
        print(f"✔ Percentiles count: {percentiles_count}")
        print(f"✔ Model fitted: {model_fitted}")
