import pandas as pd
import numpy as np
from math import sqrt
from scipy.stats import norm, linregress

from . import utils


# portfolio statistics
def total_return(
    returns, aggregate=None, compounded=True, periods=252, annualize=False
):
    """
    Calculates the total compounded return and the cumulative return over a period for an asset.

    Args:
        returns (pd.Series or pd.DataFrame): The input returns series for the asset.
        aggregate (str, optional): The aggregation period for returns. Defaults to None.
        compounded (bool, optional): If True, returns are compounded. Defaults to True.
        periods (int, optional): The number of periods for annualization. Defaults to 252.
        annualize (bool, optional): If True, the returns are annualized. Defaults to True.

    Returns:
        float: The total compounded return or the cumulative return for the asset.
    """
    if not isinstance(returns, (pd.Series, pd.DataFrame)):
        raise ValueError("Input must be a pandas Series or DataFrame.")

    if aggregate:
        returns = utils.aggregate_returns(returns, aggregate, compounded)

    if compounded:
        total = returns.add(1).prod()
    else:
        total = np.sum(returns)

    if annualize:
        total = total ** (periods / returns.count())

    return total - 1


def expected_return(
    returns,
    method="hist",
    aggregate=None,
    compounded=True,
    periods=252,
    annualize=True,
):
    """
    Returns the expected return.

    Args:
        returns (pd.Series or pd.DataFrame): The input returns series.
        method (str, optional): The method for calculating the expected return. Defaults to "mean".
        aggregate (str, optional): The aggregation period for returns. Defaults to None.
        compounded (bool, optional): If True, returns are compounded. Defaults to True.
        periods (int, optional): The number of periods for annualization. Defaults to 252.
        annualize (bool, optional): If True, returns are annualized. Defaults to True.

    Returns:
        float: The expected return.
    """
    if not isinstance(returns, (pd.Series, pd.DataFrame)):
        raise ValueError("Input must be a pandas Series or DataFrame.")

    # Aggregate returns if specified
    if aggregate:
        returns = utils.aggregate_returns(returns, aggregate, compounded)

    if method == "hist":
        expected_return = returns.mean()
    else:
        raise ValueError("Invalid method. Options are 'mean'.")

    if annualize:
        expected_return *= periods

    return expected_return


def rolling_returns(returns, window=252, periods=252):
    """
    Calculate rolling window returns for a given window size.

    Args:
        returns (pd.Series or pd.DataFrame): The input returns series.
        window (int, optional): The window size for calculating rolling returns. Defaults to 252.
        periods_per_year (int, optional): The number of periods per year for annualization. Defaults to 252.

    Returns:
        pd.Series or pd.DataFrame: The calculated rolling window returns.
    """
    return utils.rolling_metric(
        returns, total_return, window=window, periods=periods, annualize=True
    )


def volatility(
    returns,
    method="hist",
    aggregate=None,
    compounded=True,
    periods=252,
    annualize=True,
):
    """
    Calculates the volatility of returns for a period.

    Args:
        returns (pd.Series or pd.DataFrame): The input returns series.
        method (str, optional): The method for calculating the expected return. Defaults to "mean".
        aggregate (str, optional): The aggregation period for returns. Defaults to None.
        compounded (bool, optional): If True, returns are compounded. Defaults to True.
        periods (int, optional): The number of periods for annualization. Defaults to 252.
        annualize (bool, optional): If True, returns are annualized. Defaults to True.

    Returns:
        float: The calculated volatility.
    """

    if not isinstance(returns, (pd.Series, pd.DataFrame)):
        raise ValueError("Input must be a pandas Series or DataFrame.")

    # Aggregate returns if specified
    returns = utils.aggregate_returns(returns, aggregate, compounded)

    if method == "hist":
        std = returns.std()
    else:
        raise ValueError("Invalid method. Options are 'mean'.")

    if annualize:
        std *= np.sqrt(periods)

    return std


