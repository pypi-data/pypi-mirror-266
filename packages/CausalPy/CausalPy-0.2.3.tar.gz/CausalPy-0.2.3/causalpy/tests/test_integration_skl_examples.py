import pandas as pd
import pytest
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import ExpSineSquared, WhiteKernel
from sklearn.linear_model import LinearRegression

import causalpy as cp


@pytest.mark.integration
def test_did():
    """
    Test Difference in Differences (DID) Sci-Kit Learn experiment.

    Loads data and checks:
    1. data is a dataframe
    2. skl_experiements.DifferenceInDifferences returns correct type
    """

    data = cp.load_data("did")
    result = cp.skl_experiments.DifferenceInDifferences(
        data,
        formula="y ~ 1 + group*post_treatment",
        time_variable_name="t",
        group_variable_name="group",
        treated=1,
        untreated=0,
        model=LinearRegression(),
    )
    assert isinstance(data, pd.DataFrame)
    assert isinstance(result, cp.skl_experiments.DifferenceInDifferences)


@pytest.mark.integration
def test_rd_drinking():
    """
    Test Regression Discontinuity Sci-Kit Learn experiment on drinking age data.

    Loads data and checks:
    1. data is a dataframe
    2. skl_experiements.RegressionDiscontinuity returns correct type
    """
    df = (
        cp.load_data("drinking")
        .rename(columns={"agecell": "age"})
        .assign(treated=lambda df_: df_.age > 21)
    )
    result = cp.skl_experiments.RegressionDiscontinuity(
        df,
        formula="all ~ 1 + age + treated",
        running_variable_name="age",
        model=LinearRegression(),
        treatment_threshold=21,
        epsilon=0.001,
    )
    assert isinstance(df, pd.DataFrame)
    assert isinstance(result, cp.skl_experiments.RegressionDiscontinuity)


@pytest.mark.integration
def test_its():
    """
    Test Interrupted Time Series Sci-Kit Learn experiment.

    Loads data and checks:
    1. data is a dataframe
    2. skl_experiements.SyntheticControl returns correct type
    """

    df = (
        cp.load_data("its")
        .assign(date=lambda x: pd.to_datetime(x["date"]))
        .set_index("date")
    )
    treatment_time = pd.to_datetime("2017-01-01")
    result = cp.skl_experiments.SyntheticControl(
        df,
        treatment_time,
        formula="y ~ 1 + t + C(month)",
        model=LinearRegression(),
    )
    assert isinstance(df, pd.DataFrame)
    assert isinstance(result, cp.skl_experiments.SyntheticControl)


@pytest.mark.integration
def test_sc():
    """
    Test Synthetic Control Sci-Kit Learn experiment.

    Loads data and checks:
    1. data is a dataframe
    2. skl_experiements.SyntheticControl returns correct type
    """
    df = cp.load_data("sc")
    treatment_time = 70
    result = cp.skl_experiments.SyntheticControl(
        df,
        treatment_time,
        formula="actual ~ 0 + a + b + c + d + e + f + g",
        model=cp.skl_models.WeightedProportion(),
    )
    assert isinstance(df, pd.DataFrame)
    assert isinstance(result, cp.skl_experiments.SyntheticControl)


@pytest.mark.integration
def test_rd_linear_main_effects():
    """
    Test Regression Discontinuity Sci-Kit Learn experiment main effects.

    Loads data and checks:
    1. data is a dataframe
    2. skl_experiements.RegressionDiscontinuity returns correct type
    """
    data = cp.load_data("rd")
    result = cp.skl_experiments.RegressionDiscontinuity(
        data,
        formula="y ~ 1 + x + treated",
        model=LinearRegression(),
        treatment_threshold=0.5,
        epsilon=0.001,
    )
    assert isinstance(data, pd.DataFrame)
    assert isinstance(result, cp.skl_experiments.RegressionDiscontinuity)


@pytest.mark.integration
def test_rd_linear_main_effects_bandwidth():
    """
    Test Regression Discontinuity Sci-Kit Learn experiment, main effects with
    bandwidth parameter.

    Loads data and checks:
    1. data is a dataframe
    2. skl_experiements.RegressionDiscontinuity returns correct type
    """
    data = cp.load_data("rd")
    result = cp.skl_experiments.RegressionDiscontinuity(
        data,
        formula="y ~ 1 + x + treated",
        model=LinearRegression(),
        treatment_threshold=0.5,
        epsilon=0.001,
        bandwidth=0.3,
    )
    assert isinstance(data, pd.DataFrame)
    assert isinstance(result, cp.skl_experiments.RegressionDiscontinuity)


@pytest.mark.integration
def test_rd_linear_with_interaction():
    """
    Test Regression Discontinuity Sci-Kit Learn experiment with interaction.

    Loads data and checks:
    1. data is a dataframe
    2. skl_experiements.RegressionDiscontinuity returns correct type
    """
    data = cp.load_data("rd")
    result = cp.skl_experiments.RegressionDiscontinuity(
        data,
        formula="y ~ 1 + x + treated + x:treated",
        model=LinearRegression(),
        treatment_threshold=0.5,
        epsilon=0.001,
    )
    assert isinstance(data, pd.DataFrame)
    assert isinstance(result, cp.skl_experiments.RegressionDiscontinuity)


@pytest.mark.integration
def test_rd_linear_with_gaussian_process():
    """
    Test Regression Discontinuity Sci-Kit Learn experiment with Gaussian process model.

    Loads data and checks:
    1. data is a dataframe
    2. skl_experiements.RegressionDiscontinuity returns correct type
    """
    data = cp.load_data("rd")
    kernel = 1.0 * ExpSineSquared(1.0, 5.0) + WhiteKernel(1e-1)
    result = cp.skl_experiments.RegressionDiscontinuity(
        data,
        formula="y ~ 1 + x + treated",
        model=GaussianProcessRegressor(kernel=kernel),
        treatment_threshold=0.5,
        epsilon=0.001,
    )
    assert isinstance(data, pd.DataFrame)
    assert isinstance(result, cp.skl_experiments.RegressionDiscontinuity)
