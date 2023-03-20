from pathlib import Path
import subprocess
import os
import re

class STAtool:
    
    def __init__(self, print_flag=1):
        self.proc = None
        self.print_flag = print_flag         # 决定在读取输出后是否顺便打印出来 (1 为要, 0 为不要)
        self.setup_comd = ['']
        self.shell_prefix = ''
        self.status = 0          # 表示进程是否处于开启状态
    
    def init(self):
        """
        启动一个会话
        """
        self.proc = subprocess.Popen(self.setup_comd, 
                        stdin=subprocess.PIPE, 
                        stdout=subprocess.PIPE)
        # 设置输出流为非堵塞模式，否则 readline() 在没有数据时会一直挂起
        os.set_blocking(self.proc.stdout.fileno(), False)
        self.status = 1
        return self.recv(recv_mode=1)
        
    def recv(self, recv_mode=1, print_flag=None):
        """
        功能
        --------
        在向工具输入一条指令后, 去接收其输出信息. self.print_flag 决定是否顺便输出出来。
        
        输入参数
        --------
        recv_mode : bool
                决定以何种方式读取 PT 的输出内容。
        
        print_flag : bool
                决定是否顺便输出 PT 的输出内容。如果显式指定，则会覆盖 self.print_flag 的设置。
                
        输出
        --------
        根据 recv_mode 的不同有两种情况：
        1. recv_mode 为真时，一次性读入全部输出信息，并以列表返回。
        2. recv_mode 为假时，逐行读入输出信息，以 yield 产生的生成器来返回。此时 print_flag 的设置将被强制无效化。
        """
        
        if print_flag == None:
            print_flag = self.print_flag
        
        if not recv_mode:
            return self.recv_yield()
        
        output = []
        # 等待 PT 给我反应
        os.set_blocking(self.proc.stdout.fileno(), True)
        while True:
            # 扔掉开头的空白输出，并容许第一个非空行输出也可以是 pt_shell>
            sentence = self.proc.stdout.readline().decode().strip('\n')
            if sentence != '':
                output.append(sentence)  
                break
            
        os.set_blocking(self.proc.stdout.fileno(), False)
        while True:
            sentence = self.proc.stdout.readline().decode().strip('\n')
            if self.shell_prefix in sentence:
                ## 读到 pt_shell 就结束
                sentence = sentence.replace(self.shell_prefix,"").strip()
                if sentence != '':   
                    output.append(sentence)  
                elif output[-1] != '':  # 允许读取空行（但多个空行之间得合并为一个空行）（空行能够分隔输出信息的不同部分，不能丢掉）
                    output.append(sentence)
                break
            elif sentence != '':   
                output.append(sentence)  
            elif output[-1] != '':  # 允许读取空行（但多个空行之间得合并为一个空行）（空行能够分隔输出信息的不同部分，不能丢掉）
                output.append(sentence)  
            else:
                continue
        
        if print_flag == 1 and recv_mode:
            for x in output:
                print(x)
        
        os.set_blocking(self.proc.stdout.fileno(), False)
        return output
    
    def recv_yield(self):
        """recv 的生成器版本"""
         
        last_sentence = ''
        sentence = ''
        
        # 等待 PT 给我反应
        os.set_blocking(self.proc.stdout.fileno(), True)
        while True:
            # 扔掉开头的空白输出，并容许第一个非空行输出也可以是 pt_shell>
            sentence = self.proc.stdout.readline().decode().strip('\n')
            if sentence != '':
                yield sentence
                last_sentence = sentence
                break
            
        os.set_blocking(self.proc.stdout.fileno(), False)
        while True:
            sentence = self.proc.stdout.readline().decode().strip('\n')
            if self.shell_prefix in sentence:
                ## 读到 pt_shell 就结束
                sentence = sentence.replace(self.shell_prefix,"").strip()
                if sentence != '':   
                    yield sentence 
                    last_sentence = sentence
                elif last_sentence != '':  # 允许读取空行（但多个空行之间得合并为一个空行）（空行能够分隔输出信息的不同部分，不能丢掉）
                    yield sentence
                    last_sentence = sentence
                break
            elif sentence != '':   
                yield sentence
                last_sentence = sentence
            elif last_sentence != '':  # 允许读取空行（但多个空行之间得合并为一个空行）（空行能够分隔输出信息的不同部分，不能丢掉）
                yield sentence
                last_sentence = sentence
            else:
                continue
        
        os.set_blocking(self.proc.stdout.fileno(), False)
        
    def command(self, comd, recv_mode = 1, print_flag = None):
        """
        功能
        ------
        向 PT 进程发送一条指令，并返回 PT 的输出。self.print_flag 将决定是否顺便输出 PT 的输出内容。
        
        输入参数
        ----
        comd : str or bytes
                是单条 str 或 bytes 类型的命令.
        recv_mode : bool 
                recv_mode = 1 代表一次读入 PT 的所有输入内容， recv_mode = 0 表示逐行读取 PT 的输出内容。
        print_flag : bool
                决定是否顺便输出 PT 的输出内容。如果显式指定，则会覆盖 self.print_flag 的设置。
                
        返回值
        -------
        对应于 self.proc.stdout 流的 str 列表或此列表的一个生成器。
        """
            
        os.set_blocking(self.proc.stdout.fileno(), False)
        if isinstance(comd,str):
            comd = comd.encode('utf-8')
        assert isinstance(comd, bytes), "Can only read one line of bytes-type command at a time."
        if comd[-1] != 10:
            comd = comd + b'\n' 
        
        self.proc.stdin.write(comd)
        self.proc.stdin.flush()   

        # 从 Primetime 进程读取输出
        return self.recv(recv_mode=recv_mode, print_flag=print_flag)
        
    def commands(self, comds, recv_mode = 1, print_flag = None):
        """
        command 的多行版本. 输入参数 comds 是一个多行的字符串，或者是包含命令的列表。
        只会返回最后一条命令的结果。
        """
        if isinstance(comds,str):
            comds = comds.split("\n")
            comds = [x.strip() for x in comds]
        elif isinstance(comds,bytes):
            comds = comds.decode('utf-8')
            comds = comds.split("\n")
            comds = [x.strip() for x in comds]
            
        if isinstance(comds,list):
            comds = [x for x in comds if x != '']
            for i in range(len(comds)):
                if i == len(comds)-1:
                    return self.command(comds[i], recv_mode=recv_mode, print_flag=print_flag)
                else:
                    self.command(comds[i], recv_mode=recv_mode, print_flag=print_flag)
                    return None
        print("Error: Unsupported commands type.")
        return None
                
    def kill(self):
        self.proc.kill()
        self.proc.wait()
        self.status = 0
        
    def __del__(self):
        self.kill()
        
    def __enter__(self):
        self.init()
        return self
    
    def __exit__(self):
        self.kill()
        
             
