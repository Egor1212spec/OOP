import sys
import json
import itertools
from heapq import heappush, heappop

from PySide6.QtCore import Qt, QRectF, QLineF, QPointF, Signal, QObject
from PySide6.QtGui import QPen, QBrush, QColor, QPainterPathStroker, QAction, QFont, QPainter, QPalette
from PySide6.QtWidgets import (QApplication, QGraphicsView, QGraphicsScene,
                               QGraphicsItem, QGraphicsEllipseItem, QGraphicsLineItem, 
                               QGraphicsTextItem, QMainWindow, QWidget, QHBoxLayout, 
                               QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView,
                               QFileDialog, QMessageBox, QLabel, QPushButton, 
                               QInputDialog, QGroupBox, QComboBox)

VISUALS = {
    'bg': "#2b2b2b",
    'node_fill': "#3498db",
    'node_active': "#9b59b6",
    'node_border': "#ffffff",
    'edge_def': "#ecf0f1",
    'edge_path': "#f1c40f",
    'text_main': "#ffffff",
    'text_weight': "#fab1a0",
    'table_bg': "#353535",
    'dia_bg': "#555555",
    'radius': 18
}

class SolverEngine:
    @staticmethod
    def get_isomorphism(scene_nodes, table_data):
        nodes_sorted = sorted(scene_nodes, key=lambda x: x.uid)
        
        g_map = {n.uid: {} for n in nodes_sorted}
        for n in nodes_sorted:
            for link in n.links:
                target = link.end if link.start == n else link.start
                try:
                    w = int(link.val) if link.val.isdigit() else 1
                except:
                    w = 1
                g_map[n.uid][target.uid] = w

        dim = len(table_data)
        m_map = {i: {} for i in range(dim)}
        for r in range(dim):
            for c in range(dim):
                raw = table_data[r][c]
                if raw and raw.isdigit():
                    val = int(raw)
                    if val > 0: m_map[r][c] = val

        graph_weighted = any(any(w > 1 for w in adj.values()) for adj in g_map.values())
        if not graph_weighted:
            for r in m_map:
                for c in m_map[r]: m_map[r][c] = 1

        g_degs = {k: len(v) for k, v in g_map.items()}
        m_degs = {k: len(v) for k, v in m_map.items()}

        if sorted(g_degs.values()) != sorted(m_degs.values()):
            return None
        
        g_names = list(g_map.keys())
        m_idxs = list(m_map.keys())

        if len(g_names) != len(m_idxs):
            return None

        g_groups = {}
        for k, d in g_degs.items():
            g_groups.setdefault(d, []).append(k)
        
        m_groups = {}
        for k, d in m_degs.items():
            m_groups.setdefault(d, []).append(k)

        for d in g_groups:
            if d not in m_groups or len(g_groups[d]) != len(m_groups[d]):
                return None
        
        ordered_degrees = sorted(g_groups.keys())
        clusters = [(g_groups[d], m_groups[d]) for d in ordered_degrees]

        def backtrack(cluster_idx, mapping):
            if cluster_idx == len(clusters):
                return validate(mapping)
            
            vars_g, vars_m = clusters[cluster_idx]
            for perm in itertools.permutations(vars_m):
                temp_map = mapping.copy()
                for i, g_node in enumerate(vars_g):
                    temp_map[g_node] = perm[i]
                
                if backtrack(cluster_idx + 1, temp_map):
                    return temp_map
            return None

        def validate(mapping):
            for u, neighbors in g_map.items():
                u_mapped = mapping[u]
                for v, w in neighbors.items():
                    v_mapped = mapping[v]
                    if v_mapped not in m_map[u_mapped]:
                        return False
                    if w != m_map[u_mapped][v_mapped]:
                        return False
            return True

        res = backtrack(0, {})
        return {k: v + 1 for k, v in res.items()} if res else None

    @staticmethod
    def dijkstra(nodes, start, end):
        adj = {n: {} for n in nodes}
        for n in nodes:
            for link in n.links:
                target = link.end if link.start == n else link.start
                w = int(link.val) if link.val.isdigit() else 1
                old_w = adj[n].get(target, float('inf'))
                adj[n][target] = min(old_w, w)
        
        min_dist = {n: float('inf') for n in nodes}
        min_dist[start] = 0
        prev = {n: None for n in nodes}
        
        queue = [(0, id(start), start)]

        while queue:
            d, _, curr = heappop(queue)
            if d > min_dist[curr]: continue
            if curr == end: break

            for neighbor, weight in adj[curr].items():
                new_dist = d + weight
                if new_dist < min_dist[neighbor]:
                    min_dist[neighbor] = new_dist
                    prev[neighbor] = curr
                    heappush(queue, (new_dist, id(neighbor), neighbor))

        if min_dist[end] == float('inf'):
            return None
        
        path = []
        curr = end
        while curr:
            path.append(curr)
            curr = prev[curr]
        return path[::-1]


