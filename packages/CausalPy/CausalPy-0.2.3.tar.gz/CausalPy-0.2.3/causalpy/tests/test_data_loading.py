"""
Tests that example data can be loaded into data frames.
"""
import pandas as pd
import pytest

import causalpy as cp

tests = [
    "banks",
    "brexit",
    "covid",
    "did",
    "drinking",
    "its",
    "its simple",
    "rd",
    "sc",
    "anova1",
]


@pytest.mark.parametrize("dataset_name", tests)
def test_data_loading(dataset_name):
    """
    Checks that test data can be loaded into data frames and that there are no
    missing values in any column.
    """
    df = cp.load_data(dataset_name)
    assert isinstance(df, pd.DataFrame)
    # Check that there are no missing values in any column
    assert df.isnull().sum().sum() == 0
