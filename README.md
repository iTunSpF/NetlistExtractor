# NetlistExtractor

这是一个可以提取例化的门级网表的 python 脚本。部分代码改编自 [circuitgraph](https://github.com/circuitgraph/circuitgraph).

+ `netlist.py`：规定了网表的顶层类 `Netlist`，定义了网表的基本属性和一些基本操作。

+ `graphize.py`：其中的每个类均继承自 `Netlist`，规定了网表的具体的图表示方式。目前只实现了一种：wire 和 gate 都表示为节点，pin 表示为边。类自带 `draw()` 方法可以绘制出整个网表的结构。

+ `parser.py`：包含读取 verilog 例化网表的脚本。
+ `statool.py`：参见 [PT_pyshell](https://github.com/iTunSpF/PT_pyshell).  但在这个 repo 中这个脚本没有什么作用。

文件内包含两种 IO 方式，一种以可读的列表类型变量进行 IO，一种以生成器进行 IO.

用法可以参考 `example.ipynb`.  但整个脚本里完善还很远，且很长一段时间内我也不会再推进了。目前几乎只是个框架。
