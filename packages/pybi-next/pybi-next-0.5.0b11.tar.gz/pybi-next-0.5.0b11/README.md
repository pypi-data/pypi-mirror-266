# pybi

pybi 是一个使用 Python 直观简洁声明语句的BI可视化报告库。使用 pybi，你可以创建灵活强大的 BI 式交互报告。生成的报告只有一个 html 文件，用户只需要使用浏览器打开就能看到所有的交互效果，无须 Python 环境。


[点击这里，在线执行](https://carson_add.gitee.io/test_page/)


[点击这里看效果](https://gitee.com/carson_add/pybi-gallery/blob/master/src/BIExamples/Superstore.gif)


## 例子

示例请移步至 [pybi-gallery](https://gitee.com/carson_add/pybi-gallery)






## 特点

- 输出结果只有一个html文件，浏览器打开即可运行一切效果
- 数据分离。可以单独把报告中使用的数据导出为 sqlite 数据库压缩文件，让用户导入。
- 内置联动。由同一个数据源关联的控件，会互相联动影响。比如下拉框的选择会影响同一个数据源下的表格和图表。
- sql视图。开发者可以基于数据源，使用sql得到数据视图。数据视图会受到数据源变化而产生联动效果。
- grid布局。支持前端grid布局，非常灵活简单布局你的页面



## 安装

```
pip install pybi-next
```



pybi 依赖 Python 这些第三方库(开发者需要安装)：

- [pandas](https://pandas.pydata.org/)


## 使用
```python
import pybi as pbi
import pandas as pd

# pandas 加载数据
df = pd.DataFrame({"name": ["a", "b"], "age": [1, 2]})

# 设置好数据源
data = pbi.set_source(df)

# 下拉框，pybi中称为切片器
pbi.add_slicer(data["name"])
pbi.add_table(data)

pbi.to_html("example.html")
```


## 前端核心功能使用了这些库(开发者与用户都无须关心)：
- [sql.js]([sql.js](https://github.com/sql-js/sql.js/))
- [echarts]([Apache ECharts](https://echarts.apache.org/zh/index.html))
- [Vue.js - The Progressive JavaScript Framework | Vue.js (vuejs.org)](https://vuejs.org/)
- [A Vue 3 UI Framework | Element Plus (element-plus.org)](https://element-plus.org/zh-CN/)
- [plotly](https://plotly.com/javascript/)


## 文档

### button-bind_action

按钮组件允许绑定到指定的操作(称为动作).

如下示例中，点击按钮，清除页面所有切片器或输入框的输入内容
```python
pbi.add_button("重置页面状态").bind_action(pbi.actions.reset_filters)
```




