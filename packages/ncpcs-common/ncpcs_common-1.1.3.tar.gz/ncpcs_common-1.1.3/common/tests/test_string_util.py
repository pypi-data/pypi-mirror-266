from common.util.string_util import any_match, any_match_bool, extract_digit, find_all, \
    remove_special_symbols, has_chinese, is_chinese, split_text, handle_short_sentence, locate_two_word


class TestStringUtil:
    def test_any_match(self):
        result = any_match("快乐池塘栽种了梦想就变成海洋", ["快乐", "梦想", "海洋", "人生", "纱布"])
        assert result == ["快乐", "梦想", "海洋"]

    def test_any_match_bool(self):
        result = any_match_bool("快乐池塘栽种了梦想就变成海洋", ["快乐", "人生", "纱布"])
        assert result is True

    def test_extract_digit(self):
        result = extract_digit("快乐1池塘栽5种了梦想就9变成海洋")
        assert result == "159"

    def test_find_all(self):
        positions = find_all("快了1池塘栽5种了梦想就9变成海洋", '了')
        assert positions == [1, 8]

    def test_remove_special_symbols(self):
        result = remove_special_symbols("快乐池塘\n\r\b栽\t种了梦想就变成海\n洋")
        assert result == "快乐池塘栽种了梦想就变成海洋"

    def test_has_chinese(self):
        result = has_chinese("dis当ogiosdg")
        assert result is True
        result = has_chinese("disogiosdg")
        assert result is False

    def test_is_chinese(self):
        result = is_chinese("好")
        assert result is True
        result = is_chinese("1")
        assert result is False
        result = is_chinese("a")
        assert result is False
        result = is_chinese("+")
        assert result is False

    def test_handle_short_sentence(self):
        result = handle_short_sentence([(0, 10), (11, 14), (15, 30), (31, 39)])
        assert result == [(0, 14), (15, 30), (31, 39)]

    def test_split_text(self):
        result = split_text("诊疗过程: 患儿入院后完善术前相关检查，排除手术禁忌后，患儿于2018-2-7行手术治疗，术后患儿入儿科重症 监护病房，病情稳定后患儿转入我科继续治疗，患儿术后恢复良好，无发热，无恶心呕吐。查体：神志清，精神欠佳，面色苍白，呼吸尚平稳，头皮术区纱布覆盖良好，干燥无渗出，头皮无肿胀，双瞳孔等大，直径2.5mm，对光反射灵敏，球结膜无水肿，颈软，双肺呼吸音粗，心律齐、无杂音，腹部平软，无反跳痛，无肌紧张,肝脾无肿大，肠鸣音正常,肛门及外生殖器外观无畸形，脊柱生理弯曲，四肢末梢温，毛细血管充盈征＜2秒，神经系统查体克氏征、布氏征及巴宾斯基征阴性，经上级医师查房决定预约今日出院。 术后病理回报显示:髓母细胞瘤、四级。 出院医嘱: 嘱患儿出院后1个月门诊复查，定期随诊。")
        assert result == ['诊疗过程:患儿入院后完善术前相关检查，排除手术禁忌后，患儿于2018-2-7行手术治疗，术后患儿入儿科重症监护病房，病情稳定后患儿转入我科继续治疗，患儿术后恢复良好，无发热，无恶心呕吐', '查体：神志清，精神欠佳，面色苍白，呼吸尚平稳，头皮术区纱布覆盖良好，干燥无渗出，头皮无肿胀，双瞳孔等大，直径2.5mm，对光反射灵敏，球结膜无水肿，颈软，双肺呼吸音粗，心律齐、无杂音，腹部平软，无反跳痛，无肌紧张,肝脾无肿大，肠鸣音正常,肛门及外生殖器外观无畸形，脊柱生理弯曲，四肢末梢温，毛细血管充盈征＜2秒，神经系统查体克氏征、布氏征及巴宾斯基征阴性，经上级医师查房决定预约今日出院', '术后病理回报显示:髓母细胞瘤、四级', '出院医嘱:嘱患儿出院后1个月门诊复查，定期随诊']

    def test_locate_two_word(self):
        assert locate_two_word("神经母细胞瘤神经的镂空设计符合4期神经母细胞瘤收到反馈就是刘佳分4期是快乐的感觉", "神经母细胞瘤", "4期") == (0, 15)
        assert locate_two_word("神经母细胞瘤神经的镂空设计符合4期神经母细胞瘤收到反馈就是刘佳分4期是快乐的感觉", "神经母细胞瘤", "4期", keep_order=False) == (17, 15)
