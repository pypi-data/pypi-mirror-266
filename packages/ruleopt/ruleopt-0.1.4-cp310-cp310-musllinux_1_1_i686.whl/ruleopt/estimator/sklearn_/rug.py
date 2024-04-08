from __future__ import annotations
import warnings

import numpy as np
from numpy.typing import ArrayLike
from sklearn.tree import DecisionTreeClassifier

from .base_sklearn import _RUGSKLEARN
from ...rule_cost import Gini
from ...utils import check_inputs


class RUGClassifier(_RUGSKLEARN):
    """
    Rule Generation algorithm for multi-class classification. This algorithm aims at
    producing a compact and interpretable model by employing optimization-bsed rule learning.
    """

    def __init__(
        self,
        solver,
        *,
        rule_cost=Gini(),
        max_rmp_calls=20,
        threshold: float = 1.0e-6,
        random_state: int | None = None,
        class_weight: dict | str | None = None,
        criterion: str = "gini",
        splitter: str = "best",
        max_depth: int | None = None,
        min_samples_split: int = 2,
        min_samples_leaf: int = 1,
        min_weight_fraction_leaf: float = 0.0,
        max_features: int | float | str = None,
        max_leaf_nodes: int | None = None,
        min_impurity_decrease: float = 0.0,
        ccp_alpha: float = 0.0,
        monotonic_cst: ArrayLike | None = None,
    ):
        """
        Parameters
        ----------
        solver : OptimizationSolver
            An instance of a derived class inherits from the 'Optimization Solver' base class.
            The solver is responsible for optimizing the rule set based on the cost function
            and constraints.

        rule_cost : RuleCost or int, default=Gini()
            Defines the cost of rules, either as a specific calculation method (RuleCost instance)
            or a fixed cost

        max_rmp_calls : int, default=20
            Maximum number of Restricted Master Problem (RMP) iterations allowed during fitting.

        class_weight: dict, "balanced" or None, default=None
            A dictionary mapping class labels to their respective weights, the string "balanced"
            to automatically adjust weights inversely proportional to class frequencies,
            or None for no weights. Used to adjust the model in favor of certain classes.

        threshold : float, default=1.0e-6
            The minimum weight threshold for including a rule in the final model.

        random_state : int or None, default=None
            Seed for the random number generator to ensure reproducible results.
            Defaults to None.

        criterion : {"gini", "entropy", "log_loss"}, default="gini"
            The function to measure the quality of a split. Supported criteria are
            "gini" for the Gini impurity and "log_loss" and "entropy" both for the
            Shannon information gain, see :ref:`tree_mathematical_formulation`.

        splitter : {"best", "random"}, default="best"
            The strategy used to choose the split at each node. Supported
            strategies are "best" to choose the best split and "random" to choose
            the best random split.

        max_depth : int, default=None
            The maximum depth of the tree. If None, then nodes are expanded until
            all leaves are pure or until all leaves contain less than
            min_samples_split samples.

        min_samples_split : int or float, default=2
            The minimum number of samples required to split an internal node:

        min_samples_leaf : int or float, default=1
            The minimum number of samples required to be at a leaf node.
            A split point at any depth will only be considered if it leaves at
            least ``min_samples_leaf`` training samples in each of the left and
            right branches.  This may have the effect of smoothing the model,
            especially in regression.

        min_weight_fraction_leaf : float, default=0.0
            The minimum weighted fraction of the sum total of weights (of all
            the input samples) required to be at a leaf node. Samples have
            equal weight when sample_weight is not provided.

        max_features : int, float or {"sqrt", "log2"}, default=None
            The number of features to consider when looking for the best split:

        max_leaf_nodes : int, default=None
            Grow a tree with ``max_leaf_nodes`` in best-first fashion.
            Best nodes are defined as relative reduction in impurity.
            If None then unlimited number of leaf nodes.

        min_impurity_decrease : float, default=0.0
            A node will be split if this split induces a decrease of the impurity
            greater than or equal to this value.

        ccp_alpha : non-negative float, default=0.0
            Complexity parameter used for Minimal Cost-Complexity Pruning. The
            subtree with the largest cost complexity that is smaller than
            ``ccp_alpha`` will be chosen. By default, no pruning is performed.

        monotonic_cst : array-like of int of shape (n_features), default=None
            Indicates the monotonicity constraint to enforce on each feature.
            - 1: monotonic increase
            - 0: no constraint
            - -1: monotonic decrease
        """
        self._validate_parameters(
            max_rmp_calls,
            class_weight,
            criterion,
            splitter,
            max_depth,
            min_samples_split,
            min_samples_leaf,
            min_weight_fraction_leaf,
            max_features,
            max_leaf_nodes,
            min_impurity_decrease,
            ccp_alpha,
            monotonic_cst,
        )

        super().__init__(
            threshold=threshold,
            random_state=random_state,
            solver=solver,
            rule_cost=rule_cost,
            class_weight=class_weight,
        )

        self.max_rmp_calls = int(max_rmp_calls)

        self.criterion = criterion
        self.splitter = splitter
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.min_samples_leaf = min_samples_leaf
        self.min_weight_fraction_leaf = min_weight_fraction_leaf
        self.max_features = max_features
        self.max_leaf_nodes = max_leaf_nodes
        self.min_impurity_decrease = min_impurity_decrease
        self.ccp_alpha = ccp_alpha
        self.monotonic_cst = monotonic_cst

        self._temp_rules = []

    def _pspdt(
        self,
        x: np.ndarray,
        y: np.ndarray,
        vec_y: np.ndarray,
        fit_tree: DecisionTreeClassifier,
        treeno: int,
        betas: np.ndarray,
    ) -> bool:
        """
        Pricing SubProblem for Decision Trees (PSPDT) in the rule generation process.

        Parameters
        ----------
        x : np.ndarray
            Feature matrix of the training data.
        y : np.ndarray
            Target vector of the training data.
        vec_y : np.ndarray
            Preprocessed target vector, adjusted for optimization.
        fit_tree : DecisionTreeClassifier
            Fitted decision tree for rule extraction.
        treeno : int
            Identifier for the current tree in the iterative process.
        betas : np.ndarray
            Dual variables or sample weights from the latest master problem solution.

        Returns
        -------
        bool
            Indicates whether a new rule that improves the objective function was found.
        """
        no_improvement = True

        n, col = x.shape[0], np.max(self.coefficients_.cols) + 1

        # Apply the decision tree to the feature matrix
        y_rules = fit_tree.apply(x)
        preds = fit_tree.predict(x)

        for leafno in np.unique(y_rules):
            temp_rule = self._get_rule(fit_tree, leafno)

            if temp_rule in self._temp_rules:
                continue

            # Get the samples that fall into this leaf
            covers = np.where(y_rules == leafno)[0]
            leaf_y_vals = y[covers]  # y values of the samples in the leaf

            # Get the unique labels in the leaf and their counts
            unique_labels = np.arange(self.k_, dtype=np.intp)
            counts = np.zeros(self.k_, dtype=np.intp)
            unique_labels_, counts_ = np.unique(leaf_y_vals, return_counts=True)
            for i, j in enumerate(unique_labels_):
                unique_labels[j] = unique_labels_[i]
                counts[j] = counts_[i]

            # Identify the majority class in the leaf
            label = preds[covers][0]  # leaf_output

            # Create a vector for this label
            label_vector = np.full((self.k_,), -1 / (self.k_ - 1))
            label_vector[label] = 1

            # Calculate the y values for the optimization problem
            fill_ahat = np.dot(vec_y[covers, :], label_vector)

            # Prepare to check the reduced cost
            aijhat = np.zeros(n)
            aijhat[covers] = fill_ahat

            cost = self._get_rule_cost(
                temp_rule=self._get_rule(fit_tree, leafno),
                covers=covers,
                counts=counts,
                y=y,
            )

            # Calculate the reduced cost
            red_cost = np.dot(
                np.multiply(((self.k_ - 1.0) / self.k_), aijhat),
                betas,  # (betas if sample_weight is None else betas * sample_weight),
            ) - (cost * self.solver.penalty)

            # If the reduced cost is positive, update the coefficients
            if red_cost > 0:  # only columns with proper reduced costs are added
                covers_fill = np.full((covers.shape[0],), fill_ahat, dtype=np.intp)
                covers_col = np.full((covers.shape[0],), col, dtype=np.intp)
                self.coefficients_.rows = np.concatenate(
                    (self.coefficients_.rows, covers)
                )
                self.coefficients_.cols = np.concatenate(
                    (self.coefficients_.cols, covers_col)
                )
                self.coefficients_.yvals = np.concatenate(
                    (self.coefficients_.yvals, covers_fill)
                )
                self.coefficients_.costs = np.concatenate(
                    (self.coefficients_.costs, [cost])
                )

                # Calculate the distribution of the samples in the leaf across the classes
                sdist = np.zeros(self.k_, dtype=np.intp)
                sdist[unique_labels] = counts
                self.rule_info_[col] = (treeno, leafno, label, sdist)
                col += 1
                no_improvement = False

                self._temp_rules.append(temp_rule)

        # Return whether there was any improvement
        return no_improvement

    def _fit_decision_tree(
        self, x: np.ndarray, y: np.ndarray, sample_weight: np.ndarray
    ) -> DecisionTreeClassifier:
        """
        Fits a decision tree to the data, taking into account sample weights.

        Parameters
        ----------
        x : np.ndarray
            Feature matrix of the training data.
        y : np.ndarray
            Target vector of the training data.
        sample_weight : np.ndarray
            Array of weights for the samples.

        Returns
        -------
        DecisionTreeClassifier
            A decision tree classifier fitted to the weighted data.
        """
        dt = DecisionTreeClassifier(
            random_state=self._rng.integers(np.iinfo(np.int16).max),
            criterion=self.criterion,
            splitter=self.splitter,
            class_weight=self.class_weight,
            max_depth=self.max_depth,
            min_samples_split=self.min_samples_split,
            min_samples_leaf=self.min_samples_leaf,
            min_weight_fraction_leaf=self.min_weight_fraction_leaf,
            max_features=self.max_features,
            max_leaf_nodes=self.max_leaf_nodes,
            min_impurity_decrease=self.min_impurity_decrease,
            ccp_alpha=self.ccp_alpha,
            monotonic_cst=self.monotonic_cst,
        )

        if sample_weight is not None:
            dt.class_weight = None

        # Fit the decision tree to the data
        return dt.fit(x, y, sample_weight=sample_weight)


    def fit(self, x: ArrayLike, y: ArrayLike, sample_weight: ArrayLike | None = None):
        """
        Fits the RUGClassifier model to the training data using a rule generation approach.

        Parameters
        ----------
        x : array-like of shape (n_samples, n_features)
            The training input samples. Internally, it will be converted to dtype=np.float32.
        y : array-like of shape (n_samples,) or (n_samples, n_outputs)
            The target values (class labels) as integers
        sample_weight : array-like of shape (n_samples,), default=None
            Sample weights. If None, then samples are equally weighted.

        Returns
        -------
        RUGClassifier
            The fitted model, ready for making predictions.
        """
        x, y = check_inputs(x, y)
        if self._is_fitted:
            self._cleanup()

        treeno = 0
        fit_tree = self._fit_decision_tree(x, y, sample_weight=None)
        self.decision_trees_[treeno] = fit_tree

        self._get_class_infos(y)
        vec_y = self._preprocess(y)
        self._get_matrix(x, y, vec_y, fit_tree, treeno)

        sample_weight = self._get_sample_wight(sample_weight, self.class_weight, y)

        ws, betas = self.solver(
            coefficients=self.coefficients_, k=self.k_, sample_weight=sample_weight
        )

        # Rule generation
        for _ in range(self.max_rmp_calls):
            if np.all(betas == 0):
                break

            treeno += 1
            fit_tree = self._fit_decision_tree(x, y, sample_weight=betas)
            self.decision_trees_[treeno] = fit_tree

            no_improvement = self._pspdt(x, y, vec_y, fit_tree, treeno, betas)

            if no_improvement:
                break

            ws, betas = self.solver(
                coefficients=self.coefficients_,
                k=self.k_,
                ws0=ws.copy(),
                sample_weight=sample_weight,
            )

        self._fill_rules(ws)
        self._is_fitted = True

        return self

    def _validate_parameters(
        self,
        max_rmp_calls,
        class_weight,
        criterion,
        splitter,
        max_depth,
        min_samples_split,
        min_samples_leaf,
        min_weight_fraction_leaf,
        max_features,
        max_leaf_nodes,
        min_impurity_decrease,
        ccp_alpha,
        monotonic_cst,
    ):
        # max_rmp_calls check
        if not isinstance(max_rmp_calls, (float, int)):
            raise TypeError("max_rmp_calls must be an integer.")

        if max_rmp_calls < 0:
            raise ValueError("max_rmp_calls must be a non-negative integer.")

        # class_weight check
        if not isinstance(class_weight, (dict, str, type(None))) or (
            isinstance(class_weight, str) and class_weight != "balanced"
        ):
            raise ValueError("class_weight must be a dictionary, 'balanced', or None.")

        # criterion check
        if criterion not in {"gini", "entropy", "log_loss"}:
            raise ValueError(
                "criterion must be one of 'gini', 'entropy', or 'log_loss'."
            )

        # splitter check
        if splitter not in {"best", "random"}:
            raise ValueError("splitter must be 'best' or 'random'.")

        # max_depth check
        if max_depth is not None and not isinstance(max_depth, int):
            raise TypeError("max_depth must be an integer or None.")
        if isinstance(max_depth, int) and max_depth < 1:
            raise ValueError("max_depth must be greater than 0.")

        # min_samples_split check
        if not isinstance(min_samples_split, (int, float)) or min_samples_split < 2:
            raise ValueError(
                "min_samples_split must be an integer or float greater than or equal to 2."
            )

        # min_samples_leaf check
        if not isinstance(min_samples_leaf, (int, float)) or min_samples_leaf < 1:
            raise ValueError(
                "min_samples_leaf must be an integer or float greater than or equal to 1."
            )

        # min_weight_fraction_leaf check
        if not isinstance(min_weight_fraction_leaf, float) or not (
            0.0 <= min_weight_fraction_leaf <= 1.0
        ):
            raise ValueError(
                "min_weight_fraction_leaf must be a float between 0.0 and 1.0."
            )

        # max_features check
        if (
            max_features is not None
            and not isinstance(max_features, (int, float, str))
            or (isinstance(max_features, str) and max_features not in {"sqrt", "log2"})
        ):
            raise ValueError(
                "max_features must be an integer, float, 'sqrt', 'log2', or None."
            )

        # max_leaf_nodes check
        if max_leaf_nodes is not None and (
            not isinstance(max_leaf_nodes, int) or max_leaf_nodes < 1
        ):
            raise ValueError("max_leaf_nodes must be a positive integer or None.")

        # min_impurity_decrease check
        if not isinstance(min_impurity_decrease, float) or min_impurity_decrease < 0.0:
            raise ValueError("min_impurity_decrease must be a non-negative float.")

        # ccp_alpha check
        if not isinstance(ccp_alpha, float) or ccp_alpha < 0.0:
            raise ValueError("ccp_alpha must be a non-negative float.")

        # monotonic_cst check
        if monotonic_cst is not None and (
            not isinstance(monotonic_cst, (list, tuple))
            or not all(isinstance(item, int) for item in monotonic_cst)
        ):
            raise ValueError("monotonic_cst must be an array-like of integers or None.")
