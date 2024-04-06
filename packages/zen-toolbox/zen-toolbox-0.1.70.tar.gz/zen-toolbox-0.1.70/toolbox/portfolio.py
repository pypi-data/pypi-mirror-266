import numpy as np
import pandas as pd
from scipy.optimize import minimize


def portfolio_stats(weights, mu, cov):
    """
    Calculate portfolio statistics.

    Args:
        weights (np.ndarray): Weights for each asset.
        mu (pd.Series): Expected returns for each asset.
        cov (pd.DataFrame): Covariance matrix of returns for all assets.

    Returns:
        dict: A dictionary containing the portfolio return, volatility, Sharpe ratio and risk contribution.
    """
    port_ret = np.dot(weights, mu)
    port_vol = np.sqrt(np.linalg.multi_dot([weights.T, cov, weights]))
    risk_contrib = np.multiply(weights.T, np.dot(cov, weights)) / port_vol
    return {
        "Return": port_ret,
        "Volatility": port_vol,
        "Sharpe": port_ret / port_vol,
        "Risk Contribution": risk_contrib,
    }


def min_variance(weights, args):
    """
    Objective function for portfolio optimization to minimize variance.
    Returns the portfolio variance for given weights.

    Args:
        weights (np.ndarray): Weights for each asset.
        args (list): List containing expected returns and covariance matrix.

    Returns:
        float: The portfolio variance.
    """
    return portfolio_stats(weights, args[0], args[1])["Volatility"] ** 2


def max_return(weights, args):
    """
    Objective function for portfolio optimization to maximize return.
    Returns the negative portfolio return for given weights (since we are minimizing).

    Args:
        weights (np.ndarray): Weights for each asset.
        args (list): List containing expected returns and covariance matrix.

    Returns:
        float: Negative portfolio return.
    """
    return -portfolio_stats(weights, args[0], args[1])["Return"]


def max_sharpe_ratio(weights, args):
    """
    Objective function for portfolio optimization to maximize Sharpe ratio.
    Returns the negative Sharpe ratio for given weights (since we are minimizing).

    Args:
        weights (np.ndarray): Weights for each asset.
        args (list): List containing expected returns and covariance matrix.

    Returns:
        float: Negative Sharpe ratio.
    """
    return -portfolio_stats(weights, args[0], args[1])["Sharpe"]


def mean_variance(weights, args):
    """
    Objective function for portfolio optimization to maximize return for a given risk level.
    Returns the negative of return minus risk tolerance times volatility (since we are minimizing).

    Args:
        weights (np.ndarray): Weights for each asset.
        args (list): List containing expected returns, covariance matrix and risk tolerance.

    Returns:
        float: Negative of (return - risk tolerance * volatility)
    """
    port = portfolio_stats(weights, args[0], args[1])
    return -(port["Return"] - args[2] * port["Volatility"])


def risk_budget_error(weights, args):
    """
    Objective function for portfolio optimization to achieve equal risk contribution.
    Returns the sum of squared difference between each asset's risk contribution and the target risk contribution.

    Args:
        weights (np.ndarray): Weights for each asset.
        args (list): List containing expected returns and covariance matrix.

    Returns:
        float: Sum of squared differences between actual and target risk contributions.
    """
    port = portfolio_stats(weights, args[0], args[1])
    target_contribution = np.array(weights.shape[0] * [1.0 / weights.shape[0]])
    target_risk = np.multiply(target_contribution.T, port["Volatility"].T)
    return sum(np.square(port["Risk Contribution"] - target_risk))


def equal_weight_error(weights, *args):
    """
    Objective function to get the portfolio as close to equal weights as possible.
    Returns the sum of squared difference between each asset's weight and the equal weight.

    Args:
        weights (np.ndarray): Weights for each asset.

    Returns:
        float: Sum of squared differences between actual and target equal weights.
    """
    n_assets = weights.shape[0]
    target_weight = 1.0 / n_assets
    return sum(np.square(weights - target_weight))


