from prettytable import PrettyTable


def tabulate_data(column_names: list, data: list, title: str = "Table"):
    """
    Tabulate Data

    This function print the data in a nice table format.

    Parameters
    ----------
    column_names : list
        These are table headers.
    labels_true : list
        Takes in a collection of correct labels.
    data : list
        The data that you want to print in table format.

    Keyword Args
    ------------
    title : str
        The table title, the default title is "Table".

    Returns
    -------
    None

    See Also
    --------
    tabulate_translations: Tabulate translation data with translation target paired to translation source.

    Examples
    --------
    >>> column_names = ["SUBSET", "EXAMPLE(s)", "Hello"]
    >>> row_data = [["training", 5, 4],['validation', 4, 4],['test', 3, '']]
    >>> tabulate_data(column_names, row_data)
    +---------------------------------+
    |              Table              |
    +------------+------------+-------+
    | SUBSET     | EXAMPLE(s) | Hello |
    +------------+------------+-------+
    | training   |          5 |     4 |
    | validation |          4 |     4 |
    | test       |          3 |       |
    +------------+------------+-------+
    """
    assert len(data) != 0, "Data is required but got nothing."
    assert len(column_names) == len(
        data[0]
    ), f"Column names and data must have the same length, but got {len(column_names)} and {len(data)}."
    assert all(
        [len(d) == len(data[0]) for d in data]
    ), "The row data must have the same length."

    table = PrettyTable(column_names)
    for i, name in enumerate(column_names):
        if i == 0:
            table.align[name] = "l"
        else:
            table.align[name] = "r"
    for row in data:
        table.add_row(row)

    print(title)
    print(table)


__all__ = [tabulate_data]
