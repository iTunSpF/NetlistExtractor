# clocks
create_clock -period 500 -name blif_clk_net [get_ports blif_clk_net]
set_input_delay 0 -min -rise [get_ports blif_clk_net] -clock blif_clk_net
set_input_delay 250 -min -fall [get_ports blif_clk_net] -clock blif_clk_net
set_input_delay 0 -max -rise [get_ports blif_clk_net] -clock blif_clk_net
set_input_delay 250 -max -fall [get_ports G1] -clock blif_clk_net
set_input_transition 50 -min -rise [get_ports blif_clk_net] -clock blif_clk_net
set_input_transition 50 -min -fall [get_ports blif_clk_net] -clock blif_clk_net
set_input_transition 50 -max -rise [get_ports blif_clk_net] -clock blif_clk_net
set_input_transition 50 -max -fall [get_ports blif_clk_net] -clock blif_clk_net

# input ports
set_input_delay 330 -min -rise [get_ports G1] -clock blif_clk_net
set_input_delay 330 -min -fall [get_ports G1] -clock blif_clk_net
set_input_delay 330 -max -rise [get_ports G1] -clock blif_clk_net
set_input_delay 330 -max -fall [get_ports G1] -clock blif_clk_net
set_input_transition 50 -min -rise [get_ports G1] -clock blif_clk_net
set_input_transition 50 -min -fall [get_ports G1] -clock blif_clk_net
set_input_transition 50 -max -rise [get_ports G1] -clock blif_clk_net
set_input_transition 50 -max -fall [get_ports G1] -clock blif_clk_net
set_input_delay 330 -min -rise [get_ports G11] -clock blif_clk_net
set_input_delay 330 -min -fall [get_ports G11] -clock blif_clk_net
set_input_delay 330 -max -rise [get_ports G11] -clock blif_clk_net
set_input_delay 330 -max -fall [get_ports G11] -clock blif_clk_net
set_input_transition 50 -min -rise [get_ports G11] -clock blif_clk_net
set_input_transition 50 -min -fall [get_ports G11] -clock blif_clk_net
set_input_transition 50 -max -rise [get_ports G11] -clock blif_clk_net
set_input_transition 50 -max -fall [get_ports G11] -clock blif_clk_net
set_input_delay 330 -min -rise [get_ports G8] -clock blif_clk_net
set_input_delay 330 -min -fall [get_ports G8] -clock blif_clk_net
set_input_delay 330 -max -rise [get_ports G8] -clock blif_clk_net
set_input_delay 330 -max -fall [get_ports G8] -clock blif_clk_net
set_input_transition 50 -min -rise [get_ports G8] -clock blif_clk_net
set_input_transition 50 -min -fall [get_ports G8] -clock blif_clk_net
set_input_transition 50 -max -rise [get_ports G8] -clock blif_clk_net
set_input_transition 50 -max -fall [get_ports G8] -clock blif_clk_net
set_input_delay 330 -min -rise [get_ports G5] -clock blif_clk_net
set_input_delay 330 -min -fall [get_ports G5] -clock blif_clk_net
set_input_delay 330 -max -rise [get_ports G5] -clock blif_clk_net
set_input_delay 330 -max -fall [get_ports G5] -clock blif_clk_net
set_input_transition 50 -min -rise [get_ports G5] -clock blif_clk_net
set_input_transition 50 -min -fall [get_ports G5] -clock blif_clk_net
set_input_transition 50 -max -rise [get_ports G5] -clock blif_clk_net
set_input_transition 50 -max -fall [get_ports G5] -clock blif_clk_net
set_input_delay 330 -min -rise [get_ports G9] -clock blif_clk_net
set_input_delay 330 -min -fall [get_ports G9] -clock blif_clk_net
set_input_delay 330 -max -rise [get_ports G9] -clock blif_clk_net
set_input_delay 330 -max -fall [get_ports G9] -clock blif_clk_net
set_input_transition 50 -min -rise [get_ports G9] -clock blif_clk_net
set_input_transition 50 -min -fall [get_ports G9] -clock blif_clk_net
set_input_transition 50 -max -rise [get_ports G9] -clock blif_clk_net
set_input_transition 50 -max -fall [get_ports G9] -clock blif_clk_net
set_input_delay 330 -min -rise [get_ports G3] -clock blif_clk_net
set_input_delay 330 -min -fall [get_ports G3] -clock blif_clk_net
set_input_delay 330 -max -rise [get_ports G3] -clock blif_clk_net
set_input_delay 330 -max -fall [get_ports G3] -clock blif_clk_net
set_input_transition 50 -min -rise [get_ports G3] -clock blif_clk_net
set_input_transition 50 -min -fall [get_ports G3] -clock blif_clk_net
set_input_transition 50 -max -rise [get_ports G3] -clock blif_clk_net
set_input_transition 50 -max -fall [get_ports G3] -clock blif_clk_net
set_input_delay 330 -min -rise [get_ports G13] -clock blif_clk_net
set_input_delay 330 -min -fall [get_ports G13] -clock blif_clk_net
set_input_delay 330 -max -rise [get_ports G13] -clock blif_clk_net
set_input_delay 330 -max -fall [get_ports G13] -clock blif_clk_net
set_input_transition 50 -min -rise [get_ports G13] -clock blif_clk_net
set_input_transition 50 -min -fall [get_ports G13] -clock blif_clk_net
set_input_transition 50 -max -rise [get_ports G13] -clock blif_clk_net
set_input_transition 50 -max -fall [get_ports G13] -clock blif_clk_net
set_input_delay 330 -min -rise [get_ports G4] -clock blif_clk_net
set_input_delay 330 -min -fall [get_ports G4] -clock blif_clk_net
set_input_delay 330 -max -rise [get_ports G4] -clock blif_clk_net
set_input_delay 330 -max -fall [get_ports G4] -clock blif_clk_net
set_input_transition 50 -min -rise [get_ports G4] -clock blif_clk_net
set_input_transition 50 -min -fall [get_ports G4] -clock blif_clk_net
set_input_transition 50 -max -rise [get_ports G4] -clock blif_clk_net
set_input_transition 50 -max -fall [get_ports G4] -clock blif_clk_net
set_input_delay 330 -min -rise [get_ports G12] -clock blif_clk_net
set_input_delay 330 -min -fall [get_ports G12] -clock blif_clk_net
set_input_delay 330 -max -rise [get_ports G12] -clock blif_clk_net
set_input_delay 330 -max -fall [get_ports G12] -clock blif_clk_net
set_input_transition 50 -min -rise [get_ports G12] -clock blif_clk_net
set_input_transition 50 -min -fall [get_ports G12] -clock blif_clk_net
set_input_transition 50 -max -rise [get_ports G12] -clock blif_clk_net
set_input_transition 50 -max -fall [get_ports G12] -clock blif_clk_net
set_input_delay 330 -min -rise [get_ports G2] -clock blif_clk_net
set_input_delay 330 -min -fall [get_ports G2] -clock blif_clk_net
set_input_delay 330 -max -rise [get_ports G2] -clock blif_clk_net
set_input_delay 330 -max -fall [get_ports G2] -clock blif_clk_net
set_input_transition 50 -min -rise [get_ports G2] -clock blif_clk_net
set_input_transition 50 -min -fall [get_ports G2] -clock blif_clk_net
set_input_transition 50 -max -rise [get_ports G2] -clock blif_clk_net
set_input_transition 50 -max -fall [get_ports G2] -clock blif_clk_net
set_input_delay 330 -min -rise [get_ports G7] -clock blif_clk_net
set_input_delay 330 -min -fall [get_ports G7] -clock blif_clk_net
set_input_delay 330 -max -rise [get_ports G7] -clock blif_clk_net
set_input_delay 330 -max -fall [get_ports G7] -clock blif_clk_net
set_input_transition 50 -min -rise [get_ports G7] -clock blif_clk_net
set_input_transition 50 -min -fall [get_ports G7] -clock blif_clk_net
set_input_transition 50 -max -rise [get_ports G7] -clock blif_clk_net
set_input_transition 50 -max -fall [get_ports G7] -clock blif_clk_net
#set_input_delay 330 -min -rise [get_ports blif_reset_net] -clock blif_clk_net
#set_input_delay 330 -min -fall [get_ports blif_reset_net] -clock blif_clk_net
#set_input_delay 330 -max -rise [get_ports blif_reset_net] -clock blif_clk_net
#set_input_delay 330 -max -fall [get_ports blif_reset_net] -clock blif_clk_net
#set_input_transition 50 -min -rise [get_ports blif_reset_net] -clock blif_clk_net
#set_input_transition 50 -min -fall [get_ports blif_reset_net] -clock blif_clk_net
#set_input_transition 50 -max -rise [get_ports blif_reset_net] -clock blif_clk_net
#set_input_transition 50 -max -fall [get_ports blif_reset_net] -clock blif_clk_net
set_input_delay 330 -min -rise [get_ports G10] -clock blif_clk_net
set_input_delay 330 -min -fall [get_ports G10] -clock blif_clk_net
set_input_delay 330 -max -rise [get_ports G10] -clock blif_clk_net
set_input_delay 330 -max -fall [get_ports G10] -clock blif_clk_net
set_input_transition 50 -min -rise [get_ports G10] -clock blif_clk_net
set_input_transition 50 -min -fall [get_ports G10] -clock blif_clk_net
set_input_transition 50 -max -rise [get_ports G10] -clock blif_clk_net
set_input_transition 50 -max -fall [get_ports G10] -clock blif_clk_net
set_input_delay 330 -min -rise [get_ports G0] -clock blif_clk_net
set_input_delay 330 -min -fall [get_ports G0] -clock blif_clk_net
set_input_delay 330 -max -rise [get_ports G0] -clock blif_clk_net
set_input_delay 330 -max -fall [get_ports G0] -clock blif_clk_net
set_input_transition 50 -min -rise [get_ports G0] -clock blif_clk_net
set_input_transition 50 -min -fall [get_ports G0] -clock blif_clk_net
set_input_transition 50 -max -rise [get_ports G0] -clock blif_clk_net
set_input_transition 50 -max -fall [get_ports G0] -clock blif_clk_net
set_input_delay 330 -min -rise [get_ports G6] -clock blif_clk_net
set_input_delay 330 -min -fall [get_ports G6] -clock blif_clk_net
set_input_delay 330 -max -rise [get_ports G6] -clock blif_clk_net
set_input_delay 330 -max -fall [get_ports G6] -clock blif_clk_net
set_input_transition 50 -min -rise [get_ports G6] -clock blif_clk_net
set_input_transition 50 -min -fall [get_ports G6] -clock blif_clk_net
set_input_transition 50 -max -rise [get_ports G6] -clock blif_clk_net
set_input_transition 50 -max -fall [get_ports G6] -clock blif_clk_net

