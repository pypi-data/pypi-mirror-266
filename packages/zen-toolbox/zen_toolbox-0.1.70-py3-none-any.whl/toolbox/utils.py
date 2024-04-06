import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from . import stats


def extract_values_from_key(list_of_dicts, key):
    """
    Extracts values from a list of dictionaries for a specific key.

    Args:
        list_of_dicts (list): The list of dictionaries.
        key (str): The key to search for in the dictionaries.

    Returns:
        list: The list of values associated with the key in the dictionaries.
    """
    return [d[key] for d in list_of_dicts if key in d]


def count_days(start_date, end_date, business=True, holidays=[]):
    """
    Counts the number of days between two dates, optionally excluding non-business days and holidays.

    Args:
        start_date (str): The start date in the format 'YYYY-MM-DD'.
        end_date (str): The end date in the format 'YYYY-MM-DD'.
        business (bool, optional): If True, excludes non-business days (weekends). Defaults to True.
        holidays (list, optional): The list of holiday dates in the format 'YYYY-MM-DD'. Defaults to an empty list.

    Returns:
        int: The number of days between the start date and end date.
    """
    date_range = pd.date_range(start_date, end_date, freq="D")

    if business:
        holidays = pd.to_datetime(holidays)
        weekdays = np.isin(date_range.weekday, [5, 6], invert=True)
        non_holidays = np.isin(date_range, holidays, invert=True)
        valid_days = np.logical_and(weekdays, non_holidays).sum()
    else:
        valid_days = len(date_range)

    return valid_days - 1


def add_days(
    start_date,
    num_days=0,
    num_weeks=0,
    num_months=0,
    num_years=0,
    business=True,
    holidays=[],
):
    """
    Adds a specified number of days, months, or years to a date, optionally skipping non-business days and holidays.

    Args:
        start_date (str): The start date in the format 'YYYY-MM-DD'.
        num_days (int, optional): The number of days to add. Defaults to 0.
        num_weeks (int, optional): The number of weeks to add. Defaults to 0.
        num_months (int, optional): The number of months to add. Defaults to 0.
        num_years (int, optional): The number of years to add. Defaults to 0.
        business (bool, optional): If True, skips non-business days (weekends). Defaults to True.
        holidays (list, optional): The list of holiday dates in the format 'YYYY-MM-DD'. Defaults to an empty list.

    Returns:
        str: The new date after adding the specified number of days, months, or years in the format 'YYYY-MM-DD'.
    """
    date_format = "%Y-%m-%d"
    start_date = datetime.strptime(start_date, date_format)

    holidays = [datetime.strptime(h, date_format) for h in holidays]

    new_date = start_date + relativedelta(
        days=num_days, weeks=num_weeks, months=num_months, years=num_years
    )

    if business:
        while new_date.weekday() in (5, 6) or new_date in holidays:
            new_date += timedelta(days=1)

    return new_date.strftime(date_format)


def subs_business_days(start_date, days=0, holidays=[]):
    """
    Subtracts a specified number of business days from a start date, skipping weekends and specified holidays.

    Args:
        start_date (str): The start date in the format 'YYYY-MM-DD'.
        days (int, optional): The number of business days to subtract. Defaults to 0.
        holidays (list, optional): A list of holiday dates in the format 'YYYY-MM-DD' to be skipped. Defaults to an empty list.

    Returns:
        str: The new date after subtracting the specified number of business days, in the format 'YYYY-MM-DD'.
    """
    date_format = "%Y-%m-%d"
    date = datetime.strptime(start_date, date_format)
    holidays = set(datetime.strptime(h, date_format) for h in holidays)

    while days > 0:
        date -= timedelta(days=1)
        if date.weekday() < 5 and date not in holidays:
            days -= 1
    return date.strftime(date_format)


def random_bool(p, N):
    """
    Generates a random boolean numpy array of size N.

    Args:
        p (float): The probability of generating 'True'.
        N (int): The size of the array.

    Returns:
        np.ndarray: The random boolean array.
    """

    return np.random.choice(a=[True, False], size=(N,), p=[p, 1 - p])


