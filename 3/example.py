from microschemes import TAnd, TNot, TOr

inv_a = TNot()
inv_b = TNot()
term_1 = TAnd()
term_2 = TAnd()
logic_out = TOr()

inv_b.link(term_1, 2)
term_1.link(logic_out, 1)

inv_a.link(term_2, 1)
term_2.link(logic_out, 2)

print("In1 | In2 | Out")
print("----------------")

for i in range(2):
    for j in range(2):
        term_1.In1 = i
        inv_b.In1 = j
        
        inv_a.In1 = i
        term_2.In2 = j
        
        val = int(logic_out.Res)
        print(f" {i}  |  {j}  |  {val}")