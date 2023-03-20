import networkx as nx
from vparser import verilog_parser
from netlist import Netlist
from networkx.drawing.nx_agraph import to_agraph
import graphviz
from pathlib import Path
import matplotlib.pyplot as plt
import re

class HeterDiG_GateWireNodePinEdge(Netlist):
    """
    HeterDiG_GateWireNodePinEdge 类描述了一个异构图，其中 gate 和 wire 都表示成 node, 而 pin 表示为 edge.
    """
    
    def __init__(self, name = "netlist", io_flag=1, load_path = None, statool = None, statool_type = None, statool_flag = 0):
        
        self.inputs_raw = []
        self.outputs_raw = []
        self.wires_raw = []
        self.gates_raw = []
        super().__init__(name=name, io_flag=io_flag, load_path=load_path, statool = statool, statool_type=statool_type, statool_flag=statool_flag)
        
    def clean(self):
        """
        删除无用的内部属性
        """
        del self.inputs_raw, self.outputs_raw, self.wires_raw, self.gates_raw
        
    def build(self, path, io_flag=1, vlib=None):
        """
        建立图的基本结构。不涉及 lib 库和 verilog 库。
        注意，这个操作会先删除当前的 graph 对象，因此不要随意使用。
        """
        
        self.name, self.inputs_raw, self.outputs_raw, self.wires_raw, self.gates_raw = verilog_parser(path, io_flag, vlib)
        
        self.graph = nx.MultiDiGraph()
        
        # 先添加各种 wire 节点，并为其赋予 iotype
        self.graph.add_nodes_from(self.wires_raw, type="wire") 
        self.graph.add_nodes_from(self.inputs_raw, iotype="input") 
        self.graph.add_nodes_from(self.outputs_raw, iotype="output")
        
        # 接下来添加门器件
        for x in self.gates_raw:
            # 如果读过 verilog 库了，x 会形如  ['inst_19', ('CLKBUF', '2'), ('A', 'net_17', 'in'), ('Z', 'net_18', 'out')]
            # 如果没读过，x 会形如  ['inst_19', ('CLKBUF', '2'), ('A', 'net_17'), ('Z', 'net_18')]
            fanin = dict()
            fanin_n = []
            fanout = dict()
            fanout_n = []
            
            if len(x[-1]) == 3:
                # 看来读过 verilog 库
                for i in range(3,len(x)):
                    pin_name = x[i][0]
                    if x[i][2] == 'in':
                        fanin_n.append(pin_node)  # 添加 fanin 节点名称
                        fanin[pin_name] = pin_node
                    else:
                        fanout_n.append(pin_node)  # 添加 fanout 节点名称
                        fanout[pin_name] = pin_node
            else:
                # 没读过 verilog 库，那节点的输入输出就只能猜了。如果猜不透了，就看看现在还缺哪个。如果都不缺，就猜是 fanin 节点。
                # 但是 Nangate 库里引脚名 S 有可能是 input 也有可能是 output，逆天我只能说。
                # 所以说根本不可能仅仅靠简单的猜测就正确分类所有引脚
                guess_in_pattern = [r"CK", r"A\d?", r"a\d?", r"B\d?", r"b\d?", r"C\d?", r"c\d?", 
                                    r"D\d?", r"d\d?", r"SE", r"E", r"I", r"[a-zA-Z]I", r"RN", 
                                    r"IN", r"G", r"EN", r"OE", r"GN", r"S"]
                guess_out_pattern = [r"GCK",r"Z[a-zA-z0-9]?", r"Q", r"QN", r"CO", r"o"]
                fail_guess_id = []
                
                # 开始猜
                for i in range(3,len(x)):
                    pin_name = x[i][0]
                    pin_node = x[i][1]
                    guess_in = [y for y in guess_in_pattern if bool(re.match(y, pin_name))]
                    guess_out = [y for y in guess_out_pattern if bool(re.match(y, pin_name))]
                    
                    if guess_in:
                        fanin_n.append(pin_node)   # 添加 fanin 节点名称
                        fanin[pin_name] = pin_node
                    elif guess_out:
                        fanout_n.append(pin_node)  # 添加 fanout 节点名称
                        fanout[pin_name] = pin_node
                    else:
                        fail_guess_id.append(i)
                
                # 处理那些没猜出来的
                for i in fail_guess_id:
                    pin_name = x[i][0]
                    pin_node = x[i][1]
                    if not fanin:
                        # 如果 fanin 还是空的，果断分配给 fanin
                        fanin_n.append(pin_node)  # 添加 fanin 节点名称
                        fanin[pin_name] = pin_node
                    elif not fanout:
                        # 如果 fanout 还是空的，果断分配给 fanout
                        fanout_n.append(pin_node)  # 添加 fanout 节点名称
                        fanout[pin_name] = pin_node
                    else:
                        # 还踏马有猜剩下来的，只好猜是 fanin 节点。
                        print(f"名为 {x[0]} 的 {x[1]} 型门器件的 {pin_name} 引脚 IO 类型未知，已默认其输入输入引脚")
                        fanin_n.append(pin_node)  # 添加 fanin 节点名称
                        fanin[pin_name] = pin_node

                        
            # 清算的时候来了，该分出 gate 和 flipflop 了
            if ("FF" in x[1]) or ("ms" in x[1]):
                # flipflop
                attr = {
                    "type": "flipflop",
                    "function": x[2][0],    # INV
                    "spec" : x[2][1],       # 2
                    "subtype" : x[1],       # INV_X2
                    "fanin": fanin,
                    "fanout": fanout
                }
            else:
                # 普通 gate
                attr = {
                    "type": "gate",
                    "function": x[2][0],
                    "spec" : x[2][1],
                    "subtype" : x[1],
                    "fanin": fanin,
                    "fanout": fanout
                }
            
            #self.add_node(x[0],fanin_n,fanout_n,**attr)
            self.add_node(x[0],fanin_nodes=fanin,fanout_nodes=fanout,**attr)
            
    def draw(self):
        # 创建一个 AGraph 对象，用于绘图
        
        agraph = to_agraph(self.graph)

        # 设置节点的样式预设
        node_attr = {
            "wire": {
                "shape": "point",
                "width": "0.1"
            },
            "input": {
                "shape": "circle",
                "width": "0.2",
                "color": "blue"
            },
            "output": {
                "shape": "circle",
                "width": "0.2",
                "color": "green"
            },
            "gate": {
                "shape": "rectangle",
                "width": "0.4",
                "height": "0.6"
            },
            "flipflop": {
                "shape": "diamond",   
                "width": "0.4",
                "height": "0.6",
                "color": "orange"
            }
        }

        # 应用节点的样式
        for node in self.nodes:
            if "type" in self.nodes[node]:
                node_type = self.nodes[node].get('type', None)
                node_iotype = self.nodes[node].get('iotype', None)
                if (node_type == "wire") and (node_iotype != None):
                    node_type = node_iotype
                if node_type in node_attr:
                    agraph.get_node(node).attr.update(node_attr[node_type])

        # 设置边的样式
        edge_attr = {
            "fontsize": "12",
            "fontcolor": "gray",
            "arrowhead": "open",
            "arrowsize": "1",
            "color": "gray"
        }
        agraph.edge_attr.update(edge_attr)

        # 绘制图形
        agraph.layout(prog="dot", args='-Gdpi=300')
        agraph.draw(self.name + ".png",)

        # 显示图形
        img = plt.imread(self.name + ".png")
        plt.imshow(img)
        plt.axis("off")
        plt.show()