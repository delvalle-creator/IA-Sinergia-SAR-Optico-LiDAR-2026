# -*- coding: utf-8 -*-
"""
NISAR GCOV Reader - complemento QGIS independiente.

Aislamiento: todo vive en la carpeta 'nisar_gcov_reader' con nombres de clase
propios. No registra proveedores de datos, no toca variables de entorno ni
opciones de GDAL, y no importa ni modifica ningun otro complemento (incluido
el lector de productos NISAR de Nivel 1).
"""

import os
import traceback

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import (
    QAction, QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QLineEdit, QPushButton, QComboBox, QListWidget, QListWidgetItem,
    QCheckBox, QProgressBar, QFileDialog, QMessageBox, QApplication, QSpinBox,
    QDialogButtonBox, QGroupBox
)
from qgis.core import (QgsProject, QgsRasterLayer, QgsMessageLog, Qgis,
                       QgsContrastEnhancement, QgsRasterMinMaxOrigin)

from . import nisar_gcov_core as core

PLUGIN_NAME = "NISAR GCOV"
LOG_TAG = "NISAR GCOV"


class NisarGcovDialog(QDialog):

    def __init__(self, iface, parent=None):
        QDialog.__init__(self, parent)
        self.iface = iface
        self.grids = []
        self._cancel = False
        self.setWindowTitle("NISAR GCOV - abrir producto de Nivel 2")
        self.setMinimumWidth(620)
        self._build()

    # ---------------------------------------------------------------- UI
    def _build(self):
        lay = QVBoxLayout(self)

        # archivo
        g1 = QGridLayout()
        g1.addWidget(QLabel("Archivo GCOV (.h5):"), 0, 0)
        self.edFile = QLineEdit()
        g1.addWidget(self.edFile, 0, 1)
        btn = QPushButton("Examinar...")
        btn.clicked.connect(self.pick_file)
        g1.addWidget(btn, 0, 2)

        g1.addWidget(QLabel("Grilla:"), 1, 0)
        self.cbGrid = QComboBox()
        self.cbGrid.currentIndexChanged.connect(self.fill_bands)
        g1.addWidget(self.cbGrid, 1, 1, 1, 2)
        lay.addLayout(g1)

        self.lbInfo = QLabel("-")
        self.lbInfo.setWordWrap(True)
        lay.addWidget(self.lbInfo)

        # bandas
        gb = QGroupBox("Capas a abrir")
        v = QVBoxLayout(gb)
        self.lst = QListWidget()
        self.lst.setSelectionMode(QListWidget.NoSelection)
        v.addWidget(self.lst)
        h = QHBoxLayout()
        b1 = QPushButton("Solo polarizaciones")
        b1.clicked.connect(lambda: self.check_all(pol_only=True))
        b2 = QPushButton("Todas")
        b2.clicked.connect(lambda: self.check_all(pol_only=False))
        b3 = QPushButton("Ninguna")
        b3.clicked.connect(lambda: self.check_all(none=True))
        for b in (b1, b2, b3):
            h.addWidget(b)
        h.addStretch()
        v.addLayout(h)
        lay.addWidget(gb)

        # opciones
        gb2 = QGroupBox("Opciones")
        g2 = QGridLayout(gb2)
        self.chDb = QCheckBox("Convertir gamma0 a decibeles (10*log10) en los terminos de la diagonal")
        self.chDb.setChecked(True)
        g2.addWidget(self.chDb, 0, 0, 1, 3)

        g2.addWidget(QLabel("Formato de salida:"), 1, 0)
        self.cbFmt = QComboBox()
        self.cbFmt.addItem("GeoTIFF (un archivo por capa) - QGIS y SNAP", "gtiff")
        self.cbFmt.addItem("BEAM-DIMAP (.dim) - formato nativo de SNAP", "dimap")
        self.cbFmt.addItem("Matriz C3 para SNAP (solo cuadripolar)", "c3")
        g2.addWidget(self.cbFmt, 1, 1, 1, 2)

        g2.addWidget(QLabel("Submuestreo:"), 2, 0)
        self.spStep = QSpinBox()
        self.spStep.setRange(1, 50)
        self.spStep.setValue(1)
        self.spStep.setPrefix("1 de cada ")
        self.spStep.setSuffix("  celdas  (1 = resolucion completa)")
        self.spStep.valueChanged.connect(self.update_estimate)
        g2.addWidget(self.spStep, 2, 1, 1, 2)

        g2.addWidget(QLabel("Recorte lon/lat:"), 3, 0)
        self.edBbox = QLineEdit()
        self.edBbox.setPlaceholderText(
            "opcional -  minlon,minlat,maxlon,maxlat   ej: -71.85,-43.25,-71.05,-42.35")
        g2.addWidget(self.edBbox, 3, 1, 1, 2)

        g2.addWidget(QLabel("Carpeta de salida:"), 4, 0)
        self.edOut = QLineEdit()
        g2.addWidget(self.edOut, 4, 1)
        b4 = QPushButton("...")
        b4.clicked.connect(self.pick_out)
        g2.addWidget(b4, 4, 2)

        self.chLoad = QCheckBox("Cargar los resultados en el proyecto de QGIS")
        self.chLoad.setChecked(True)
        g2.addWidget(self.chLoad, 5, 0, 1, 3)
        lay.addWidget(gb2)

        self.lbEstim = QLabel("")
        lay.addWidget(self.lbEstim)

        self.bar = QProgressBar()
        self.bar.setValue(0)
        lay.addWidget(self.bar)
        self.lbStatus = QLabel("")
        lay.addWidget(self.lbStatus)

        bb = QDialogButtonBox()
        self.btnRun = bb.addButton("Procesar", QDialogButtonBox.AcceptRole)
        self.btnClose = bb.addButton("Cerrar", QDialogButtonBox.RejectRole)
        self.btnRun.clicked.connect(self.run)
        self.btnClose.clicked.connect(self.on_close)
        lay.addWidget(bb)

    def on_close(self):
        self._cancel = True
        self.reject()

    # ------------------------------------------------------------ acciones
    def pick_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar producto NISAR GCOV", "",
            "NISAR GCOV (*.h5 *.hdf5 *.he5);;Todos (*.*)")
        if path:
            self.edFile.setText(path)
            self.load_file(path)

    def pick_out(self):
        d = QFileDialog.getExistingDirectory(self, "Carpeta de salida", self.edOut.text())
        if d:
            self.edOut.setText(d)

    def load_file(self, path):
        self.cbGrid.clear()
        self.lst.clear()
        self.grids = []
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            self.grids = core.open_grids(path)
        except Exception as e:
            QApplication.restoreOverrideCursor()
            QMessageBox.critical(self, PLUGIN_NAME,
                                 u"No se pudo leer el archivo:\n\n%s" % e)
            QgsMessageLog.logMessage(traceback.format_exc(), LOG_TAG, Qgis.Critical)
            return
        QApplication.restoreOverrideCursor()

        for g in self.grids:
            self.cbGrid.addItem("%s  (%d x %d)" % (g.path, g.nx, g.ny))
        base = os.path.splitext(os.path.basename(path))[0]
        self.edOut.setText(os.path.join(os.path.dirname(path), base + "_gcov"))
        self.fill_bands()

    def current_grid(self):
        i = self.cbGrid.currentIndex()
        if 0 <= i < len(self.grids):
            return self.grids[i]
        return None

    def fill_bands(self):
        self.lst.clear()
        g = self.current_grid()
        if g is None:
            self.lbInfo.setText("-")
            return
        gt = g.geotransform
        self.lbInfo.setText(
            u"CRS: EPSG:%s    pixel: %.1f m    origen: %.1f , %.1f    tamano: %d x %d" %
            (g.epsg if g.epsg else u"no declarado en el producto",
             gt[1], gt[0], gt[3], g.nx, g.ny) +
            (u"\nProducto cuadripolar: se puede exportar la matriz C3 para SNAP."
             if core.c3_disponible(g) else u""))
        self._c3 = core.c3_disponible(g)
        for b in g.bands:
            etiqueta = b.name
            if b.is_aux:
                etiqueta += "   [auxiliar]"
            if b.is_complex:
                etiqueta += "   [complejo: se escribe como real + imag]"
            it = QListWidgetItem(etiqueta)
            it.setFlags(it.flags() | Qt.ItemIsUserCheckable)
            it.setCheckState(Qt.Checked if (b.is_pol and not b.is_complex)
                             else Qt.Unchecked)
            it.setData(Qt.UserRole, b.name)
            self.lst.addItem(it)
        try:
            self.lst.itemChanged.disconnect()
        except Exception:
            pass
        self.lst.itemChanged.connect(lambda *_: self.update_estimate())
        self.update_estimate()

    def update_estimate(self):
        g = self.current_grid()
        if g is None:
            return
        step = self.spStep.value()
        nxo, nyo, gto = core.out_geometry(g, step)
        n = max(1, len(self.selected_bands()))
        mb = nxo * nyo * 4.0 * n / (1024.0 * 1024.0)
        self.lbEstim.setText(
            u"Salida: %d x %d px, pixel %.1f m, %d capa(s)  ~%.0f MB sin comprimir"
            % (nxo, nyo, abs(gto[1]), n, mb))

    def check_all(self, pol_only=False, none=False):
        g = self.current_grid()
        if g is None:
            return
        for i in range(self.lst.count()):
            it = self.lst.item(i)
            b = g.band(it.data(Qt.UserRole))
            if none:
                st = Qt.Unchecked
            elif pol_only:
                st = Qt.Checked if (b and b.is_pol) else Qt.Unchecked
            else:
                st = Qt.Checked
            it.setCheckState(st)
        self.update_estimate()

    def selected_bands(self):
        out = []
        for i in range(self.lst.count()):
            it = self.lst.item(i)
            if it.checkState() == Qt.Checked:
                out.append(it.data(Qt.UserRole))
        return out

    def _progress(self, frac, msg):
        self.bar.setValue(int(frac * 100))
        self.lbStatus.setText(msg)
        QApplication.processEvents()
        return not self._cancel

    def run(self):
        path = self.edFile.text().strip()
        g = self.current_grid()
        names = self.selected_bands()
        if not path or g is None:
            QMessageBox.warning(self, PLUGIN_NAME, u"Elegi primero un archivo GCOV.")
            return
        if not names:
            QMessageBox.warning(self, PLUGIN_NAME, u"No hay ninguna capa marcada.")
            return
        outdir = self.edOut.text().strip()
        if not outdir:
            QMessageBox.warning(self, PLUGIN_NAME, u"Indica una carpeta de salida.")
            return

        txt = self.edBbox.text().strip()
        if txt:
            try:
                vals = [float(v) for v in txt.replace(";", ",").split(",")]
                if len(vals) != 4:
                    raise ValueError("hacen falta cuatro numeros")
                core.recortar_lonlat(g, *vals)
            except Exception as e:
                QMessageBox.warning(self, PLUGIN_NAME,
                                    u"Recorte invalido:\n\n%s" % e)
                return
        else:
            g.col0 = g.row0 = 0
            g.ncols, g.nrows = g.nx, g.ny

        self._cancel = False
        self.btnRun.setEnabled(False)
        fmt = self.cbFmt.currentData()
        try:
            if fmt == "c3":
                dim = core.export_c3(path, g, outdir, step=self.spStep.value(),
                                     progress=self._progress)
                written = []
                if dim:
                    base = os.path.splitext(dim)[0] + ".data"
                    written = [os.path.join(base, f) for f in sorted(os.listdir(base))
                               if f.lower().endswith(".img")]
                    msg = u"Matriz C3 escrita:\n%s\n\nAbrila en SNAP con File > Open Product." % dim
                else:
                    msg = u"Proceso cancelado."
            elif fmt == "dimap":
                dim = core.export_dimap(path, g, names, outdir,
                                        to_db=self.chDb.isChecked(),
                                        step=self.spStep.value(),
                                        progress=self._progress)
                written = []
                if dim:
                    base = os.path.splitext(dim)[0] + ".data"
                    written = [os.path.join(base, f) for f in sorted(os.listdir(base))
                               if f.lower().endswith(".img")]
                    msg = u"Producto SNAP escrito:\n%s" % dim
                else:
                    msg = u"Proceso cancelado."
            else:
                written = core.export_bands(path, g, names, outdir,
                                            to_db=self.chDb.isChecked(),
                                            step=self.spStep.value(),
                                            progress=self._progress)
                msg = u"%d archivo(s) escritos en:\n%s" % (len(written), outdir)
        except Exception as e:
            self.btnRun.setEnabled(True)
            QMessageBox.critical(self, PLUGIN_NAME, u"Error durante la conversion:\n\n%s" % e)
            QgsMessageLog.logMessage(traceback.format_exc(), LOG_TAG, Qgis.Critical)
            return

        if self.chLoad.isChecked():
            for f in written:
                lyr = QgsRasterLayer(f, os.path.splitext(os.path.basename(f))[0])
                if lyr.isValid():
                    # sin esto la capa se ve lavada: el minimo absoluto de una
                    # imagen de radar es un valor extremo aislado que aplasta
                    # todo el resto del histograma
                    try:
                        lyr.setContrastEnhancement(
                            QgsContrastEnhancement.StretchToMinimumMaximum,
                            QgsRasterMinMaxOrigin.CumulativeCut)
                    except Exception:
                        pass
                    QgsProject.instance().addMapLayer(lyr)
                else:
                    QgsMessageLog.logMessage(u"Capa invalida: %s" % f, LOG_TAG, Qgis.Warning)

        self.bar.setValue(100)
        self.lbStatus.setText(u"Listo.")
        self.btnRun.setEnabled(True)
        QMessageBox.information(self, PLUGIN_NAME, msg)


