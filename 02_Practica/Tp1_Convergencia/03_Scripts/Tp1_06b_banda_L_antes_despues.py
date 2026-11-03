# -*- coding: utf-8 -*-
r"""Tp1, B_CONCORDIA: la banda L (SAOCOM y ALOS-2) antes, durante y después de la crecida de 2023.

Paso 6b del Tp1 (26/10/2026; revisado el 27/10/2026). Lee los recortes que ya están en disco; no descarga nada.

INSUMO QUE YA VIENE HECHO: la máscara de agua de crecida de banda C del 04/11/2023 y la del óptico
(MNDWI) del mismo día salen del Tp6 (Tp6_Inundaciones/05_Resultados/02_Rasters). El alumno las construye
recién el miércoles, en el Tp6; el lunes las usa tal como vienen hechas. Si faltan, el programa
lo dice y termina sin error de Python.

Qué hace
  1. Describe cada escena de banda L sobre el sitio: haz, pasada, mirada, incidencia, píxeles con dato,
     medianas de gamma0 por polarización en tierra y en el agua permanente.
  2. Arma los pares antes-después de una misma geometría:
       banda L  SAOCOM TNA  10/10/2023 -> 11/11/2023 (32 días, mismo haz y misma órbita, sitio entero)
       banda L  SAOCOM TNB  31/10/2023 -> 08/11/2023 (8 días, mismo haz, mitad oeste del sitio)
       banda C  Sentinel-1  23/10/2023 -> 04/11/2023 (12 días, órbita 68)
     y mide el cambio (después menos antes, en dB) por zona: agua permanente (JRC >= 90 %),
     agua de crecida de banda C del 04/11 (Tp6), agua de crecida del óptico del 04/11 que la banda C
     no marcó (Tp6, MNDWI), tierra y clases de MapBiomas 2023.
     Para la banda C, la zona «agua de crecida de banda C» es circular (sale de su propia máscara);
     la zona del óptico no lo es para ninguna de las dos bandas.
  3. Figuras (RGB copolarizada-cruzada-cociente con los rangos fijos del curso; antes y después sobre el río;
     mapas de cambio) y una muestra para Orange.

Uso (Miniforge Prompt, entorno sar, en Tp1_Convergencia\03_Scripts):
    python Tp1_06b_banda_L_antes_despues.py
    python Tp1_06b_banda_L_antes_despues.py --base <otra carpeta 02_Practica>
"""
import argparse
import csv
import datetime as dt
import os
import sys

import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.warp import reproject
from scipy import ndimage

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.colors import ListedColormap  # noqa: E402
from matplotlib.patches import Patch, Rectangle  # noqa: E402

# ---------------------------------------------------------------- parámetros (se pueden cambiar en la orden)
ap = argparse.ArgumentParser(description="Banda L antes y durante la crecida de 2023 en B_CONCORDIA")
ap.add_argument("--base", default=r"D:\CURSOS_CEREGEO_2026\02_Practica",
                help="carpeta 02_Practica del curso")
ap.add_argument("--muestra", type=int, default=20000, help="píxeles al azar para Orange")
ap.add_argument("--semilla", type=int, default=2023, help="semilla fija del sorteo de la muestra")
ap.add_argument("--nodata_gamma", type=float, default=0.0,
                help="valor de γ0 que se toma como sin dato si el GeoTIFF no lo declara (por defecto 0)")
args = ap.parse_args()
B = args.base
TP1 = os.path.join(B, "Tp1_Convergencia")
TP6 = os.path.join(B, "Tp6_Inundaciones")
SAO = os.path.join(TP1, "02_Subsets_SNAP_QGIS", "SAOCOM_gamma0", "QGIS_GeoTIFF")
ALO = os.path.join(TP1, "02_Subsets_SNAP_QGIS", "ALOS2_gamma0", "QGIS_GeoTIFF")
G6 = os.path.join(TP6, "02_Subsets_SNAP_QGIS", "QGIS_GeoTIFF")
R6 = os.path.join(TP6, "05_Resultados", "02_Rasters")
TAB = os.path.join(TP1, "05_Resultados", "04_Tablas")
GRA = os.path.join(TP1, "05_Resultados", "05_Graficos", "Figuras_del_desarrollo")
CTL = os.path.join(TP1, "05_Resultados", "06_Control_calidad")
ORA = os.path.join(TP1, "08_Orange", "datos")
for d in (TAB, GRA, CTL, ORA):
    os.makedirs(d, exist_ok=True)

