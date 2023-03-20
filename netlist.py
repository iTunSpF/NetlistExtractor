from functools import reduce, cached_property
from itertools import combinations, product, chain
from collections.abc import Iterable
import warnings
from inspect import *
import networkx as nx
import pathlib 
from statool import PT_session
import pickle

GeneratorDualWarn = "You are using one generator to create another dependent one! Please make sure there's only one generator to avoid possible error!"

class Netlist:
    """
    网表的最顶层类. 目前，这个类是基于 节点为主 的图来开发的。边上的操作几乎没有。
    ------------
    Netlist 类携带的 nx.MultiDiGraph 对象是未定的。比如，您可以基于以下图表示方案来开发 Netlist 的子类
    + 以 gate, flipflop, net, pin 都为节点的异构图。
    + 以 gate, flipflop 和 net 都为节点, pin 为边的异构图。
    + 以 gate, flipflop 为节点, net 为边的同构图。
    + 以 timing arc 为边的, pin 为节点的异构图。
    + 任意其他满足下列条件的图表示方案。
    
    不管采用什么图表示方案, Netlist 类都假设这些图满足：
    + 是有向无环图。
    + 节点或边很可能具有 "type" 和 "subtype" 的属性。
      (对 gate 和 flipflop, 其 type 应当分别是 "gate" 和 "flipflop"，而 “INX_X2“ 是 subtype, "INX" 是 function, "2" 是 area)
    + 所有节点都具有 iotype, 表示其属于 GND,, VDD, PO 还是 PI. 但鉴于 benchmark 中没有 VDD 和 GND, 所以暂时只有 "input" 和 "output" 两种取值。
    
    初始化方法：
    ------------
    `netlist = Netlist(self, name="netlist", io_flag = 1, graph=nx.MultiDiGraph(), load_path = None, statool = None, statool_type = None, statool_flag = 0)`
    
    传入参数
    ----------
    name : str
            网表名，即顶层模块名。
    graph : networkx.MultiDiGraph
            网表对应的有向图。如果一开始就传入，则相当于用传入的 graph 来创建一个同样的 Netlist.
    io_flag : bool
            进行网表内数据 IO 时所默认采用的数据类型。如不指定，则默认为 io_flag = 1, 即使用 列表类型。否则为 生成器 类型。
    load_path : str or pathlib.Path
            一个指向 pickle 类型文件的路径，其中存放了用于初始化 self.graph 的信息。
    statool : class
            定义在 statool.py 中的工具类。如果指定了，就会使用指定的 tool 类实例。
    statool_type : str
            用于指定使用 statool.py 中的何种工具类。如果没有显式传入 statool 但却指定了 statool_type, 则会根据指定的 statool_type 来初始化一个工具类对象。
    statool_flag : bool
            用于初始化工具类时作为传入的 flag, 它将会控制外部 sta timer 是否要在交互时自动打印输出。默认为不自动打印。你也可以通过修改 self.tool.flag 的值来改变它。

    类属性
    ---------
    公共属性：
    + self.name = "netlist"
    + self.graph = nx.MultiDiGraph()
    + self.default_io_flag = 1
    
    通过 @property 获得的只读属性：
    + self.nodes
    + self.edges
    + self.inputs 
    + self.outputs
    + self.gates
    + self.flipflops
    + self.wires
    + self.io
    + self.ntypes
    + self.nsubtypes
    + self.niotypes
    + self.nfunctions
    
    """

    def __init__(self, name="netlist", io_flag = 1, graph=nx.MultiDiGraph(), load_path = None, statool = None, statool_type = None, statool_flag = 0):
        """
        创建一个新的网表 Netlist (带 Networkx Graph)

        传入参数
        ----------
        name : str
                网表名，即顶层模块名。
        graph : networkx.MultiDiGraph, etc.
                网表对应的有向图。如果一开始就传入，则相当于用传入的 graph 来创建一个同样的 Netlist.
        io_flag : bool
                进行网表内数据 IO 时所默认采用的数据类型。如不指定，则默认为 io_flag = 1, 即使用 列表类型。否则为 生成器 类型。
        load_path : str or pathlib.Path
                一个指向 pickle 类型文件的路径，其中存放了用于初始化 self.graph 的信息。
        statool : class
                定义在 statool.py 中的工具类。如果指定了，就会使用指定的 tool 类实例。
        statool_type : str
                用于指定使用 statool.py 中的何种工具类。如果没有显式传入 statool 但却指定了 statool_type, 则会根据指定的 statool_type 来初始化一个工具类对象。
        statool_flag : bool
                用于初始化工具类时作为传入的 flag, 它将会控制外部 sta timer 是否要在交互时自动打印输出。默认为不自动打印。你也可以通过修改 self.tool.flag 的值来改变它。

        类属性
        ---------
        公共属性：
        + self.name = "netlist"
        + self.graph = nx.MultiDiGraph()
        + self.default_io_flag = 1
        + self.tool = None
        + self.tool_type = None
        
        通过 @property 获得的只读属性：
        + self.nodes
        + self.edges
        + self.inputs 
        + self.outputs
        + self.gates
        + self.flipflops
        + self.wires
        + self.io
        + self.ntypes
        + self.nsubtypes
        + self.niotypes
        + self.nfunctions

        """
        
        assert isinstance(name, str), "name must be a string"
        assert isinstance(graph, nx.MultiDiGraph), "graph must be a networkx.MultiDiGraph"
        
        self.name = name
        self.graph = graph
        self.default_io_flag = io_flag
        
        if isinstance(load_path, str) or isinstance(load_path, pathlib.PosixPath):
            try:
                self.load(load_path)
            except:
                warnings.warn("Graph load failed!")
        
        if statool:
            pass
        else:
            if not statool_type:
                if statool_type in ["pt", "primetime","PT","Primetime","pt_shell", "PrimeTime", "PRIMETIME"]:
                    self.tool = PT_session(statool_flag)
                    
        self.tool = statool    # statool 应当是定义在 statool 中的某一个类的实例
        
    # 接下来这三个函数只是把 graph 上的操作转嫁到 netlist 上。
    def __contains__(self, n):
        """检查 graph 中是否含有节点 n."""
        return self.graph.__contains__(n)

    def __len__(self):
        """检查网表中的节点总数."""
        return self.graph.__len__()

    def __iter__(self):
        """迭代遍历网表的节点."""
        return self.graph.__iter__()
    
    @property
    def nodes(self):
        """
        返回网表所有的节点。

        Returns
        -------
        generator or list of str
                返回一个 生成器 或 列表 (取决于 io_flag)。

        """
        return self.graph.nodes
    
    @property
    def edges(self):
        """
        返回网表所有的边。

        Returns
        -------
        generator or list of str
                返回一个 生成器 或 列表 (取决于 io_flag)。

        """
        return self.graph.edges
    
    @property
    def inputs(self):
        """
        返回网表所有的 input 类型的节点。

        Returns
        -------
        generator or list of str
                返回一个 生成器 或 列表 (取决于 io_flag)。

        """
        return self.filter_niotype("input", self.default_io_flag)
    
    @property
    def outputs(self):
        """
        返回网表所有的 output 类型的节点。

        Returns
        -------
        generator or list of str
                返回一个 生成器 或 列表 (取决于 io_flag)。

        """
        return self.filter_niotype("output", self.default_io_flag)
    
    @property
    def wires(self):
        """
        返回网表所有的 wire 类型的节点。

        Returns
        -------
        generator or list of str
                返回一个 生成器 或 列表 (取决于 io_flag)。

        """
        return self.filter_ntype("wire", self.default_io_flag)
    
    @property
    def gates(self):
        """
        返回网表所有的 gate 类型的节点。

        Returns
        -------
        generator or list of str
                返回一个 生成器 或 列表 (取决于 io_flag)。

        """
        return self.filter_ntype("gate", self.default_io_flag)
    
    @property
    def flipflops(self):
        """
        返回网表所有的 flipflop 类型的节点。

        Returns
        -------
        generator or list of str
                返回一个 生成器 或 列表 (取决于 io_flag)。

        """
        return self.filter_ntype("flipflop", self.default_io_flag)
    
    @property
    def ntypes(self):
        """
        返回 netlist 的节点的所有 type 可能值。

        Returns
        -------
        list of str
        """
        return list(set(self.ntype(self.nodes, io_flag=self.default_io_flag, warn_ignore=1 )))
    
    @property
    def nsubtypes(self):
        """
        返回 netlist 的节点的所有 subtype 可能值。

        Returns
        -------
        list of str
        """
        return list(set(self.nsubtype(self.nodes, io_flag=self.default_io_flag, warn_ignore=1 )))
    
    @property
    def nfunctions(self):
        """
        返回 netlist 的节点的所有 function 可能值。

        Returns
        -------
        list of str
        """
        return list(set(self.nfunction(self.nodes, io_flag=self.default_io_flag, warn_ignore=1 )))
    
    @property
    def niotypes(self):
        """
        返回 netlist 的节点的所有 iotype 可能值。

        Returns
        -------
        list of str
        """
        return list(set(self.niotype(self.nodes, io_flag=self.default_io_flag, warn_ignore=1 )))
    
    @property
    def io(self):
        """
        返回网表所有的 input 和 output 的 iotype 的节点。

        Returns
        -------
        generator or list of str
                返回一个 生成器 或 列表 (取决于 io_flag)。

        """
        if self.default_io_flag == 0:
            return chain(self.inputs, self.outputs)
        else:
            return self.inputs + self.outputs

    def copy(self):
        """返回网表的一个副本。"""
        return Netlist(name=self.name, graph=self.graph.copy())
    
    def save(self, file=None):
        """保存图结构的 pickle 类型文件到 file. 其中 file 可以自动加上扩展名。"""
        try:
            # 如果 networkx 是 3.0 之前的老版本
            file_path = file
            if file_path == None:
                file_path = 'graph_data/' + self.name + ".pkl"
            if file_path.endswith('.pkl'):
                nx.write_gpickle(self.graph, file_path)
                print(f"已成功将图保存到 {file_path} 文件中。" )
            else:
                nx.write_gpickle(self.graph, file_path+".pkl")
                print(f"已成功将图保存到 {file_path}.pkl 文件中。" )
        except:
            file_path = file
            if file_path == None:
                file_path = 'graph_data/' + self.name + ".gpickle"
            if file_path.endswith('.gpickle'):
                with open(file_path, 'wb') as f:
                    pickle.dump(self.graph, f, pickle.HIGHEST_PROTOCOL)
                print(f"已成功将图保存到 {file_path} 文件中。" )    
            else:
                with open(file_path+'.gpickle', 'wb') as f:
                    pickle.dump(self.graph, f, pickle.HIGHEST_PROTOCOL)
                print(f"已成功将图保存到 {file_path}.gpickle 文件中。" )       
            
    def load(self, file=None):
        """从 pickle 类型文件 file 中读取图结构. 其中 file 可以自动加上扩展名。"""
        try:
            # 如果 networkx 是 3.0 之前的老版本
            file_path = file
            if file_path == None:
                file_path = 'graph_data/' + self.name + ".pkl"
            if file_path.endswith('.pkl'):
                self.graph = nx.read_gpickle(self.graph, file_path)
                print(f"已成功从 {file_path} 中读取并加载类型为 {type(self.graph)} 的图。" )
            else:
                self.graph = nx.read_gpickle(self.graph, file_path+".pkl")
                print(f"已成功从 {file_path}.pkl 中读取并加载类型为 {type(self.graph)} 的图。" )
        except:
            file_path = file
            if file_path == None:
                file_path = 'graph_data/' + self.name + ".gpickle"
            if file_path.endswith('.gpickle'):
                with open(file_path, 'rb') as f:
                    self.graph = pickle.load(f)
                print(f"已成功从 {file_path} 中读取并加载类型为 {type(self.graph)} 的图。" ) 
            else:
                with open(file_path+'.gpickle', 'rb') as f:
                    self.graph = pickle.load(f)
                print(f"已成功从 {file_path}.gpickle 中读取并加载类型为 {type(self.graph)} 的图。" )
        
    def is_cyclic(self):
        """
        检查网表是否有环。

        Returns
        -------
        bool
                Existence of cycle

        """
        return not nx.is_directed_acyclic_graph(self.graph)
    
    def topo_sort(self):
        """
        返回一个生成器，以拓扑顺序依次返回若干组节点。

        Returns
        -------
        iter of str
                Ordered node names.

        """
        return nx.topological_sort(self.graph)

    def ntype(self, ns, io_flag=1, warn_ignore=0):
        """
        返回节点或节点可迭代对象的每一个成员的类型。

        Parameters
        ----------
        ns : str or iterable of str
                节点或节点可迭代对象
                
        io_flag : bool int
                为 0, 表示返回的可迭代对象为一个生成器。
                为 1 时, 表示返回的可迭代对象为一个列表。

        Returns
        -------
        str or iterable of str
                这些节点的类型，以单个字符串或字符串的可迭代对象来返回。

        Raises
        ------
        KeyError
                如果节点不存在时所报的错误。

        """
        if isinstance(ns, str):  
            # 如果 ns 是单个节点，而不是节点的可迭代对象
            if ns in self.graph.nodes:
                try:
                    return self.graph.nodes[ns]["type"]
                except:
                    if warn_ignore:
                        pass
                    else:
                        warnings.warn(f"Node {ns} does not have a type defined.")
            else:
                raise KeyError(f"Node {ns} does not exist.")
        else:
            if io_flag == 0:
                if isgenerator(ns):
                    warnings.warn(GeneratorDualWarn)
                return (self.ntype(n,io_flag,warn_ignore) for n in ns if self.ntype(n,io_flag,warn_ignore))
            else:
                return [self.ntype(n,io_flag,warn_ignore) for n in ns if self.ntype(n,io_flag,warn_ignore)]  
            
    def nsubtype(self, ns, io_flag=1, warn_ignore=0):
        """
        返回节点或节点可迭代对象的每一个成员的子类型 (例如，对于 gate 来说子类型形如 INV_X2)。

        Parameters
        ----------
        ns : str or iterable of str
                节点或节点可迭代对象
                
        io_flag : bool int
                为 0, 表示返回的可迭代对象为一个生成器。
                为 1 时, 表示返回的可迭代对象为一个列表。

        Returns
        -------
        str or iterable of str
                这些节点的子类型，以单个字符串或字符串的可迭代对象来返回。

        Raises
        ------
        KeyError
                如果节点不存在时所报的错误。

        """
        if isinstance(ns, str):  
            # 如果 ns 是单个节点，而不是节点的可迭代对象
            if ns in self.graph.nodes:
                try:
                    return self.graph.nodes[ns]["subtype"]
                except:
                    if warn_ignore:
                        pass
                    else:
                        warnings.warn(f"Node {ns} does not have a subtype defined.")
            else:
                raise KeyError(f"Node {ns} does not exist.")
        else:
            if io_flag == 0:
                if isgenerator(ns):
                    warnings.warn(GeneratorDualWarn)
                return (self.nsubtype(n,io_flag,warn_ignore) for n in ns if self.nsubtype(n,io_flag,warn_ignore))
            else:
                return [self.nsubtype(n,io_flag,warn_ignore) for n in ns if self.nsubtype(n,io_flag,warn_ignore)]  
            
    def nfunction(self, ns, io_flag=1, warn_ignore=0):
        """
        返回节点或节点可迭代对象的每一个成员的功能 (例如，对于 gate 来说功能形如 INV)。

        Parameters
        ----------
        ns : str or iterable of str
                节点或节点可迭代对象
                
        io_flag : bool int
                为 0, 表示返回的可迭代对象为一个生成器。
                为 1 时, 表示返回的可迭代对象为一个列表。

        Returns
        -------
        str or iterable of str
                这些节点的功能，以单个字符串或字符串的可迭代对象来返回。

        Raises
        ------
        KeyError
                如果节点不存在时所报的错误。
        """
        
        if isinstance(ns, str):  
            # 如果 ns 是单个节点，而不是节点的可迭代对象
            if ns in self.graph.nodes:
                try:
                    return self.graph.nodes[ns]["function"]
                except:
                    if warn_ignore:
                        pass
                    else:
                        warnings.warn(f"Node {ns} does not have a function defined.")
            else:
                raise KeyError(f"Node {ns} does not exist.")
        else:
            if io_flag == 0:
                if isgenerator(ns):
                    warnings.warn(GeneratorDualWarn)
                return (self.nfunction(n,io_flag,warn_ignore) for n in ns if self.nfunction(n,io_flag,warn_ignore))
            else:
                return [self.nfunction(n,io_flag,warn_ignore) for n in ns if self.nfunction(n,io_flag,warn_ignore)]  
            
    def niotype(self, ns, io_flag=1, warn_ignore=0):
        """
        返回节点或节点可迭代对象的每一个成员的 IO 类别 (对于 wire 来说有可能是 input 或 output)。

        Parameters
        ----------
        ns : str or iterable of str
                节点或节点可迭代对象
                
        io_flag : bool int
                为 0, 表示返回的可迭代对象为一个生成器。
                为 1 时, 表示返回的可迭代对象为一个列表。

        Returns
        -------
        str or iterable of str
                这些节点的 IO 类别，以单个字符串或字符串的可迭代对象来返回。

        Raises
        ------
        KeyError
                如果节点不存在时所报的错误。

        """
        if isinstance(ns, str):  
            # 如果 ns 是单个节点，而不是节点的可迭代对象
            if ns in self.graph.nodes:
                try:
                    return self.graph.nodes[ns]["iotype"]
                except:
                    if warn_ignore:
                        pass
                    else:
                        warnings.warn(f"Node {ns} does not have a iotype defined.")
            else:
                raise KeyError(f"Node {ns} does not exist.")
        else:
            if io_flag == 0:
                if isgenerator(ns):
                    warnings.warn(GeneratorDualWarn)
                return (self.niotype(n,io_flag,warn_ignore) for n in ns if self.niotype(n,io_flag,warn_ignore))
            else:
                return [self.niotype(n,io_flag,warn_ignore) for n in ns if self.niotype(n,io_flag,warn_ignore)] 

    def filter_ntype(self, ntypes, io_flag=1):
        """
        返回所有 "type" 属性 in ntypes 的节点。

        Parameters
        ----------
        ntypes : str or iterable of str
                Type(s) to filter in.
                
        io_flag : bool int
                默认为 0, 表示返回的可迭代对象为一个生成器。
                为 1 时, 表示返回的可迭代对象为一个列表。

        Returns
        -------
        dict or generator or list
                当 ntypes 是可迭代对象时返回一个字典，
                每个 key 代表一个 type, 每个 value 是包含相应类型的节点的一个生成器或列表 (取决于 io_flag)。
                当 ntypes 是单个 str 变量时返回一个生成器或列表 (取决于 io_flag)。

        """
        
        if isinstance(ntypes, str):  
            # 如果输入的 ntypes 是单个节点
            if io_flag == 0:
                return (n for n in self.graph.nodes if self.ntype(n, warn_ignore=1) == ntypes)
            else:
                return [n for n in self.graph.nodes if self.ntype(n, warn_ignore=1) == ntypes]
        else:
            # 如果输入的 ntypes 是可迭代对象
            ntypes = set(ntypes)   # 去除相同的 type.
            
            node_dict = dict()
            
            # 用 #type 次遍历来获得所有相关的节点（我暂时没想到怎么用一次遍历取出这些节点的同时还能封装成多个生成器）
            for ty in ntypes:
                if io_flag == 0:
                    node_dict[ty] = (n for n in self.graph.nodes if self.ntype(n, warn_ignore=1) == ty)
                else:
                    node_dict[ty] = [n for n in self.graph.nodes if self.ntype(n, warn_ignore=1) == ty]

            return node_dict
    
    def filter_nsubtype(self, nsubtypes, io_flag=1):
        """
        返回所有 "subtype" 属性 in nsubtypes 的节点。

        Parameters
        ----------
        nsubtypes : str or iterable of str
                Type(s) to filter in.
                
        io_flag : bool int
                默认为 0, 表示返回的可迭代对象为一个生成器。
                为 1 时, 表示返回的可迭代对象为一个列表。

        Returns
        -------
        dict or generator or list
                当 nsubtypes 是可迭代对象时返回一个字典，
                每个 key 代表一个 type, 每个 value 是包含相应类型的节点的一个生成器或列表 (取决于 io_flag)。
                当 nsubtypes 是单个 str 变量时返回一个生成器或列表 (取决于 io_flag)。

        """
        
        if isinstance(nsubtypes, str):  
            # 如果输入的 nsubtypes 是单个节点
            if io_flag == 0:
                return (n for n in self.graph.nodes if self.nsubtype(n, warn_ignore=1) == nsubtypes)
            else:
                return [n for n in self.graph.nodes if self.nsubtype(n, warn_ignore=1) == nsubtypes]
        else:
            # 如果输入的 nsubtypes 是可迭代对象
            nsubtypes = set(nsubtypes)   # 去除相同的 type.
            
            node_dict = dict()
            
            # 用 #type 次遍历来获得所有相关的节点（我暂时没想到怎么用一次遍历取出这些节点的同时还能封装成多个生成器）
            for ty in nsubtypes:
                if io_flag == 0:
                    node_dict[ty] = (n for n in self.graph.nodes if self.nsubtype(n, warn_ignore=1) == ty)
                else:
                    node_dict[ty] = [n for n in self.graph.nodes if self.nsubtype(n, warn_ignore=1) == ty]

            return node_dict

    def filter_nfunction(self, nfuncs, io_flag=1):
        """
        返回所有 "type" 属性 in nfuncs 的节点。

        Parameters
        ----------
        nfuncs : str or iterable of str
                Type(s) to filter in.
                
        io_flag : bool int
                默认为 0, 表示返回的可迭代对象为一个生成器。
                为 1 时, 表示返回的可迭代对象为一个列表。

        Returns
        -------
        dict or generator or list
                当 nfuncs 是可迭代对象时返回一个字典，
                每个 key 代表一个 type, 每个 value 是包含相应类型的节点的一个生成器或列表 (取决于 io_flag)。
                当 nfuncs 是单个 str 变量时返回一个生成器或列表 (取决于 io_flag)。

        """
        
        if isinstance(nfuncs, str):  
            # 如果输入的 nfuncs 是单个节点
            if io_flag == 0:
                return (n for n in self.graph.nodes if self.nfunction(n, warn_ignore=1) == nfuncs)
            else:
                return [n for n in self.graph.nodes if self.nfunction(n, warn_ignore=1) == nfuncs]
        else:
            # 如果输入的 nfuncs 是可迭代对象
            nfuncs = set(nfuncs)   # 去除相同的 func.
            
            node_dict = dict()
            
            # 用 #nfuncs 次遍历来获得所有相关的节点（我暂时没想到怎么用一次遍历取出这些节点的同时还能封装成多个生成器）
            for ty in nfuncs:
                if io_flag == 0:
                    node_dict[ty] = (n for n in self.graph.nodes if self.nfunction(n, warn_ignore=1) == ty)
                else:
                    node_dict[ty] = [n for n in self.graph.nodes if self.nfunction(n, warn_ignore=1) == ty]

            return node_dict

    def filter_niotype(self, niotypes, io_flag=1):
        """
        返回所有 "iotype" 属性 in niotypes 的节点。

        Parameters
        ----------
        ntypes : str or iterable of str
                Type(s) to filter in.
                
        io_flag : bool int
                默认为 0, 表示返回的可迭代对象为一个生成器。
                为 1 时, 表示返回的可迭代对象为一个列表。

        Returns
        -------
        dict or generator or list
                当 ntypes 是可迭代对象时返回一个字典，
                每个 key 代表一个 type, 每个 value 是包含相应类型的节点的一个生成器或列表 (取决于 io_flag)。
                当 ntypes 是单个 str 变量时返回一个生成器或列表 (取决于 io_flag)。

        """
        
        if isinstance(niotypes, str):  
            # 如果输入的 ntypes 是单个节点
            if io_flag == 0:
                return (n for n in self.graph.nodes if self.niotype(n, warn_ignore=1) == niotypes)
            else:
                return [n for n in self.graph.nodes if self.niotype(n, warn_ignore=1) == niotypes]
        else:
            # 如果输入的 niotypes 是可迭代对象
            niotypes = set(niotypes)   # 去除相同的 iotype.
            
            node_dict = dict()
            
            # 用 #niotypes 次遍历来获得所有相关的节点（我暂时没想到怎么用一次遍历取出这些节点的同时还能封装成多个生成器）
            for ty in niotypes:
                if io_flag == 0:
                    node_dict[ty] = (n for n in self.graph.nodes if self.niotype(n, warn_ignore=1) == ty)
                else:
                    node_dict[ty] = [n for n in self.graph.nodes if self.niotype(n, warn_ignore=1) == ty]

            return node_dict

    def add_node(self, n, fanin_nodes=[], fanout_nodes=[], **attr):
        """
        向网表中加入一个节点, 连接关系是可选的. 如果指定了 fanin_nodes 和 fanout_nodes, 会把节点连接过去。
        如果 fanin 和 fanout 中的节点尚不存在，会自动创建一个无属性的节点。
        【这只是“添加节点”的基本形式。以后有需要的话还可以对异构图和同构图分别构造 “在边上插入 gate” 的功能】
        
        Parameters
        ----------
        n : str
                新节点 名
        fanin : str, dict or iterable of str (可以为空)
                fanin 节点或节点的可迭代对象。如果传入是一个字典，则键值对形如 "A": "G3"
        fanout : str, dict or iterable of str (可以为空)
                fanout 节点或节点的可迭代对象。如果传入是一个字典，则键值对形如 "ZN": "G5"
        **attr : 新节点的独立性属性，包括 type, iotype, subtype, area, location, fanin 等

        Returns
        -------
        str
                新节点 名.

        """
        if isinstance(fanin_nodes,dict) and isinstance(fanout_nodes,dict):
            # 如果以字典的形式指定了各个连接的名称
            for k,v in fanin_nodes.items():
                self.graph.add_edge(v, n, type = "fanin", subtype=k)
            for k,v in fanout_nodes.items():
                self.graph.add_edge(n, v, type = "fanout", subtype=k)
            # 向 graph 中添加节点
            self.graph.add_node(n, **attr)
            
        else:
            # 如果未指定连接名称，只指定了连接关系。
            if not fanin_nodes:
                fanin_nodes = []
            if not fanout_nodes:
                fanout_nodes = []
            
            if isinstance(fanin_nodes, str):
                fanin_nodes = [fanin_nodes]
            fanin_nodes = list(fanin_nodes)
            if isinstance(fanout_nodes, str):
                fanout_nodes = [fanout_nodes]
            fanout_nodes = list(fanout_nodes)

            # 向 graph 中添加节点
            self.graph.add_node(n, **attr)

            # 连接 fanin 和 fanout
            self.connect(n, fanout_nodes)
            self.connect(fanin_nodes, n)

        return n

    def get_edge_data(self, u, v, key=None, default=None):
        """
        和 self.graph.get_edge_data() 完全等效。
        """
        return self.graph.get_edge_data(u, v, key, default)
    
    def remove_nodes(self, ns):
        """
        简单地移除一个或若干节点，不作任何善后。

        Parameters
        ----------
        ns : str or iterable of str
                需要移除的节点或节点的可迭代对象.

        """
        if isinstance(ns, str):
            ns = [ns]
        self.graph.remove_nodes_from(ns)   # 如果节点本来就不存在，也不会报错。

    def connect(self, us, vs):
        """
        为传入的两组节点之间建立全连接的边。（并不是画一个完全图，而是像神经网络的全连接层那样。）

        Parameters
        ----------
        us : str or iterable of str
                第一个/组节点
        vs : str or iterable of str
                第二个/组节点 

        """
        if not us or not vs:
            return       # 如果传了个寂寞就直接开摆

        if isinstance(us, str):
            us = [us]
        us = list(us)
        if isinstance(vs, str):
            vs = [vs]
        vs = list(vs)

        # 检查这些节点是否确实存在于图中
        for n in us:
            if n not in self.graph:
                raise ValueError(f"node '{n}' does not exist.")
        for n in vs:
            if n not in self.graph:
                raise ValueError(f"node '{n}' does not exist.")

        # connect
        self.graph.add_edges_from((u, v) for u in us for v in vs)

    def disconnect(self, us, vs):
        """
        connect 的反向操作，去除两组节点的全连接性。

        Parameters
        ----------
        us : str or iterable of str
                第一个/组节点
        vs : str or iterable of str
                第二个/组节点 

        """
        if isinstance(us, str):
            us = [us]
        us = list(us)
        if isinstance(vs, str):
            vs = [vs]
        vs = list(vs)
        self.graph.remove_edges_from((u, v) for u in us for v in vs)

    def fanin(self, ns, io_flag=1):
        """
        列出 ns 中每一个节点的 fanin 节点。
        【疑问: 如果 edge 有名称，那么怎么看 edge 的 fanin 节点呢？】

        Parameters
        ----------
        ns : str or iterable of str
                需要查询 fanin 的节点或节点可迭代对象。
                
        io_flag : bool int
                默认为 0, 表示返回的可迭代对象为一个生成器。
                为 1 时, 表示返回的可迭代对象为一个列表。

        Returns
        -------
        list of sublist of str, or generator of list of str, or list
                当 ns 是一个可迭代对象时，返回 列表类型 或 生成器类型 的 查询结果。作为元素的 list 是每个 ns 成员的 fanin 节点列表。
                当 ns 是单个节点时，直接返回其 fanin 节点列表。

        """
        
        if isinstance(ns, str):
            return list(self.graph.predecessors(ns))
        else:
            if io_flag == 0:
                return ( self.fanin(n,io_flag) for n in ns )
            else:
                return [ self.fanin(n,io_flag) for n in ns ]
            

    def fanout(self, ns, io_flag=1):
        """
        列出 ns 中每一个节点的 fanout 节点。
        【疑问: 如果 edge 有名称，那么怎么看 edge 的 fanout 节点呢？】

        Parameters
        ----------
        ns : str or iterable of str
                需要查询 fanout 的节点或节点可迭代对象。
                
        io_flag : bool int
                默认为 0, 表示返回的可迭代对象为一个生成器。
                为 1 时, 表示返回的可迭代对象为一个列表。

        Returns
        -------
        list of sublist of str, or generator of list of str, or list
                当 ns 是一个可迭代对象时，返回 列表类型 或 生成器类型 的 查询结果。作为元素的 list 是每个 ns 成员的 fanout 节点列表。
                当 ns 是单个节点时，直接返回其 fanout 节点列表。
        """
        
        if isinstance(ns, str):
            return list(self.graph.successors(ns))
        else:
            if io_flag == 0:
                return ( self.fanout(n,io_flag) for n in ns )
            else:
                return [ self.fanout(n,io_flag) for n in ns ]


    def transitive_fanin(self, ns, io_flag=1):
        """
        列出 ns 中每一个节点的 transitive fanin 节点（所有的前驱节点）。
        【疑问: 如果 edge 有名称，那么怎么看 edge 的 transitive fanin 节点呢？】

        Parameters
        ----------
        ns : str or iterable of str
                需要查询 transitive fanin 的节点或节点可迭代对象。
                
        io_flag : bool int
                默认为 0, 表示返回的可迭代对象为一个生成器。
                为 1 时, 表示返回的可迭代对象为一个列表。

        Returns
        -------
        list of sublist of str, or generator of list of str, or list
                当 ns 是一个可迭代对象时，返回 列表类型 或 生成器类型 的 查询结果。作为元素的 list 是每个 ns 成员的 transitive fanin 节点列表。
                当 ns 是单个节点时，直接返回其 transitive fanin 节点列表。
        """
        
        if isinstance(ns, str):
            return list(self.graph.ancestors(ns))
        else:
            if io_flag == 0:
                return ( self.transitive_fanin(n,io_flag) for n in ns )
            else:
                return [ self.transitive_fanin(n,io_flag) for n in ns ]
        
        
    def transitive_fanout(self, ns, io_flag=1):
        """
        列出 ns 中每一个节点的 transitive fanout 节点（所有的后继节点）。
        【疑问: 如果 edge 有名称，那么怎么看 edge 的 transitive fanout 节点呢？】

        Parameters
        ----------
        ns : str or iterable of str
                需要查询 transitive fanin 的节点或节点可迭代对象。
                
        io_flag : bool int
                为 0 时, 表示返回的可迭代对象为一个生成器。
                为 1 时, 表示返回的可迭代对象为一个列表。

        Returns
        -------
        list of sublist of str, or generator of list of str, or list
                当 ns 是一个可迭代对象时，返回 列表类型 或 生成器类型 的 查询结果。作为元素的 list 是每个 ns 成员的 transitive fanout 节点列表。
                当 ns 是单个节点时，直接返回其 transitive fanout 节点列表。
        """
        
        if isinstance(ns, str):
            return list(self.graph.descendants(ns))
        else:
            if io_flag == 0:
                return ( self.transitive_fanout(n,io_flag) for n in ns )
            else:
                return [ self.transitive_fanout(n,io_flag) for n in ns ]
        
    def paths(self, source, target, cutoff=None, io_flag=0):
        """
        获取从节点 u 到节点 v 的所有 path. （目前只支持传入一对节点，暂不支持两组节点之间）.
        由于即便在较小的 design 中, 两点之间的路径数量也可能非常大，所以 io_flag 默认为 0.
        
        本质基于 nx.all_simple_paths() 函数。

        Parameters
        ----------
        source: str
                Source node.
        target: str
                Target node.
        cutoff: int
                Depth to stop the search. Only paths of length <= cutoff are returned.

        Returns
        -------
        generator of list of str
                The paths from source to target.
        """
        paths = nx.all_simple_paths(self.graph, source, target, cutoff=cutoff) 
        return paths if io_flag == 0 else list(paths)


    def startpoints(self, ns=None, io_flag=1):
        """
        查询 node, nodes, or netlist 的 startpoints.
        【这个函数尚不可用，接口未经过调整】

        Parameters
        ----------
        ns : str or iterable of str
                Node(s) to compute startpoints for.

        Returns
        -------
        list of str
                Startpoints of ns.

        """
        
        if isinstance(ns, str):
            ns = [ns]

        if ns:
            # 自己 + 自己的所有前驱 
            return (set(ns) | self.transitive_fanin(ns)) & self.startpoints()
        return self.inputs()

    def endpoints(self, ns=None, io_flag=1):
        """
        Compute the endpoints of a node, nodes, or netlist.
        【这个函数尚不可用，接口未经过调整】

        Parameters
        ----------
        ns : str or iterable of str
                Node(s) to compute endpoints for.

        Returns
        -------
        set of str
                Endpoints of ns.

        """
        if isinstance(ns, str):
            ns = [ns]

        if ns:
            return (set(ns) | self.transitive_fanout(ns)) & self.endpoints()
        return self.outputs() | self.filter_type("bb_input")

    def fanout_depth(self, n, pessimism=1):
        """
        计算 单个节点 的 后继深度 列表（后继有多少 output port, 这个列表就会有多长）。
        当在 后继节点 上发生 reconverge 时,  pessimism 会决定 深度取大还是取小。
        pessimism = 1 时, 深度总是取小。pessimism = 0 时，深度总是取大。
        【函数功能待测试】

        Parameters
        ----------
        n : str 
                要计算深度的节点。
        pessimism: bool
                当在 后继节点 上发生 reconverge 时,  pessimism 会决定 深度取大还是取小。
                pessimism = 1 时, 深度总是取小。pessimism = 0 时，深度总是取大。

        Returns
        -------
        dict = {str endnode: int depth} 
                节点 n 到所有边缘边缘节点的深度。

        """
        def update_dict(dict1, dict2, pessimism):
            new_dict = dict(dict1)

            for k, v in dict2.items():
                if k in new_dict:
                    if pessimism:
                        new_dict[k] = min(new_dict[k], v)  # 悲观更新：深度取小
                    else:
                        new_dict[k] = max(new_dict[k], v)  # 悲观更新：深度取大
                else:
                    new_dict[k] = v  # 添加新的键值对
        
        
        def visit_node(n, depth, pessimism=1):
            # 访问节点 n 的所有后继，认为 n 的深度为 n，后继的节点依次 +1，
            # 返回自己和所有后继的深度（以字典的形式）
            
            # 先拓展搜索前沿
            reachable = self.fanout(n, io_flag=1)
            
            # 初始化返回值
            visited = {n:depth}
        
            if not reachable:
                # 已经到终点了，那就直接返回.
                pass
            else:
                # 没到终点，就去下一层看看
                for u in reachable:
                    visited_temp = visit_node(u, depth+1)
                    visited = update_dict(visited, visited_temp, pessimism)
            
            return visited

        # 判断 图 是否是无环的。如果有环就报错。
        if self.is_cyclic():
            raise ValueError("Cannot compute depth of cyclic netlist")

        # 起点的所在深度为 0
        depth = 0

        # 递归
        visited = visit_node(n, depth, pessimism)

        return {key:value for key, value in visited.items() if key in self.endpoints(n, io_flag=1)}
        
    def fanin_depth(self, n, pessimism=1):
        """
        计算 单个节点 的 前驱深度 列表（前驱中有多少 input port, 这个列表就会有多长）。
        当在前驱节点上发生 reconverge 时,  pessimism 会决定 深度取大还是取小。
        pessimism = 1 时, 深度总是取小。pessimism = 0 时，深度总是取大。
        【函数功能待测试】

        Parameters
        ----------
        n : str 
                要计算深度的节点。
        pessimism: bool
                当在前驱节点上发生 reconverge 时,  pessimism 会决定 深度取大还是取小。
                pessimism = 1 时, 深度总是取小。pessimism = 0 时，深度总是取大。

        Returns
        -------
        dict = {str endnode: int depth} 
                节点 n 到所有边缘边缘节点的深度。

        """
        
        def update_dict(dict1, dict2, pessimism):
            new_dict = dict(dict1)

            for k, v in dict2.items():
                if k in new_dict:
                    if pessimism:
                        new_dict[k] = min(new_dict[k], v)  # 悲观更新：深度取小
                    else:
                        new_dict[k] = max(new_dict[k], v)  # 悲观更新：深度取大
                else:
                    new_dict[k] = v  # 添加新的键值对
        
        
        def visit_node(n, depth, pessimism=1):
            # 访问节点 n 的所有前驱，认为 n 的深度为 n，前驱的节点依次 +1，
            # 返回自己和所有前驱的深度（以字典的形式）
            
            # 先拓展搜索前沿
            reachable = self.fanin(n, io_flag=1)
            
            # 初始化返回值
            visited = {n:depth}
        
            if not reachable:
                # 已经到终点了，那就直接返回.
                pass
            else:
                # 没到终点，就去下一层看看
                for u in reachable:
                    visited_temp = visit_node(u, depth+1)
                    visited = update_dict(visited, visited_temp, pessimism)
            
            return visited

        # 判断 图 是否是无环的。如果有环就报错。
        if self.is_cyclic():
            raise ValueError("Cannot compute depth of cyclic netlist")

        # 起点的所在深度为 0
        depth = 0

        # 递归
        visited = visit_node(n, depth, pessimism)

        return {key:value for key, value in visited.items() if key in self.startpoints(n, io_flag=1)}

    def reconvergent_fanout_nodes(self):
        """
        Get nodes that have fanout that reconverges.
        【这个函数尚不可用，接口未经过调整】

        Returns
        -------
        generator of str
                A generator of nodes that have reconvergent fanout

        """
        for node in self.nodes():
            fo = self.fanout(node)
            if len(fo) > 1:
                for a, b in combinations(fo, 2):
                    if self.transitive_fanout(a) & self.transitive_fanout(b):
                        yield node
                        break

    def has_reconvergent_fanout(self):
        """
        Check if a netlist has any reconvergent fanout present.
        【这个函数尚不可用，接口未经过调整】

        Returns
        -------
        bool
            Whether or not reconvergent fanout is present

        """
        try:
            next(self.reconvergent_fanout_nodes())
            return True
        except StopIteration:
            return False


    def uid(self, n, blocked=None):
        """
        Generate a unique net name based on `n`.
        【这个函数尚不可用，接口未经过调整】

        Parameters
        ----------
        n : str
                Name to uniquify
        blocked : set of str
                Addtional names to block

        Returns
        -------
        str
                Unique name

        """
        if blocked is None:
            blocked = []

        if n not in self.graph and n not in blocked:
            return n
        i = 0
        while f"{n}_{i}" in self.graph or f"{n}_{i}" in blocked:
            if i < 10:
                i += 1
            else:
                i *= 7
        return f"{n}_{i}"

    def kcuts(self, n, k, computed=None):
        """
        Generate k-cuts.
        【这个函数尚不可用，接口未经过调整】

        Parameters
        ----------
        n : str
                Node to compute cuts for.
        k : int
                Maximum cut width.

        Returns
        -------
        iter of str
                k-cuts.

        """
        if computed is None:
            computed = {}

        if n in computed:
            return computed[n]

        # helper function
        def merge_cut_sets(a_cuts, b_cuts):
            merged_cuts = []
            for a_cut, b_cut in product(a_cuts, b_cuts):
                merged_cut = a_cut | b_cut
                if len(merged_cut) <= k:
                    merged_cuts.append(merged_cut)
            return merged_cuts

        if self.fanin(n):
            fanin_cut_sets = [self.kcuts(f, k, computed) for f in self.fanin(n)]
            cuts = reduce(merge_cut_sets, fanin_cut_sets) + [{n}]
        else:
            cuts = [{n}]

        # add cuts
        computed[n] = cuts
        return cuts

    def remove_unloaded(self, inputs=False):
        """
        Remove nodes with no load until fixed point.
        【这个函数尚不可用，接口未经过调整】

        Parameters
        ----------
        inputs : bool
                If True, unloaded inputs will be removed too.

        Returns
        -------
        iter of str
                Removed nodes.

        """
        unloaded = [
            n
            for n in self.graph
            if self.type(n) not in ["bb_input"]
            and not self.is_output(n)
            and not self.fanout(n)
        ]
        removed = []
        while unloaded:
            n = unloaded.pop()
            for fi in self.fanin(n):
                if not inputs and self.type(fi) in ["input", "bb_output"]:
                    continue
                if not self.is_output(fi) and len(self.fanout(fi)) == 1:
                    unloaded.append(fi)
            self.remove(n)
            removed.append(n)
        return removed