class NisarGcovReaderPlugin(object):

    def __init__(self, iface):
        self.iface = iface
        self.action = None
        self.dlg = None

    def initGui(self):
        icon_path = os.path.join(os.path.dirname(__file__), "icon.png")
        icon = QIcon(icon_path) if os.path.exists(icon_path) else QIcon()
        self.action = QAction(icon, u"Abrir producto NISAR GCOV...",
                              self.iface.mainWindow())
        self.action.triggered.connect(self.show_dialog)
        # se registra en los dos menus: en algunas versiones de QGIS el submenu
        # de Raster no se dibuja, y el de Complementos siempre esta disponible
        self.iface.addPluginToMenu(u"&" + PLUGIN_NAME, self.action)
        try:
            self.iface.addPluginToRasterMenu(u"&" + PLUGIN_NAME, self.action)
        except Exception:
            pass
        self.iface.addToolBarIcon(self.action)

    def unload(self):
        if self.action:
            for quitar in (self.iface.removePluginMenu,
                           self.iface.removePluginRasterMenu):
                try:
                    quitar(u"&" + PLUGIN_NAME, self.action)
                except Exception:
                    pass
            self.iface.removeToolBarIcon(self.action)
            self.action = None

    def show_dialog(self):
        if self.dlg is None:
            self.dlg = NisarGcovDialog(self.iface, self.iface.mainWindow())
        self.dlg.show()
        self.dlg.raise_()
        self.dlg.activateWindow()
