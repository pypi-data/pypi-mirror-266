Utils
+++++

utils package comes with a simple helper function for converting ``seconds`` to ``hours``, ``minutes`` and ``seconds``.

Example:

.. code-block:: 

    from helperfns.utils import hms_string

    start = time.time()
    for i in range(100000):
    pass
    end = time.time()

    print(hms_string(end - start))


Output:

.. code-block:: shell

    '0:00:00.01'

The ``hms_string`` takes in the following as arguments.

+-------------+---------------------------------+------+
| Argument    | Description                     | Type |
+=============+=================================+======+
| sec_elapsed | Time in seconds to be converted | Any  |
+-------------+---------------------------------+------+
