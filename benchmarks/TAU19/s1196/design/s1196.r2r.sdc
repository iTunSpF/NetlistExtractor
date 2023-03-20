# clocks
create_clock -period 700 -name blif_clk_net [get_ports blif_clk_net]
set_input_delay 0 -min -rise [get_ports blif_clk_net] -clock blif_clk_net
set_input_delay 350 -min -fall [get_ports blif_clk_net] -clock blif_clk_net
set_input_delay 0 -max -rise [get_ports blif_clk_net] -clock blif_clk_net
set_input_delay 350 -max -fall [get_ports blif_clk_net] -clock blif_clk_net
set_input_transition 50 -min -rise [get_ports blif_clk_net] -clock blif_clk_net
set_input_transition 50 -min -fall [get_ports blif_clk_net] -clock blif_clk_net
set_input_transition 50 -max -rise [get_ports blif_clk_net] -clock blif_clk_net
set_input_transition 50 -max -fall [get_ports blif_clk_net] -clock blif_clk_net