def rolling_volatility(returns, window=252, periods=252, annualize=True):
    """
    Calculates the rolling volatility of returns.

    Args:
        returns (pd.Series or pd.DataFrame): The input returns series.
        rolling_period (int, optional): The rolling window period for calculating volatility. Defaults to 126.
        periods_per_year (int, optional): The number of periods per year for annualization. Defaults to 252.
        annualize (bool, optional): If True, the volatility is annualized. Defaults to True.

    Returns:
        pd.Series or pd.DataFrame: The calculated rolling volatility.
    """
    return utils.rolling_metric(
        returns, volatility, window=window, periods=periods, annualize=annualize
    )


def sharpe(returns, rf=0, periods=252, annualize=True):
    """
    Calculates the Sharpe ratio of excess returns.

    Args:
        returns (pd.Series or pd.DataFrame): The input returns series.
        rf (float, optional): The risk-free rate. Defaults to 0.
        periods (int, optional): The number of periods per year for annualization. Defaults to 252.
        annualize (bool, optional): If True, the Sharpe ratio is annualized. Defaults to True.
        

    Returns:
        float: The calculated Sharpe ratio.
    """

    excess_returns = utils.to_excess_returns(returns, rf)
    sharpe = excess_returns.mean() / excess_returns.std(ddof=1)
    if annualize:
        sharpe *= np.sqrt(periods)
    return sharpe


def rolling_sharpe(returns, rf, window=252, periods=252, annualize=True):
    """
    Calculates the rolling Sharpe ratio of excess returns.

    Args:
        returns (pd.Series or pd.DataFrame): The input returns series.
        rf (float, optional): The risk-free rate. Defaults to 0.
        window (int, optional): The rolling window period for calculating the Sharpe ratio. Defaults to 252.
        periods_per_year (int, optional): The number of periods per year for annualization. Defaults to 252.
        annualize (bool, optional): If True, the Sharpe ratio is annualized. Defaults to True.

    Returns:
        pd.Series or pd.DataFrame: The calculated rolling Sharpe ratio.
    """
    # Convert returns and risk-free rate to excess returns
    excess_returns = utils.to_excess_returns(returns, rf)

    return utils.rolling_metric(
        excess_returns, sharpe, window=window, periods=periods, annualize=annualize
    )


def sortino(returns, rf=0, periods=252, annualize=True, target=0, adjusted=False):
    """
    Calculates the Sortino ratio of excess returns.

    Args:
        returns (pd.Series or pd.DataFrame): The input returns series.
        rf (float, optional): The risk-free rate. Defaults to 0.
        periods (int, optional): The number of periods per year for annualization. Defaults to 252.
        annualize (bool, optional): If True, the Sortino ratio is annualized. Defaults to True.
        target (float, optional): The minimum acceptable return. Defaults to 0.

    Returns:
        float: The calculated Sortino ratio.
    """
    excess_returns = utils.to_excess_returns(returns, rf)
    downside_returns = excess_returns.copy()
    downside_returns[downside_returns > target] = 0
    # downside_deviation = np.sqrt((downside_returns**2).sum() / len(downside_returns))
    sortino = excess_returns.mean() / downside_returns.std(ddof=1)
    if annualize:
        sortino *= np.sqrt(periods)
    if adjusted:
        sortino /= sqrt(2)
    return sortino


def rolling_sortino(
    returns, rf, window=252, periods=252, annualize=True, target=0, adjusted=False
):
    """
    Calculates the rolling Sortino ratio of excess returns.

    Args:
        returns (pd.Series or pd.DataFrame): The input returns series.
        rf (float, optional): The risk-free rate. Defaults to 0.
        window (int, optional): The rolling window period for calculating the Sortino ratio. Defaults to 252.
        periods_per_year (int, optional): The number of periods per year for annualization. Defaults to 252.
        annualize (bool, optional): If True, the Sortino ratio is annualized. Defaults to True.
        target (float, optional): The minimum acceptable return. Defaults to 0.

    Returns:
        pd.Series or pd.DataFrame: The calculated rolling Sortino ratio.
    """
    # Convert returns and risk-free rate to excess returns
    excess_returns = utils.to_excess_returns(returns, rf)

    return utils.rolling_metric(
        excess_returns,
        sortino,
        window=window,
        periods=periods,
        annualize=annualize,
        target=target,
        adjusted=adjusted,
    )


