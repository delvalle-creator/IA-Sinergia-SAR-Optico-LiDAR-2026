# Dibuja el lienzo de un workflow de Orange (.ows) en PNG sin abrir la interfaz, con el mismo motor de Orange.
import sys, os
from AnyQt.QtWidgets import QApplication
from AnyQt.QtGui import QImage, QPainter, QColor
from AnyQt.QtCore import Qt, QRectF
app = QApplication(sys.argv[:1])
from Orange.canvas.config import Config
from orangecanvas import config as occ
cfg = Config(); occ.set_default(cfg); cfg.init()
from orangecanvas.registry import WidgetRegistry
from orangecanvas.scheme import Scheme
from orangecanvas.scheme.readwrite import scheme_load
from orangecanvas.canvas.scene import CanvasScene
src, out, scale = sys.argv[1], sys.argv[2], float(sys.argv[3]) if len(sys.argv) > 3 else 2.5
reg = WidgetRegistry()
disc = cfg.widget_discovery(reg)
disc.run(cfg.widgets_entry_points())
sch = Scheme()
with open(src, 'rb') as f:
    scheme_load(sch, f, registry=reg)
scene = CanvasScene()
scene.set_registry(reg)
scene.set_scheme(sch)
scene.clearSelection()
for n in scene.node_items: n.setSelected(False)
r = scene.itemsBoundingRect().adjusted(-20, -20, 20, 20)
img = QImage(int(r.width() * scale), int(r.height() * scale), QImage.Format_ARGB32)
img.fill(QColor('white'))
p = QPainter(img); p.setRenderHint(QPainter.Antialiasing); p.setRenderHint(QPainter.TextAntialiasing)
scene.render(p, QRectF(0, 0, img.width(), img.height()), r)
p.end()
print('OK', img.save(out), img.width(), img.height(), len(sch.nodes), len(sch.links))
