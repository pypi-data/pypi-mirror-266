# lanQ

Language quality evaluation tool.

## Run it

Clone the project into your environment.

```
git clone ssh://git@gitlab.pjlab.org.cn:1122/qa/lanq.git
```

Install the requirement packages.

```
pip install -r requirements.txt
```

Add the test data file `test_data.json` into `/lanQ/data/predictions` directory.  
Then execute `main.py` with parameter `-f`.

```
python main.py -f test_data.json
```

You will get the same name result file `test_data.json` in `lanQ/data/results`.

## Data format

There are 2 data format supported.  
One is model type style, contain `id`, `prompt` and `prediction` keys, as follows:  

```
{"id": "0", "prompt": "how old are you?", "prediction": "I am 8 years old."}
```

Another is data type style, have `id` and `content` keys, such as:

```
{"id":"Bl1b6P41SlcCHv8gfhLy","content":"秦始皇嬴政，从此结束了贵族王侯专政的王国时代，进入了君主专制的帝国时代。"}
```

No matter what data format is, each line of data is `json` type and each data file only has one format data.   
Besides, data exits in data file with `jsonline` style, refering to `test_data1.json` or `test_data2.json`.

## Reading result

The file in `/lanQ/data/results` directory has format as follows:

```
{
    "score": 50.0,
    "num_good": 1,
    "num_bad": 1,
    "total": 2,
    "ERROR_RULE_COLON_END": {
        "0": "冒号结尾"
    },
    "ERROR_SPECIAL_CHARACTER": {
        "1": "特殊符号�"
    }
}
```

`score` is `num_good` / `total`, meaning the quality of data.  
`num_good` is the count of good data.  
`num_bad` is the count of bad data, which has some error.  
`total` is the count of all data and is also the count of line in data file.  
`ERROR_RULE_COLON_END` and `ERROR_SPECIAL_CHARACTER` is the error name.  
`0` and `1` is the data id.  
`冒号结尾` and `特殊符号�` is the error reason.

## How to Use

First, you should install the package.

```
pip install lanQ
```

After installing the tool in python environment, wo can import it in our project as follows.

```
from lanQ_rule import common_rule
```

At this time, we can use all functions in `common_rule.py`. The parameter `content` is must `string` type, such as:

```
common_bracket_unmatch(content)
```

We will get a result, which is a json type and has a key `error_status`.  
If `error_status` is `False`, which means content has problem, the result will have other 2 keys: `error_type` and `error_type`, for example:  

```
{
   'error_status': True, 
   'error_type': 'ERROR_RULE_COLON_END', 
   'error_reason': '冒号结尾'
}
```

## Upload 

Update the version number in `setup.py`

```
setup(
    name="lanQ",
    version="x.y",
    ...
)
```

Make a .tar file for using in other project. 
You will get a .tar file in `lanQ/dist/`

```
python .\setup.py sdist
```

Upload the .tar file to Internet.

```
twine upload .\dist\lanQ-x.y.tar.gz
```

## Summary of Quality Functions

The Category in below table is the same name `.py` file in `lanQ/lanQ_rule/` path.  
Function's name are arranged in alphabetical order.

Function Name | Description                                             | Category | Version
-|---------------------------------------------------------|----------|-
common_bracket_unmatch | check whether bracket is matches                        | common   | 1.0
common_chaos_en | check whether content has English messy code            | common   | 1.0
common_chaos_symbol | check whether content has a lot of meaningless words    | common   | 1.0
common_chaos_zh | check whether content has Chinese messy code            | common   | 1.0
common_colon_end | check whether the last char is ':'                      | common   | 1.0
common_content_null | check whether content is null | common   | 1.0
common_doc_repeat | check whether content repeats                           | common   | 1.0
common_enter_continuous | check whether content has more than 8 continious enter | common   | 1.0
common_enter_more | check whether enter / content is more than 25% | common   | 1.0
common_language_mixed | check whether content is mixed in Chinese and English   | common   | 1.0
common_no_punc | check whether content has paragraph without punctuations | common   | 1.0
common_space_more | check whether content has more than 500 space | common   | 1.0
common_special_character | check whether special char in content, such as '�'      | common   | 1.0
common_url_only | check whether content is all urls | common   | 1.0
common_word_stuck | check whether words are stuck | common   | 1.0
model_advertisement | check whether content has model advertisement | model    | 1.0
model_watermark | check whether content has watermark | model    | 1.0
prompt_chinese_produce_english | check whether chinese prompt produce english prediction | prompt   | 1.0
prompt_english_produce_chinese | check whether english prompt produce chinese prediction | prompt   | 1.0

## RoadMap
 - 1.5:
   - 支持多种数据格式的convert
 - 1.4:
   - 增加函数的可配置性
 - 1.3:
   - 重新组织 config.py 对外开放用户配置接口
 - ~~1.2~~:
   - 更新 main.py 和 config.py 使用 callable 类型组织函数调用

## Release Notes
 - 1.1:
   - 新增 base.py 抽取基础功能;
   - functions 按字母顺序排列
 - 1.0:   
   - 新增 1.0 functions;  
   - 新增 common_rule 模块;  
   - 新增 model_rule 模块;  
   - 新增 prompt_rule 模块;  
   - 新增 convert 功能;
   - 新增 main.py 支持本质运行。