def tracking_error(returns, benchmark):
    """
    Calculates the Tracking Error of a portfolio or strategy against a benchmark.

    Parameters:
    - returns: A pandas Series or DataFrame representing the portfolio returns
    - benchmark: A pandas Series or DataFrame representing the benchmark returns

    Returns:
    - Tracking Error as a float
    """
    # Subtracts the benchmark returns from the portfolio returns
    error = utils.to_excess_returns(returns, benchmark)

    # Calculates the standard deviation of these differences
    return error.std()


def omega(returns, required_returns=0.0, periods=None, compounded=False):
    """
    Determines the Omega ratio of a strategy, which is a risk-return performance
    measure of an investment asset, portfolio, or strategy.

    The Omega ratio is calculated as the probability-weighted return of the
    strategy for outcomes above a certain threshold, divided by
    the probability-weighted return for outcomes below that threshold.

    Parameters:
    - returns: Array of returns.
    - required_returns: The minimum acceptable return. Defaults to 0.0.
    - periods: The number of periods, typically trading days in a year. Defaults to 252.

    Returns:
    - Omega ratio of the strategy. If the denominator is zero (i.e., there's no downside),
      returns "inf" to signify infinite return.

    References:
    - https://en.wikipedia.org/wiki/Omega_ratio
    """
    # Calculate the excess returns
    returns_less_thresh = utils.to_excess_returns(
        returns, required_returns, periods=periods, compounded=compounded
    )

    # Separate the returns into positive and negative
    gain = returns_less_thresh[returns_less_thresh > 0.0].sum()
    loss = returns_less_thresh[returns_less_thresh < 0.0].sum()

    # # If there is no downside, return "infinite"
    loss = loss.replace(0, np.inf)

    # Calculate and return the Omega ratio
    return gain / np.abs(loss)


def calmar(returns, aggregate=None, compounded=True, periods=252, annualize=True):
    """
    Calculates the Calmar ratio of a strategy, defined as the compound annual growth
    rate (CAGR) divided by the absolute value of the maximum drawdown.

    The Calmar ratio is a performance metric that measures the relationship between
    the average rate of return and the maximum drawdown risk of a trading system.

    Parameters:
    - returns: List of float returns.

    Returns:
    - The Calmar ratio. If the maximum drawdown is zero (i.e., no drawdown),
      returns 'inf' to signify infinite return.

    Raises:
    - ValueError: If returns list is empty.

    References:
    - https://en.wikipedia.org/wiki/Calmar_ratio
    """

    cagr_ratio = total_return(
        returns,
        aggregate=aggregate,
        compounded=compounded,
        periods=periods,
        annualize=annualize,
    )
    max_dd = max_drawdown(returns)

    # If there's no drawdown, return 'inf' to signify infinite return
    max_dd = max_dd.replace(0, np.inf)

    # Calculate and return the Calmar ratio
    return cagr_ratio / np.abs(max_dd)


def skew(returns):
    """
    Calculates the skewness of the returns. Skewness is a measure of
    the asymmetry of the probability distribution of a real-valued
    random variable about its mean. In simpler terms, skewness tells
    you the amount and direction of skew (departure from horizontal
    symmetry).

    Parameters:
    - returns: Array or DataFrame of asset returns.

    Returns:
    - Skewness of the returns.
    """
    return returns.skew()


def kurtosis(returns):
    """
    Calculates the kurtosis of the returns. Kurtosis is a statistical
    measure used to describe the distribution of observed data around
    the mean. It is a measure of the "tailedness" of the probability
    distribution.

    Parameters:
    - returns: Array or DataFrame of asset returns.

    Returns:
    - Kurtosis of the returns.
    """
    return returns.kurtosis()


def max_drawdown(returns):
    """
    Calculates the maximum drawdown of the returns. Drawdown is the
    peak-to-trough decline during a specific recorded period of an
    investment, fund or commodity, usually quoted as the percentage
    between the peak and the trough.

    Parameters:
    - returns: Array or DataFrame of asset returns.

    Returns:
    - Maximum drawdown of the returns.
    """
    dd = utils.to_drawdown_series(returns)
    return dd.min()


