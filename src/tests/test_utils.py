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

    def test_seconds_human_friendly(self):
        for i in range(60):
            if i in range(2):
                assert seconds_human_friendly(i) == f'{i} segundo'
            else:
                assert seconds_human_friendly(i) == f'{i} segundos'

        one_minute = 60
        assert seconds_human_friendly(one_minute) == '01:00'
        ten_minutes = 600
        assert seconds_human_friendly(ten_minutes) == '10:00'
        one_hour = 3600
        assert seconds_human_friendly(one_hour) == '1:00:00'

        one_hour_thirty_minutes = one_hour + ten_minutes*3
        assert seconds_human_friendly(one_hour_thirty_minutes) == '1:30:00'

        ten_hours_twentyfive_minutes_fiftynine_seconds = one_hour*10 + round(ten_minutes*2.5) + 59
        assert seconds_human_friendly(ten_hours_twentyfive_minutes_fiftynine_seconds) == '10:25:59'
        
        twentythree_hours_fiftynine_minutes_fiftynine_seconds = one_hour*23 + round(ten_minutes*5.9) + 59
        assert seconds_human_friendly(twentythree_hours_fiftynine_minutes_fiftynine_seconds) == '23:59:59'

        one_day = one_hour * 24
        assert seconds_human_friendly(one_day) == '1 dia, 0:00:00'

        two_days = one_hour * 24 * 2
        assert seconds_human_friendly(two_days) == '2 dias, 0:00:00'

