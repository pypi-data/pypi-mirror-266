class TestTables:
    def test_tabulate_data(self):
        from helperfns.tables import tabulate_data
        import pytest

        with pytest.raises(AssertionError) as exc_info:
            tabulate_data([], [])

        assert str(exc_info.value) == "Data is required but got nothing."
