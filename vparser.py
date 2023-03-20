import re
from pathlib import Path
from itertools import groupby

def flatten(nested_list, io_flag=1):
    """展平一个嵌套列表，列表元素是字符串也可以。同时去除英文逗号和空格"""
    if io_flag == 0: 
        return (elem.replace(".", "").replace(" ", "") for sublist in nested_list for elem in (flatten(sublist) if isinstance(sublist, list) else [sublist]))
    else:
        return [elem.replace(".", "").replace(" ", "") for sublist in nested_list for elem in (flatten(sublist) if isinstance(sublist, list) else [sublist])]

def verilog_parser(path, io_flag=1, vlib=None): 
    """ 
    功能
    -------
    对例化网表文件进行解析，并返回结果。只能解析非常简单的例化网表，文件内容格式可以参考 TAU15, TAU19 或 ISPD13 benchmark circuits.
    简而言之，其中的每个例化网表中只有 wire, input, output, submodule 这四种语句，均以分号作为结尾，且仅有一个顶层模块。此外，这样的简单网表还满足：
    + No hierarchy, no buses, no behavioral keywords
    + Single clock domain
    + Cell pins are only connected with wires 
    + Inputs and outputs are implicitly connected to wires with the same name
    + No unconnected pins, no escape characters in names
    + No power or ground nets
    
    理论上 wire 和 net 的概念应当有所区别。但我们总是用名为 wire 的变量指代 net 或 wire.
    
    Parameters
    ----------
    path : str or pathlib.Path
            指定要解析的网表文件，不限定文件拓展名，只要是文本文件就行。
    io_flag : bool
            0 表示以 生成器类型 返回, 1 表示以 列表类型 返回.
            实验下来，生成器 IO 比 列表 IO 快 5~9 倍。
    vlib : str or pathlib.Path 【相应功能待实现】
            指定用来规定引脚关系的 verilog submodule 工艺库，例如 NangateOpenCellLibrary.v
            如果指定了，则会自动为其更新引脚信息。不指定则默认为 None
    
    Returns
    -------
    module_name : str
            网表的设计名，即顶层模块名
    inputs : list or generator of str
            包含每个 input 端口 的 wire 名称。 
    outputs : list or generator of str
            包含每个 output 端口 的 wire 名称。
    wires : list or generator of str
            包含每个 wire 名称（含 IO 端口）。
    gates : list or generator of sublist
            每个 sublist 都代表一个 gate (或称 submodule).
            例如，网表中的一行 "CLKBUF_X2 inst_19 ( .A(net_17), .Z(net_18) );" 将会转换为一个 sublist 为 ['inst_19', 'CLKBUF_X2', ('CLKBUF', '2'), ('A', 'net_17'), ('Z', 'net_18')]
            
    """
    def split_flatten(nested_list, io_flag=1):
        # 忽略换行符，用逗号分离出不同的成分，再将得到的嵌套列表展平，
        # 最后去除每个字符串中多余的空格，以及开头的第一个英文句号
        if io_flag == 0:
            nested_list = flatten((x.replace('\n','').split(',') for x in nested_list), io_flag)
            return (x.strip().lstrip(".") for x in nested_list)
        else:
            nested_list = flatten([x.replace('\n','').split(',') for x in nested_list])
            return [x.strip().lstrip(".") for x in nested_list]

    def instance_post_process(x):
        # 把初步读到的 gates 中的引脚信息和 gate 功能提取出来
        # 完全以 列表类型 来输入输出。
        x = flatten(list(map(lambda y: y.split(","), x)));
        return [x[1], x[0], re.match(r"([a-zA-Z0-9]*)_*[a-zA-Z0-9](\d+)",x[0]).groups()] + [x[i] if i<2 else re.match(r'(\w*)\((\w*)\)',x[i]).groups() for i in range(2,len(x))] 
        # return [x[1], re.match(r"([a-zA-Z0-9]*)_*X(\d+)",x[0]).groups()] + [x[i] if i<2 else re.match(r'(\w*)\((\w*)\)',x[i]).groups() for i in range(2,len(x))] 
    
    with open(path, 'r') as f:
        content = f.read()
        
    pattern = r'(?P<type>module|wire|input|output|(?:[a-zA-Z0-9]+)_*X(?:\d+))\s+(?P<description>[^;]+)\s*;'
    matches = groupby(re.findall(pattern, content), key=lambda x: x[0] if x[0] in ("wire","input","module","output") else "gate")
    # 此处 matches 变成一个只有 5 个元素的生成器。第一个元素形如 ('module', <itertools._grouper at 0x26db6c359a0>)，后面则是 input, output, wire 和 gate.

    if io_flag == 0:
        # 这里必须用 list(next(matches)[1]) 而不能用 next(matches)[1]。
        # 因为如果用一个 母生成器 的元素来生成另一个 子生成器。那么一旦 母生成器 在其他地方被 next 了，那么 子生成器 的 状态也会发生变化
        module_name = re.findall(r"(\w+)\s*\(", next(next(matches)[1])[1])[0]
        inputs = split_flatten((x[1] for x in list(next(matches)[1])), io_flag)
        outputs = split_flatten((x[1] for x in list(next(matches)[1])), io_flag)
        wires = split_flatten((x[1] for x in list(next(matches)[1])), io_flag)
        gates = ((x[0],) + re.match(r'\s*([\w_]+)\s*\(\s*(\..*?\))\s*\)\s*', x[1], re.DOTALL).groups() for x in list(next(matches)[1]))
        
    else:
        module_name = re.findall(r"(\w+)\s*\(", next(next(matches)[1])[1])[0]
        inputs = split_flatten([x[1] for x in next(matches)[1]], io_flag)
        outputs = split_flatten([x[1] for x in next(matches)[1]], io_flag)
        wires = split_flatten([x[1] for x in next(matches)[1]], io_flag)
        gates = [(x[0],) + re.match(r'\s*([\w_]+)\s*\(\s*(\..*?\))\s*\)\s*', x[1], re.DOTALL).groups() for x in next(matches)[1]]

    # 把每个引脚的信息后处理一下，并且把 gate 的功能性前缀提取出来，如 INV_X2 提取为 ("INV","2")
    gates = (instance_post_process(x) for x in gates) if io_flag == 0 else [instance_post_process(x) for x in gates]
    
    return module_name, inputs, outputs, wires, gates
    
