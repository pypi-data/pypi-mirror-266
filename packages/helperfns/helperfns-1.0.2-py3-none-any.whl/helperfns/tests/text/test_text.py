class TestText:

    def test_clean_sentence(self):
        from helperfns.text import clean_sentence

        assert clean_sentence("text 1 # https://url.com/bla1/blah1/") == "text"

    def test_de_contract(self):
        from helperfns.text import de_contract

        assert de_contract("I'm") == "I am"

    def test_generate_bigrams(self):
        from helperfns.text import generate_bigrams

        assert sorted(generate_bigrams(["This", "film", "is", "terrible"])) == sorted(
            [
                "This",
                "film",
                "is",
                "terrible",
                "This film",
                "film is",
                "is terrible",
            ]
        )

    def test_generate_ngrams(self):
        from helperfns.text import generate_ngrams

        assert sorted(generate_ngrams(["This", "film", "is", "terrible"])) == sorted(
            [
                "This",
                "film",
                "is",
                "terrible",
                "film is terrible",
                "This film is",
            ]
        )
