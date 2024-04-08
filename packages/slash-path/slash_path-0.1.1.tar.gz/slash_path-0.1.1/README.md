## 处理windows路径

直接复制windows路径中，字符串中包含反斜杠，一般需要改成双反斜杠或者rstr。
用slash_path，可以直接用反斜杠的windows路径，产生Path对象，更方便一些。


## 参考项目

主要代码参考了这个最后一个：https://discourse.techart.online/t/python-handling-windows-path-with-characters/12045/18。

## 安装
```
$ pip install slash_path
```


## 使用

```python
from slash_path import SlashPath
path_str = 'D:\next_cloud\newfile.txt'
sp = SlashPath(path_str)

```
更多范例参见utest文件夹。