class Link(QGraphicsLineItem):
    def __init__(self, n1, n2, val="", scene_ref=None):
        super().__init__()
        self.start = n1
        self.end = n2
        self.val = val
        self.highlight = False
        self._scene_ref = scene_ref
        
        self.setZValue(-1)
        
        self._pen_def = QPen(QColor(VISUALS['edge_def']), 3)
        self._pen_def.setCapStyle(Qt.RoundCap)
        self._pen_def.setJoinStyle(Qt.RoundJoin)
        
        self._pen_path = QPen(QColor(VISUALS['edge_path']), 5)
        self._pen_path.setCapStyle(Qt.RoundCap)
        
        self.setPen(self._pen_def)
        
        self.lbl = QGraphicsTextItem(val, self)
        self.lbl.setDefaultTextColor(QColor(VISUALS['text_weight']))
        self.lbl.setFont(QFont("Segoe UI", 11, QFont.Bold))
        
        self.sync_pos()

    def sync_pos(self):
        p1 = self.start.scenePos()
        p2 = self.end.scenePos()
        line = QLineF(p1, p2)
        self.setLine(line)
        
        if self.lbl.toPlainText():
            self.lbl.setVisible(True)
            c = line.center()
            self.lbl.setPos(c.x() - self.lbl.boundingRect().width() / 2, 
                            c.y() - self.lbl.boundingRect().height() / 2 - 10)
        else:
            self.lbl.setVisible(False)

    def update_val(self, txt):
        if self.val != txt:
            self.val = txt
            self.lbl.setPlainText(txt)
            self.sync_pos()
            if self._scene_ref:
                self._scene_ref.notify_link_changed(self)

    def set_path_style(self, active):
        self.highlight = active
        self.setPen(self._pen_path if active else self._pen_def)

    def mouseDoubleClickEvent(self, evt):
        new_w, ok = QInputDialog.getText(None, "Вес ребра", "Введите число:", text=self.val)
        if ok: self.update_val(new_w)
        super().mouseDoubleClickEvent(evt)
        
    def shape(self):
        path = super().shape()
        stroker = QPainterPathStroker()
        stroker.setWidth(15)
        return stroker.createStroke(path)


class Vertex(QGraphicsEllipseItem):
    def __init__(self, uid, x, y):
        r = VISUALS['radius']
        super().__init__(-r, -r, r*2, r*2)
        self.uid = uid
        self.links = []
        self.solution_idx = None

        self.setPos(x, y)
        
        self.brush_def = QBrush(QColor(VISUALS['node_fill']))
        self.brush_act = QBrush(QColor(VISUALS['node_active']))
        
        self.setBrush(self.brush_def)
        self.setPen(QPen(QColor(VISUALS['node_border']), 2))
        
        self.setZValue(10)
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemSendsGeometryChanges)

        self.txt = QGraphicsTextItem(uid, self)
        self.txt.setDefaultTextColor(Qt.white)
        self.txt.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self._center_text()

        self.sol_txt = QGraphicsTextItem("", self)
        self.sol_txt.setDefaultTextColor(QColor("#2ecc71"))
        self.sol_txt.setFont(QFont("Segoe UI", 14, QFont.ExtraBold))
        self.sol_txt.setPos(r, -r*1.5)

    def _center_text(self):
        rect = self.txt.boundingRect()
        self.txt.setPos(-rect.width() / 2, -rect.height() / 2)

    def add_link(self, l):
        self.links.append(l)

    def remove_link(self, l):
        if l in self.links: self.links.remove(l)

    def set_active(self, state):
        self.setBrush(self.brush_act if state else self.brush_def)

    def set_result(self, val):
        self.solution_idx = val
        self.sol_txt.setPlainText(f"[{val}]" if val else "")

    def itemChange(self, change, val):
        if change == QGraphicsItem.ItemPositionHasChanged and self.scene():
            for l in self.links: l.sync_pos()
        return super().itemChange(change, val)