if __name__ == "__main__":
    # io_flag = 0 表示以 生成器 类型作为 IO 类型。io_flag = 1 表示以 List 类型作为 IO 类型。
    # 实验下来，生成器 IO Flow 比 列表 IO Flow 大概会快 5~9 倍。
    io_flag = 1

    # 第一个文件较大（一百多 MB，2300多万行），第二个文件很小（几 kb）
    file_name = r"Q:\PDKs&Benchmark&etc\Benchmarks\TAU15\vga_lcd_iccad_eval\vga_lcd_iccad.v"
    #file_name = r"Q:\PDKs&Benchmark&etc\Benchmarks\TAU15\s27\s27.v"

    path = Path(file_name)
    module_name, inputs, outputs, wires, gates = verilog_parser(path,io_flag)

    if io_flag == 1:  
        print("------------------------------")
        print("|######| Design: " + module_name + " |######|\n ------------------------------")
        print("Input ports are listed as follows (8 items at most): " )
        print(inputs[0:min(8,len(inputs))])
        print("------------------------------")
        print("Output ports are listed aas follows (8 items at most): " )
        print(outputs[0:min(8,len(outputs))])
        print("------------------------------")
        print("Wires are listed as follows (8 items at most): " )
        print(wires[0:min(8,len(wires))])
        print("------------------------------")
        print("Gates are listed as follows (8 items at most): " )
        print(gates[0:min(8,len(gates))])
        print("------------------------------")
    else:                     
        pass