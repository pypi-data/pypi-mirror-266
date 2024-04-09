Tables
++++++

In the tables sub package you can print your data in tabular form for example:

.. code-block::

    from helperfns.tables import tabulate_data

    column_names = ["SUBSET", "EXAMPLE(s)", "Hello"]
    row_data = [["training", 5, 4],['validation', 4, 4],['test', 3, '']]
    tabulate_data(column_names, row_data)

.. note:: The above code will yield the following table in the terminal console or within a notebook.


+------------+------------+-------+
| SUBSET     | EXAMPLE(s) | Hello |
+============+============+=======+
| training   |          5 |     4 |
+------------+------------+-------+
| validation |          4 |     4 |
+------------+------------+-------+
| test       |          3 |       |
+------------+------------+-------+

The following is the table of arguments for the ``tabulate_data`` helper function

+--------------+------------------------------------+----------------------------------------------+
| Argument     | Description                        | Type                                         |
+==============+====================================+==============================================+
| column_names | List of column names               | list                                         |
+--------------+------------------------------------+----------------------------------------------+
| data         | Data to be tabulated               | list                                         |
+--------------+------------------------------------+----------------------------------------------+
| title        | Title of the table                 | str                                          |
+--------------+------------------------------------+----------------------------------------------+