LOG = open(os.path.join(CTL, "Tp1_06b_banda_L_antes_despues.log"), "w", encoding="utf-8")

# Los insumos del Tp6 (YA VIENE HECHO): si faltan, se avisa con palabras y se termina.
FALTAN = [r for r in (os.path.join(TP6, "05_Resultados", "02_Rasters", "B_agua_por_sensor_20231104_20m.tif"),
                      os.path.join(TP6, "05_Resultados", "02_Rasters", "B_extension_y_duracion_C_20m.tif"))
          if not os.path.exists(r)]
if FALTAN:
    msg = ("Falta la máscara de agua del Tp6: este paso usa un insumo YA VIENE HECHO.\n"
           "No se encontró:\n  " + "\n  ".join(FALTAN))
    print(msg)
    LOG.write(msg + "\n")
    LOG.close()
    sys.exit(1)


def p(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    LOG.write(s + "\n")
    LOG.flush()


p("Tp1_06b_banda_L_antes_despues.py  %s" % dt.datetime.now().strftime("%d/%m/%Y %H:%M"))
p("Base: %s" % B)

# ---------------------------------------------------------------- grilla común (la del Tp6, 20 m, EPSG:32721)
REF = os.path.join(R6, "B_agua_por_sensor_20231104_20m.tif")
with rasterio.open(REF) as r:
    T, CRS, H, W = r.transform, r.crs, r.height, r.width
    agua_c = r.read(1)
    agua_opt = r.read(2)
PIX_HA = abs(T.a * T.e) / 1e4


def leer(ruta, banda=1, metodo=Resampling.average, nodata=None, cero_sin_dato=False):
    """Lleva una banda a la grilla común. cero_sin_dato=True (γ0): si el GeoTIFF no declara su valor
    sin dato, los valores iguales a --nodata_gamma (0 por defecto) no entran al promedio del remuestreo."""
    out = np.full((H, W), np.nan, dtype="float32")
    with rasterio.open(ruta) as r:
        a = r.read(banda).astype("float32")
        nd = r.nodata if nodata is None else nodata
        if nd is not None and not np.isnan(nd):
            a[a == nd] = np.nan
        if cero_sin_dato:
            a[a == args.nodata_gamma] = np.nan
        reproject(a, out, src_transform=r.transform, src_crs=r.crs, dst_transform=T, dst_crs=CRS,
                  resampling=metodo, src_nodata=np.nan, dst_nodata=np.nan)
    return out


def db(x):
    with np.errstate(divide="ignore", invalid="ignore"):
        return 10 * np.log10(np.where(x > 0, x, np.nan))


# ---------------------------------------------------------------- capas de referencia
jrc = leer(os.path.join(G6, "B_CONCORDIA_JRC_GSW_ocurrencia.tif"), metodo=Resampling.nearest)
with rasterio.open(os.path.join(G6, "B_CONCORDIA_MapBiomas_cobertura_1985_2025.tif")) as r:
    ib = list(r.descriptions).index("cobertura_2023") + 1
mb = leer(os.path.join(G6, "B_CONCORDIA_MapBiomas_cobertura_1985_2025.tif"), banda=ib,
          metodo=Resampling.nearest, nodata=0)
with rasterio.open(os.path.join(R6, "B_extension_y_duracion_C_20m.tif")) as r:
    ref_seca = r.read(3)
perm = jrc >= 90
crecida_c = (agua_c == 1)
crecida_opt_sin_c = (agua_opt == 1) & ~crecida_c & ~perm   # agua del óptico que la C no marcó
tierra = (~perm) & (~crecida_c) & (ref_seca != 1) & ~(jrc >= 10)

CLASES = {3: "Bosques cerrados", 6: "Bosques inundables", 9: "Silvicultura", 11: "Herbáceas inundables",
          12: "Herbáceas", 15: "Pastura", 19: "Cultivos temporarios", 36: "Cultivos perennes",
          24: "Áreas urbanas", 33: "Ríos y lagunas"}

# ---------------------------------------------------------------- escenas
SC = [  # clave, sensor, fecha, hora, haz, rol
    ("L_20231010", "SAOCOM-1B", "10/10/2023", "21:16", "TNA", "antes"),
    ("L_20231031", "SAOCOM-1B", "31/10/2023", "21:10", "TNB", "durante"),
    ("L_20231108", "SAOCOM-1A", "08/11/2023", "21:13", "TNB", "durante"),
    ("L_20231111", "SAOCOM-1B", "11/11/2023", "21:16", "TNA", "durante"),
    ("L_20260916", "SAOCOM-1B", "16/09/2026", "21:16", "TNA", "tres años después"),
]
INC = {"TNA": "17,6 a 27,3°", "TNB": "27,2 a 35,5°"}
L = {}
for k, sen, f, h, haz, rol in SC:
    d = {}
    for pol in ("HH", "HV", "VV"):
        d[pol] = leer(os.path.join(SAO, "B_CONCORDIA_SAOCOM_%s_QP_gamma0_Gamma0_%s.tif" % (k, pol)),
                      cero_sin_dato=True)
    L[k] = d
ALOS = {pol: leer(os.path.join(ALO, "B_CONCORDIA_ALOS2_L_20231116_WBD_gamma0_Gamma0_%s.tif" % pol),
                  cero_sin_dato=True)
        for pol in ("HH", "HV")}
C = {}
for f in ("20231023", "20231104"):
    ruta = os.path.join(G6, "B_CONCORDIA_S1_C_%s.tif" % f)
    C[f] = {"VV": leer(ruta, 1, cero_sin_dato=True), "VH": leer(ruta, 2, cero_sin_dato=True)}

# franja de ruido del borde del haz en los TNB: se apartan los 2,5 km del borde con dato
def sin_borde(valido, km=2.5):
    dist = ndimage.distance_transform_edt(valido)
    return valido & (dist * abs(T.a) > km * 1000)


# ---------------------------------------------------------------- 1. escenas
def med(a, m):
    v = a[m & np.isfinite(a)]
    return float(np.median(v)) if v.size else float("nan")


filas = []
p("\n1. Escenas de banda L sobre B_CONCORDIA (medianas de gamma0 en dB)")
p("%-11s %-10s %-4s %-12s %7s  %18s  %18s" % ("sensor", "fecha", "haz", "incidencia", "%sitio",
                                             "tierra HH/HV/VV", "agua perm. HH/HV/VV"))
todas = [(SC[i][1], SC[i][2], SC[i][3], SC[i][4], INC[SC[i][4]], SC[i][5], L[SC[i][0]]) for i in range(5)]
todas.insert(4, ("ALOS-2 PALSAR-2", "16/11/2023", "15:11", "ScanSAR WBD", "39 a 42°", "durante",
                 {"HH": ALOS["HH"], "HV": ALOS["HV"], "VV": np.full((H, W), np.nan, "float32")}))
for sen, f, h, haz, inc, rol, d in todas:
    val = np.isfinite(d["HH"])
    pc = 100 * val.mean()
    t = [med(db(d[x]), tierra) for x in ("HH", "HV", "VV")]
    w = [med(db(d[x]), perm) for x in ("HH", "HV", "VV")]
    p("%-11s %-10s %-4s %-12s %6.1f   %5.1f %5.1f %5.1f   %5.1f %5.1f %5.1f" % (sen[:11], f, haz[:4], inc, pc, *t, *w))
    filas.append({"sensor": sen, "fecha": f, "hora_utc": h, "haz": haz, "pasada": "descendente",
                  "mirada": "derecha (al oeste)", "incidencia": inc, "momento": rol,
                  "pixeles_validos_%": round(pc, 1),
                  "tierra_HH_db": round(t[0], 1), "tierra_HV_db": round(t[1], 1),
                  "tierra_VV_db": "" if np.isnan(t[2]) else round(t[2], 1),
                  "agua_perm_HH_db": round(w[0], 1), "agua_perm_HV_db": round(w[1], 1),
                  "agua_perm_VV_db": "" if np.isnan(w[2]) else round(w[2], 1),
                  "contraste_HH_tierra_agua_db": round(t[0] - w[0], 1)})
with open(os.path.join(TAB, "B_CONCORDIA_banda_L_escenas.csv"), "w", newline="", encoding="utf-8") as fh:
    wr = csv.DictWriter(fh, fieldnames=list(filas[0].keys()))
    wr.writeheader()
    wr.writerows(filas)

# ---------------------------------------------------------------- 2. pares antes-después
mask_tnb = sin_borde(np.isfinite(L["L_20231031"]["HH"]) & np.isfinite(L["L_20231108"]["HH"]))
PARES = [
    ("L", "SAOCOM TNA", "10/10/2023", "11/11/2023", 32, ("HH", "HV", "VV"),
     lambda pol: (L["L_20231010"][pol], L["L_20231111"][pol]), None),
    ("L", "SAOCOM TNB", "31/10/2023", "08/11/2023", 8, ("HH", "HV", "VV"),
     lambda pol: (L["L_20231031"][pol], L["L_20231108"][pol]), mask_tnb),
    ("C", "Sentinel-1 órbita 68", "23/10/2023", "04/11/2023", 12, ("VV", "VH"),
     lambda pol: (C["20231023"][pol], C["20231104"][pol]), None),
]
ZONAS = [("agua permanente (JRC >= 90 %)", perm), ("agua de crecida de banda C, 04/11 (Tp6)", crecida_c),
         ("agua del óptico 04/11 sin la de C (Tp6)", crecida_opt_sin_c),
         ("tierra (sin agua)", tierra)]
ZONAS += [(("MapBiomas 2023: " + n), (mb == c) & ~crecida_c & ~perm) for c, n in CLASES.items()]
filas2 = []
DELTA = {}
p("\n2. Pares antes-después (cambio = después - antes, mediana en dB; n = píxeles de 20 m)")
for banda, sen, f0, f1, dias, pols, fn, extra in PARES:
    p("  %s  %s  %s -> %s (%d días)" % (banda, sen, f0, f1, dias))
    for pol in pols:
        a0, a1 = fn(pol)
        dd = db(a1) - db(a0)
        if extra is not None:
            dd = np.where(extra, dd, np.nan)
        DELTA[(sen, pol)] = dd
        gen = med(dd, tierra)
        for zn, zm in ZONAS:
            v = dd[zm & np.isfinite(dd)]
            if v.size < 50:
                continue
            q25, q50, q75 = np.percentile(v, [25, 50, 75])
            filas2.append({"banda": banda, "sensor": sen, "antes": f0, "despues": f1, "dias": dias, "pol": pol,
                           "zona": zn, "n_pixeles": int(v.size), "cambio_mediano_db": round(float(q50), 2),
                           "p25_db": round(float(q25), 2), "p75_db": round(float(q75), 2),
                           "cambio_menos_general_db": round(float(q50 - gen), 2)})
            if pol in ("HH", "VV") and not zn.startswith("MapBiomas"):
                p("     %-3s %-42s n=%8d  mediana %+5.1f dB (p25 %+5.1f, p75 %+5.1f)" % (pol, zn, v.size, q50, q25, q75))
with open(os.path.join(TAB, "B_CONCORDIA_antes_despues_por_zona.csv"), "w", newline="", encoding="utf-8") as fh:
    wr = csv.DictWriter(fh, fieldnames=list(filas2[0].keys()))
    wr.writeheader()
    wr.writerows(filas2)


# ---------------------------------------------------------------- 4. figuras
RAN = {"co": (-25.0, 0.0), "cruz": (-32.0, -8.0), "coc": (0.0, 15.0)}  # rangos fijos del curso (armar_subsets.RANGOS_RGB)


def rgb(d, co="HH", cr="HV"):
    a, b = db(d[co]), db(d[cr])
    c = a - b
    out = np.zeros((H, W, 4), "float32")
    for i, (x, (lo, hi)) in enumerate(((a, RAN["co"]), (b, RAN["cruz"]), (c, RAN["coc"]))):
        out[..., i] = np.clip((x - lo) / (hi - lo), 0, 1)
    out[..., 3] = np.isfinite(a).astype("float32")
    out[~np.isfinite(out)] = 0
    return out


EXT = (T.c / 1000, (T.c + W * T.a) / 1000, (T.f + H * T.e) / 1000, T.f / 1000)
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11})
# Recorte del río frente a Concordia (UTM 21S, km)
ZX0, ZX1, ZY0, ZY1 = 393.0, 407.0, 6516.0, 6530.0


