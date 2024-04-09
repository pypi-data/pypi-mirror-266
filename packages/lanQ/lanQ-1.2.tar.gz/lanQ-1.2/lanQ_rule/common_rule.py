import re
import os
import sys
import numpy
import jieba
import string
import langid
import textstat
import unicodedata
import zhon.hanzi
from collections import Counter
from hanziconv import HanziConv

sys.path.append(os.path.dirname(__file__))

from base import *
from const import *

def common_bracket_unmatch(content: str) -> dict:
    """检查开闭括号数量是否一致."""
    res = {'error_status': False}
    flag = ''
    if content.count('[') != content.count(']'):
        flag = '[ 和 ]'
    if content.count('{') != content.count('}'):
        flag = '{ 和 }'
    if content.count('【') != content.count('】'):
        flag = '【 和 】'
    if content.count('《') != content.count('》'):
        flag = '《 和 》'
    if flag != '':
        res["error_status"] = True
        res["error_type"] = ERROR_BRACKET_UNMATCH
        res['error_reason'] = '括号数量不匹配： ' + flag
    return res

def common_chaos_en(content: str) -> dict:
    """检查content内是否有英文乱码."""
    res = {'error_status': False}
    lan = langid.classify(content)[0]
    if lan != 'en':
        return res
    s = normalize(content)
    str_len = len(s)
    seg_len = len(list(jieba.cut(s)))
    num_bytes = len(content.encode('utf-8'))
    tokens_len = int(num_bytes * 0.248)
    if str_len == 0 or seg_len == 0 or tokens_len < 50:
        return res
    if str_len / seg_len <= 1.2:
        res["error_status"] = True
        res["error_type"] = ERROR_CHAOS_EN
        res['error_reason'] = '英文乱码'
    return res

def common_chaos_symbol(content: str) -> dict:
    """检查content内是否有大量非正文内容."""
    res = {'error_status': False}
    pattern = r'[0-9a-zA-Z\u4e00-\u9fa5]'
    s = re.sub(pattern, '', content)
    str_len = len(content)
    symbol_len = len(s)
    if str_len == 0 or symbol_len == 0:
        return res
    if symbol_len / str_len > 0.5:
        res["error_status"] = True
        res["error_type"] = ERROR_CHAOS_SYMBOL
        res['error_reason'] = '大量非正文内容'
    return res

def common_chaos_zh(content: str) -> dict:
    """检查content内是否有中文乱码."""
    res = {'error_status': False}
    lan = langid.classify(content)[0]
    if lan != 'zh':
        return res
    s = normalize(content)
    pattern = r'[a-zA-Zāáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜ\n\s]'
    s = re.sub(pattern, '', s)
    s_simplified = HanziConv.toSimplified(s)
    str_len = len(s)
    seg_len = len(list(jieba.cut(s_simplified)))
    num_bytes = len(content.encode('utf-8'))
    tokens_len = int(num_bytes * 0.248)
    if str_len == 0 or seg_len == 0 or tokens_len < 50:
        return res
    if str_len / seg_len <= 1.1:
        res["error_status"] = True
        res["error_type"] = ERROR_CHAOS_ZH
        res['error_reason'] = '中文乱码'
    return res

def common_check_photo(content: str) -> dict:
    """content是否包含图片"""
    res = {'error_status': False}
    pattern = '!\[\]\(http[s]?://.*?jpeg "\n"\)'
    matches = re.findall(pattern, content)
    if matches:
        res["error_status"] = True
        res["error_type"] = ERROR_CHECK_PHOTO
        res['error_reason'] = matches
    return res

def common_colon_end(content: str) -> dict:
    """content最后一个字符是冒号."""
    res = {'error_status': False}
    if len(content) <= 0:
        return res
    if content[-1] == ':':
        res['error_status'] = True
        res['error_type'] = ERROR_RULE_COLON_END
        res['error_reason'] = '冒号结尾'
    return res

def common_content_null(content: str) -> dict:
    """检查content内是否为空."""
    res = {'error_status': False}
    count = len(content.strip())
    if count == 0:
        res["error_status"] = True
        res["error_type"] = ERROR_CONTENT_NULL
        res['error_reason'] = '内容为空'
    return res

def common_doc_repeat(content: str) -> dict:
    """检查content内是否有连续重复."""
    res = {'error_status': False}
    repeat_score = base_rps_frac_chars_in_dupe_ngrams(6, content)
    if repeat_score >= 80:
        res["error_status"] = True
        res["error_type"] = ERROR_DOC_REPEAT
        res['error_reason'] = '文本重复度过高： ' + str(repeat_score)
    return res

def common_enter_continuous(content: str) -> dict:
    """检查content内是否有连续大于8个的回车."""
    res = {'error_status': False}
    pattern = r'\n{8,}|\r{8,}'
    matches = re.findall(pattern, content)
    if matches:
        res["error_status"] = True
        res["error_type"] = ERROR_ENTER_CONTINUOUS
        res['error_reason'] = '存在连续8个回车'
    return res

def common_enter_more(content: str) -> dict:
    """检查content内是否有超过25%正文占比的回车."""
    res = {'error_status': False}
    enter_count = content.count('\n')
    count = len(content)
    if count == 0:
        return res
    ratio = enter_count / count * 100
    if ratio >= 25:
        res["error_status"] = True
        res["error_type"] = ERROR_ENTER_MORE
        res['error_reason'] = '回车超过正文25%'
    return res