# output ports
set_output_delay 0 -min -rise [get_ports G549] -clock blif_clk_net
set_output_delay 0 -min -fall [get_ports G549] -clock blif_clk_net
set_output_delay 0 -max -rise [get_ports G549] -clock blif_clk_net
set_output_delay 0 -max -fall [get_ports G549] -clock blif_clk_net
set_load -pin_load 4 [get_ports G549]
set_output_delay 0 -min -rise [get_ports G542] -clock blif_clk_net
set_output_delay 0 -min -fall [get_ports G542] -clock blif_clk_net
set_output_delay 0 -max -rise [get_ports G542] -clock blif_clk_net
set_output_delay 0 -max -fall [get_ports G542] -clock blif_clk_net
set_load -pin_load 4 [get_ports G542]
set_output_delay 0 -min -rise [get_ports G530] -clock blif_clk_net
set_output_delay 0 -min -fall [get_ports G530] -clock blif_clk_net
set_output_delay 0 -max -rise [get_ports G530] -clock blif_clk_net
set_output_delay 0 -max -fall [get_ports G530] -clock blif_clk_net
set_load -pin_load 4 [get_ports G530]
set_output_delay 0 -min -rise [get_ports G552] -clock blif_clk_net
set_output_delay 0 -min -fall [get_ports G552] -clock blif_clk_net
set_output_delay 0 -max -rise [get_ports G552] -clock blif_clk_net
set_output_delay 0 -max -fall [get_ports G552] -clock blif_clk_net
set_load -pin_load 4 [get_ports G552]
set_output_delay 0 -min -rise [get_ports G45] -clock blif_clk_net
set_output_delay 0 -min -fall [get_ports G45] -clock blif_clk_net
set_output_delay 0 -max -rise [get_ports G45] -clock blif_clk_net
set_output_delay 0 -max -fall [get_ports G45] -clock blif_clk_net
set_load -pin_load 4 [get_ports G45]
set_output_delay 0 -min -rise [get_ports G547] -clock blif_clk_net
set_output_delay 0 -min -fall [get_ports G547] -clock blif_clk_net
set_output_delay 0 -max -rise [get_ports G547] -clock blif_clk_net
set_output_delay 0 -max -fall [get_ports G547] -clock blif_clk_net
set_load -pin_load 4 [get_ports G547]
set_output_delay 0 -min -rise [get_ports G548] -clock blif_clk_net
set_output_delay 0 -min -fall [get_ports G548] -clock blif_clk_net
set_output_delay 0 -max -rise [get_ports G548] -clock blif_clk_net
set_output_delay 0 -max -fall [get_ports G548] -clock blif_clk_net
set_load -pin_load 4 [get_ports G548]
set_output_delay 0 -min -rise [get_ports G537] -clock blif_clk_net
set_output_delay 0 -min -fall [get_ports G537] -clock blif_clk_net
set_output_delay 0 -max -rise [get_ports G537] -clock blif_clk_net
set_output_delay 0 -max -fall [get_ports G537] -clock blif_clk_net
set_load -pin_load 4 [get_ports G537]
set_output_delay 0 -min -rise [get_ports G551] -clock blif_clk_net
set_output_delay 0 -min -fall [get_ports G551] -clock blif_clk_net
set_output_delay 0 -max -rise [get_ports G551] -clock blif_clk_net
set_output_delay 0 -max -fall [get_ports G551] -clock blif_clk_net
set_load -pin_load 4 [get_ports G551]
set_output_delay 0 -min -rise [get_ports G532] -clock blif_clk_net
set_output_delay 0 -min -fall [get_ports G532] -clock blif_clk_net
set_output_delay 0 -max -rise [get_ports G532] -clock blif_clk_net
set_output_delay 0 -max -fall [get_ports G532] -clock blif_clk_net
set_load -pin_load 4 [get_ports G532]
set_output_delay 0 -min -rise [get_ports G539] -clock blif_clk_net
set_output_delay 0 -min -fall [get_ports G539] -clock blif_clk_net
set_output_delay 0 -max -rise [get_ports G539] -clock blif_clk_net
set_output_delay 0 -max -fall [get_ports G539] -clock blif_clk_net
set_load -pin_load 4 [get_ports G539]
set_output_delay 0 -min -rise [get_ports G546] -clock blif_clk_net
set_output_delay 0 -min -fall [get_ports G546] -clock blif_clk_net
set_output_delay 0 -max -rise [get_ports G546] -clock blif_clk_net
set_output_delay 0 -max -fall [get_ports G546] -clock blif_clk_net
set_load -pin_load 4 [get_ports G546]
set_output_delay 0 -min -rise [get_ports G535] -clock blif_clk_net
set_output_delay 0 -min -fall [get_ports G535] -clock blif_clk_net
set_output_delay 0 -max -rise [get_ports G535] -clock blif_clk_net
set_output_delay 0 -max -fall [get_ports G535] -clock blif_clk_net
set_load -pin_load 4 [get_ports G535]
set_output_delay 0 -min -rise [get_ports G550] -clock blif_clk_net
set_output_delay 0 -min -fall [get_ports G550] -clock blif_clk_net
set_output_delay 0 -max -rise [get_ports G550] -clock blif_clk_net
set_output_delay 0 -max -fall [get_ports G550] -clock blif_clk_net
set_load -pin_load 4 [get_ports G550]