class EditorScene(QGraphicsScene):
    structure_changed = Signal() 
    link_data_changed = Signal(object, object, str)

    def __init__(self):
        super().__init__()
        self.setBackgroundBrush(QBrush(QColor(VISUALS['bg'])))
        self.setSceneRect(0, 0, 2000, 2000)
        
        self._name_counter = 0
        self._link_source = None
        self._block_signals = False

    def get_vertex_list(self):
        items = [i for i in self.items() if isinstance(i, Vertex)]
        return sorted(items, key=lambda x: x.uid)

    def _next_name(self):
        n = self._name_counter
        res = ""
        while n >= 0:
            res = chr(ord('A') + (n % 26)) + res
            n = n // 26 - 1
        self._name_counter += 1
        return res

    def add_vertex(self, pos, name=None):
        if not name: name = self._next_name()
        v = Vertex(name, pos.x(), pos.y())
        self.addItem(v)
        if not self._block_signals:
            self.structure_changed.emit()
        return v

    def add_link(self, v1, v2, w=""):
        if v1 == v2: return
        for l in v1.links:
            if (l.start == v1 and l.end == v2) or (l.start == v2 and l.end == v1):
                if l.val != w:
                    l.update_val(w)
                return
        
        lnk = Link(v1, v2, w, scene_ref=self)
        self.addItem(lnk)
        v1.add_link(lnk)
        v2.add_link(lnk)
        
        if not self._block_signals:
            self.link_data_changed.emit(v1.uid, v2.uid, w)

    def remove_element(self, item):
        structure_affected = False
        link_affected = False
        
        if isinstance(item, Vertex):
            for l in list(item.links): 
                self.remove_element(l)
            self.removeItem(item)
            structure_affected = True
            
        elif isinstance(item, Link):
            u, v = item.start.uid, item.end.uid
            item.start.remove_link(item)
            item.end.remove_link(item)
            self.removeItem(item)
            if not self._block_signals:
                self.link_data_changed.emit(u, v, "")
            
        elif isinstance(item, QGraphicsTextItem):
            self.remove_element(item.parentItem())

        if structure_affected and not self._block_signals:
            self.structure_changed.emit()

    def notify_link_changed(self, link):
        if not self._block_signals:
            self.link_data_changed.emit(link.start.uid, link.end.uid, link.val)

    def reset(self):
        self._block_signals = True
        self.clear()
        self._name_counter = 0
        self._link_source = None
        self._block_signals = False
        self.structure_changed.emit()

    def keyReleaseEvent(self, e):
        if e.key() == Qt.Key_Shift and self._link_source:
            self._link_source.set_active(False)
            self._link_source = None
        super().keyReleaseEvent(e)

    def mousePressEvent(self, e):
        pos = e.scenePos()
        target = self.itemAt(pos, self.views()[0].transform())
        
        if isinstance(target, QGraphicsTextItem): 
            target = target.parentItem()

        if e.button() == Qt.LeftButton:
            if e.modifiers() & Qt.ShiftModifier:
                if isinstance(target, Vertex):
                    if self._link_source:
                        self._link_source.set_active(False)
                        if self._link_source != target:
                            self.add_link(self._link_source, target)
                        self._link_source = target
                        self._link_source.set_active(True)
                    else:
                        self._link_source = target
                        target.set_active(True)
                else:
                    if self._link_source:
                        self._link_source.set_active(False)
                        self._link_source = None
            else:
                if self._link_source:
                    self._link_source.set_active(False)
                    self._link_source = None
                
                if not target:
                    valid = True
                    for v in self.get_vertex_list():
                        if QLineF(pos, v.scenePos()).length() < 50:
                            valid = False; break
                    if valid: self.add_vertex(pos)

            if target: super().mousePressEvent(e)
            
        elif e.button() == Qt.RightButton:
            if self._link_source:
                self._link_source.set_active(False)
                self._link_source = None
            if target: self.remove_element(target)