def patrimonio_analysis(
    pl_inicial,
    ap,
    ex,
    months=1200,
    freq_ap=1,
    timing_ap=False,
    max_ap=999999999,
    max_ex=999999999,
    ap_till=720,
    ap_from=1,
    freq_ex=1,
    timing_ex=True,
    ex_till=1200,
    ex_from=1,
    juro_real=0.02,
    step_freq_ap=0,
    step_ap=0.0,
    step_freq_ex=0,
    step_ex=0.0,
    extra_ap=0,
    extra_prob_ap=0.0,
    extra_ex=0,
    extra_prob_ex=0.0,
    extra=[],
):
    """
    Analyzes the patrimonio (wealth) over a certain number of months, given a number of conditions.

    Args:
        pl_inicial (float): The initial patrimonio.
        ap (float): The aportes (contributions).
        ex (float): The despesas (expenses).
        months (int, optional): The number of months for the analysis. Defaults to 1200.
        freq_ap (int, optional): The frequency of the contributions. Defaults to 1.
        timing_ap (bool, optional): Whether the timing of the contributions is at the beginning or end of the month. Defaults to False.
        max_ap (int, optional): The maximum contribution. Defaults to 999999999.
        max_ex (int, optional): The maximum expense. Defaults to 999999999.
        ap_till (int, optional): The month till which contributions are made. Defaults to 720.
        ap_from (int, optional): The month from which contributions start. Defaults to 1.
        freq_ex (int, optional): The frequency of the expenses. Defaults to 1.
        timing_ex (bool, optional): Whether the timing of the expenses is at the beginning or end of the month. Defaults to True.
        ex_till (int, optional): The month till which expenses are made. Defaults to 1200.
        ex_from (int, optional): The month from which expenses start. Defaults to 1.
        juro_real (float, optional): The real interest rate. Defaults to 0.02.
        step_freq_ap (int, optional): The step frequency of the contributions. Defaults to 0.
        step_ap (float, optional): The step size of the contributions. Defaults to 0.0.
        step_freq_ex (int, optional): The step frequency of the expenses. Defaults to 0.
        step_ex (float, optional): The step size of the expenses. Defaults to 0.0.
        extra_ap (float, optional): The extra contributions. Defaults to 0.
        extra_prob_ap (float, optional): The probability of extra contributions. Defaults to 0.0.
        extra_ex (float, optional): The extra expenses. Defaults to 0.
        extra_prob_ex (float, optional): The probability of extra expenses. Defaults to 0.0.
        extra (list, optional): The list of extra values. Defaults to [].

    Returns:
        dict: A dictionary containing the final patrimonio, the patrimonio trajectory, and other related information.
    """
    extra = pd.DataFrame(
        np.array(extra), columns=["months", "aportes", "despesas"]
    )
    df = pd.DataFrame(np.arange(1, months + 1, 1), columns=["months"])
    df["years"] = df["months"] / 12
    df["aportes"] = np.minimum(
        max_ap,
        (
            (df["months"] % freq_ap == 0)
            & (df["months"] <= ap_till)
            & (df["months"] >= ap_from)
        )
        * (ap * (1 + step_ap) ** (df["months"] // step_freq_ap)),
    ) + extra_ap * random_bool(extra_prob_ap, months)
    df["despesas"] = np.minimum(
        max_ex,
        (
            (df["months"] % freq_ex == 0)
            & (df["months"] <= ex_till)
            & (df["months"] >= ex_from)
        )
        * (ex * (1 + step_ex) ** (df["months"] // step_freq_ex)),
    ) + extra_ex * random_bool(extra_prob_ex, months)

    df["aportes"] = df["aportes"] + extra["aportes"]
    df["despesas"] = df["despesas"] + extra["despesas"]

    return calculate_patrimonio(df, pl_inicial, timing_ap, timing_ex, juro_real)


def calculate_patrimonio(df, pl_inicial, timing_ap, timing_ex, juro_real):
    """
    Calculates the patrimony value over time for a portfolio or financial asset.

    Args:
        df (pd.DataFrame): A DataFrame containing columns 'aportes' (contributions) and 'despesas' (expenses).
        pl_inicial (float): Initial value of the portfolio or financial asset.
        timing_ap (bool): If True, contributions are included in the patrimony before the return calculation for the month.
        timing_ex (bool): If True, expenses are deducted from the patrimony before the return calculation for the month.
        juro_real (float): Real interest rate used in the calculation of the patrimony.

    Returns:
        pd.DataFrame: A DataFrame similar to df, with an additional 'patrimonio' column with the calculated patrimony.
    """
    juro_real = (1 + juro_real) ** (1 / 12) - 1
    result = []
    for i, r in df.iterrows():
        result.append(
            (
                (pl_inicial if i == 0 else result[i - 1])
                + (r["aportes"] if timing_ap else 0)
                - (r["despesas"] if timing_ex else 0)
            )
            * (1 + juro_real)
            + (r["aportes"] if not timing_ap else 0)
            - (r["despesas"] if not timing_ex else 0)
        )
    df["patrimonio"] = result

    return df


def sensitivity_analysis(data, function, var_x, var_y):
    """
    Performs a sensitivity analysis of a given function on two variables.

    Args:
        data (dict): A dictionary containing data to be passed to the function. The values for the keys in var_x and var_y will be overridden.
        function (callable): The function to perform the sensitivity analysis on.
        var_x (dict): A dictionary with 'key' and 'values' fields representing the first variable.
        var_y (dict): A dictionary with 'key' and 'values' fields representing the second variable.

    Returns:
        list[tuple]: A list of tuples, each containing a value of var_x, a value of var_y, and the result of the function for these values.
    """

    # Initialize results list
    results = []

    # Iterate over all values in var_x and var_y
    for x in var_x["values"]:
        for y in var_y["values"]:
            # Update data dict
            data[var_x["key"]] = x
            data[var_y["key"]] = y

            # Call function with updated data as parameters
            result = function(**data)

            # Store x, y, and result in results list
            results.append((x, y, result))

    return results


import pandas as pd


def setup(
    data,
    dropna=False,
    dropzeros=False,
    trim_leading_zeros=False,
    trim_trailing_zeros=False,
):
    """
    Prepares a DataFrame for time-series operations by ensuring the index is a DateTimeIndex and is sorted in ascending order.

    Args:
        data (dict): A dictionary of data to be turned into a DataFrame.
        dropna (bool, optional): If True, drop rows with NaN values. Defaults to False.
        dropzeros (bool, optional): If True, drop rows where all columns have zeros, across the entire DataFrame. Defaults to False.
        trim_leading_zeros (bool, optional): If True, trim leading rows where all or any columns have zeros. Defaults to False.
        trim_trailing_zeros (bool, optional): If True, trim trailing rows where any columns have zeros. Defaults to False.

    Returns:
        pd.DataFrame: A DataFrame with a DateTimeIndex sorted in ascending order.
    """
    df = pd.DataFrame(data)
    df.index = pd.to_datetime(df.index)
    df.sort_index(inplace=True)

    if dropna:
        df.dropna(inplace=True)

    if dropzeros:
        df = df[df.ne(0).any(axis=1)]

    if trim_leading_zeros:
        while (df.iloc[0] == 0).any():
            df = df.iloc[1:]

    if trim_trailing_zeros:
        while (df.iloc[-1] == 0).any():
            df = df.iloc[:-1]

    return df


def returning(data):
    if isinstance(data.index, pd.DatetimeIndex):
        data.index = data.index.strftime("%Y-%m-%d")
    return data


def clean(data, fill_method="zero"):
    """
    Cleans the data by replacing missing values and infinities.

    Args:
        data (pd.DataFrame): The input data.
        fill_method (str, optional): The method to use for filling missing values. Defaults to 'ffill'.
            Options are:
            - 'ffill': forward fill, which propagates the last observed non-null value forward until another non-null value is met.
            - 'bfill': backward fill, which propagates the next observed non-null value backwards until another non-null value is met.
            - 'zero': fill with zeros.

    Returns:
        pd.DataFrame: The cleaned data.
    """

    # Copy the data to avoid modifying the original DataFrame
    data_clean = data.copy()

    # Fill missing values
    if fill_method == "ffill":
        data_clean = data_clean.ffill()
    elif fill_method == "bfill":
        data_clean = data_clean.bfill()
    elif fill_method == "zero":
        data_clean = data_clean.fillna(0)
    else:
        raise ValueError(
            "Invalid fill method. Options are 'ffill', 'bfill', and 'zero'."
        )

    # Replace infinities
    data_clean = data_clean.replace([np.inf, -np.inf], 0)

    return data_clean


def filter_dataframe(df, end_date, start_date=None, periods=None):
    """
    Filter the DataFrame by date range and drop columns with missing data.

    Args:
        df (pd.DataFrame): DataFrame with daily returns for assets.
        end_date (str): The final date in "YYYY-MM-DD" format.
        start_date (str, optional): The initial date in "YYYY-MM-DD" format. Defaults to None.
        periods (int, optional): The number of past years from the end_date to calculate the start_date if not provided.

    Returns:
        pd.DataFrame: Filtered DataFrame with rows within the specified date range and only columns with complete data.
    """
    # Calculate start_date if not provided
    if start_date is None and periods is not None:
        start_date = add_days(end_date, num_years=-periods)

    if start_date is None:
        raise ValueError("Either start_date or periods must be provided.")

    # Filter rows by date range
    df = df.loc[start_date:end_date]

    # Drop columns with missing data
    df = df.dropna(axis=1)

    return df


def match_vol(returns, target):
    """
    Adjusts the returns of a portfolio or an asset to match a target level of volatility.

    The function computes the standard deviation (volatility) of the input returns,
    then scales the returns such that the returns standard deviation matches the target.

    This function assumes returns and their volatility are normally distributed,
    which is a common but not always accurate assumption in financial markets.

    Args:
        returns (Union[pd.DataFrame, pd.Series]): A DataFrame or Series containing the returns of the assets.
        target (float): The target volatility level to which the returns should be adjusted.

    Returns:
        Union[pd.DataFrame, pd.Series]: Returns a DataFrame or Series with the adjusted returns of the assets.
    """

    # Adjust the returns to match the target volatility
    return returns / returns.std() * target


def to_returns(prices, log_returns=False, clean=False):
    """
    Calculates the returns of one or more assets in a DataFrame or Series.

    Args:
        prices (Union[pd.DataFrame, pd.Series]): A DataFrame or Series containing the prices of the assets.
        log_returns (bool, optional): If True, calculates log returns instead of simple returns. Defaults to False.

    Returns:
        Union[pd.DataFrame, pd.Series]: Returns a DataFrame or Series with the returns of the assets.
    """

    # Ensure input is a DataFrame
    if isinstance(prices, (pd.Series)):
        prices = setup(prices)

    if not isinstance(prices, (pd.DataFrame)):
        raise ValueError("Input must be a pandas DataFrame or Series.")

    # Calculate returns for each asset individually
    returns = prices.apply(
        lambda x: np.log(x / x.shift(1)).dropna()
        if log_returns
        else x.pct_change().dropna(),
        axis=0,
    )

    return returns


def to_cumulative_returns(returns, compounded=True):
    """
    Calculates the cumulative returns of the assets.

    Args:
        returns (pd.DataFrame): A DataFrame containing the returns of the assets.
        compounded (bool): If True, calculates the compounded return. If False, calculates the simple return.
                      Defaults to True.

    Returns:
        pd.DataFrame: A DataFrame containing the cumulative returns.
    """
    if compounded:
        return returns.add(1).cumprod() - 1
    else:
        return returns.cumsum()


def rebase(prices, base=100, base_date=None, matching=False):
    """
    Rebase a series to a given initial base.

    Args:
        prices (pd.DataFrame): The input price data.
        base (float, optional): The base value for the rebased series. Defaults to 100.
        base_date (str, optional): The date from which the base value should start. If not provided, the base value starts from the first non-NaN date for each asset in the data.
        matching (bool, optional): If True, uses the most recent available date or base_date (if provided) for all columns. Defaults to False.

    Returns:
        pd.DataFrame: The rebased series.
    """
    # Convert the input to DataFrame if it's a Series
    if isinstance(prices, pd.Series):
        prices = setup(prices)

    # Convert the base_date to Timestamp if it's provided
    base_date = pd.to_datetime(base_date) if base_date else None

    if matching:
        # If 'matching' is True, find the latest first valid index among all columns
        latest_base_date = max(
            [prices[column].first_valid_index() for column in prices.columns]
        )
        # If base_date is provided, use it if it's later than the latest_base_date.
        base_date = max(latest_base_date, base_date) if base_date else latest_base_date

    for column in prices.columns:
        # If base_date is not provided, use the first non-NaN date for each asset
        actual_base_date = prices[column].first_valid_index()
        actual_base_date = (
            actual_base_date if not base_date else max(actual_base_date, base_date)
        )
        # Get the price at the base date
        base_price = prices.loc[actual_base_date, column]

        # Rebase the prices for this asset
        prices[column] = prices[column] / base_price * base

    return prices


def to_quotes(returns, base=100, base_date=None, periods=None, compounded=True):
    """
    Converts return data into quote prices.

    Args:
        returns (pd.DataFrame): The return data.
        base (float, optional): The base value for the quote prices. Defaults to 100.
        base_date (str, optional): The date from which the base value should start. If not provided, the base value starts from the beginning of the data.
        periods (int, optional): The number of periods in a year for converting annualized returns to daily. If not provided, no conversion occurs.
        compounded (bool, optional): If True, calculates compounded returns. If False, calculates simple returns. Defaults to True.

    Returns:
        pd.DataFrame: The quote prices.
    """
    if periods is not None:
        if compounded:
            returns = (1 + returns) ** (1 / periods) - 1
        else:
            returns = returns / periods

    # Calculate cumulative returns
    cumulative_returns = 1 + to_cumulative_returns(returns, compounded)

    # Rebase the quotes to the given base and base_date
    rebased_quotes = rebase(cumulative_returns, base, base_date)

    return rebased_quotes


def to_excess_returns(returns, rf=0.0, periods=None, compounded=True):
    """
    Calculates excess returns.

    Args:
        returns (np.ndarray, pd.DataFrame or pd.Series): The input returns.
        rf (float or pd.Series, optional): The risk-free rate. Defaults to 0.0.
        periods (int, optional): The number of periods for the risk-free rate calculation.
        compounded (bool, optional): If True, calculates compounded returns. If False, calculates simple returns. Defaults to True.

    Returns:
        np.ndarray, pd.DataFrame or pd.Series: The excess returns.

    """

    # If rf is a DataFrame, ensure it only has a single column
    if isinstance(rf, pd.DataFrame):
        # if DataFrame has more than one column, select the first one
        rf = rf.iloc[:, 0]

    if isinstance(rf, pd.Series):
        # Align the returns and rf to ensure they have the same dates
        returns, rf = returns.align(rf, join="inner", axis=0)

    if periods is not None:
        if compounded:
            rf = np.power(1 + rf, 1.0 / periods) - 1.0
        else:
            rf = rf / periods

    excess_returns = returns.sub(rf, axis=0)

    return excess_returns


def group_returns(returns, period_freq, compounded=True, periods=None, annualize=False):
    """
    Summarizes returns based on grouping criteria.

    Args:
        returns (pd.DataFrame or pd.Series): The input returns.
        period_freq (str): The period frequency (e.g., 'D', 'M', 'Q', 'Y')
        compounded (bool, optional): If True, calculates compounded returns. Defaults to True.
        periods (int, optional): The number of periods for annualization. Defaults to None.
        annualize (bool, optional): If True, the returns are annualized. Defaults to False.

    Returns:
        pd.DataFrame or pd.Series: The summarized returns.
    """
    if not isinstance(returns.index, pd.DatetimeIndex):
        returns = setup(returns)

    grouped_returns = returns.resample(period_freq).apply(
        lambda x: stats.total_return(
            x, compounded=compounded, periods=periods, annualize=annualize
        )
    )

    # convert the index back to datetime (normalized to remove the time part)
    grouped_returns.index = grouped_returns.index.normalize().strftime("%Y-%m-%d")

    return grouped_returns


def aggregate_returns(returns, period=None, compounded=True):
    """
    Aggregates returns based on date periods.

    Args:
        returns (pd.DataFrame or pd.Series): The input returns.
        period (str or list, optional): The desired date period for aggregation. Defaults to None.
        compounded (bool, optional): If True, calculates compounded returns. Defaults to True.

    Returns:
        pd.DataFrame or pd.Series: The aggregated returns.
    """
    if period is None or "day" in period:
        return returns

    groupby_mapping = {
        "month": "M",
        "quarter": "Q",
        "year": "Y",
        "week": "W",
        "eow": "W",
        "eom": "M",
        "eoq": "Q",
        "eoy": "Y",
    }

    period_freq = groupby_mapping.get(period, "D")  # defaults to daily if not found

    return group_returns(returns, period_freq, compounded=compounded)


def to_drawdown_series(returns):
    """
    Convert returns series to drawdown series.

    Args:
        returns (pd.Series or pd.DataFrame): The input returns series.

    Returns:
        pd.Series or pd.DataFrame: The drawdown series.
    """
    prices = to_quotes(returns)
    prices = clean(prices)

    max_prices = np.maximum.accumulate(prices)
    dd = prices / max_prices - 1.0

    # Handle division by zero or infinity
    dd = dd.replace([np.inf, -np.inf], np.nan).fillna(0)

    return dd


def rolling_metric(returns, function, window=252, **kwargs):
    """
    Calculate a rolling metric using a given function.

    Args:
        returns (pd.Series or pd.DataFrame): The input returns series.
        function (callable): The function to apply on the rolling window.
        window (int, optional): The rolling window period for calculating the metric. Defaults to 252.
        **kwargs: Optional keyword arguments that are passed to the function.

    Returns:
        pd.Series or pd.DataFrame: The calculated rolling metric.
    """

    # Ensure the function is callable
    if not callable(function):
        raise ValueError("The function argument must be callable.")

    # Calculate rolling metric using the provided function
    roll_metric = returns.rolling(window).apply(lambda x: function(x, **kwargs))

    return roll_metric[window:]


def drawdown_details(drawdown):
    """
    Calculates detailed information about each drawdown period within a given series of drawdown data.
    A drawdown period is defined as a continuous period of time where the drawdown is below 0.
    The start of a drawdown period is the time when the drawdown first goes below 0,
    and the end of a drawdown period is the time when the drawdown recovers to 0.

    For each drawdown period, this function will provide the following information:
    1. Start date of the drawdown period
    2. Valley date, i.e., the date with the maximum drawdown within the period
    3. End date of the drawdown period
    4. Duration of the drawdown period in days
    5. Maximum drawdown during the period, as a percentage

    Parameters:
    - drawdown: A Pandas DataFrame or Series that contains drawdown information.

    Returns:
    - A Pandas DataFrame that contains detailed information about each drawdown period.
    """

    def _drawdown_details(single_drawdown):
        # Define drawdown periods: '1' for drawdown, '0' for no drawdown
        drawdown_periods = (single_drawdown != 0).astype(int)

        # Identify the start and end of each drawdown period
        drawdown_diff = drawdown_periods.diff()
        starts = drawdown_diff[drawdown_diff == 1].index
        ends = drawdown_diff[drawdown_diff == -1].index

        # Handle case when no drawdowns found
        if starts.size == 0:
            columns = ["start", "valley", "end", "days", "max drawdown"]
            return pd.DataFrame(columns=columns)

        # Handle case when drawdown starts from the first data point
        if starts[0] > ends[0]:
            starts = starts.insert(0, single_drawdown.index[0])

        # Handle case when drawdown continues till the last data point
        if starts[-1] > ends[-1]:
            ends = ends.append(pd.Index([single_drawdown.index[-1]]))

        # Calculate drawdown details for each period
        data = []
        for start, end in zip(starts, ends):
            period = single_drawdown[start:end]
            valley_date = period.idxmin()
            max_drawdown = period.min()
            data.append(
                [
                    start.date(),
                    valley_date.date(),
                    end.date(),
                    (end - start).days,
                    max_drawdown * 100,
                ]
            )

        columns = ["start", "valley", "end", "days", "max drawdown"]
        df = pd.DataFrame(data, columns=columns)

        return df

    if isinstance(drawdown, pd.DataFrame):
        return pd.concat(
            {col: _drawdown_details(drawdown[col]) for col in drawdown.columns}, axis=1
        )

    return _drawdown_details(drawdown)


def corr_to_cov(correlation, std_dev):
    """
    Convert a correlation matrix to a covariance matrix.

    Args:
        correlation (pd.DataFrame): The input correlation matrix.
        std_dev (pd.Series): The standard deviations for each asset.

    Returns:
        pd.DataFrame: The calculated covariance matrix.
    """

    # Calculate the covariance matrix by multiplying the correlation with outer product of standard deviations
    covariance = correlation.mul(std_dev, axis=0).mul(std_dev, axis=1)

    return covariance


def cov_to_corr(covariance):
    """
    Convert a covariance matrix to a correlation matrix.

    Args:
        covariance (pd.DataFrame): The input covariance matrix.

    Returns:
        pd.DataFrame: The calculated correlation matrix.
    """

    # Calculate the standard deviation for each asset
    std_dev = np.sqrt(np.diag(covariance))

    # Calculate the correlation matrix by dividing the covariance matrix with the outer product of standard deviations
    correlation = covariance / np.outer(std_dev, std_dev)

    # Return as a DataFrame with same index and columns as the covariance matrix
    return pd.DataFrame(correlation, index=covariance.index, columns=covariance.columns)
