import collections

from common.service.medical_text import extract_all_relation_key, extract_medical_text, sentence_count, \
    random_pick_relation_key
from common.util.database_connection_util import get_tumour_stage_connection


class TestSqlUtil:
    def test_extract_all_relation_key(self):
        pass
        # conn = get_tumour_stage_connection(b'my pleasure lord')
        # cursor = conn.cursor()
        # relation_key_list = extract_all_relation_key(cursor)
        # for relation_key in relation_key_list:
        #     print(relation_key)

    def test_extract_medical_text(self):
        conn = get_tumour_stage_connection(b'')
        cursor = conn.cursor()
        relation_key_list = extract_all_relation_key(cursor)[:1000]
        sentence_list = []
        for relation_key in relation_key_list:
            medical_text_list = extract_medical_text(cursor, relation_key)
            for medical_text in medical_text_list:
                sentence_list.extend(medical_text['文本列表'])
        sentence_count(sentence_list)

    def test_sentence_count(self):
        sentence_list = ["测试", "测试", "四大皆空", "第三方i哦", "第三方i哦", "第三方i哦"]
        sentence_count(sentence_list)

    def test_random_pick_relation_key(self):
        conn = get_tumour_stage_connection(b'')
        cursor = conn.cursor()
        all_relation_key_list = extract_all_relation_key(cursor)
        relation_key_dict = collections.defaultdict(list)
        for relation_key in all_relation_key_list:
            relation_key_dict[relation_key.medical_institution_code].append(relation_key)
        assert len(random_pick_relation_key(relation_key_dict, 500)) == 500
        assert len(random_pick_relation_key(relation_key_dict, 37)) == 37

