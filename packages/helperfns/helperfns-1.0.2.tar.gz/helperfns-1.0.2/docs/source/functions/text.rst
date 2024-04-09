Text
++++

The text package offers two main function which are ``clean_sentence``, ``de_contract``, ``generate_ngrams`` and ``generate_bigrams``

The ``clean_sentence`` helper function clean the sentence by removing the noise from it.

.. code-block:: 

    from helperfns.text import *
    # cleans the sentence
    print(clean_sentence("text 1 # https://url.com/bla1/blah1/"))

Here is the table of arguments for the ``clean_sentence`` function:

+----------+-----------------------------------------------+------+
| Argument | Description                                   | Type |
+==========+===============================================+======+
| sent     | Input sentence                                | str  |
+----------+-----------------------------------------------+------+
| lower    | Flag to convert to lower case (default: True) | bool |
+----------+-----------------------------------------------+------+


If you want to get a list of all english words you can do it as follows:

.. code-block::

    # list of all english words
    print(english_words)

You can use the  ``de_contract`` method to de-contract strings as follows:

.. code-block:: 

    # converts strings like `I'm` to 'I am'
    print(de_contract("I'm"))

Here is the table of arguments for the ``de_contract`` function:

+----------+---------------------+------+
| Argument | Description         | Type |
+==========+=====================+======+
| word     | Word to de-contract | str  |
+----------+---------------------+------+


You can also generate bigrams using the ``generate_bigrams`` as follows:

.. code-block::

    # generate bigrams from a list of word
    print(text.generate_bigrams(['This', 'film', 'is', 'terrible']))


Here is the table of arguments for the ``generate_bigrams`` function:

+----------+------------------------+------+
| Argument | Description            | Type |
+==========+========================+======+
| x        | List of input elements | list |
+----------+------------------------+------+


Apart from generating bigrams ``helperfns.text`` also provides you with a utility to generate n-grams using the  ``generate_ngrams``. Here is an example of how you can use this function

.. code-block:: 

    # generates n-grams from a list of words
    print(text.generate_ngrams(['This', 'film', 'is', 'terrible']))

Here is a table of arguments for the ``generate_ngrams`` function.

+----------+-----------------------------------------------------+------+
| Argument | Description                                         | Type |
+==========+=====================================================+======+
| x        | List of input elements                              | list |
+----------+-----------------------------------------------------+------+
| grams    | Number of grams for generating n-grams (default: 3) | int  |
+----------+-----------------------------------------------------+------+