def common_html_entity(content: str) -> dict:
    """检测content是否包含实体标记"""
    res = {'error_status': False}
    entities = [
        "nbsp",
        "lt",
        "gt",
        "amp",
        "quot",
        "apos",
        "hellip",
        "ndash",
        "mdash",
        "lsquo",
        "rsquo",
        "ldquo",
        "rdquo",
    ]
    full_entities_1 = [f"&{entity}；" for entity in entities]
    full_entities_2 = [f"&{entity};" for entity in entities]
    full_entities_3 = [f"＆{entity};" for entity in entities]
    full_entities_4 = [f"＆{entity}；" for entity in entities]
    full_entities = (
        full_entities_1 + full_entities_2 + full_entities_3 + full_entities_4
    )
    # half_entity_1 = [f"{entity}；" for entity in entities]
    half_entity_2 = [f"＆{entity}" for entity in entities]
    half_entity_3 = [f"&{entity}" for entity in entities]
    # half_entity_4 = [f"{entity};" for entity in entities]
    half_entities = half_entity_2 + half_entity_3
    # maked_entities = [f"{entity}" for entity in entities]
    all_entities = full_entities + half_entities
    for entity in all_entities:
        if entity in content:
            res["error_status"] = True
            res["error_type"] = ERROR_HTML_ENTITY
            res['error_reason'] = 'html实体标记'
    return res

def common_img_html_tag(content: str) -> dict:
    """content是否包含图片或html标签"""
    res = {'error_status': False}
    pattern = r"(<img[^>]*>)|<p[^>]*>(.*?)<\/p>|<o:p[^>]*>(.*?)<\/o:p>"
    matches = re.findall(pattern, content)
    if matches:
        res["error_status"] = True
        res["error_type"] = ERROR_IMG_HTML_TAG
        res['error_reason'] = matches
    return res

def common_invisible_char(content: str) -> dict:
    """content是否包含不可见字符"""
    res = {'error_status': False}
    pattern = r"[\u2000-\u200F\u202F\u205F\u3000\uFEFF\u00A0\u2060-\u206F\uFEFF\xa0]"
    matches = re.findall(pattern, content)
    if matches:
        res["error_status"] = True
        res["error_type"] = ERROR_INVISIBLE_CHAR
        res['error_reason'] = matches
    return res

def common_language_mixed(content: str) -> dict:
    """检查content内是否有中英文混杂."""
    res = {'error_status': False}
    s = normalize(content)
    en_len = len(re.findall(r'[a-zA-Z]', s))
    zh_len = len(re.findall(r'[\u4e00-\u9fa5]', s))
    count_len = len(s)
    if count_len == 0:
        return res
    if en_len / count_len >= 0.5 and zh_len / count_len >= 0.1:
        res["error_status"] = True
        res["error_type"] = ERROR_LANGUAGE_MIXED
        res['error_reason'] = '中英文混杂'
    return res

def common_no_punc(content: str) -> dict:
    """检查content内是否有大段无标点."""
    res = {'error_status': False}
    paragraphs = content.split('\n')
    max_word_count = 0
    for paragraph in paragraphs:
        if len(paragraph) == 0:
            continue
        sentences = re.split(r'[-–.!?,;•、。！？，；·]', paragraph)
        for sentence in sentences:
            words = sentence.split()
            word_count = len(words)
            if word_count > max_word_count:
                max_word_count = word_count
    text_stat_res = textstat.flesch_reading_ease(content)
    if int(max_word_count) > 56 and text_stat_res < 20:
        res["error_status"] = True
        res["error_type"] = ERROR_NO_PUNC
        res['error_reason'] = '段落无标点'
    return res

def common_space_more(content: str) -> dict:
    """检查content内是否有连续500个以上的空格."""
    res = {'error_status': False}
    pattern = r' {500,}'
    matches = re.findall(pattern, content)
    if matches:
        res["error_status"] = True
        res["error_type"] = ERROR_SPACE_MORE
        res['error_reason'] = '存在连续500个空格'
    return res

def common_special_character(content: str) -> dict:
    res = {'error_status': False}
    pattern = r"[�□\^]|\{\/U\}"
    matches = re.findall(pattern, content)
    if matches:
        res["error_status"] = True
        res["error_type"] = ERROR_SPECIAL_CHARACTER
        res['error_reason'] = matches
    return res

def common_url_only(content: str) -> dict:
    """检查content内是否只有url."""
    res = {'error_status': False}
    pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'  # noqa
    s = re.sub(pattern, '', content)
    count = len(s.strip())
    if count == 0:
        res["error_status"] = True
        res["error_type"] = ERROR_URL_ONLY
        res['error_reason'] = '内容只有url'
    return res

def common_word_stuck(content: str) -> dict:
    """检查content内是否有英文单词黏连."""
    res = {'error_status': False}
    words = re.findall(r'[a-zA-Z]+', content)
    max_word_len = 0
    for word in words:
        if len(word) > max_word_len:
            max_word_len = len(word)
    if max_word_len > 45:
        res["error_status"] = True
        res["error_type"] = ERROR_WORD_STUCK
        res['error_reason'] = '英文单词黏连'
    return res