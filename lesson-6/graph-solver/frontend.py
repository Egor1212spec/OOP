import tkinter as tk
from tkinter import ttk, messagebox
import math
import random
import backend

class GraphSolverGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Graph Problem Solver")
        self.geometry("1150x750")
        
        self.setup_styles()
        self.grid_vars = []
        self.node_coords = {}
        self.dim_val = 7
        
        container = tk.PanedWindow(self, orient=tk.HORIZONTAL, bg='#dddddd')
        container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.left_p = ttk.Frame(container)
        self.right_p = ttk.Frame(container)
        
        container.add(self.left_p, minsize=400, width=500)
        container.add(self.right_p, minsize=400)
        
        self.build_controls()
        self.build_visualizer()
        
        self.mode_var.set(True)
        self.update_mode()

    def setup_styles(self):
        s = ttk.Style()
        s.theme_use('clam')
        s.configure("TButton", padding=6)
        s.configure("Big.TButton", font=('Arial', 11, 'bold'))

    def build_controls(self):
        pad_opts = {'padx': 8, 'pady': 6}
        
        grp_sets = ttk.LabelFrame(self.left_p, text="Configuration")
        grp_sets.pack(fill=tk.X, **pad_opts)
        
        fr_top = ttk.Frame(grp_sets)
        fr_top.pack(fill=tk.X, pady=5)
        
        ttk.Label(fr_top, text="Vertices count:").pack(side=tk.LEFT, padx=5)
        self.spin_dim = ttk.Spinbox(fr_top, from_=3, to=16, width=5, command=self.rebuild_grid)
        self.spin_dim.set(7)
        self.spin_dim.pack(side=tk.LEFT)
        
        self.mode_var = tk.BooleanVar()
        cbtn = ttk.Checkbutton(grp_sets, text="Use Edge Weights", variable=self.mode_var, command=self.update_mode)
        cbtn.pack(anchor='w', padx=5)
        
        self.grp_table = ttk.LabelFrame(self.left_p, text="Adjacency Matrix")
        self.grp_table.pack(fill=tk.BOTH, expand=True, **pad_opts)
        
        self.tbl_frame = ttk.Frame(self.grp_table)
        self.tbl_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        grp_text = ttk.LabelFrame(self.left_p, text="Graph Definition")
        grp_text.pack(fill=tk.BOTH, expand=True, **pad_opts)
        
        self.txt_edges = tk.Text(grp_text, height=10, font=('Consolas', 10))
        self.txt_edges.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        grp_res = ttk.LabelFrame(self.left_p, text="Target Vertices")
        grp_res.pack(fill=tk.X, **pad_opts)
        self.ent_targets = ttk.Entry(grp_res)
        self.ent_targets.pack(fill=tk.X, padx=5, pady=5)

    def build_visualizer(self):
        top_bar = ttk.Frame(self.right_p)
        top_bar.pack(fill=tk.X, pady=5, padx=5)
        
        ttk.Button(top_bar, text="Refresh View", command=self.render_graph).pack(side=tk.RIGHT)
        ttk.Label(top_bar, text="Graph Preview", font=('Arial', 12)).pack(side=tk.LEFT)
        
        self.cv = tk.Canvas(self.right_p, bg='white', bd=2, relief=tk.SUNKEN)
        self.cv.pack(fill=tk.BOTH, expand=True, padx=5)
        
        btn_run = ttk.Button(self.right_p, text="CALCULATE", style="Big.TButton", command=self.process_solution)
        btn_run.pack(fill=tk.X, padx=10, pady=10)
        
        self.lbl_status = ttk.Label(self.right_p, text="Ready", font=('Courier', 12), anchor='center', background='#eeeeee', relief=tk.GROOVE)
        self.lbl_status.pack(fill=tk.X, padx=10, pady=(0, 10), ipady=10)

    def update_mode(self):
        w = self.mode_var.get()
        self.txt_edges.delete('1.0', tk.END)
        self.ent_targets.delete(0, tk.END)
        
        if w:
            self.txt_edges.insert('1.0', "A-B 10\nA-C 15\nB-C 8\nC-D 12\nD-E 5")
            self.ent_targets.insert(0, "A, E")
        else:
            self.txt_edges.insert('1.0', "A-B\nB-C\nC-D\nD-E\nE-A")
            self.ent_targets.insert(0, "B, D")
            
        self.rebuild_grid()
        self.render_graph()

    def rebuild_grid(self):
        try:
            n = int(self.spin_dim.get())
        except:
            return
        
        self.dim_val = n
        for w in self.tbl_frame.winfo_children():
            w.destroy()
            
        self.grid_vars = [[None]*n for _ in range(n)]
        use_w = self.mode_var.get()
        
        for r in range(n + 1):
            self.tbl_frame.rowconfigure(r, weight=1)
            self.tbl_frame.columnconfigure(r, weight=1)
            
            for c in range(n + 1):
                if r==0 and c==0: continue
                
                if r==0:
                    ttk.Label(self.tbl_frame, text=str(c)).grid(row=r, column=c)
                elif c==0:
                    ttk.Label(self.tbl_frame, text=str(r)).grid(row=r, column=c)
                else:
                    i, j = r-1, c-1
                    if i == j:
                        tk.Frame(self.tbl_frame, bg='grey').grid(row=r, column=c, sticky='nsew')
                    elif use_w:
                        e = ttk.Entry(self.tbl_frame, justify='center', width=3)
                        e.grid(row=r, column=c, sticky='nsew', padx=1, pady=1)
                        if j < i: e.config(state='disabled')
                        else:
                            e.bind('<KeyRelease>', lambda ev, x=i, y=j: self.mirror_val(x, y))
                        self.grid_vars[i][j] = e
                    else:
                        bv = tk.BooleanVar()
                        chk = ttk.Checkbutton(self.tbl_frame, variable=bv, command=lambda x=i, y=j: self.mirror_bool(x, y))
                        chk.grid(row=r, column=c)
                        if j < i: chk.config(state='disabled')
                        self.grid_vars[i][j] = bv

    def mirror_val(self, r, c):
        src = self.grid_vars[r][c].get()
        dst = self.grid_vars[c][r]
        dst.config(state='normal')
        dst.delete(0, tk.END)
        dst.insert(0, src)
        dst.config(state='disabled')

    def mirror_bool(self, r, c):
        val = self.grid_vars[r][c].get()
        self.grid_vars[c][r].set(val)

    def parse_gui_data(self):
        adj = {}
        nodes = set()
        weights = {}
        raw = self.txt_edges.get('1.0', tk.END)
        is_w = self.mode_var.get()
        
        for l in raw.upper().split('\n'):
            l = l.strip().replace('—', '-').replace(',', ' ')
            parts = [p for p in l.replace('-', ' ').split() if p]
            
            if not parts: continue
            
            u = parts[0]
            nodes.add(u)
            if u not in adj: adj[u] = []
            
            if len(parts) >= 2:
                v = parts[1]
                if len(parts) > 2 and parts[-1].isdigit() and is_w:
                    w = parts[-1]
                else:
                    w = None
                
                nodes.add(v)
                if v not in adj: adj[v] = []
                
                key = tuple(sorted((u, v)))
                if key not in weights:
                    adj[u].append(v)
                    adj[v].append(u)
                    if w: weights[key] = w
                    else: weights[key] = ""
                    
        return adj, sorted(list(nodes)), weights

    def render_graph(self):
        self.cv.delete('all')
        adj, nodes, w_map = self.parse_gui_data()
        w, h = self.cv.winfo_width(), self.cv.winfo_height()
        
        if w < 50: 
            self.after(100, self.render_graph)
            return
            
        coords = {n: (random.randint(50, w-50), random.randint(50, h-50)) for n in nodes}
        
        factor = 20000.0
        temp = w / 8.0
        
        for _ in range(60):
            deltas = {n: [0,0] for n in nodes}
            
            for n1 in nodes:
                for n2 in nodes:
                    if n1 == n2: continue
                    dx = coords[n1][0] - coords[n2][0]
                    dy = coords[n1][1] - coords[n2][1]
                    d = (dx**2 + dy**2)**0.5 + 0.1
                    rep = (factor / d**2)
                    deltas[n1][0] += (dx/d) * rep
                    deltas[n1][1] += (dy/d) * rep
            
            edge_list = []
            for u in adj:
                for v in adj[u]:
                    if u < v: edge_list.append((u, v))
            
            for u, v in edge_list:
                dx = coords[u][0] - coords[v][0]
                dy = coords[u][1] - coords[v][1]
                d = (dx**2 + dy**2)**0.5 + 0.1
                att = (d**2) / 200.0
                deltas[u][0] -= (dx/d) * att
                deltas[u][1] -= (dy/d) * att
                deltas[v][0] += (dx/d) * att
                deltas[v][1] += (dy/d) * att
            
            for n in nodes:
                dx, dy = deltas[n]
                dist = (dx**2 + dy**2)**0.5
                capped = min(dist, temp)
                if dist > 0:
                    coords[n] = (
                        min(w-20, max(20, coords[n][0] + (dx/dist)*capped)),
                        min(h-20, max(20, coords[n][1] + (dy/dist)*capped))
                    )
            temp *= 0.95

        drawn = set()
        for u, neighbors in adj.items():
            for v in neighbors:
                pair = tuple(sorted((u, v)))
                if pair in drawn: continue
                drawn.add(pair)
                x1, y1 = coords[u]
                x2, y2 = coords[v]
                self.cv.create_line(x1, y1, x2, y2, fill='#555555')
                
                lbl = w_map.get(pair)
                if lbl:
                    mx, my = (x1+x2)/2, (y1+y2)/2
                    self.cv.create_rectangle(mx-8, my-8, mx+8, my+8, fill='white', outline='')
                    self.cv.create_text(mx, my, text=lbl, fill='red', font=('Arial', 9))

        for n, (x, y) in coords.items():
            self.cv.create_oval(x-15, y-15, x+15, y+15, fill='#87CEEB', outline='black')
            self.cv.create_text(x, y, text=n, font=('Arial', 10, 'bold'))

    def process_solution(self):
        rows = []
        is_w = self.mode_var.get()
        n = self.dim_val
        
        for r in range(n):
            line_vals = []
            for c in range(n):
                if r == c:
                    line_vals.append("0")
                else:
                    raw = self.grid_vars[r][c].get()
                    if is_w:
                        line_vals.append(raw if raw else "0")
                    else:
                        line_vals.append("1" if raw else "0")
            rows.append(" ".join(line_vals))
            
        mat_str = "\n".join(rows)
        g_str = self.txt_edges.get("1.0", tk.END)
        t_str = self.ent_targets.get()
        
        res = backend.solve(mat_str, g_str, t_str, is_w)
        
        color = 'red' if "Error" in res or "not found" in res or "mismatch" in res else 'green'
        self.lbl_status.config(text=res, foreground=color)

if __name__ == "__main__":
    app = GraphSolverGUI()
    app.mainloop()