class PT_session(STAtool):
    """
    Primetime 会话类。
    
    注意, 这内部的 parser 我全都强制令 recv_mode = 0 来做了。recv_mode = 1 的场景应该也不会用到。
    
    
    施工计划：
    + 一个解析 pt 的输出内容的一般性函数。
    + 正则表达式读 timing_arc 信息的函数。
    """
    
    def __init__(self, print_flag=1):
        super().__init__(print_flag)
        self.setup_comd = ['pt_shell']
        self.shell_prefix = "pt_shell>"
        
    def setup_tau19(self, design_name):
        """读取 TAU19 benchmark 的东西（但是是以我的文件夹结构为准，你可以自己调整）"""
        if self.status == 0:
            self.init()
            
        current_dir = os.path.dirname(os.path.abspath(__file__))
        print(current_dir)
        base_path = current_dir + "/benchmarks"
        benchmark_repo = "TAU19"

        #design_name = "s1196"
        lib_name = "NangateOpenCellLibrary"
        lib_base = f"{base_path}/{benchmark_repo}/lib"

        search_path = f"{base_path}/{benchmark_repo}/{design_name}"
        link_path = lib_base + f"/{lib_name}_typical.lib" + " " + lib_base + f"/{lib_name}_slow.lib" + " " + lib_base + f"/{lib_name}_fast.lib"
        verilog_path = search_path + f"/design/{design_name}.v"
        spef_path = search_path + f"/design/{design_name}.spef"
        sdc_path = search_path + f"/design/{design_name}.sdc"

        self.command(f'set search_path "{search_path}"')
        self.command(f'set link_path "* {link_path}"')
        self.command(f'read_verilog {verilog_path}')
        self.command(f'current_design "{design_name}"')
        self.command('link_design')
        self.command(f'read_parasitics -format SPEF {spef_path}')
        self.command(f'read_sdc -echo {sdc_path}')
        self.command(f'update_timing')
        
        return 1