def avg_drawdown(dd_details):
    """
    Calculates the average maximum drawdown for each asset.

    Parameters:
    - dd_details: A DataFrame containing drawdown details.

    Returns:
    - A Series that contains the average maximum drawdown for each asset in the input DataFrame.

    Note:
    The drawdown details DataFrame should have a multi-index where the top level contains asset names,
    and the second level contains drawdown detail categories, one of which should be 'max drawdown'.
    """
    res = {}
    for c in dd_details.columns.get_level_values(0).unique():
        res[c] = dd_details[c]["max drawdown"].mean() / 100
    return pd.DataFrame(res, index=[0]).squeeze(axis=0)


def longest_drawdown_days(dd_details):
    """
    Calculates the duration of the longest drawdown period.

    Parameters:
    - dd_details: A DataFrame containing drawdown details.

    Returns:
    - A Series that contains the duration of the longest drawdown period for each column in the input DataFrame.
    """
    res = {}
    for c in dd_details.columns.get_level_values(0).unique():
        res[c] = dd_details[c]["days"].max()
    return pd.DataFrame(res, index=[0]).squeeze(axis=0)


def avg_drawdown_days(dd_details):
    """
    Calculates the average duration of drawdown periods.

    Parameters:
    - dd_details: A DataFrame containing drawdown details.

    Returns:
    - A Series that contains the average duration of drawdown periods for each column in the input DataFrame.
    """
    res = {}
    for c in dd_details.columns.get_level_values(0).unique():
        res[c] = dd_details[c]["days"].mean()
    return pd.DataFrame(res, index=[0]).squeeze(axis=0)


def beta(returns, benchmark):
    """
    Calculates the beta of each asset in the portfolio.

    Beta measures the volatility of an investment (e.g. a security or portfolio)
    in comparison to the market as a whole.

    Parameters:
    - returns: DataFrame or Series of asset returns.
    - benchmark: Series of benchmark returns.

    Returns:
    - Series of betas for each asset.
    """
    if isinstance(returns, pd.Series):
        returns = returns.to_frame()
    betas = pd.Series(dtype="float64", index=returns.columns)

    for column in returns:
        asset_returns = returns[column].dropna()

        # Align asset_returns and benchmark
        asset_returns, benchmark_aligned = asset_returns.align(benchmark, join="inner")

        covariance_matrix = pd.concat([asset_returns, benchmark_aligned], axis=1).cov()
        betas[column] = covariance_matrix.iloc[0, 1] / covariance_matrix.iloc[1, 1]

    return betas


def alpha(returns, benchmark, periods=252, betas=None):
    """
    Calculates the alpha of each asset in the portfolio.

    Alpha measures the amount that the investment has returned in comparison
    to the market index or other broad benchmark that it is compared against.

    Parameters:
    - returns: DataFrame or Series of asset returns.
    - benchmark: Series of benchmark returns.
    - periods: Number of periods per year. Default is 252 (trading days in a year).

    Returns:
    - Series of alphas for each asset.
    """
    if isinstance(returns, pd.Series):
        returns = returns.to_frame()
    alphas = pd.Series(dtype="float64", index=returns.columns)

    if betas is None:
        betas = beta(returns, benchmark)

    for column in returns:
        asset_returns = returns[column].dropna()

        # Align asset_returns and benchmark
        asset_returns, benchmark_aligned = asset_returns.align(benchmark, join="inner")

        expected_returns = benchmark_aligned.mean() * betas[column]
        alphas[column] = (asset_returns.mean() - expected_returns) * periods

    return alphas


def treynor_ratio(returns, benchmark, rf=0.0, periods=252):
    """
    Calculates the Treynor ratio of each asset in the portfolio.

    The Treynor ratio measures rewards per unit of beta risk.

    Parameters:
    - returns: DataFrame of asset returns.
    - benchmark: Series of benchmark returns.
    - rf_rate: Risk-free rate. Default is 0.0.
    - periods: Number of periods per year. Default is 252 (trading days in a year).

    Returns:
    - Series of Treynor ratios for each asset.
    """
    # Align returns and benchmark
    aligned_returns, aligned_benchmark = returns.align(benchmark, join="inner", axis=0)

    asset_betas = beta(aligned_returns, aligned_benchmark)
    excess_return = utils.to_excess_returns(aligned_returns, rf)
    treynor_ratios = excess_return.mean() / asset_betas
    return treynor_ratios * periods


