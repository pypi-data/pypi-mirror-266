from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Model:
    """
    Represents a model (dataframe/table representing a DAG step) as an input
    to a function.

    e.g.::

        @bauplan.model(
            columns=[
                'bar',
            ],
        )
        def some_parent_model():
            return pyarrow.Table.from_pydict({'bar': [1, 2, 3]})

        # the decorator is used to specify a given
        # function as a model
        @bauplan.model(
            columns=[
                'foo',
            ],
            materialize=True,
        )
        def your_cool_model(
            # parent models are passed as inputs, using bauplan.Model
            # class
            parent_0=bauplan.Model(
                'some_parent_model',
                columns=['bar'],
            )
        ):
            # Can return a pandas dataframe or a pyarrow table
            return pyarrow.Table.from_pandas(
                pd.DataFrame({
                    'foo': parent0['bar'] * 2,
                })
            )

    :param name: The name of the model.
    :param columns: The list of columns in the model.
    :param filter: The optional filter for the model. Defaults to None.
    """

    name: str
    columns: List[str]
    filter: Optional[str] = None
