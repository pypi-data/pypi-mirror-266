"""
This module contains standard expectations that can be used to test data artifact in a
Bauplan pipeline. Using these expectations instead of hand-made ones will make your
pipeline easier to maintain, and significantly faster and more memory-efficient.

Each function should return a boolean, so that the wrapping function can assert or just
print out messages.
"""

from typing import Any

import pyarrow as pa
import pyarrow.compute as pc


def _calculate_string_concatenation(table: pa.Table, columns: list, separator: str = '') -> Any:
    """
    Given a pyarrow table and a list of column names, concatenate the columns into a new column.
    The caller of the function can then used the column to compare it with an existing column or add it.

    The function does attempt type conversion to string if a column is not of type pa.string().

    """
    fields = []
    for column in columns:
        fields.append(
            pc.cast(table[column], pa.string()) if table[column].type != pa.string() else table[column]
        )
    # last item needs to be the separator
    fields.append(separator)

    return pc.binary_join_element_wise(*fields)


def _calculate_column_mean(table: pa.Table, column_name: str) -> float:
    """
    Use built-in pyarrow compute functions to calculate the mean of a column.
    """
    return pc.mean(table[column_name]).as_py()


def expect_column_equal_concatenation(
    table: pa.Table,
    target_column: str,
    columns: list,
    separator: str = '',
) -> Any:
    """
    Given a target column and a list of columns, expect the target column to be equal to the concatenation
    of the columns in the list.

    If the columns are not of type pa.string(), the function will attempt to convert them to string.

    If a custom separator is needed (default: the empty string), it can be passed as an argument.

    It returns a boolean, so that the wrapping function can assert on it and produce a custom error message.
    """
    # produce a new column that is the concatenation of the columns in the list
    # and compare the new column with the target column
    return pc.all(
        pc.equal(
            _calculate_string_concatenation(table, columns, separator),
            table[target_column],
        )
    ).as_py()


def expect_column_mean_greater_than(table: pa.Table, column_name: str, value: float) -> bool:
    """
    Given a column name, expect the mean of that column to be greater than value.

    Return a boolean, so that the wrapping function can assert on it and produce
    any custom error messages.
    """
    _mean = _calculate_column_mean(table, column_name)
    return _mean > value


def expect_column_mean_greater_or_equal_than(table: pa.Table, column_name: str, value: float) -> bool:
    """
    Given a column name, expect the mean of that column to be greater or equal than value.

    Return a boolean, so that the wrapping function can assert on it and produce
    any custom error messages.
    """
    _mean = _calculate_column_mean(table, column_name)
    return _mean >= value


def expect_column_mean_smaller_than(table: pa.Table, column_name: str, value: float) -> bool:
    """
    Given a column name, expect the mean of that column to be smaller than value.

    Return a boolean, so that the wrapping function can assert on it and produce
    any custom error messages.
    """
    _mean = _calculate_column_mean(table, column_name)
    return _mean < value


def expect_column_mean_smaller_or_equal_than(table: pa.Table, column_name: str, value: float) -> bool:
    """
    Given a column name, expect the mean of that column to be smaller or equal than value.

    Return a boolean, so that the wrapping function can assert on it and produce
    any custom error messages.
    """
    _mean = _calculate_column_mean(table, column_name)
    return _mean <= value


def _column_nulls(table: pa.Table, column_name: str) -> int:
    """
    Return number of nulls in a column.
    """
    return table[column_name].null_count


def expect_column_some_null(table: pa.Table, column_name: str) -> bool:
    """
    Given a column name, expect the column to have nulls.

    Return a boolean, so that the wrapping function can assert on it and produce
    any custom error messages.
    """
    return _column_nulls(table, column_name) > 0


def expect_column_no_nulls(table: pa.Table, column_name: str) -> bool:
    """
    Given a column name, expect the column to not have nulls.

    Return a boolean, so that the wrapping function can assert on it and produce
    any custom error messages.
    """
    return _column_nulls(table, column_name) == 0


def expect_column_all_null(table: pa.Table, column_name: str) -> bool:
    """
    Given a column name, expect the column to be all nulls.

    Return a boolean, so that the wrapping function can assert on it and produce
    any custom error messages.
    """
    return _column_nulls(table, column_name) == table[column_name].length()


def _column_unique(table: pa.Table, column_name: str) -> int:
    """
    Return number of unique values in a column.
    """
    return len(pc.unique(table[column_name]))


def expect_column_all_unique(table: pa.Table, column_name: str) -> bool:
    """
    Given a column name, expect the column to have all unique values.

    Return a boolean, so that the wrapping function can assert on it and produce
    any custom error messages.
    """
    return _column_unique(table, column_name) == len(table[column_name])


def expect_column_not_unique(table: pa.Table, column_name: str) -> bool:
    """
    Given a column name, expect the column to have non-unique values.

    Return a boolean, so that the wrapping function can assert on it and produce
    any custom error messages.
    """
    return _column_unique(table, column_name) < len(table[column_name])


def _column_accepted_values(table: pa.Table, column_name: str, accepted_values: list) -> Any:
    """
    Return number of unique values in a column.
    """
    return pc.all(pc.is_in(table[column_name], pa.array(accepted_values))).as_py()


def expect_column_accepted_values(table: pa.Table, column_name: str, accepted_values: list) -> Any:
    """
    Given a column name, expect the column to have only accepted values.

    Return a boolean, so that the wrapping function can assert on it and produce
    any custom error messages.
    """

    return _column_accepted_values(table, column_name, accepted_values)