def information_ratio(returns, benchmark, periods=252):
    """
    Calculates the information ratio of each asset in the portfolio.

    The information ratio is a measure of portfolio returns above the returns of a
    benchmark to the volatility of those returns.

    Parameters:
    - returns: DataFrame of asset returns.
    - benchmark: Series of benchmark returns.
    - periods: Number of periods per year. Default is 252 (trading days in a year).

    Returns:
    - Series of information ratios for each asset.
    """
    # Align returns and benchmark
    returns, benchmark = returns.align(benchmark, join="inner", axis=0)
    return sharpe(returns, benchmark, periods, annualize=True)


def value_at_risk(returns, confidence=0.95):
    """
    Calculates the daily Value at Risk (VaR) using the variance-covariance method.

    Parameters:
    - returns: DataFrame or Series of asset returns.
    - confidence: Confidence level for VaR. Default is 0.95.

    Returns:
    - Series of VaR for each asset.
    """
    res = {}
    for c in returns:
        r = utils.clean(returns[c])
        mu = r.mean()
        sigma = r.std()
        res[c] = norm.ppf(1 - confidence, mu, sigma)
    return pd.DataFrame(res, index=[0]).squeeze(axis=0)


def conditional_value_at_risk(returns, confidence=0.95):
    """
    Calculates the daily Conditional Value at Risk (CVaR), also known as Expected Shortfall (ES).

    Parameters:
    - returns: DataFrame or Series of asset returns.
    - confidence: Confidence level for CVaR. Default is 0.95.

    Returns:
    - Series of CVaR for each asset.
    """
    var = value_at_risk(returns, confidence=confidence)
    if isinstance(returns, pd.Series):
        cvar = returns[returns < var].mean()
    else:  # DataFrame
        cvar = returns.apply(lambda x: x[x < var[x.name]].mean())
    return cvar


def serenity_index(returns, rf=0):
    """
    Calculates the Serenity Index, a performance measure that takes into account both returns and downside risk.
    The Serenity Index was introduced by KeyQuant in their research paper on absolute performance trading.

    Parameters:
    - returns: DataFrame or Series of asset returns.
    - rf: Risk-free rate. Can be a scalar or a Series.

    Returns:
    - A Series of Serenity Index values for each asset.
    """
    # Convert to drawdown series
    drawdown = to_drawdown_series(returns)

    # Calculate the Pitfall, a measure of downside risk
    pitfall = -value_at_risk(drawdown) / returns.std()

    return ulcer_performance_index(returns, rf) * pitfall


def ulcer_index(returns):
    """
    Calculates the Ulcer Index, a measure of downside risk.
    The Ulcer Index is the square root of the mean of the squared percentage drawdowns.

    Parameters:
    - returns: DataFrame or Series of asset returns.

    Returns:
    - A Series of Ulcer Index values for each asset.
    """
    dd = utils.to_drawdown_series(returns)
    return np.sqrt(np.divide((dd**2).sum(), returns.shape[0] - 1))


def ulcer_performance_index(returns, rf=0):
    """
    Calculates the Ulcer Performance Index (UPI), a performance measure that takes into account both returns and downside risk.
    The UPI is the average excess return divided by the Ulcer Index.

    Parameters:
    - returns: DataFrame or Series of asset returns.
    - rf: Risk-free rate. Can be a scalar or a Series.

    Returns:
    - A Series of UPI values for each asset.
    """
    # Compute excess returns
    excess_returns = utils.to_excess_returns(returns, rf)

    # Compute the total return
    total_returns = total_return(excess_returns, annualize=True)

    # Compute the UPI
    return total_returns / ulcer_index(returns)


def tail_ratio(returns, cutoff=0.95):
    """
    Measures the ratio between the right and left tail of returns' distribution.

    Parameters:
    - returns: DataFrame or Series of asset returns.
    - cutoff (optional): The percentile to be considered as a cutoff for the tails. Defaults to 0.95.

    Returns:
    - Series: Tail ratio for each asset.
    """
    return returns.apply(lambda x: abs(x.quantile(cutoff) / x.quantile(1 - cutoff)))