def ejes(ax, tit):
    ax.set_title(tit, fontsize=11)
    ax.set_xlabel("Este (km, UTM 21S)")
    ax.set_ylabel("Norte (km)")
    ax.set_facecolor("white")
    ax.tick_params(labelsize=9)


# (a) las seis escenas de banda L en RGB
fig, axs = plt.subplots(2, 3, figsize=(15, 11.2))
paneles = [("SAOCOM-1B, 10/10/2023, TNA\nantes de la crecida", rgb(L["L_20231010"])),
           ("SAOCOM-1B, 31/10/2023, TNB\ndurante (mitad oeste)", rgb(L["L_20231031"])),
           ("SAOCOM-1A, 08/11/2023, TNB\ndurante (mitad oeste)", rgb(L["L_20231108"])),
           ("SAOCOM-1B, 11/11/2023, TNA\ndurante, misma geometría que el 10/10", rgb(L["L_20231111"])),
           ("ALOS-2 PALSAR-2, 16/11/2023, ScanSAR\ndurante (otro sensor)", rgb(ALOS)),
           ("SAOCOM-1B, 16/09/2026, TNA\ntres años después", rgb(L["L_20260916"]))]
for ax, (t, im) in zip(axs.ravel(), paneles):
    ax.imshow(im, extent=EXT, interpolation="nearest")
    ax.add_patch(Rectangle((ZX0, ZY0), ZX1 - ZX0, ZY1 - ZY0, fill=False, ec="yellow", lw=1.5))
    ejes(ax, t)