class MatrixGrid(QTableWidget):
    cell_value_changed = Signal(int, int, str)

    def __init__(self):
        super().__init__()
        self.setStyleSheet(f"background-color: {VISUALS['table_bg']}; color: white; gridline-color: #666;")
        self.horizontalHeader().setDefaultSectionSize(40)
        self.verticalHeader().setDefaultSectionSize(30)
        self.itemChanged.connect(self._on_item_changed)
        self._internal_change = False

    def resize_grid(self, nodes):
        self._internal_change = True
        n = len(nodes)
        
        self.setRowCount(n)
        self.setColumnCount(n)
        
        labels = [node.uid for node in nodes]
        self.setHorizontalHeaderLabels(labels)
        self.setVerticalHeaderLabels(labels)

        for r in range(n):
            for c in range(n):
                val = ""
                u = nodes[r]
                v = nodes[c]
                for l in u.links:
                    if l.end == v or l.start == v:
                        val = l.val
                        break
                
                it = QTableWidgetItem(val)
                it.setTextAlignment(Qt.AlignCenter)
                
                if r == c:
                    it.setFlags(Qt.ItemIsEnabled)
                    it.setBackground(QColor(VISUALS['dia_bg']))
                else:
                    it.setBackground(QColor(VISUALS['table_bg']))
                
                self.setItem(r, c, it)
        
        self._internal_change = False

    def _on_item_changed(self, it):
        if self._internal_change: return
        
        r, c = it.row(), it.column()
        if r == c: return
        
        txt = it.text()
        if txt and not txt.isdigit():
            if txt != "":
                self._internal_change = True
                it.setText("")
                self._internal_change = False
                return
            
        self._internal_change = True
        mirror = self.item(c, r)
        if mirror: mirror.setText(txt)
        self._internal_change = False
        
        self.cell_value_changed.emit(r, c, txt)

    def get_raw_data(self):
        rows = self.rowCount()
        res = []
        for r in range(rows):
            row_vals = []
            for c in range(rows):
                it = self.item(r, c)
                row_vals.append(it.text() if it else "")
            res.append(row_vals)
        return res
    
    def update_cell_from_graph(self, r, c, val):
        if r >= self.rowCount() or c >= self.columnCount(): return
        
        self._internal_change = True
        it1 = self.item(r, c)
        it2 = self.item(c, r)
        if it1: it1.setText(val)
        if it2: it2.setText(val)
        self._internal_change = False

    def load_matrix(self, data):
        self._internal_change = True
        for r in range(len(data)):
            for c in range(len(data)):
                if r < self.rowCount() and c < self.columnCount():
                    val = data[r][c]
                    it = self.item(r, c)
                    if it: it.setText(val)
        self._internal_change = False


class AppWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Graph Iso-Solver")
        self.resize(1200, 750)
        
        self.scene = EditorScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setDragMode(QGraphicsView.ScrollHandDrag)
        
        self.grid = MatrixGrid()
        
        self.scene.structure_changed.connect(self._sync_graph_to_matrix_structure)
        self.scene.link_data_changed.connect(self._sync_graph_to_matrix_data)
        self.grid.cell_value_changed.connect(self._sync_matrix_to_graph)
        
        self._build_ui()
        self._build_menu()

    def _sync_graph_to_matrix_structure(self):
        nodes = self.scene.get_vertex_list()
        self.grid.resize_grid(nodes)
        self._refresh_combos()

    def _sync_graph_to_matrix_data(self, u_uid, v_uid, val):
        nodes = self.scene.get_vertex_list()
        try:
            r = next(i for i, n in enumerate(nodes) if n.uid == u_uid)
            c = next(i for i, n in enumerate(nodes) if n.uid == v_uid)
            self.grid.update_cell_from_graph(r, c, val)
        except StopIteration:
            pass

    def _sync_matrix_to_graph(self, r, c, val):
        nodes = self.scene.get_vertex_list()
        if r < len(nodes) and c < len(nodes):
            u = nodes[r]
            v = nodes[c]
            
            self.scene._block_signals = True
            
            existing_link = None
            for l in u.links:
                if l.end == v or l.start == v:
                    existing_link = l
                    break
            
            if val == "":
                if existing_link:
                    self.scene.removeItem(existing_link)
                    u.remove_link(existing_link)
                    v.remove_link(existing_link)
            else:
                if existing_link:
                    existing_link.update_val(val)
                else:
                    self.scene.add_link(u, v, val)
            
            self.scene._block_signals = False

    def _build_ui(self):
        main_wid = QWidget()
        layout = QHBoxLayout(main_wid)
        
        left_box = QVBoxLayout()
        
        grp_mat = QGroupBox("Matrix Input")
        l_mat = QVBoxLayout()
        l_mat.addWidget(self.grid)
        grp_mat.setLayout(l_mat)
        
        grp_ctrl = QGroupBox("Operations")
        l_ctrl = QVBoxLayout()
        
        path_row = QHBoxLayout()
        self.cb_start = QComboBox()
        self.cb_end = QComboBox()
        self.cb_start.addItem("-")
        self.cb_end.addItem("-")
        
        self.cb_start.currentIndexChanged.connect(self._calc_path)
        self.cb_end.currentIndexChanged.connect(self._calc_path)
        
        path_row.addWidget(QLabel("Start:"))
        path_row.addWidget(self.cb_start)
        path_row.addWidget(QLabel("End:"))
        path_row.addWidget(self.cb_end)
        l_ctrl.addLayout(path_row)
        
        l_ctrl.addSpacing(15)
        
        btn_run = QPushButton("FIND ISOMORPHISM")
        btn_run.setStyleSheet("background-color: #27ae60; color: white; padding: 10px; font-weight: bold;")
        btn_run.clicked.connect(self._run_solver)
        l_ctrl.addWidget(btn_run)
        
        btn_clr_res = QPushButton("Reset Solution Labels")
        btn_clr_res.clicked.connect(self._reset_labels)
        l_ctrl.addWidget(btn_clr_res)
        
        btn_clr_w = QPushButton("Clear Graph")
        btn_clr_w.setStyleSheet("background-color: #c0392b; color: white;")
        btn_clr_w.clicked.connect(self._wipe_all)
        l_ctrl.addWidget(btn_clr_w)
        
        info = QLabel("\n[Controls]\nLeft Click: Add Node\nShift+Click: Link Nodes\nRight Click: Delete\nDouble Click Edge: Set Weight")
        info.setStyleSheet("color: #95a5a6; font-size: 10px;")
        l_ctrl.addWidget(info)
        
        grp_ctrl.setLayout(l_ctrl)
        
        left_box.addWidget(grp_mat, 2)
        left_box.addWidget(grp_ctrl, 0)
        
        right_box = QVBoxLayout()
        right_box.addWidget(QLabel("Canvas"))
        right_box.addWidget(self.view)
        
        layout.addLayout(left_box, 1)
        layout.addLayout(right_box, 3)
        self.setCentralWidget(main_wid)

    def _build_menu(self):
        mb = self.menuBar()
        fm = mb.addMenu("File")
        
        a_save = QAction("Save...", self)
        a_save.triggered.connect(self._save_json)
        fm.addAction(a_save)
        
        a_load = QAction("Load...", self)
        a_load.triggered.connect(self._load_json)
        fm.addAction(a_load)
        
        a_wipe = QAction("Reset All", self)
        a_wipe.triggered.connect(self._wipe_all)
        fm.addAction(a_wipe)

    def _refresh_combos(self):
        nodes = sorted([n.uid for n in self.scene.get_vertex_list()])
        s_curr = self.cb_start.currentText()
        e_curr = self.cb_end.currentText()
        
        self.cb_start.blockSignals(True)
        self.cb_end.blockSignals(True)
        
        self.cb_start.clear(); self.cb_end.clear()
        self.cb_start.addItem("-"); self.cb_end.addItem("-")
        self.cb_start.addItems(nodes); self.cb_end.addItems(nodes)
        
        if s_curr in nodes: self.cb_start.setCurrentText(s_curr)
        if e_curr in nodes: self.cb_end.setCurrentText(e_curr)
            
        self.cb_start.blockSignals(False)
        self.cb_end.blockSignals(False)
        self._calc_path()

    def _calc_path(self):
        for i in self.scene.items():
            if isinstance(i, Link): i.set_path_style(False)
            
        s_txt = self.cb_start.currentText()
        e_txt = self.cb_end.currentText()
        
        if s_txt == "-" or e_txt == "-" or s_txt == e_txt: return
        
        v_list = self.scene.get_vertex_list()
        start = next((x for x in v_list if x.uid == s_txt), None)
        end = next((x for x in v_list if x.uid == e_txt), None)
        
        if not start or not end: return
        
        path = SolverEngine.dijkstra(v_list, start, end)
        if path:
            for i in range(len(path) - 1):
                u, v = path[i], path[i+1]
                for l in u.links:
                    if l.start == v or l.end == v:
                        l.set_path_style(True)
                        break

    def _run_solver(self):
        nodes = self.scene.get_vertex_list()
        data = self.grid.get_raw_data()
        
        if not nodes:
            QMessageBox.warning(self, "Warning", "Graph is empty")
            return

        res = SolverEngine.get_isomorphism(nodes, data)
        if res:
            txt = "Solution Found:\n"
            for k in sorted(res.keys()):
                val = res[k]
                txt += f"{k} -> {val}\n"
                for n in nodes:
                    if n.uid == k: n.set_result(str(val))
            QMessageBox.information(self, "Result", txt)
        else:
            QMessageBox.critical(self, "Fail", "No isomorphism found.")

    def _reset_labels(self):
        for n in self.scene.get_vertex_list(): n.set_result(None)

    def _clear_weights(self):
        for i in self.scene.items():
            if isinstance(i, Link): i.update_val("")

    def _wipe_all(self):
        self.scene.reset()

    def _save_json(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save", "", "JSON (*.json)")
        if not path: return
        
        v_list = self.scene.get_vertex_list()
        v_map = {v: i for i, v in enumerate(v_list)}
        
        nodes_js = [{"id": i, "name": v.uid, "x": v.x(), "y": v.y()} for i, v in enumerate(v_list)]
        edges_js = []
        
        seen_links = set()
        for v in v_list:
            for l in v.links:
                if l in seen_links: continue
                seen_links.add(l)
                edges_js.append({
                    "u": v_map[l.start],
                    "v": v_map[l.end],
                    "w": l.val
                })
        
        blob = {
            "graph": {
                "nodes": nodes_js, "edges": edges_js, 
                "counter": self.scene._name_counter
            },
            "matrix": self.grid.get_raw_data()
        }
        
        try:
            with open(path, 'w') as f: json.dump(blob, f, indent=2)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _load_json(self):
        path, _ = QFileDialog.getOpenFileName(self, "Load", "", "JSON (*.json)")
        if not path: return
        
        try:
            with open(path, 'r') as f: blob = json.load(f)
            
            self.scene._block_signals = True
            self.scene.reset()
            self.scene._block_signals = False
            
            g = blob.get("graph", {})
            self.scene._name_counter = g.get("counter", 0)
            
            id_to_node = {}
            for n_obj in g.get("nodes", []):
                v = self.scene.add_vertex(QPointF(n_obj['x'], n_obj['y']), n_obj['name'])
                id_to_node[n_obj['id']] = v
            
            for e_obj in g.get("edges", []):
                v1 = id_to_node.get(e_obj['u'])
                v2 = id_to_node.get(e_obj['v'])
                if v1 and v2:
                    self.scene.add_link(v1, v2, e_obj.get('w', ""))
            
            if "matrix" in blob:
                self.grid.load_matrix(blob.get("matrix", []))
            
            self._sync_graph_to_matrix_structure()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    pal = app.palette()
    pal.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
    pal.setColor(QPalette.ColorRole.WindowText, Qt.white)
    pal.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
    pal.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
    pal.setColor(QPalette.ColorRole.ToolTipBase, Qt.white)
    pal.setColor(QPalette.ColorRole.ToolTipText, Qt.white)
    pal.setColor(QPalette.ColorRole.Text, Qt.white)
    pal.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
    pal.setColor(QPalette.ColorRole.ButtonText, Qt.white)
    pal.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
    pal.setColor(QPalette.ColorRole.HighlightedText, Qt.black)
    app.setPalette(pal)

    w = AppWindow()
    w.show()
    sys.exit(app.exec())