def optimize_portfolio(
    mu,
    cov,
    optim_func,
    bounds,
    constraints,
    risk_tolerance=None,
    TOLERANCE=1e-10,
    method="SLSQP",
    initial_weights=None,
):
    """
    Optimize a portfolio by minimizing a given objective function.

    Args:
        mu (pd.Series): Expected returns for each asset.
        cov (pd.DataFrame): Covariance matrix of returns for all assets.
        optim_func (callable): The function to minimize.
        bounds (sequence): Bounds for decision variables for the minimization.
        constraints (dict): Constraints definition for the minimization.
        risk_tolerance (float, optional): Risk tolerance for 'mean_variance' optimization. Defaults to None.
        TOLERANCE (float, optional): Tolerance for optimization. Defaults to 1e-10.
        method (str, optional): Method for optimization. Defaults to "SLSQP" (Sequential Least Squares Programming).

    Returns:
        tuple: Optimal weights and the corresponding portfolio statistics.
    """
    # Equal weights as a starting point for optimization
    if initial_weights is None:
        initial_weights = np.array(len(mu.index) * [1.0 / len(mu.index)])

    # Arguments for the optimization function
    args = [mu, cov]
    if risk_tolerance is not None:
        args.append(risk_tolerance)
    # Minimization
    result = minimize(
        optim_func,
        initial_weights,
        args=args,
        method=method,
        bounds=bounds,
        constraints=constraints,
        tol=TOLERANCE,
    )

    # Get the optimal weights
    optimal_weights = pd.Series(result.x, index=mu.index)

    # Calculate portfolio stats
    port_stats = portfolio_stats(optimal_weights, mu, cov)

    return optimal_weights, port_stats


def calculate_prior(port_stats, optimal_weights, cov, lbd=None):
    """
    Calculate prior returns (also known as implied returns) based on portfolio statistics.

    Args:
        port_stats (dict): Portfolio statistics including return, volatility, Sharpe ratio, and risk contribution.
        optimal_weights (pd.Series): Optimal weights for each asset.
        cov (pd.DataFrame): Covariance matrix of returns for all assets.

    Returns:
        pd.Series: Prior (implied) returns for each asset.
    """
    if lbd is None:
        lbd = port_stats["Return"] / np.square(port_stats["Volatility"])
    implied_returns = lbd * np.dot(cov, optimal_weights)
    prior = pd.Series(implied_returns, index=optimal_weights.index)
    return prior


def calculate_omega(P, cov, tau=1 / 52):
    """
    Calculate Omega matrix for Black-Litterman model.

    Args:
        P (pd.DataFrame): Matrix expressing the views on the assets.
        cov (pd.DataFrame): Covariance matrix of returns for all assets.
        tau (float, optional): Scalar indicating the uncertainty in the prior estimate of returns. Defaults to 1/52.

    Returns:
        np.ndarray: Omega matrix.
    """
    omega = np.diag(P @ (tau * cov) @ P.T).T
    return np.identity(P.shape[0]) * omega


def calculate_posterior(P, Q, prior, cov, tau=1 / 52, omega=None):
    """
    Calculate posterior returns based on views using Black-Litterman model.

    Args:
        P (pd.DataFrame): Matrix expressing the views on the assets.
        Q (pd.Series): Investor's views on the returns of the assets.
        prior (pd.Series): Prior (implied) returns for each asset.
        cov (pd.DataFrame): Covariance matrix of returns for all assets.
        tau (float, optional): Scalar indicating the uncertainty in the prior estimate of returns. Defaults to 1/52.
        omega (np.ndarray, optional): Omega matrix. If None, it's assumed to be zeros.

    Returns:
        pd.Series: Posterior returns for each asset.
    """
    if omega is None:
        omega = np.zeros((Q.shape[0], Q.shape[0]))

    posterior = prior + tau * cov @ P.T @ np.linalg.inv(tau * P @ cov @ P.T + omega) @ (
        Q - P @ prior
    )
    return posterior


def calibrate_omega(omega_k, p, q, prior, cov, inv_cov, lbd, w_k_p, tau):
    """
    Calibrate the omega value for each view.

    Args:
        omega_k (float): Initial omega value.
        p (pd.Series): Single row from P matrix expressing the view on the assets.
        q (float): Single view on the return of the assets.
        prior (pd.Series): Prior (implied) returns for each asset.
        cov (pd.DataFrame): Covariance matrix of returns for all assets.
        inv_cov (np.ndarray): Inverse of the covariance matrix.
        lbd (float): Lagrange multiplier.
        w_k_p (pd.Series): Initial portfolio weights.
        tau (float): Scalar indicating the uncertainty in the prior estimate of returns.

    Returns:
        float: Squared difference between the initial and updated portfolio weights.
    """
    r_k = prior + (tau * cov @ p.T) * np.array(
        1 / (tau * p @ cov @ p.T + omega_k) * (q - p @ prior)
    )
    w_k = 1 / lbd * (inv_cov @ r_k)
    return np.square(np.sum(w_k_p - w_k))


