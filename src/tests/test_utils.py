from ..utils import *

class TestUtils():
    """Tests for utils.py"""

    def test_is_int_with_int(self):
        assert is_int(1) == True
        assert is_int(-1) == True

    def test_is_int_with_string(self):
        assert is_int('1') == True
        assert is_int('-1') == True
        assert is_int('a') == False
        assert is_int('') == False
        assert is_int('abcdefghij') == False