def recovery_factor(returns):
    """
    Measures how fast the strategy recovers from drawdowns.

    Parameters:
    - returns: DataFrame or Series of asset returns.

    Returns:
    - Series: Recovery factor for each asset.
    """
    max_dd = max_drawdown(returns)
    return total_return(returns, annualize=True) / abs(max_dd)


def r_squared(returns, benchmark):
    """
    Measures how well the variations in returns are explained by the benchmark.

    Parameters:
    - returns: DataFrame of asset returns.
    - benchmark: Series or DataFrame of benchmark returns (with one column).

    Returns:
    - Series: R-squared value for each asset.
    """
    returns, benchmark = returns.align(benchmark, join="inner", axis=0)

    # Check if benchmark is a DataFrame and reduce it to a Series if it has only one column
    if isinstance(benchmark, pd.DataFrame) and len(benchmark.columns) == 1:
        benchmark = benchmark.squeeze()

    res = {}
    for c in returns:
        r = utils.clean(returns[c])
        _, _, r_val, _, _ = linregress(r, benchmark)
        res[c] = r_val**2
    return pd.Series(res)


def rolling_greeks(returns, benchmark, window=252, periods=252):
    """
    Calculates the rolling beta and alpha of each asset in the portfolio.

    Parameters:
    - returns: DataFrame or Series of asset returns.
    - benchmark: Series of benchmark returns.
    - window: Size of the moving window for rolling calculations.
    - periods: Number of periods per year. Default is 252 (trading days in a year).

    Returns:
    - DataFrame of rolling betas for each asset.
    - DataFrame of rolling alphas for each asset.
    """
    if isinstance(returns, pd.Series):
        returns = returns.to_frame()

    rolling_betas = pd.DataFrame(index=returns.index, columns=returns.columns)
    rolling_alphas = pd.DataFrame(index=returns.index, columns=returns.columns)

    for column in returns:
        asset_returns, benchmark_aligned = (
            returns[column].dropna().align(benchmark, join="inner")
        )

        for i in range(window, len(asset_returns) + 1):
            window_returns = asset_returns.iloc[i - window : i]
            window_benchmark = benchmark_aligned.iloc[i - window : i]

            betas = beta(window_returns.to_frame(), window_benchmark)
            alphas = alpha(window_returns.to_frame(), window_benchmark, periods, betas)

            # Store the calculated alpha and beta
            rolling_alphas.loc[window_returns.index[-1], column] = alphas[0]
            rolling_betas.loc[window_returns.index[-1], column] = betas[0]

    return rolling_betas, rolling_alphas


def monthly_returns(returns, eoy=True):
    """
    Calculates and formats monthly returns into a DataFrame, optionally with end-of-year (EOY) returns.
    The function supports input either as a DataFrame (with each column being a different asset)
    or a Series (a single asset).

    Args:
        returns (pd.DataFrame or pd.Series): Asset returns.
        eoy (bool, optional): Whether to include end-of-year returns. Defaults to True.

    Returns:
        pd.DataFrame: A DataFrame where each cell represents the return for a given asset in a particular month/year.
        If 'eoy' is True, an 'EOY' column is added for each asset.
    """

    # Convert to DataFrame if necessary (when input is a Series)
    if isinstance(returns, pd.Series):
        returns = returns.to_frame()

    # Convert index to DatetimeIndex if it's not already
    if not isinstance(returns.index, pd.DatetimeIndex):
        returns.index = pd.to_datetime(returns.index)

    # Aggregate returns to the monthly level
    monthly_returns = utils.aggregate_returns(returns, period="month")

    if not isinstance(monthly_returns.index, pd.DatetimeIndex):
        monthly_returns.index = pd.to_datetime(monthly_returns.index)
    # Extract Year and Month from the datetime index and create respective columns
    monthly_returns["Year"] = monthly_returns.index.year
    monthly_returns["Month"] = monthly_returns.index.month_name().str[:3]

    # Create a pivot table with Years as rows and Months as columns
    pivot_table = monthly_returns.pivot(index="Year", columns="Month")

    # Ensure columns are in the correct order (by month) for each asset
    months = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]
    pivot_table = pivot_table.reindex(columns=months, level=1)

    # If 'eoy' is True, calculate yearly returns and add them as 'EOY' columns for each asset
    if eoy:
        yearly_returns = utils.aggregate_returns(returns, period="year")
        if not isinstance(yearly_returns.index, pd.DatetimeIndex):
            yearly_returns.index = pd.to_datetime(yearly_returns.index)
        yearly_returns["Year"] = yearly_returns.index.year
        yearly_returns["Month"] = "EOY"
        yearly_pivot = yearly_returns.pivot(index="Year", columns="Month")
        pivot_table = pd.concat([pivot_table, yearly_pivot], axis=1)

    return pivot_table


