"""Groups basic generative models."""

import pickle
import warnings
from abc import ABC, abstractmethod

import numpy as np

from .._core import _WeakLabelInfo
from .._typing import ListLike, MatrixLike


class _Model(_WeakLabelInfo, ABC):
    """Create a Model object."""

    def __init__(
        self,
        polarities: ListLike,
        cardinality: int = 0,
    ):
        """
        Parameters
        ----------
        polarities:
            List that maps weak labels to polarities, size n_weak.
        cardinality:
            Number of possible label values.

            If unspecified, it will be inferred from the maximum value in polarities.

        Example
        -------
        >>> polarities = [1, 0, 1, 1]
        >>> cardinality = 2
        >>> model = ModelClass(polarities, cardinality)
        """
        ABC.__init__(self)
        _WeakLabelInfo.__init__(self, polarities, cardinality)

    def save(self, filepath):
        """Save the model to a file.

        Parameters
        ----------
        filepath : str
            Path to the file where the model will be saved.

        Example
        -------
        >>> model.save("label_model.pkl")
        """
        with open(filepath, "wb") as file:
            pickle.dump(self, file)

    @classmethod
    def load(cls, filepath):
        """Load a saved model from a file.

        Parameters
        ----------
        filepath : str
            Path to the file containing the saved model.

        Returns
        -------
        The loaded model object.

        Example
        -------
        >>> model = ModelClass.load("label_model.pkl")
        """
        with open(filepath, "rb") as file:
            model = pickle.load(file)
        return model

    @abstractmethod
    def predict_proba(self, L: MatrixLike) -> np.ndarray:
        """Predict probabilites for the given weak label matrix.

        Parameters
        ----------
        L:
            Weak label dataframe.

            Shape: (n_samples, n_weak)

        Returns
        -------
            Array of predicted probabilities of shape (len(L), cardinality)


        Example
        -------
        >>> L = [[1, 0, 1, 2], [0, 1, 0, 0]]
        >>> proba = base_model.predict_proba(L)
        >>> # proba.shape = (len(L), cardinality)
        """
        pass

    def predict(self, L: MatrixLike, strategy: str = "majority") -> np.ndarray:
        """Predict labels for the given weak label matrix using the specified
        strategy.

        Parameters
        ----------
        L
            Weak label dataframe.

            Shape: (n_samples, n_weak)
        strategy
            Prediction strategy to use. Supported values: majority, probability.

            Controls how labels are predicted from the predicted probabilites.

            - majority: Predict the label with the highest number of votes.

            - probability: Predict label j with probability proba[i, j].

              This can be useful to enforce specific class_balances in the predictions.

            Default is "majority".

            If there are no votes for a sample, will predict -1.

        Returns
        -------
            1-D array of predicted labels of size n_samples

        Example
        -------
        >>> L = [[1, 0, 1, 2], [0, 1, 0, 0]]
        >>> predictions = base_model.predict(L)
        >>> # predictions.shape = (len(L),)
        """
        proba = self.predict_proba(L)
        unlabeled = proba.sum(axis=1) == 0
        if strategy == "majority":
            # Predict -1 if no votes were cast for all categories
            # Else predict the majority
            predictions = np.where(unlabeled, -1, proba.argmax(axis=1))
        elif strategy == "probability":
            # Predict -1 if no votes were cast for all categories
            # Else use probability matching / Thompson sampling
            filled_proba = proba.copy()
            filled_proba[unlabeled] = 1 / self.cardinality
            predictions = np.apply_along_axis(
                lambda x: np.random.choice(self.cardinality, p=x),
                axis=1,
                arr=filled_proba,
            )
            predictions = np.where(unlabeled, -1, predictions)
        else:
            raise ValueError('strategy should be "majority" or "probability"')

        return predictions


class Voter(_Model):
    """Basic model that bases its decisions on a sum of votes (optionally
    weighted) for each class."""

    def __init__(self, polarities: ListLike, cardinality: int = 0):
        super().__init__(polarities, cardinality)
        self.votes_weights = 1

    def _get_votes(self, L: MatrixLike) -> np.ndarray:
        """Compute the sum of votes for each label based on the given weak
        label matrix.

        Parameters
        ----------
        L : pd.DataFrame
            Weak label dataframe.

            Shape: (n_samples, n_weak)

        Returns
        -------
        votes : np.ndarray
            2-D array where votes[i.j] = sum votes for class j for sample i.

            Shape: (n_samples, n_classes)
        """
        L = np.array(L)
        votes = L @ self.polarities_matrix
        return votes

    def _normalize_preds(self, preds: np.ndarray) -> np.ndarray:
        # Normalize votes per row
        row_wise_sum = preds.sum(axis=1)
        # In case there were no votes for this row, no need to renormalize
        row_wise_sum = np.where(row_wise_sum == 0, 1, row_wise_sum).reshape(-1, 1)
        proba = preds / row_wise_sum
        return proba

    def fit(self, L: MatrixLike, class_balances: ListLike = []) -> None:
        """Fit the Voter model. This computes the weights for each class.

        Reweighing the votes help especially when specific classes have a
        high overlap in their weak labels.

        The weights are computed so the weighted sum of votes over
        training matches the given class balance.

        This guarantees mean(y_pred_proba_train) = class_balance.

        For majority voting, do not use fit.

        Parameters
        ----------
        L : pd.DataFrame
            Weak label dataframe.
        class_balances : ListLike
            Numpy array of shape cardinality giving a weight to each class.

            When unspecified, assumes all classes are equally likely.


        Example
        -------
        >>> L = [[1, 0, 1, 2], [0, 1, 2, 1], [1, 2, 1, 0], [0, 1, 0, 2]]
        >>> class_balances = [0.6, 0.4]
        >>> base_model.fit(L, class_balances)
        """
        if not class_balances:
            class_balances = np.ones(self.cardinality) / self.cardinality
        self.class_balances = np.array(class_balances)

        # Learn votes weights per class
        # vote weights is the factor that will reweigh the predicted probabilites

        # Compute the product between the weak label matrix and the polarities matrix
        # To get the sum of votes per label
        votes = self._get_votes(L)

        # Mean votes per class
        votes_mean = votes.mean(axis=0)
        # Deal with the case where there are no votes for a class
        no_votes = np.where(votes_mean == 0)[0]
        if no_votes.size > 0:
            for i in no_votes:
                warnings.warn(
                    (
                        f"No votes were given to labeling function {i},"
                        "assuming its balance is correct which is likely wrong"
                    ),
                    UserWarning,
                )
            votes_mean[no_votes] = self.class_balances[no_votes]
        votes_weights = self.class_balances / votes_mean
        self.votes_weights = votes_weights

    def predict_proba(self, L: MatrixLike) -> np.ndarray:
        """Predict probabilites using weighted voting.

        Parameters
        ----------
        L : pd.DataFrame
            Weak label dataframe.

        Returns
        -------
            Array of predicted probabilities of shape (len(L), cardinality)

        Example
        -------
        >>> L = [[1, 0, 1, 2], [0, 1, 0, 0]]
        >>> proba = snorkel_model.predict_proba(L)
        >>> # proba.shape = (len(L), cardinality)
        """
        votes = self._get_votes(L)
        weighted_votes = votes * self.votes_weights
        proba = self._normalize_preds(weighted_votes)
        return proba
