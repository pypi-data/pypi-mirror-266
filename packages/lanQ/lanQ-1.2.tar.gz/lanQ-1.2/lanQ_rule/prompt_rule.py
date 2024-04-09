import re
import os
import sys
import langid

sys.path.append(os.path.dirname(__file__))

from base import *
from const import *

def prompt_chinese_produce_english(prompt: str, prediction: str) -> dict:
    """检查中文promt生成英文prediction."""
    res = {'error_status': False}
    lan_prompt = langid.classify(prompt)[0]
    lan_prediction = langid.classify(prediction)[0]
    if lan_prompt == 'zh' and lan_prediction == 'en':
        res['error_status'] = True
        res['error_type'] = ERROR_CHINESE_PRODUCE_ENGLISH
        res['error_reason'] = '中文提示，生成英文内容'
    return res

def prompt_english_produce_chinese(prompt: str, prediction: str) -> dict:
    """检查英文promt生成中文prediction."""
    res = {'error_status': False}
    lan_prompt = langid.classify(prompt)[0]
    lan_prediction = langid.classify(prediction)[0]
    if lan_prompt == 'en' and lan_prediction == 'zh':
        res['error_status'] = True
        res['error_type'] = ERROR_ENGLISH_PRODUCE_CHINESE
        res['error_reason'] = '英文提示，生成中文内容'
    return res