def optimize_omega(
    port_stats, weights, P, Q, C, prior, cov, tau=1 / 52, TOLERANCE=1e-10
):
    """
    Optimize the Omega matrix for Black-Litterman model by calibrating the omega values.

    Args:
        port_stats (dict): Portfolio statistics including return, volatility, Sharpe ratio, and risk contribution.
        weights (pd.Series): Current portfolio weights for each asset.
        P (pd.DataFrame): Matrix expressing the views on the assets.
        Q (pd.Series): Investor's views on the returns of the assets.
        C (float): Confidence level for the views.
        prior (pd.Series): Prior (implied) returns for each asset.
        cov (pd.DataFrame): Covariance matrix of returns for all assets.
        tau (float, optional): Scalar indicating the uncertainty in the prior estimate of returns. Defaults to 1/52.
        TOLERANCE (float, optional): Tolerance for optimization. Defaults to 1e-10.

    Returns:
        np.ndarray: Optimized Omega matrix.
    """
    omega_cons = {"type": "ineq", "fun": lambda x: x}
    omega = calculate_omega(P, cov, tau)
    lbd = port_stats["Return"] / np.square(port_stats["Volatility"])
    inv_cov = np.linalg.inv(cov)
    omega_calibrated = []
    for i in range(Q.shape[0]):
        r_k_100 = prior + (tau * cov @ P[i].T) * np.array(
            1 / (tau * P[i] @ cov @ P[i].T) * (Q[i] - P[i] @ prior)
        )
        w_k_100 = 1 / lbd * (inv_cov @ r_k_100)
        d_k_100 = w_k_100 - weights
        tilt_k_100 = d_k_100 * C[i]
        w_k_p = weights + tilt_k_100
        opt = minimize(
            calibrate_omega,
            np.diag(omega)[i],
            method="SLSQP",
            constraints=omega_cons,
            tol=TOLERANCE,
            args=(P[i], Q[i], prior, cov, inv_cov, lbd, w_k_p, tau),
        )
        omega_calibrated.append(opt.x)
    return np.identity(Q.shape[0]) * omega_calibrated


def calculate_efficient_frontier(
    mu, cov, bounds, constraints, num_points=100, TOLERANCE=1e-10, method="SLSQP"
):
    """
    Calculate the efficient frontier for given expected returns and covariance matrix.

    Args:
        mu (pd.Series): Expected returns for each asset.
        cov (pd.DataFrame): Covariance matrix of returns for all assets.
        bounds (list of tuples): Bounds for asset weights in the portfolio.
        constraints (dict): Constraints for the portfolio optimization.
        num_points (int, optional): Number of points to calculate on the efficient frontier. Defaults to 50.
        TOLERANCE (float, optional): Tolerance for optimization. Defaults to 1e-10.
        method (str, optional): Optimization method to use. Defaults to "SLSQP".

    Returns:
        dict: A dictionary containing series for returns and volatilities of the efficient frontier,
              and a dataframe for asset weights.
    """

    # Optimize for minimum variance and maximum return
    _, min_vol = optimize_portfolio(
        mu, cov, min_variance, bounds, constraints, TOLERANCE=TOLERANCE, method=method
    )
    _, max_ret = optimize_portfolio(
        mu, cov, max_return, bounds, constraints, TOLERANCE=TOLERANCE, method=method
    )

    target_vols = np.linspace(min_vol["Volatility"], max_ret["Volatility"], num_points)

    # Calculate the efficient frontier
    ef_rets = []
    ef_vols = []
    ef_weights = []
    opt_weight = None
    for tv in target_vols:
        # Create efficient frontier constraints
        ef_constraints = constraints + (
            {
                "type": "eq",
                "fun": lambda x: portfolio_stats(x, mu, cov)["Volatility"] - tv,
            },
        )
        opt_weight, opt_stats = optimize_portfolio(
            mu,
            cov,
            max_return,
            bounds,
            ef_constraints,
            TOLERANCE=TOLERANCE,
            method=method,
            initial_weights=opt_weight,
        )
        ef_rets.append(opt_stats["Return"])
        ef_vols.append(opt_stats["Volatility"])
        ef_weights.append(opt_weight)

    sorted_indices = np.argsort(ef_vols)
    ef_rets = np.array(ef_rets)[sorted_indices]
    ef_vols = np.array(ef_vols)[sorted_indices]
    weights_df = pd.DataFrame(ef_weights).iloc[sorted_indices]

    return {"Returns": ef_rets, "Volatilities": ef_vols, "Weights": weights_df}
