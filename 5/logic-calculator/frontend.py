import tkinter as tk
from tkinter import ttk, messagebox
from backend import LogicSolver

class LogicApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Logic Master Tool")
        self.geometry("950x720")
        self.engine = LogicSolver()
        
        style = ttk.Style()
        style.theme_use('clam')
        
        self.tabs = ttk.Notebook(self)
        self.tabs.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.tab_gen = TableGenerator(self.tabs, self.engine)
        self.tab_solve = ExamSolver(self.tabs, self.engine)
        
        self.tabs.add(self.tab_gen, text=" Генератор ")
        self.tabs.add(self.tab_solve, text=" Решатель ")

class TableGenerator(ttk.Frame):
    def __init__(self, parent, engine):
        super().__init__(parent)
        self.engine = engine
        self.raw_data = []
        self.is_editing = False
        self._init_ui()

    def _init_ui(self):
        top_panel = ttk.LabelFrame(self, text="Ввод формулы")
        top_panel.pack(fill='x', padx=10, pady=5)
        
        self.entry_var = tk.StringVar()
        self.entry = ttk.Entry(top_panel, textvariable=self.entry_var, font=('Consolas', 11))
        self.entry.pack(fill='x', padx=5, pady=5)
        self.entry.bind('<Return>', self.run_calc)
        
        btn_box = ttk.Frame(top_panel)
        btn_box.pack(fill='x', padx=5, pady=5)
        
        presets = ["x and not y", "x <= y", "(x == z) or w", "x or y or z"]
        for p in presets:
            ttk.Button(btn_box, text=p, width=15, 
                       command=lambda v=p: self.entry_var.set(v)).pack(side='left', padx=2)
            
        action_panel = ttk.Frame(self)
        action_panel.pack(fill='x', padx=10)
        
        ttk.Button(action_panel, text="Построить", command=self.run_calc).pack(side='left')
        
        self.chk_edit = tk.IntVar()
        ttk.Checkbutton(action_panel, text="Редактор", variable=self.chk_edit, 
                        command=self.toggle_edit).pack(side='left', padx=15)
        
        self.btn_restore = ttk.Button(action_panel, text="DNF -> Формула", 
                                      state='disabled', command=self.do_restore)
        self.btn_restore.pack(side='left')
        
        filter_panel = ttk.LabelFrame(self, text="Фильтрация")
        filter_panel.pack(fill='x', padx=10, pady=5)
        
        self.filter_mode = tk.StringVar(value='all')
        modes = [('Все', 'all'), ('Только 1', 'true'), ('Только 0', 'false'), ('Minority', 'minority')]
        for lbl, val in modes:
            ttk.Radiobutton(filter_panel, text=lbl, variable=self.filter_mode, 
                            value=val, command=self.refresh_grid).pack(side='left', padx=10)

        self.tree = ttk.Treeview(self, show='headings')
        self.tree.pack(fill='both', expand=True, padx=10, pady=5)
        self.tree.bind('<Double-1>', self.on_click_cell)
        
        self.status = ttk.Label(self, text="Готов", foreground="gray")
        self.status.pack(anchor='w', padx=10)

    def run_calc(self, event=None):
        f = self.entry_var.get()
        if not f: return
        try:
            self.engine.build(f)
            self.raw_data = None
            self.refresh_grid()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def refresh_grid(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
            
        data_source = self.raw_data if self.raw_data else self.engine.query('all')
        f_mode = self.filter_mode.get()
        
        display_rows = []
        if f_mode == 'all':
            display_rows = data_source
        elif f_mode == 'true':
            display_rows = [x for x in data_source if x['out']]
        elif f_mode == 'false':
            display_rows = [x for x in data_source if not x['out']]
        elif f_mode == 'minority':
            ones = sum(1 for x in data_source if x['out'])
            zeros = len(data_source) - ones
            target = True if ones < zeros else False
            if ones == zeros:
                display_rows = data_source
            else:
                display_rows = [x for x in data_source if x['out'] == target]
        
        vars_list = self.engine._vars
        if not display_rows and not vars_list:
            return

        cols = vars_list + ['OUT']
        self.tree['columns'] = cols
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=60, anchor='center')
            
        for row in display_rows:
            vals = [row[v] for v in vars_list]
            vals.append(str(int(row['out'])))
            self.tree.insert('', 'end', values=vals)
            
        self.update_status(data_source)

    def update_status(self, data):
        if not data: return
        ones = sum(1 for x in data if x['out'])
        total = len(data)
        self.status.config(text=f"Rows: {total} | True: {ones} | False: {total-ones}")

    def toggle_edit(self):
        self.is_editing = bool(self.chk_edit.get())
        if self.is_editing and self.raw_data is None:
            self.raw_data = [r.copy() for r in self.engine.query('all')]
        self.btn_restore['state'] = 'normal' if self.is_editing else 'disabled'
        
    def on_click_cell(self, event):
        if not self.is_editing: return
        item_id = self.tree.identify_row(event.y)
        if not item_id: return
        
        vals = self.tree.item(item_id, 'values')
        current_vars = {v: int(vals[i]) for i, v in enumerate(self.engine._vars)}
        
        for row in self.raw_data:
            match = all(row[k] == v for k, v in current_vars.items())
            if match:
                row['out'] = not row['out']
                break
        self.refresh_grid()

    def do_restore(self):
        try:
            res = self.engine.to_dnf()
            win = tk.Toplevel(self)
            win.title("Result")
            t = tk.Text(win, height=4, width=40)
            t.pack(padx=10, pady=10)
            t.insert('1.0', res)
        except Exception as e:
            messagebox.showerror("Error", str(e))

