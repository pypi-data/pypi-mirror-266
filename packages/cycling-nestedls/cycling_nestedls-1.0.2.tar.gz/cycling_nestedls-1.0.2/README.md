# cycling_nestedls

[![Downloads](https://pypi.org/project/cycling-nestedls)](https://pypi.org/project/cycling-nestedls/1.0.1/)

刚开始学会上传PYPI，以及编写**readme.md文件** .


## Installation

```
pip install cycling_nestedls
```

https://pypi.org/project/cycling-nestedls （我想要星星⭐(9_9-))

## Usage

example:

```python
import cycling_nestedls

a=['wangzha','meiye',['zhuxiaomin','runtu','chengxiang',['qiuqiu','mixian']]]

demo=cycling_nestedls(a)

```


![png](https://raw.githubusercontent.com/cornradio/imgs/main/20230218220613.png)



## Get help

Get help ➡️ [Github issue](https://github.com/sgys22/picture_url)

## Update log

计划1.0.3：
```python
cycling_nestedls(the_list,tab=True)
```
`1.0.2`修改了readme.md文件

`1.0.1`第一次上传，但是代码不健全

`1.0.0` first release(但是没有真正上传到PYPI，因为第一次！。)

## how to upload a new version (for me)

en: https://packaging.python.org/tutorials/packaging-projects/ 

zh: https://python-packaging-zh.readthedocs.io/zh_CN/latest/minimal.html#id2

> make sure have twine installed first

1. change `setup.py`
2. testing `python3 setup.py develop`
3. `python3 setup.py sdist`
4. `twine upload dist/*`

>都是叉来的！

test code :
```
python3

import cycling_nestedls

cycling_nestedls.cycling_nestedls()

```

## 编译readme.md
#### 是不是下一级
> 注释
>> 这会是什么
```python
print('hallo aiop102')
```

