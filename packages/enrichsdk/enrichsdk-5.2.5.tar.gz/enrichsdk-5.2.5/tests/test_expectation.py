import os
import json
import pytest

from enrichsdk.quality import *


def test_expectation_manager():
    """
    Test manager configuration
    """

    mgr = ExpectationManagerBase()
    with pytest.raises(NotInitialized) as excinfo:
        mgr.validate(None, None)

    mgr.initialize()

    with pytest.raises(InvalidExpectation) as excinfo:
        mgr.validate(None, None)

    with pytest.raises(NoExpectations) as excinfo:
        mgr.validate(None, [])


def test_unknown_expectation():
    """
    Test unknown expectation
    """

    mgr = ExpectationManagerBase()
    mgr.initialize()

    with pytest.raises(UnsupportedExpectation) as excinfo:
        mgr.validate(None, {"expectation": "Unknown_XXX"})


@pytest.mark.parametrize("df", [None, "", 1, []])
def test_table_columns_invalid_frame(df):
    """
    Test unknown expectation
    """

    mgr = ExpectationManagerBase()
    mgr.initialize()

    with pytest.raises(InvalidExpectation) as excinfo:
        mgr.validate(df, {"expectation": "table_columns_exist"})

    result = mgr.validate(
        df, {"expectation": "table_columns_exist", "params": {"columns": "hello"}}
    )

    assert len(result) == 1
    assert result[0]["expectation"] == "table_columns_exist"
    assert not result[0]["passed"]
    assert "extra" in result[0] and "Not a dataframe" in result[0]["extra"]["reason"]


@pytest.mark.parametrize(
    "df",
    [
        pd.DataFrame([]),
        pd.DataFrame([{"hello1": 1}]),
    ],
)
def test_table_columns_missing_columns(df):
    """
    Test unknown expectation
    """

    mgr = ExpectationManagerBase()
    mgr.initialize()

    with pytest.raises(InvalidExpectation) as excinfo:
        mgr.validate(df, {"expectation": "table_columns_exist"})

    result = mgr.validate(
        df, {"expectation": "table_columns_exist", "params": {"columns": "hello"}}
    )

    assert len(result) == 1
    assert result[0]["expectation"] == "table_columns_exist"
    assert not result[0]["passed"]
    assert "extra" in result[0] and "Missing column" in result[0]["extra"]["reason"]


@pytest.mark.parametrize(
    "df,error",
    [
        (pd.DataFrame([]), "Wrong position"),
        (pd.DataFrame([{"col1": 1}]), "Wrong position"),
        (pd.DataFrame([[1]], columns=["col1"]), "Wrong position"),
        (pd.DataFrame([[1, 2]], columns=["col1", "col2"]), "Wrong position"),
        (pd.DataFrame([[1, 2, 3]], columns=["col2", "col3", "col1"]), "Wrong position"),
    ],
)
def test_table_columns_with_position(df, error):
    """
    Test column positioning
    """

    mgr = ExpectationManagerBase()
    mgr.initialize()

    with pytest.raises(InvalidExpectation) as excinfo:
        mgr.validate(df, {"expectation": "table_columns_exist"})

    # Test position = 1
    result = mgr.validate(
        df,
        {
            "expectation": "table_columns_exist_with_position",
            "params": {"columns": {"hello": 1}},
        },
    )

    assert len(result) == 1
    assert result[0]["expectation"] == "table_columns_exist_with_position"
    assert not result[0]["passed"]
    assert "extra" in result[0] and error in result[0]["extra"]["reason"]


@pytest.mark.parametrize("df", [pd.DataFrame([])])
def test_custom_check(df):
    """
    Test custom expectation
    """

    # => Create a custom expectation
    class CustomExpectation(ExpectationBase):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.name = "custom_expectation"

    # Manager should pickup this new class
    mgr = ExpectationManagerBase()
    mgr.initialize()

    # Dont raise any error
    mgr.validate(df, {"expectation": "custom_expectation"})

    # Test position = 1
    result = mgr.validate(df, {"expectation": "custom_expectation", "params": {}})

    assert len(result) == 1
    assert result[0]["expectation"] == "custom_expectation"
    assert result[0]["passed"]