class ExamSolver(ttk.Frame):
    def __init__(self, parent, engine):
        super().__init__(parent)
        self.engine = engine
        self._init_ui()  # Исправлено имя метода!

    def _init_ui(self):  # Исправлено имя метода (было _setup)!
        frame_top = ttk.Frame(self)
        frame_top.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(frame_top, text="Выражение:").grid(row=0, column=0, sticky='w')
        self.f_entry = ttk.Entry(frame_top, width=40)
        self.f_entry.grid(row=0, column=1, padx=5, sticky='we')
        
        ttk.Button(frame_top, text="Решить", command=self.solve).grid(row=0, column=2, padx=5)
        
        frame_mid = ttk.Frame(self)
        frame_mid.pack(fill='both', expand=True, padx=10)
        
        f_left = ttk.LabelFrame(frame_mid, text="Фрагмент таблицы")
        f_left.pack(side='left', fill='both', expand=True)
        
        cols = ['C1', 'C2', 'C3', 'C4', 'R']
        self.grid_tv = ttk.Treeview(f_left, columns=cols, show='headings', height=8)
        for c in cols:
            self.grid_tv.heading(c, text=c)
            self.grid_tv.column(c, width=40, anchor='center')
        self.grid_tv.pack(fill='both', expand=True, pady=5)
        self.grid_tv.bind('<Double-1>', self.cycle_val)
        
        btn_bar = ttk.Frame(f_left)
        btn_bar.pack(fill='x')
        ttk.Button(btn_bar, text="+ Стр", command=self.add_row).pack(side='left')
        ttk.Button(btn_bar, text="- Стр", command=self.del_row).pack(side='left')
        ttk.Button(btn_bar, text="Clear", command=self.wipe).pack(side='right')

        f_right = ttk.LabelFrame(frame_mid, text="Ответы")
        f_right.pack(side='right', fill='both', expand=True, padx=(5, 0))
        
        self.out_log = tk.Text(f_right, width=20, state='disabled', bg="#f0f0f0")
        self.out_log.pack(fill='both', expand=True, padx=2, pady=2)

        for _ in range(3): self.add_row()

    def add_row(self):
        self.grid_tv.insert('', 'end', values=['', '', '', '', '0'])

    def del_row(self):
        s = self.grid_tv.selection()
        if s: self.grid_tv.delete(s[0])

    def wipe(self):
        for x in self.grid_tv.get_children():
            self.grid_tv.delete(x)
            
    def cycle_val(self, event):
        item = self.grid_tv.identify_row(event.y)
        col = self.grid_tv.identify_column(event.x)
        if not item or not col: return
        
        c_idx = int(col.replace('#', '')) - 1
        vals = list(self.grid_tv.item(item, 'values'))
        
        curr = vals[c_idx]
        if c_idx < 4:
            nxt = "0" if curr == "" else ("1" if curr == "0" else "")
        else:
            nxt = "1" if curr == "0" else "0"
            
        vals[c_idx] = nxt
        self.grid_tv.item(item, values=vals)

    def solve(self):
        f_str = self.f_entry.get()
        data = []
        for item in self.grid_tv.get_children():
            v = self.grid_tv.item(item, 'values')
            row = {}
            try:
                for i in range(4):
                    k = f"F{i+1}"
                    row[k] = int(v[i]) if v[i] in ('0', '1') else None
                row['result'] = bool(int(v[4]))
                data.append(row)
            except ValueError:
                continue 
                
        if not data: return
        
        self.out_log.config(state='normal')
        self.out_log.delete('1.0', 'end')
        
        try:
            res = self.engine.find_mapping(f_str, data)
            if not res:
                self.out_log.insert('end', "Нет решений")
            else:
                for r in res:
                    self.out_log.insert('end', f"{r}\n")
        except Exception as ex:
            self.out_log.insert('end', "Ошибка")
            print(ex)
        self.out_log.config(state='disabled')

if __name__ == "__main__":
    app = LogicApp()
    app.mainloop()