def outliers(returns, quantile=0.95):
    """
    Identifies the outliers in the return series based on a specified quantile.

    Args:
        returns (pd.DataFrame or pd.Series): Asset returns.
        quantile (float, optional): The quantile used for outlier identification. Defaults to 0.95.

    Returns:
        pd.DataFrame or pd.Series: A subset of 'returns' including only the outliers.
    """
    # Determine the outliers: values greater than the defined quantile
    return returns[returns > returns.quantile(quantile)].dropna(how="all")


def best(returns, n=1, aggregate=None, compounded=True):
    """
    Returns the 'n' best day/month/week/quarter/year's return for each asset.

    Args:
        returns (pd.DataFrame or pd.Series): The input returns.
        n (int): Number of best returns to fetch for each asset. Default is 1.
        aggregate (str or list, optional): The desired date period for aggregation. Defaults to None.
        compounded (bool, optional): If True, calculates compounded returns. Defaults to True.

    Returns:
        pd.DataFrame: The 'n' best returns along with dates for each asset.
    """
    # Aggregate returns if necessary
    if aggregate:
        returns = utils.aggregate_returns(returns, aggregate, compounded)

    # Initialize an empty DataFrame to store the results
    best_returns = pd.DataFrame()

    # Loop over each asset
    for asset in returns.columns:
        # Sort the returns in descending order and fetch the first 'n' returns
        best_returns_asset = (
            returns[[asset]].sort_values(by=asset, ascending=False).head(n)
        )
        # Append to the result DataFrame
        best_returns = pd.concat([best_returns, best_returns_asset], axis=1)

    return best_returns


def worst(returns, n=1, aggregate=None, compounded=True):
    """
    Returns the 'n' worst day/month/week/quarter/year's return for each asset.

    Args:
        returns (pd.DataFrame or pd.Series): The input returns.
        n (int): Number of worst returns to fetch for each asset. Default is 1.
        aggregate (str or list, optional): The desired date period for aggregation. Defaults to None.
        compounded (bool, optional): If True, calculates compounded returns. Defaults to True.

    Returns:
        pd.DataFrame: The 'n' worst returns along with dates for each asset.
    """
    # Aggregate returns if necessary
    if aggregate:
        returns = utils.aggregate_returns(returns, aggregate, compounded)

    # Initialize an empty DataFrame to store the results
    worst_returns = pd.DataFrame()

    # Loop over each asset
    for asset in returns.columns:
        # Sort the returns in ascending order and fetch the first 'n' returns
        worst_returns_asset = (
            returns[[asset]].sort_values(by=asset, ascending=True).head(n)
        )
        # Append to the result DataFrame
        worst_returns = pd.concat([worst_returns, worst_returns_asset], axis=1)

    return worst_returns


def calculate_annual_covariance(df, periods=252):
    """
    Calculate the annual covariance matrix of a dataframe of asset returns.

    Args:
        df (pd.DataFrame): The dataframe containing asset returns.
        periods (int, optional): The number of periods in a year. Defaults to 252.

    Returns:
        pd.DataFrame: The annual covariance matrix.
    """

    # Calculate the covariance of the dataframe and scale it to an annual measure
    covariance = df.cov() * periods

    return covariance


def calculate_correlation(df):
    """
    Calculate the correlation matrix of a dataframe.

    Args:
        df (pd.DataFrame): The dataframe for which to calculate the correlation matrix.

    Returns:
        pd.DataFrame: The correlation matrix.
    """

    # Calculate the correlation of the dataframe
    correlation = df.corr()

    return correlation