fig.legend(handles=[Patch(color=(1, 0, 0), label="R = HH (-25 a 0 dB)"), Patch(color=(0, 1, 0), label="G = HV (-32 a -8 dB)"),
                    Patch(color=(0, 0, 1), label="B = HH/HV (0 a 15 dB)")],
           loc="lower center", ncol=3, frameon=False, fontsize=11)
fig.tight_layout(rect=(0, 0.04, 1, 1))
fig.savefig(os.path.join(GRA, "B_CONCORDIA_banda_L_seis_escenas_RGB.png"), dpi=150)
plt.close(fig)


# (b) antes y después sobre el río, banda C y banda L, mismo recorte
def recorte(im):
    c0 = int((ZX0 * 1000 - T.c) / T.a)
    c1 = int((ZX1 * 1000 - T.c) / T.a)
    r0 = int((ZY1 * 1000 - T.f) / T.e)
    r1 = int((ZY0 * 1000 - T.f) / T.e)
    return im[r0:r1, c0:c1]


def rgb_c(d):
    return rgb(d, "VV", "VH")


EXTZ = (ZX0, ZX1, ZY0, ZY1)
fig, axs = plt.subplots(2, 2, figsize=(12.5, 12.6))
for ax, (t, im) in zip(axs.ravel(), [
        ("Banda C, Sentinel-1, 23/10/2023 (antes)\nR = VV, G = VH, B = VV/VH", rgb_c(C["20231023"])),
        ("Banda C, Sentinel-1, 04/11/2023 (durante)\nR = VV, G = VH, B = VV/VH", rgb_c(C["20231104"])),
        ("Banda L, SAOCOM, 10/10/2023 (antes)\nR = HH, G = HV, B = HH/HV", rgb(L["L_20231010"])),
        ("Banda L, SAOCOM, 11/11/2023 (durante)\nR = HH, G = HV, B = HH/HV", rgb(L["L_20231111"]))]):
    ax.imshow(recorte(im), extent=EXTZ, interpolation="nearest")
    ejes(ax, t)
