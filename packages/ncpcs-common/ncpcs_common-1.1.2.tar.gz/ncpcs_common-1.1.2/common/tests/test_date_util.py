from common.util.date_util import convert_compact_timestamp_to_standard, convert_standard_timestamp_to_compact, \
    timestamp_parse, timeseg_parse, diff_between_dates


class TestDateUtil:
    def test_convert_compact_timestamp_to_standard(self):
        timestamp = convert_compact_timestamp_to_standard("20201202150001")
        assert timestamp == '2020-12-02 15:00:01'
        timestamp = convert_compact_timestamp_to_standard("0201202150001")
        assert timestamp is None
        timestamp = convert_compact_timestamp_to_standard("sdf20201202150001")
        assert timestamp is None

    def test_convert_standard_timestamp_to_compact(self):
        timestamp = convert_standard_timestamp_to_compact("2020-12-02 15:00:01")
        assert timestamp == '20201202150001'

    def test_timeseg_parse(self):
        assert timeseg_parse("两周三天", "20231231000000") == '2023-12-14'
        assert timeseg_parse("一年", "20231231000000") == '2022-12-31'

    def test_timestamp_parse(self):
        assert timestamp_parse("2023年02月03日") == '2023-02-03'
        assert timestamp_parse("2018-5月") == '2018-05'
        assert timestamp_parse("2020-07-271") == '2020-07-27'
        assert timestamp_parse("2009年") == '2009'
        assert timestamp_parse("2021.6.6") == '2021-06-06'
        assert timestamp_parse("2020-02-0918，30输血后疗效评估记录1.输血指征、诊断：急性髓系白血病(M1型)2.输血时间：2020年02月08日") == '2020-02-09'

    def test_diff_between_dates(self):
        assert diff_between_dates("2018-03-12 00:00:00", "2022-05-11 00:00:00") == '4-1-29'




