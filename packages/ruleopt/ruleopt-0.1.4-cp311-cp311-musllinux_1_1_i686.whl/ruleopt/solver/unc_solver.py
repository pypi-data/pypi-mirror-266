import numpy as np
from scipy.sparse import csr_matrix
from ..utils import check_module_available
from .base import OptimizationSolver

TORCH_AVAILABLE = check_module_available("torch")


class _TorchSolverManager:
    _torch_solver_class = None

    @staticmethod
    def _initialize_solver():
        from torch import ones, relu, sum, matmul, sub, mul, float32, dot
        from torch.nn import Module, Parameter

        class _TorchSolver(Module):
            """
            A solver module for using PyTorch.

            This module is designed to solve optimization problems with a specific structure,
            leveraging the PyTorch framework for gradient-based optimization.

            Attributes:
                max_rule (int): The maximum number of rules to be selected.
                ws (torch.nn.Parameter): Weights associated with each rule.
                gates (torch.nn.Parameter): Gate parameters to control rule selection.
                vs (torch.nn.Parameter): Slack variables for handling constraints.
                penalty (float): Penalty parameter for the objective function.
                a_hat (torch.Tensor): Coefficient matrix after processing.
                costs (torch.Tensor): Cost associated with each rule.
            """

            def __init__(
                self, m, n, penalty, costs, k, constraint_cost, sample_weight=None
            ):
                """
                Initializes the Solver with given parameters and coefficients.

                Parameters:
                    m (int): Number of rules.
                    penalty (float): Penalty parameter for the cost in the objective function.
                    coefficients (object): An object containing the sparse matrix coefficients ('yvals', 'rows', 'cols'),
                                            and costs associated with each rule ('costs').
                    k (float): A scaling factor for the coefficients.
                    max_rule (int): The maximum number of rules to be selected.
                """
                super().__init__()

                self.ws = Parameter(ones(m, dtype=float32, requires_grad=True) * 0.5)

                self.betas = Parameter(ones(n, dtype=float32, requires_grad=True) * 0.5)

                self.sample_weight = sample_weight
                self.penalty = penalty
                self.constraint_cost = constraint_cost
                self.costs = costs
                self.k = k
                self.m = m

            def forward(self, a_hat):
                """
                Defines the forward pass for the optimization problem.

                Performs the selection of rules based on the weighted gates, calculates the
                objective function, and applies penalties for constraint violations.

                Returns:
                    torch.Tensor: The total loss comprising the objective function and penalties for constraint violations.
                """
                betas = relu(self.betas)
                ws = relu(self.ws)

                dual_constraint_violation = (
                    sum(
                        (
                            sub(
                                matmul(a_hat.t(), betas.unsqueeze(-1)).squeeze(),
                                mul(self.costs, self.penalty),
                            )
                        ).relu_(),
                        dim=0,
                    )
                    + sum(
                        (
                            sub(
                                self.betas,
                                (
                                    1
                                    if self.sample_weight is None
                                    else self.sample_weight
                                ),
                            )
                        ).relu_(),
                        dim=0,
                    )
                ) * self.constraint_cost

                dual_objective = sum(betas, dim=0)

                vs = sub(1, matmul(a_hat, ws.unsqueeze(-1)).squeeze()).relu_()

                primal_objective = self.penalty * dot(self.costs, ws) + (
                    sum(vs, dim=0)
                    if self.sample_weight is None
                    else dot(vs, self.sample_weight)
                )

                total_loss = (
                    -dual_objective
                    + primal_objective
                    + (primal_objective - dual_objective).pow(2)
                    + dual_constraint_violation
                )

                return total_loss

        return _TorchSolver

    @classmethod
    def get_solver(cls, *args, **kwargs):
        if cls._torch_solver_class is None:
            cls._torch_solver_class = cls._initialize_solver()
        return cls._torch_solver_class(*args, **kwargs)