fig.tight_layout()
fig.savefig(os.path.join(GRA, "B_CONCORDIA_antes_despues_rio_C_y_L.png"), dpi=150)
plt.close(fig)

# (c) mapas de cambio: L HH (TNA) y C VV, más el agua de crecida de C del 04/11 como contorno
fig, axs = plt.subplots(1, 2, figsize=(15, 8.6))
cm = plt.get_cmap("RdBu_r")
for ax, (t, dd) in zip(axs, [("Banda L, SAOCOM TNA: HH 11/11 menos HH 10/10", DELTA[("SAOCOM TNA", "HH")]),
                             ("Banda C, Sentinel-1: VV 04/11 menos VV 23/10", DELTA[("Sentinel-1 órbita 68", "VV")])]):
    im = ax.imshow(dd, extent=EXT, cmap=cm, vmin=-8, vmax=8, interpolation="nearest")
    ax.contour(np.flipud(crecida_c.astype(float)), levels=[0.5], colors="black", linewidths=0.4,
               extent=EXT, origin="lower")
    ejes(ax, t)
cb = fig.colorbar(im, ax=axs, orientation="horizontal", fraction=0.05, pad=0.1, shrink=0.6)
cb.set_label("Cambio de retrodispersión, después menos antes (dB). Azul: baja (agua lisa nueva); rojo: sube. "
             "Contorno negro: agua de crecida de banda C del 04/11/2023 (Tp6).")
