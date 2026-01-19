import re
from itertools import product, permutations

class LogicSolver:
    def __init__(self):
        self._table = []
        self._vars = []
        self._expr = ""

    def _parse(self, formula):
        tokens = re.findall(r'\b[a-zA-Z_]\w*\b', formula)
        reserved = {'and', 'or', 'not', 'True', 'False'}
        return sorted(list(set(t for t in tokens if t not in reserved)))

    def build(self, formula):
        self._expr = formula
        self._vars = self._parse(formula)
        self._table = []
        
        bytecode = compile(formula, '<string>', 'eval')
        
        for vector in product((0, 1), repeat=len(self._vars)):
            ctx = dict(zip(self._vars, vector))
            try:
                res = eval(bytecode, {}, ctx)
                entry = ctx.copy()
                entry['out'] = bool(res)
                self._table.append(entry)
            except:
                pass
        return self._table

    def query(self, mode='all'):
        if mode == '1':
            return [r for r in self._table if r['out']]
        if mode == '0':
            return [r for r in self._table if not r['out']]
        
        ones = sum(1 for r in self._table if r['out'])
        zeros = len(self._table) - ones
        
        if mode == 'min':
            return self.query('1') if ones < zeros else self.query('0')
            
        return self._table

    def stats(self):
        if not self._table:
            return {}
        total = len(self._table)
        ones = sum(1 for r in self._table if r['out'])
        return {
            'cnt': total,
            'ones': ones,
            'zeros': total - ones,
            'bias': '1' if ones < (total - ones) else '0'
        }

    def to_dnf(self):
        rows = self.query('1')
        if not rows:
            return "False"
        if len(rows) == len(self._table):
            return "True"
            
        parts = []
        for r in rows:
            sub = []
            for v in self._vars:
                sub.append(v if r[v] else f"not {v}")
            parts.append(f"({' and '.join(sub)})")
        return " or ".join(parts)

    def find_mapping(self, formula, fragment):
        v_list = self._parse(formula)
        n = len(v_list)
        if n != 4:
            return []

        full_rows = []
        target = fragment[0].get('result')
        
        bytecode = compile(formula, '<string>', 'eval')
        for vec in product((0, 1), repeat=n):
            ctx = dict(zip(v_list, vec))
            if bool(eval(bytecode, {}, ctx)) == target:
                full_rows.append(vec)

        col_keys = sorted([k for k in fragment[0].keys() if k != 'result'])
        valid_perms = []

        for p in permutations(v_list):
            
            def check_row(frag_row, real_row_vec):
                for i, key in enumerate(col_keys):
                    val = frag_row[key]
                    v_name = p[i]
                    v_idx = v_list.index(v_name)
                    if val is not None and val != real_row_vec[v_idx]:
                        return False
                return True

            for candidate_subset in permutations(full_rows, len(fragment)):
                match = True
                for i in range(len(fragment)):
                    if not check_row(fragment[i], candidate_subset[i]):
                        match = False
                        break
                
                if match:
                    s = "".join(p)
                    if s not in valid_perms:
                        valid_perms.append(s)
        
        return valid_perms