class TestUtils:
    def test_hms_string(self):
        from helperfns.utils import hms_string
        import time

        start = time.time()
        time.sleep(2)
        end = time.time()
        assert "02" in hms_string(end - start)