fig.savefig(os.path.join(GRA, "B_CONCORDIA_cambio_L_y_C.png"), dpi=150, bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------- 5. muestra para Orange
rng = np.random.default_rng(args.semilla)
ok = (np.isfinite(DELTA[("SAOCOM TNA", "HH")]) & np.isfinite(DELTA[("Sentinel-1 órbita 68", "VV")])
      & np.isin(mb, list(CLASES.keys())))
idx = np.flatnonzero(ok.ravel())
sel = rng.choice(idx, size=min(args.muestra, idx.size), replace=False)
# La muestra conserva las tres zonas del workflow Tp1_G (la zona del óptico está en la tabla por zona).
zona = np.where(perm, "agua permanente", np.where(crecida_c, "agua de crecida (C 04/11)", "tierra"))
cols = {
    "clase_mapbiomas_2023": np.vectorize(lambda c: CLASES.get(int(c), ""))(mb.ravel()[sel]),
    "zona": zona.ravel()[sel],
    "L_HH_antes_db": db(L["L_20231010"]["HH"]).ravel()[sel],
    "L_HH_despues_db": db(L["L_20231111"]["HH"]).ravel()[sel],
    "L_HV_antes_db": db(L["L_20231010"]["HV"]).ravel()[sel],
    "L_HV_despues_db": db(L["L_20231111"]["HV"]).ravel()[sel],
    "cambio_L_HH_db": DELTA[("SAOCOM TNA", "HH")].ravel()[sel],
    "cambio_L_HV_db": DELTA[("SAOCOM TNA", "HV")].ravel()[sel],
    "C_VV_antes_db": db(C["20231023"]["VV"]).ravel()[sel],
    "C_VV_despues_db": db(C["20231104"]["VV"]).ravel()[sel],
    "cambio_C_VV_db": DELTA[("Sentinel-1 órbita 68", "VV")].ravel()[sel],
    "cambio_C_VH_db": DELTA[("Sentinel-1 órbita 68", "VH")].ravel()[sel],
}
ruta_m = os.path.join(ORA, "B_CONCORDIA_antes_despues_muestra.csv")
with open(ruta_m, "w", newline="", encoding="utf-8") as fh:
    wr = csv.writer(fh)
    wr.writerow(list(cols.keys()))
    for i in range(sel.size):
        wr.writerow([cols[k][i] if isinstance(cols[k][i], str) else round(float(cols[k][i]), 2) for k in cols])
p("\n4. Muestra para Orange: %d píxeles al azar con clase de MapBiomas y los dos cambios -> %s" % (sel.size, ruta_m))
p("Tablas en %s; figuras en %s" % (TAB, GRA))
p("SIGUIENTE PASO: paso 7, Tp1_07_matriz_convergencia.py")
LOG.close()
