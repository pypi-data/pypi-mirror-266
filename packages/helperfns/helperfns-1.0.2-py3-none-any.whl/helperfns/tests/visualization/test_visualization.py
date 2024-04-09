class TestVisualization:

    def test_plot_simple_confusion_matrix(self):
        from helperfns.visualization import plot_simple_confusion_matrix
        import pytest

        with pytest.raises(ValueError) as exc_info:
            plot_simple_confusion_matrix([], [])

        assert (
            str(exc_info.value)
            == "zero-size array to reduction operation maximum which has no identity"
        )

    def test_plot_complicated_confusion_matrix(self):
        from helperfns.visualization import plot_complicated_confusion_matrix
        import pytest

        with pytest.raises(ValueError) as exc_info:
            plot_complicated_confusion_matrix([], [])

        assert (
            str(exc_info.value)
            == "zero-size array to reduction operation maximum which has no identity"
        )

    def test_plot_classification_report(self):
        from helperfns.visualization import plot_classification_report
        import pytest

        with pytest.raises(KeyError) as exc_info:
            plot_classification_report([], [])

        assert str(exc_info.value) == "'support'"
