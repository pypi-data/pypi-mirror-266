from __future__ import annotations
import warnings
from typing import Union, Dict
from abc import abstractmethod
import numpy as np
from numpy.typing import ArrayLike
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.utils.class_weight import compute_sample_weight

from ..aux_classes import Coefficients, Rule
from ..rule_cost import RuleCost
from ..utils import check_inputs
from ..solver.base import OptimizationSolver


class _RUGBASE(BaseEstimator, ClassifierMixin):
    """
    The foundational class for all estimators in the ruleopt library. `_RUGBASE` provides
    the core framework that every model in ruleopt builds upon.

    Parameters
    ----------
    solver : OptimizationSolver
        An instance of a derived class inherits from the 'Optimization Solver' base class.
        The solver is responsible for optimizing the rule set based on the cost function
        and constraints.

    rule_cost : RuleCost or int
        Defines the cost of rules, either as a specific calculation method (RuleCost instance)
        or a fixed cost

    class_weight: dict, "balanced" or None
        A dictionary mapping class labels to their respective weights, the string "balanced"
        to automatically adjust weights inversely proportional to class frequencies,
        or None for no weights. Used to adjust the model in favor of certain classes.

    threshold : float
        The minimum weight threshold for including a rule in the final model

    random_state : int or None
        Seed for the random number generator to ensure reproducible results.
        Defaults to None.
    """

    def __init__(
        self,
        solver: OptimizationSolver,
        rule_cost: Union[RuleCost, int],
        class_weight: Dict[int, float],
        threshold: float,
        random_state: Union[None, int],
    ):

        self._validate_rug_parameters(
            threshold=threshold,
            random_state=random_state,
            rule_cost=rule_cost,
            solver=solver,
            class_weight=class_weight,
        )
        self.threshold = float(threshold)
        self.rule_cost = rule_cost
        self.solver = solver
        self.random_state = random_state
        self.class_weight = class_weight

        # Additional initializations
        self._rng = np.random.default_rng(
            random_state if random_state is not None else None
        )
        self.decision_trees_ = {}
        self.decision_rules_ = {}
        self.rule_info_ = {}
        self.coefficients_ = Coefficients()

        self._is_fitted: bool = False
        self.majority_class_: int = None
        self.majority_probability_: float = None
        self.k_: float = None
        self.classes_: np.array = None
        self.rule_columns_: np.array = None

    def _cleanup(self) -> None:
        """
        Clean up the model by resetting all of its attributes.
        """
        # Resetting all dictionaries
        self.decision_trees_ = {}
        self.decision_rules_ = {}
        self.rule_info_ = {}

        # Cleaning up coefficients
        self.coefficients_.cleanup()

        # Resetting the random number generator
        self._rng = np.random.default_rng(self.random_state)

    @abstractmethod
    def _get_rule(self, *arg, **kwargs) -> Rule: ...

    @abstractmethod
    def _get_matrix(self, *arg, **kwargs) -> None: ...

    def _get_class_infos(self, y: np.ndarray) -> None:
        """
        Computes and stores information about the classes in the dataset.

        This method calculates the majority class, its probability, the total number
        of unique classes, and stores an array of unique class labels.

        Parameters
        ----------
        y : np.ndarray
            The target values, expected to be a 1D numpy array of class labels.

        Sets Attributes
        ---------------
        majority_class_ : int
            The class label with the highest frequency in `y`.
        majority_probability_ : float
            The proportion of samples in `y` belonging to the majority class,
            calculated as the count of the majority class divided by the total number of samples.
        k_ : float
            The total number of unique classes in `y`.
        classes_ : np.array
            An array of the unique class labels present in the dataset.
        """
        classes, class_counts = np.unique(y, return_counts=True)

        self.majority_class_ = classes[np.argmax(class_counts)]
        self.majority_probability_ = class_counts / np.sum(class_counts)

        self.k_ = classes.shape[0]
        self.classes_ = classes

    def _preprocess(self, y: np.ndarray) -> np.ndarray:
        """
        Transforms the target values into a vector. If the target
        class is k and there are K classes, then all components but
        the kth are set to -1/(K-1) and the kth component is set to 1. 

        Parameters
        ----------
        y : np.ndarray
            The target values as a 1D numpy array of class labels.

        Returns
        -------
        np.ndarray
            The preprocessed target values in a one-hot-encoded format, adjusted for the model's
            optimization process.
        """

        # Convert the labels into kth unit vector
        vec_y = np.eye(self.k_)[y]

        # Replace 0s with -1/(K-1)
        vec_y[vec_y == 0] = -1 / (self.k_ - 1)

        return vec_y

    def _get_rule_cost(
        self, temp_rule: Rule, covers: np.ndarray, counts: np.ndarray, y: np.ndarray
    ) -> float:
        """
        Calculates the cost of a rule.

        Depending on the `rule_cost` attribute, this method either calls a custom cost
        function defined in a `RuleCost` instance or returns a fixed cost for the rule.

        Parameters
        ----------
        temp_rule : Rule
            The rule for which the cost is being calculated.
        covers : np.ndarray
            An array indicating whether each instance in the dataset is covered by the rule.
        counts : np.ndarray
            An array indicating the count of instances covered by the rule, segmented by class.
        y : np.ndarray
            The target array, containing the actual class labels of the instances.

        Returns
        -------
        float
            The calculated cost of the rule.
        """

        if isinstance(self.rule_cost, RuleCost):
            return self.rule_cost(
                temp_rule=temp_rule, covers=covers, counts=counts, y=y
            )
        elif isinstance(self.rule_cost, int):
            return self.rule_cost
        else:
            raise TypeError(
                f"Unsupported type for `rule_cost`: {type(self.rule_cost)}.",
                "Expected a RuleCost instance or an int.",
            )

    def _fill_rules(self, weights: np.ndarray) -> None:
        """
        Selects and stores rules based on their weights and a predefined threshold.

        Parameters
        ----------
        weights : np.ndarray
            An array containing the weights of each rule.

        Modifies
        --------
        rule_columns_ : np.ndarray
            Updated to include indices of the selected rules, ordered by their weight.
        decision_rules_ : Dict[int, Rule]
            Populated with the selected and ordered rules, keyed by their new indices.
        """
        # Scale the weights
        max_weight = np.max(weights)
        if max_weight != 1 and max_weight > 1.0e-6:
            weights = np.divide(weights, max_weight)

        # Select columns where weights are above the threshold
        selected_columns = np.where(weights > self.threshold)[0]

        # Order the selected columns by their weights
        weight_order = np.argsort(-weights[selected_columns])
        ordered_columns = selected_columns[weight_order]

        # Assign the ordered columns to the class attribute
        self.rule_columns_ = ordered_columns

        # Iterate over the columns and fill the rules dictionary
        for i, col in enumerate(ordered_columns):
            treeno, leafno, label, sdist = self.rule_info_[col]
            fit_tree = self.decision_trees_[treeno]
            rule = self._get_rule(fit_tree, leafno)
            rule.label = label
            rule.weight = weights[col]
            rule.sdist = sdist
            self.decision_rules_[i] = rule

    def _predict_base(
        self,
        x: np.ndarray,
        indices: list = None,
        threshold: float = 0,
        *,
        predict_info=False,
    ) -> np.ndarray:
        """
        Calculates the base class weights for each instance based on selected rules.
        Optionally returns additional prediction info.

        Parameters
        ----------
        x : np.ndarray
            The feature matrix for the instances to predict.
        indices : list, optional
            Specific indices of rules to use for prediction. If None, all rules
            are used.
        threshold : float, default=0
            The threshold for selecting rules based on their weights.
        predict_info : bool, default=False
            If True, returns additional information about the prediction process
            including indices of samples with missed values, number of rules
            applied per sample, and average rule length per sample. Otherwise,
            returns only the array of raw class weights.

        Returns
        -------
        np.ndarray
            An array of raw class weights for each instance, used as the basis for final
            prediction.
            If predict_info is True, also returns arrays containing indices of samples
            with missed values, number of rules applied per sample, and average rule
            length per sample.
        """

        # Check if the model has been fitted
        if indices is None:
            indices = []
        if not self.decision_trees_:
            raise ValueError("You need to fit the RUG model first")

        # If no specific indices are provided, use all rule indices
        if len(indices) == 0:
            indices = list(self.decision_rules_.keys())

        # If provided indices exceed the available rules, return a warning
        elif np.max(indices) > len(self.decision_rules_):
            warnings.warn(f"\n There are only {len(self.decision_rules_)} rules")
            return None

        rule_lengths = np.zeros(x.shape[0], dtype=np.intp)
        sum_class_weights_arr = np.empty(shape=(x.shape[0], self.k_), dtype=np.float64)

        # Initialize arrays to track missing values and rule lengths per sample
        missed_values_index_ = np.empty((0,), dtype=np.intp)
        rules_per_sample_ = np.zeros(x.shape[0], dtype=np.intp)
        rule_length_per_sample_ = np.zeros(x.shape[0], dtype=np.float64)

        # Iterate over each sample in the feature matrix x
        for sindx, x0 in enumerate(x):
            # Initialize an array to hold class weights for this sample
            sum_class_weights = np.zeros(self.k_, dtype=np.float64)
            rule_lengths[sindx] = 0

            # Iterate over each rule and apply it to the sample
            for indx, rule in self.decision_rules_.items():
                # Only apply the rule if its index is in the specified indices,
                # it applies to the sample, and its weight is above the threshold
                if indx in indices and rule.check_rule(x0) and rule.weight >= threshold:
                    # Add the weight of the rule to the weight for its class
                    sum_class_weights[rule.label] += rule.weight
                    # Increment the count of rules applied to this sample
                    rules_per_sample_[sindx] += 1
                    # Add the length of the rule to the total rule length for this sample
                    rule_lengths[sindx] += len(rule)

            # If any rules were applied to this sample, calculate the average rule length
            if rule_lengths[sindx] > 0:
                rule_length_per_sample_[sindx] = (
                    rule_lengths[sindx] / rules_per_sample_[sindx]
                )
            else:
                # If no rules were applied to this sample, add it to the missed values index
                missed_values_index_ = np.concatenate((missed_values_index_, [sindx]))

            # Add the class weights for this sample to the array of class weights
            sum_class_weights_arr[sindx, :] = sum_class_weights

        # Return the array of class weights
        if predict_info:
            warnings.warn(
                "Enabling 'predict_info' will return additional prediction "
                "details, including indices of samples with missed values, "
                "number of rules applied per sample, and average rule length "
                "per sample. While this information is useful for in-depth "
                "analysis, it may increase computational overhead and complexity "
                "of result interpretation. Use this feature judiciously."
            )
            return missed_values_index_, rules_per_sample_, rule_length_per_sample_

        else:
            return sum_class_weights_arr

    def predict(
        self,
        x: ArrayLike,
        indices: list | None = None,
        threshold: float = 0.0,
        *,
        predict_info: bool = False,
    ) -> np.ndarray:
        """
        Predicts class labels for the given data, optionally returning
        additional prediction info.

        Parameters
        ----------
        x : array-like of shape (n_samples, n_features)
            The training input samples. Internally, it will be converted to dtype=np.float32.
        indices : list or None, default=None
            Specific indices of rules to use for prediction. If None,
            all rules are used.
        threshold : float, default=0
            The threshold for selecting rules based on their weights.
        predict_info : bool, default=False
            If True, returns additional information about the prediction
            process including indices of samples with missed values, number
            of rules applied per sample, and average rule length per sample.
            Otherwise, returns only the predicted class labels.

        Returns
        -------
        np.ndarray
            An array of predicted class labels for each instance in `x`.
            If predict_info is True, also returns arrays containing indices
            of samples with missed values, number of rules applied per sample,
            and average rule length per sample.
        """

        if indices is None:
            indices = []

        x = check_inputs(x)

        if predict_info:
            missed_values_index_, rules_per_sample_, rule_length_per_sample_ = (
                self._predict_base(x, indices, threshold, predict_info=predict_info)
            )
            return missed_values_index_, rules_per_sample_, rule_length_per_sample_

        else:
            sum_class_weights_arr = self._predict_base(
                x, indices, threshold, predict_info=predict_info
            )

        return_prediction = np.empty(shape=(x.shape[0],), dtype=np.intp)

        # Convert the class weights into class predictions
        for sindx, sum_class_weights in enumerate(sum_class_weights_arr):
            # If the sum of the class weights is 0, predict the majority class
            if np.sum(sum_class_weights) <= 10e-6:
                return_prediction[sindx] = self.majority_class_
            else:
                # Otherwise, predict the class with the highest weight
                return_prediction[sindx] = np.argmax(sum_class_weights)

        # Return the predicted classes
        return return_prediction

    def predict_proba(
        self,
        x: ArrayLike,
        indices: list | None = None,
        threshold: float = 0.0,
        *,
        predict_info: bool = False,
    ):
        """
        Predicts class probabilities for the given data, optionally
        returning additional prediction info.

        Parameters
        ----------
        x : array-like of shape (n_samples, n_features)
            The training input samples. Internally, it will be converted to dtype=np.float32.
        indices : list or None, default=None
            Specific indices of rules to use for calculating probabilities.
            If None, all rules are used.
        threshold : float, default=0
            The threshold for selecting rules based on their weights.
        predict_info : bool, default=False
            If True, returns additional information about the prediction process
            including indices of samples with missed values, number of rules applied
            per sample, and average rule length per sample. Otherwise, returns only
            the probabilities of each class for each sample.

        Returns
        -------
        np.ndarray
            An array where each row corresponds to a sample in `x` and each column
            to a class, containing the probability of each class for each sample.
            If predict_info is True, also returns arrays containing indices of samples
            with missed values, number of rules applied per sample, and average rule
            length per sample.
        """

        if indices is None:
            indices = []

        x = check_inputs(x)

        if predict_info:
            missed_values_index_, rules_per_sample_, rule_length_per_sample_ = (
                self._predict_base(x, indices, threshold, predict_info=predict_info)
            )
            return missed_values_index_, rules_per_sample_, rule_length_per_sample_

        else:
            sum_class_weights_arr = self._predict_base(
                x, indices, threshold, predict_info=predict_info
            )

        return_prediction = np.empty(shape=(x.shape[0], self.k_), dtype=np.float64)

        # Convert the class weights into class probabilities
        for sindx, sum_class_weights in enumerate(sum_class_weights_arr):
            total_weight = np.sum(sum_class_weights)
            if total_weight <= 10e-6:
                # If the sum of the class weights is 0, predict the majority class probabilities
                return_prediction[sindx, :] = self.majority_probability_
            else:
                # Otherwise, divide the class weights by the total weight
                # to get the class probabilities
                return_prediction[sindx, :] = np.divide(sum_class_weights, total_weight)

        # Return the class probabilities
        return return_prediction

    def _get_sample_wight(self, sample_weight, class_weight, y):
        """
        Calculates the final sample weights based on initial sample weights, class weights and
        target values.

        Parameters
        ----------
        sample_weight : array-like, shape (n_samples,) or None
            Initial weights of samples. If None, all samples are assumed to have weight one.
        class_weight : dict, "balanced" or None
            Weights associated with classes in the form {class_label: weight}. Can be "balanced"
            to automatically adjust weights inversely proportional to class frequencies in the input data
            or None for equal weights.
        y : array-like, shape (n_samples,)
            Array of target values (class labels).

        Returns
        -------
        final_sample_weights : array-like, shape (n_samples,) or None
            The computed array of weights for each sample in the dataset. Returns None if all computed
            weights are equal to one, indicating no weighting is necessary.
        """
        if class_weight is None and sample_weight is None:
            return None

        if sample_weight is not None:
            if (
                not isinstance(sample_weight, np.ndarray)
                or sample_weight.shape != y.shape
            ):
                raise ValueError(
                    "sample_weight must be a numpy array of the same shape as y."
                )

        final_sample_weights = np.ones_like(y, dtype=np.float64)

        if class_weight is not None:
            if isinstance(class_weight, dict):
                if len(class_weight.keys()) != np.unique(y).size:
                    raise ValueError(
                        "The class_weight dictionary must have a key for each unique value in y."
                    )

            final_sample_weights *= compute_sample_weight(class_weight, y)
        if sample_weight is not None:
            final_sample_weights *= sample_weight

        if np.min(final_sample_weights) != 1:
            warnings.warn(
                "Minimum sample weight automatically scaled to 1 for consistency."
            )
            final_sample_weights /= np.min(final_sample_weights)

        return final_sample_weights

    def _validate_rug_parameters(
        self,
        threshold: float,
        solver: OptimizationSolver,
        class_weight: Dict[int:float],
        random_state: int | None,
        rule_cost,
    ):
        if not isinstance(threshold, (float, int)) or threshold < 0:
            raise TypeError("threshold must be a non-negative float or integer.")

        if not isinstance(solver, (OptimizationSolver)):
            raise TypeError("solver should be inherited from OptimizationSolver.")

        if not (isinstance(random_state, int) or random_state is None):
            raise TypeError("random_state must be an integer or None.")

        if not isinstance(rule_cost, (int, RuleCost)):
            raise TypeError("rule_cost must be an instance of RuleCost or an integer.")

        if isinstance(rule_cost, int) and rule_cost < 0:
            raise ValueError("If rule_cost is an integer, it must be non-negative.")

        if not (
            isinstance(class_weight, dict)
            and all(
                isinstance(k, int) and isinstance(v, float)
                for k, v in class_weight.items()
            )
            or class_weight in ["balanced", None]
        ):
            raise TypeError(
                "class_weight must be a dictionary with integer keys and float values, 'balanced', or None."
            )

    @property
    def is_fitted(self):
        """
        Indicates whether the model is fitted.

        Returns
        -------
        bool
            True if the model is fitted, False otherwise.
        """

        return self._is_fitted

    @property
    def decision_rules(self):
        """
        Returns the rules extracted from the decision trees, after optimization.

        Returns
        -------
        Dict[int, Rule]
            A dictionary where keys are rule indices and values are Rule objects.
        """

        return self.decision_rules_

    @property
    def decision_trees(self):
        """
        Returns dictionary that stores the decision tree models.

        Returns
        -------
        Dict[int, Any]
            A dictionary containing decision tree models, with identifiers as keys
            and decision
            tree instances as values.
        """
        return self.decision_trees_

    @property
    def rule_info(self):
        """
        Returns information about each rule.

        Returns
        -------
        Dict[int, Tuple[int, int, int, np.ndarray]]
            A dictionary with rule indices as keys and tuples containing information about
            each rule as values. The tuple structure is (rule_id, feature_index, threshold,
            values_array).
        """

        return self.rule_info_

    @property
    def coefficients(self):
        """
        Stores coefficients associated with the rules during optimization.

        Returns
        -------
        Coefficients
            An object or array-like structure storing coefficients related to each rule.
        """

        return self.coefficients_

    @property
    def majority_class(self):
        """
        Returns the class label of the majority class in the dataset.

        Returns
        -------
        int
            The label of the majority class.
        """

        return self.majority_class_

    @property
    def majority_probability(self):
        """
        Returns the probability of the majority class in the dataset.

        Returns
        -------
        float
            The probability of encountering the majority class in the dataset.
        """

        return self.majority_probability_

    @property
    def k(self):
        """
        Returns the total number of unique classes in the dataset.

        Returns
        -------
        float
            The total number of unique classes.
        """

        return self.k_

    @property
    def classes(self):
        """
        Returns unique class labels in the dataset.

        Returns
        -------
        np.ndarray
            An array containing the unique class labels of the dataset.
        """

        return self.classes_

    @property
    def rule_columns(self):
        """
        Returns indices of rules selected as part of the model.

        Returns
        -------
        np.ndarray
            An array of indices corresponding to the rules included in the model.
        """

        return self.rule_columns_