class UNCSolver(OptimizationSolver):
    """
    A gradient descent solver for optimization problems, leveraging PyTorch for gradient-based optimization.

    This solver iteratively updates parameters to minimize an objective function, applying penalties
    for constraint violations. It utilizes a gradient descent approach with early stopping based on
    a patience parameter to prevent overfitting.
    """

    def __new__(cls, *args, **kwargs):
        if not TORCH_AVAILABLE:
            raise ImportError(
                "PyTorch is required for this class but is not installed.",
                "Please install it with 'pip install torch'",
            )
        instance = super(UNCSolver, cls).__new__(cls)
        return instance

    def __init__(
        self,
        penalty: float = 2.0,
        constraint_cost: float = 100.0,
        lr: float = 0.1,
        weight_decay: float = 0.1,
        patience: int = 100,
        device: str = "cpu",
        use_sparse: bool = False,
    ) -> None:
        """
        Parameters
        ----------
        penalty : float, default=2.0
            Penalty parameter for the cost in the objective function.

        lr : float, default=0.1
            Learning rate for the Adam optimizer.
            
        constraint_cost : float, default=100
            Penalty parameter for constraint violations. 

        weight_decay : float, default=0.01
            Weight decay (L2 penalty) for the optimizer.

        patience : int, default=100
            Number of iterations to wait for an improvement before stopping the optimization.

        device : {"cuda", "cpu"}, default="cpu"
            The device on which to perform computations.

        use_sparse : bool, default=False
            Determines whether to use a sparse matrix representation for the optimization
            problem. Using sparse matrices can significantly reduce memory usage and improve
            performance for large-scale problems with many zeros in the data.
        """
        self.penalty = penalty
        self.lr = lr
        self.weight_decay = weight_decay
        self.patience = patience
        self.device = device
        self.use_sparse = use_sparse
        self.constraint_cost = constraint_cost
        super().__init__()
        super()._check_params()

    def __call__(self, coefficients, k, sample_weight=None, *args, **kwargs):
        """
        Executes the heuristic optimization process on given problem coefficients.

        Parameters
        ----------
        coefficients : object
            An object containing the sparse matrix coefficients ('yvals', 'rows', 'cols'),
            and costs associated with each rule ('costs').

        k : float
            A scaling factor for the coefficients.

        Returns
        -------
        ws : numpy.ndarray
            The optimized weights for each rule after the optimization process.
        vs : numpy.ndarray
            The vs values indicating constraint violations for the optimized solution.
        """
        ### LAZY IMPORT
        from torch import tensor, sparse_csr_tensor, from_numpy, float32, clip
        from torch.optim import Adam
        from torch.optim.lr_scheduler import ReduceLROnPlateau

        a_hat = csr_matrix(
            (
                coefficients.yvals,
                (coefficients.rows, coefficients.cols),
            ),
            dtype=np.float64,
        ) * ((k - 1.0) / k)

        if not self.use_sparse:
            a_hat = tensor(a_hat.toarray(), dtype=float32, device=self.device)

        else:
            a_hat = sparse_csr_tensor(
                from_numpy(a_hat.indptr),
                from_numpy(a_hat.indices),
                from_numpy(a_hat.data),
                dtype=float32,
                device=self.device,
            )

        if sample_weight is not None:
            sample_weight = tensor(sample_weight, dtype=float32, device=self.device)

        costs = tensor(coefficients.costs, dtype=float32, device=self.device)

        n, m = a_hat.shape

        solver = _TorchSolverManager.get_solver(
            m=m,
            n=n,
            k=k,
            penalty=self.penalty,
            constraint_cost=self.constraint_cost,
            costs=costs,
            sample_weight=sample_weight,
        ).to(self.device)

        optimizer = Adam(
            solver.parameters(), lr=self.lr, weight_decay=self.weight_decay
        )
        scheduler = ReduceLROnPlateau(
            optimizer, "min", factor=0.9, patience=self.patience // 5
        )

        best_loss = float("inf")
        counter = 0

        while True:
            optimizer.zero_grad(set_to_none=True)
            loss = solver(a_hat)
            loss.backward()
            optimizer.step()
            
            scheduler.step(loss)

            if loss.item() < best_loss:
                best_loss = loss.item()
                ws = solver.ws.clone()
                betas = solver.betas.clone()
                counter = 0
            else:
                counter += 1
                if counter > self.patience:
                    break

        return (
            clip(ws, min=0).detach().cpu().numpy(),
            clip(betas, min=0).detach().cpu().numpy(),
        )
