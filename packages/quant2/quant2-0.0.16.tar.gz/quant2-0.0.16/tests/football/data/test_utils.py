from quant.football.data.utils import time_secs2str, time_str2secs


def test_time_secs2str():
    text = "2024-03-28 09:01:06"
    assert time_secs2str(time_str2secs(text)) == text
