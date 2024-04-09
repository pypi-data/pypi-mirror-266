Usage
+++++


The ``helperfns`` package is made up of different sub packages such as:

#. ``tables``
#. ``text``
#. ``utils``
#. ``visualization``


The following simple example show how you can use this package to tabulate your data.


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

