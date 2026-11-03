# -*- coding: utf-8 -*-
"""des_embeddings.py - Desarrollo del docente (22/10/2026): embeddings anuales AlphaEarth en los Tp1 a Tp7.

Uso:  python des_embeddings.py <Tp1|Tp2|Tp3|Tp5|Tp6|Tp7> [BASE] [rgb|pila] [--tierra_fuera]
      En el Tp6, --tierra_fuera evalua solo los pixeles fuera del agua (agregado el 27/10/2026).
      En el Tp2, el tercer argumento elige con que entra el radar al kNN (agregado el 27/10/2026):
        rgb  (por defecto, como antes): las nueve bandas de los RGB de 8 bits estirados por escena;
        pila: las bandas de la pila en dB (C SNAP VV y VH, L HH y HV del 30/09, P HH y VH), promediadas en
              lineal a la grilla de trabajo y estandarizadas. Conserva la escala fisica y el mismo tratamiento
              en todas las bandas. Las salidas llevan el sufijo _pila.
Salidas en 00_COMUN/09_Herramientas/desarrollo_docente/<Tp>/embeddings: figura PNG, tabla CSV y bitacora TXT.

Embeddings: 64 dimensiones int8; valor = signo(DN) * (DN/127,5)^2, -128 = sin dato. Se trabajan normalizados (norma 1):
la semejanza entre dos pixeles es el producto escalar (coseno). Clasificacion con pocas muestras: k vecinos mas cercanos
(k = 5) con 20 pixeles sorteados por clase (semilla 2026); se evalua en todos los demas pixeles.
"""
import os, sys, csv, re
import numpy as np
import rasterio
from rasterio.warp import reproject, Resampling
from rasterio.transform import Affine
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

# Argumentos posicionales (las opciones que empiezan con "--", como --tierra_fuera del Tp6, se leen aparte).
POS = [a for a in sys.argv[1:] if not a.startswith("--")]
TP = POS[0]
BASE = POS[1] if len(POS) > 1 else r"D:\CURSOS_CEREGEO_2026\02_Practica"
RADAR = POS[2] if len(POS) > 2 else "rgb"
OUT = os.path.join(BASE, "00_COMUN", "09_Herramientas", "desarrollo_docente", TP, "embeddings")
os.makedirs(OUT, exist_ok=True)
# Tipografía: por defecto la de siempre (serif). Con la variable de entorno DES_FUENTE=sans se usa la
# misma letra sin serifa que el resto de las figuras del Desarrollo (agregado el 27/10/2026).
if os.environ.get("DES_FUENTE", "serif") == "sans":
    plt.rcParams["font.family"] = ["DejaVu Sans", "Arial", "Liberation Sans"]
else:
    plt.rcParams["font.family"] = ["Times New Roman", "Liberation Serif", "DejaVu Serif"]
plt.rcParams["font.size"] = 12
RNG = np.random.default_rng(2026)
LOG = []
def log(s):
    print(s); LOG.append(s)

def ruta(*p): return os.path.join(BASE, *p)
def qg(tpdir, nombre): return ruta(tpdir, "02_Subsets_SNAP_QGIS", "QGIS_GeoTIFF", nombre)

def leer_emb(path, f):
    with rasterio.open(path) as s:
        H, W = s.height // f, s.width // f
        a = s.read(out_shape=(64, H, W), resampling=Resampling.nearest).astype(np.float32)
        T = s.transform * Affine.scale(s.width / W, s.height / H)
        crs = s.crs
    nod = (a == -128).any(0)
    v = np.sign(a) * (a / 127.5) ** 2
    n = np.linalg.norm(v, axis=0); n[n == 0] = 1
    v = v / n
    v[:, nod] = np.nan
    log("Embedding %s: %d x %d pixeles (cada %d de 10 m), %.1f %% con dato" % (os.path.basename(path), H, W, f, 100 * (~nod).mean()))
    return v, T, crs, (H, W)

def leer_rgb(path, f):
    with rasterio.open(path) as s:
        H, W = s.height // f, s.width // f
        a = s.read(out_shape=(min(3, s.count), H, W), resampling=Resampling.nearest).astype(np.float32)
    return np.dstack([np.clip(x / 255.0, 0, 1) for x in a])

def a_grilla(path, banda, T, crs, shape, rs=Resampling.nearest, nod=None, a_db=False):
    """a_db=True: la banda es potencia lineal; se promedia en lineal a la grilla y despues se pasa a dB."""
    o = np.full(shape, np.nan, np.float32)
    with rasterio.open(path) as s:
        a = s.read(banda).astype(np.float32)
        nd = s.nodata if nod is None else nod
        if nd is not None and not np.isnan(nd): a[a == nd] = np.nan
        if a_db:
            a[a <= 0] = np.nan
            rs = Resampling.average
        reproject(a, o, src_transform=s.transform, src_crs=s.crs, dst_transform=T, dst_crs=crs,
                  resampling=rs, src_nodata=np.nan, dst_nodata=np.nan)
    if a_db:
        o = (10 * np.log10(o)).astype(np.float32)
    return o

def paleta_mapbiomas():
    q = qg("Tp1_Convergencia", "B_CONCORDIA_MapBiomas_cobertura_1985_2025.qml")
    pal = {}
    for v, lab, col in re.findall(r'value="(\d+)" label="([^"]+)" color="(#[0-9A-Fa-f]{6})"', open(q, encoding="utf-8").read()):
        for a_, b_ in (("Herbaceas", "Herbáceas"), ("herbacea", "herbácea"), ("Rios", "Ríos"), ("oceano", "océano"), ("Areas", "Áreas"), ("areas", "áreas"), ("Vegetacion", "Vegetación"), ("No observado", "No observado")):
            lab = lab.replace(a_, b_)
        pal[int(v)] = (lab, col)
    return pal

def knn(Xall, Xs, ys, k=5, coseno=True):
    """Clase por voto de los k vecinos mas cercanos. Xall (N, d) sin NaN."""
    out = np.empty(len(Xall), ys.dtype)
    for i in range(0, len(Xall), 100000):
        b = Xall[i:i + 100000]
        if coseno:
            S = b @ Xs.T
        else:
            S = -((b[:, None, :] - Xs[None, :, :]) ** 2).sum(-1)
        idx = np.argpartition(-S, k, axis=1)[:, :k]
        u, inv = np.unique(ys, return_inverse=True)
        cnt = np.zeros((len(b), len(u)), np.int16)
        lab = inv[idx]
        for j in range(k):
            cnt[np.arange(len(b)), lab[:, j]] += 1
        out[i:i + len(b)] = u[np.argmax(cnt, axis=1)]
    return out

def sorteo(ref, clases, n=20):
    idx = []
    for c in clases:
        w = np.flatnonzero(ref == c)
        idx.append(RNG.choice(w, n, replace=False))
    return np.concatenate(idx)

def metricas(ref, pred, clases):
    filas = []
    oa = (ref == pred).mean()
    for c in clases:
        tp = ((pred == c) & (ref == c)).sum(); pp = (pred == c).sum(); rp = (ref == c).sum()
        pu = tp / pp if pp else np.nan; pr = tp / rp if rp else np.nan
        f1 = 2 * pu * pr / (pu + pr) if pu + pr else np.nan
        filas.append((c, rp, pr, pu, f1))
    return oa, filas

def guardar(nombre, fig):
    p = os.path.join(OUT, nombre); fig.savefig(p, dpi=170, bbox_inches="tight"); plt.close(fig); log("figura: " + p)

def tabla(nombre, encabezado, filas):
    p = os.path.join(OUT, nombre)
    with open(p, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f); w.writerow(encabezado); w.writerows(filas)
    log("tabla: " + p)

def escala_norte(ax, pix_m, largo_m=5000):
    """Barra de escala (en pixeles de pix_m metros) abajo a la izquierda y flecha de norte arriba a la derecha.
    Agregado el 27/10/2026: los mapas del curso llevan escala y norte."""
    from matplotlib.patches import Rectangle
    y1, y0 = ax.get_ylim(); x0, x1 = ax.get_xlim()
    L = largo_m / pix_m; X = x0 + 0.05 * (x1 - x0); Y = y1 - 0.05 * (y1 - y0); h = 0.015 * (y1 - y0)
    ax.add_patch(Rectangle((X, Y - h), L / 2, h, fc="k", ec="k", lw=0.5, zorder=10))
    ax.add_patch(Rectangle((X + L / 2, Y - h), L / 2, h, fc="w", ec="k", lw=0.5, zorder=10))
    ax.text(X + L / 2, Y - 1.8 * h, "%d km" % (largo_m // 1000), ha="center", va="bottom", fontsize=9, zorder=11)
    XN = x1 - 0.08 * (x1 - x0); YN = y0 + 0.06 * (y1 - y0)
    ax.annotate("", xy=(XN, YN), xytext=(XN, YN + 0.08 * (y1 - y0)), arrowprops=dict(arrowstyle="-|>", color="k", lw=1.2))
    ax.text(XN, YN - 0.01 * (y1 - y0), "N", ha="center", va="bottom", fontsize=9, fontweight="bold")
def mapa_clases(ax, arr, clases, pal, titulo):
    cols = [pal.get(int(c), (str(c), "#999999"))[1] for c in clases]
    cm = ListedColormap(cols); norm = BoundaryNorm(np.arange(len(clases) + 1) - 0.5, len(clases))
    m = np.full(arr.shape, np.nan)
    for i, c in enumerate(clases): m[arr == c] = i
    ax.imshow(m, cmap=cm, norm=norm, interpolation="nearest"); ax.set_title(titulo, fontsize=12); ax.axis("off")

def clasificacion(emb_path, anio_mb, mb_path, comp_feats, comp_nombre, tpdir, f, cp_path, titulo_sitio):
    E, T, crs, sh = leer_emb(emb_path, f)
    mb = a_grilla(mb_path, anio_mb - 1985 + 1, T, crs, sh)
    pal = paleta_mapbiomas()
    ok = np.isfinite(E).all(0) & np.isfinite(mb) & (mb > 0)
    comp = None
    if comp_feats is not None:
        comp = np.stack([a_grilla(p, b[0], T, crs, sh, a_db=True) if isinstance(b, tuple)
                         else a_grilla(p, b, T, crs, sh, Resampling.bilinear) for p, b in comp_feats])
        ok &= np.isfinite(comp).all(0)
    ref = mb[ok].astype(int)
    u, c = np.unique(ref, return_counts=True)
    clases = [int(x) for x, n in zip(u, c) if n >= 500 and x != 27]
    sel = np.isin(ref, clases); log("Clases MapBiomas %d con >= 500 pixeles: %s" % (anio_mb, ", ".join(pal.get(x, (str(x),))[0] for x in clases)))
    X = E[:, ok].T[sel]; R = ref[sel]
    si = sorteo(R, clases); resto = np.ones(len(R), bool); resto[si] = False
    pe = knn(X, X[si], R[si])
    oa_e, fe = metricas(R[resto], pe[resto], clases)
    log("Embeddings, kNN (k=5, 20 muestras por clase): exactitud global %.1f %%" % (100 * oa_e))
    filas = []; oa_c = None; pc = None
    if comp is not None:
        Z = comp[:, ok].T[sel]; Z = (Z - Z.mean(0)) / (Z.std(0) + 1e-6)
        Z /= np.linalg.norm(Z, axis=1, keepdims=True) + 1e-6
        pc = knn(Z, Z[si], R[si]); oa_c, fc = metricas(R[resto], pc[resto], clases)
        log("%s, kNN con las mismas muestras: exactitud global %.1f %%" % (comp_nombre, 100 * oa_c))
    for i, (cl, n, pr, pu, f1) in enumerate(fe):
        fila = [pal.get(cl, (str(cl),))[0], n, round(100 * pr, 1), round(100 * pu, 1), round(f1, 2)]
        if comp is not None: fila.append(round(fc[i][4], 2))
        filas.append(fila)
    enc = ["Clase MapBiomas", "Pixeles de referencia", "Exactitud del productor (%)", "Exactitud del usuario (%)", "F1 embeddings"] + (["F1 " + comp_nombre] if comp is not None else [])
    filas.append(["Exactitud global (%)", int((~np.isin(np.arange(len(R)), si)).sum()), "", "", round(100 * oa_e, 1)] + ([round(100 * oa_c, 1)] if comp is not None else []))
    tabla("%s_embeddings_knn%s.csv" % (TP, SUF), enc, filas)
    # mapas
    full_e = np.full(sh, np.nan); full_mb = np.full(sh, np.nan); okidx = np.flatnonzero(ok.ravel())[sel]
    full_e.ravel()[okidx] = pe; full_mb.ravel()[okidx] = R
    paneles = [("(a) Embeddings AlphaEarth %d, CP1-CP2-CP3" % anio_mb, "rgb"), ("(b) MapBiomas %d (referencia)" % anio_mb, full_mb), ("(c) kNN con embeddings (OA %.0f %%)" % (100 * oa_e), full_e)]
    if comp is not None:
        full_c = np.full(sh, np.nan); full_c.ravel()[okidx] = pc; paneles.append(("(d) kNN con %s (OA %s %%)" % (comp_nombre, ("%.0f" % (100 * oa_c))), full_c))
    fig, axs = plt.subplots(1, len(paneles), figsize=(4.6 * len(paneles), 5.2))
    for ax, (t, a) in zip(axs, paneles):
        if isinstance(a, str):
            ax.imshow(leer_rgb(cp_path, f)); ax.set_title(t, fontsize=12); ax.axis("off")
        else:
            mapa_clases(ax, a, clases, pal, t)
        escala_norte(ax, abs(T.a))
    fig.legend(handles=[Patch(color=pal[c][1], label=pal[c][0]) for c in clases if c in pal], loc="upper center",
               bbox_to_anchor=(0.5, 0.04), ncol=min(5, len(clases)), fontsize=10, frameon=False)
    guardar("%s_embeddings_knn%s.png" % (TP, SUF), fig)

SUF = "_pila" if (TP == "Tp2" and RADAR == "pila") else ""
def guardar_log():
    open(os.path.join(OUT, "%s_embeddings%s.log" % (TP, SUF)), "w", encoding="utf-8").write("\n".join(LOG) + "\n")

# ---------------------------------------------------------------- practicos
if TP == "Tp1":
    d = "Tp1_Convergencia"
    clasificacion(qg(d, "B_CONCORDIA_AlphaEarth_embeddings_2023_10m.tif"), 2023, qg(d, "B_CONCORDIA_MapBiomas_cobertura_1985_2025.tif"),
                  [(qg(d, "B_CONCORDIA_S2_20231104.tif"), b) for b in range(1, 11)], "Sentinel-2 04/11/2023", d, 4,
                  qg(d, "B_CONCORDIA_AlphaEarth_embeddings_2023_10m_CP1_CP2_CP3_RGB_8bit.tif"), "B_CONCORDIA, 2023")
elif TP == "Tp2":
    d = "Tp2_SAR_multibanda"; R = ruta(d, "05_Resultados", "02_Rasters")
    if RADAR == "pila":
        # bandas de la pila en lineal (numero de banda en A2_IBICUY_pila_gamma0_lineal.tif), pasadas a dB
        pila = ruta(d, "02_Subsets_SNAP_QGIS", "A2_IBICUY_pila_gamma0_lineal.tif")
        with rasterio.open(pila) as s_:
            desc = list(s_.descriptions)
        quiero = ["C_SNAP_gamma0_VV", "C_SNAP_gamma0_VH", "L_NISAR_gamma0_HH_20260930", "L_NISAR_gamma0_HV_20260930",
                  "P_BIOMASS_gamma0_HH", "P_BIOMASS_gamma0_VH"]
        feats = [(pila, (desc.index(q) + 1,)) for q in quiero]
        log("Radar desde la pila en dB (promediada en lineal a la grilla, estandarizada): " + ", ".join(quiero))
        nombre_radar = "radar C + L + P (pila en dB)"
    else:
        feats = [(os.path.join(R, n), b) for n in ("A2_IBICUY_RGB_C_S1.tif", "A2_IBICUY_RGB_L_NISAR_20260930.tif", "A2_IBICUY_RGB_P_BIOMASS.tif") for b in (1, 2, 3)]
        nombre_radar = "radar C + L + P"
    clasificacion(qg(d, "A2_IBICUY_AlphaEarth_embeddings_2025_10m.tif"), 2025, qg(d, "A2_IBICUY_MapBiomas_cobertura_1985_2025.tif"),
                  feats, nombre_radar, d, 2, qg(d, "A2_IBICUY_AlphaEarth_embeddings_2025_10m_CP1_CP2_CP3_RGB_8bit.tif"), "A2_IBICUY, 2025")
elif TP == "Tp3":
    d = "Tp3_Armonizacion"; f = 2
    E, T, crs, sh = leer_emb(qg(d, "A2_IBICUY_AlphaEarth_embeddings_2025_10m.tif"), f)
    mb = a_grilla(qg(d, "A2_IBICUY_MapBiomas_cobertura_1985_2025.tif"), 41, T, crs, sh)
    CL = 3
    pal = paleta_mapbiomas(); ok = np.isfinite(E).all(0) & np.isfinite(mb) & (mb > 0)
    ref = mb.copy(); ref[~ok] = np.nan
    w = np.flatnonzero((ref == CL).ravel()); s = RNG.choice(w, 20, replace=False)
    Ef = E.reshape(64, -1); proto = np.nanmean(Ef[:, s], axis=1); proto /= np.linalg.norm(proto)
    sim = np.full(sh, np.nan); sim.ravel()[ok.ravel()] = proto @ Ef[:, ok.ravel()]
    filas = []
    u, c = np.unique(ref[ok], return_counts=True)
    for x, n in zip(u, c):
        if n < 500: continue
        v = sim[ok & (ref == x)]
        filas.append([pal.get(int(x), (str(int(x)),))[0], int(n), round(float(np.median(v)), 3), round(float(np.percentile(v, 10)), 3), round(float(np.percentile(v, 90)), 3)])
    # umbral que mejor separa bosque cerrado del resto (F1)
    best = (0, 0)
    for t in np.arange(0.5, 0.99, 0.01):
        p = sim >= t; y = ref == CL
        tp = (p & y & ok).sum(); f1 = 2 * tp / ((p & ok).sum() + (y & ok).sum())
        if f1 > best[1]: best = (t, f1)
    filas.append(["Umbral de mejor F1 para bosque cerrado", "", round(best[0], 2), "F1", round(best[1], 2)])
    tabla("Tp3_embeddings_similitud.csv", ["Clase MapBiomas 2025", "Pixeles", "Semejanza mediana", "Percentil 10", "Percentil 90"], filas)
    log("Semejanza al prototipo de bosque cerrado (20 pixeles sorteados): umbral %.2f, F1 %.2f" % best)
    fig, axs = plt.subplots(1, 3, figsize=(15, 5.6))
    axs[0].imshow(leer_rgb(qg(d, "A2_IBICUY_AlphaEarth_embeddings_2025_10m_CP1_CP2_CP3_RGB_8bit.tif"), f)); axs[0].set_title("(a) Embeddings 2025, CP1-CP2-CP3"); axs[0].axis("off")
    im = axs[1].imshow(sim, cmap="viridis", vmin=0.3, vmax=1); axs[1].set_title("(b) Semejanza al bosque cerrado"); axs[1].axis("off")
    axs[1].contour(np.isfinite(sim) & (sim >= best[0]), levels=[0.5], colors="w", linewidths=0.4)
    cb = fig.colorbar(im, ax=axs[1], orientation="horizontal", fraction=0.05, pad=0.03); cb.set_label("coseno (1 = igual al prototipo)")
    mf = np.where(ok, (ref == CL).astype(float), np.nan)
    axs[2].imshow(mf, cmap=ListedColormap(["#eeeeee", pal[CL][1]]), vmin=0, vmax=1, interpolation="nearest"); axs[2].set_title("(c) MapBiomas 2025: bosques cerrados (monte)"); axs[2].axis("off")
    fig.legend(handles=[Patch(color=pal[CL][1], label=pal[CL][0]), Patch(color="#eeeeee", label="Otras clases"), Line2D([], [], color="k", lw=0.8, label="Contorno blanco en (b): semejanza >= %.2f" % best[0])],
               loc="upper center", bbox_to_anchor=(0.5, 0.03), ncol=3, frameon=False, fontsize=10)
    guardar("Tp3_embeddings_similitud.png", fig)
elif TP in ("Tp5", "Tp6"):
    if TP == "Tp5":
        d = "Tp5_Incendios"; f = 3
        E, T, crs, sh = leer_emb(qg(d, "A1_DELTA_QUEMAS_AlphaEarth_embeddings_2020_10m.tif"), f)
        ref = a_grilla(qg(d, "A1_DELTA_QUEMAS_MapBiomas_fuego_anual_1999_2025.tif"), 22, T, crs, sh, nod=255)
        lab1, lab0, nom = "Quemado 2020 (MapBiomas Fuego)", "No quemado", "quema"
        otro = a_grilla(ruta(d, "05_Resultados", "02_Rasters", "A1_variante_multisensor.tif"), 1, T, crs, sh)
        otro_nom = "variante multisensor del Tp5"
        cp = qg(d, "A1_DELTA_QUEMAS_AlphaEarth_embeddings_2020_10m_CP1_CP2_CP3_RGB_8bit.tif")
    else:
        d = "Tp6_Inundaciones"; f = 4
        E, T, crs, sh = leer_emb(qg(d, "B_CONCORDIA_AlphaEarth_embeddings_2023_10m.tif"), f)
        jrc = a_grilla(qg(d, "B_CONCORDIA_JRC_GSW_ocurrencia.tif"), 1, T, crs, sh)
        ref = np.full(sh, np.nan); ref[jrc >= 80] = 1; ref[jrc == 0] = 0
        lab1, lab0, nom = "Agua permanente (JRC >= 80 %)", "Tierra (JRC 0 %)", "agua"
        otro = a_grilla(ruta(d, "05_Resultados", "02_Rasters", "B_variante_C_20231104.tif"), 1, T, crs, sh)
        otro_nom = "agua en banda C del 04/11/2023 (Tp6)"
        cp = qg(d, "B_CONCORDIA_AlphaEarth_embeddings_2023_10m_CP1_CP2_CP3_RGB_8bit.tif")
    ok = np.isfinite(E).all(0) & np.isfinite(ref)
    R = ref[ok].astype(int); X = E[:, ok].T
    si = sorteo(R, [0, 1]); resto = np.ones(len(R), bool); resto[si] = False
    okall = np.isfinite(E).all(0); Xall = E[:, okall].T
    pall = knn(Xall, X[si], R[si])
    pm = np.full(sh, np.nan); pm[okall] = pall
    oa, fil = metricas(R[resto], pm[ok][resto], [0, 1])
    log("kNN %s con 20 + 20 muestras: exactitud global %.1f %% frente a la referencia" % (nom, 100 * oa))
    ev = (otro == 1); val = np.isfinite(otro) & okall
    acu = (pm[ev & okall] == 1).mean(); fuera = (pm[val & ~ev] == 1).mean()
    log("Dentro de la %s: %.1f %% marcado como %s por los embeddings; fuera: %.1f %%" % (otro_nom, 100 * acu, nom, 100 * fuera))
    if TP == "Tp6" and "--tierra_fuera" in sys.argv:
        # opcional (27/10/2026): comparar con la TIERRA fuera del agua permanente (JRC = 0), no con el resto
        # del sitio, que incluye el rio y el embalse
        tierra = val & ~ev & (jrc == 0)
        log("En la tierra fuera del agua permanente (JRC = 0): %.1f %% marcado como %s" % (100 * (pm[tierra] == 1).mean(), nom))
    filas = [[lab0, int((R[resto] == 0).sum()), round(100 * fil[0][2], 1), round(100 * fil[0][3], 1), round(fil[0][4], 2)],
             [lab1, int((R[resto] == 1).sum()), round(100 * fil[1][2], 1), round(100 * fil[1][3], 1), round(fil[1][4], 2)],
             ["Exactitud global (%)", "", "", "", round(100 * oa, 1)],
             ["%% de la %s marcado por los embeddings" % otro_nom, int(ev.sum()), "", "", round(100 * acu, 1)],
             ["%% del resto marcado por los embeddings" % (), int((val & ~ev).sum()), "", "", round(100 * fuera, 1)]]
    tabla("%s_embeddings_knn.csv" % TP, ["Clase", "Pixeles", "Exactitud del productor (%)", "Exactitud del usuario (%)", "F1 / valor"], filas)
    fig, axs = plt.subplots(1, 3, figsize=(15, 5.6))
    axs[0].imshow(leer_rgb(cp, f)); axs[0].set_title("(a) Embeddings, CP1-CP2-CP3"); axs[0].axis("off")
    c1 = "#d4271e" if TP == "Tp5" else "#2532e4"
    axs[1].imshow(pm, cmap=ListedColormap(["#f0f0f0", c1]), vmin=0, vmax=1, interpolation="nearest"); axs[1].set_title("(b) kNN con embeddings: %s" % nom); axs[1].axis("off")
    om = np.where(val, ev.astype(float), np.nan)
    axs[2].imshow(om, cmap=ListedColormap(["#f0f0f0", c1]), vmin=0, vmax=1, interpolation="nearest"); axs[2].set_title("(c) %s" % otro_nom[0].upper() + otro_nom[1:]); axs[2].axis("off")
    if TP == "Tp5" and os.environ.get("DES_LEYENDA_POR_PANEL"):
        # (b) es quemado en todo 2020 (referencia MapBiomas Fuego); (c), la V4 mide 15/07-13/10
        axs[1].legend(handles=[Patch(color=c1, label="Quemado 2020 (kNN)"), Patch(color="#f0f0f0", ec="0.6", label=lab0)],
                      loc="upper center", bbox_to_anchor=(0.5, -0.02), ncol=1, frameon=False, fontsize=10)
        axs[2].legend(handles=[Patch(color=c1, label="Quemado 15/07-13/10 (V4)"), Patch(color="#f0f0f0", ec="0.6", label=lab0)],
                      loc="upper center", bbox_to_anchor=(0.5, -0.02), ncol=1, frameon=False, fontsize=10)
    else:
        fig.legend(handles=[Patch(color=c1, label=lab1.split(" (")[0]), Patch(color="#f0f0f0", label=lab0.split(" (")[0])], loc="upper center", bbox_to_anchor=(0.5, 0.03), ncol=2, frameon=False)
    guardar("%s_embeddings_knn.png" % TP, fig)
elif TP == "Tp7":
    d = "Tp7_Barrancas_deslizamientos"; f = 1
    A, T, crs, sh = leer_emb(qg(d, "E1_DIAMANTE_BARRANCA_AlphaEarth_embeddings_2018_10m.tif"), f)
    B, _, _, _ = leer_emb(qg(d, "E1_DIAMANTE_BARRANCA_AlphaEarth_embeddings_2025_10m.tif"), f)
    sim = (A * B).sum(0)
    import geopandas as gpd
    from rasterio.features import rasterize
    def mask(path, layer=None, tipo=None):
        g = gpd.read_file(path, layer=layer) if layer else gpd.read_file(path)
        if tipo: g = g[g.tipo == tipo]
        g = g.to_crs(crs)
        return rasterize([(x, 1) for x in g.geometry], out_shape=sh, transform=T, all_touched=True).astype(bool), g
    tab = ruta(d, "04_Tablas_de_trabajo")
    mc, gc = mask(os.path.join(tab, "E1_cicatriz_y_deposito.gpkg"), "formas", "cicatriz")
    md, gd = mask(os.path.join(tab, "E1_cicatriz_y_deposito.gpkg"), "formas", "deposito")
    ml, gl = mask(os.path.join(tab, "E1_ladera_reparada.gpkg"))
    mr, gr_ = mask(os.path.join(tab, "E1_zona_referencia.gpkg"))
    ok = np.isfinite(sim)
    umbral = float(np.nanpercentile(sim[ml & ~mc & ~md & ok], 10))
    filas = []
    for nom, m in [("Cicatriz (CBERS-4A)", mc), ("Deposito (CBERS-4A)", md), ("Ladera relevada en 2018", ml & ~mc & ~md), ("Anillo de referencia", mr), ("Todo el sitio", ok)]:
        v = sim[m & ok]
        filas.append([nom, int(v.size), round(float(np.median(v)), 3), round(float(np.percentile(v, 10)), 3), round(100 * float((v < umbral).mean()), 1)])
        log("%s: %d pixeles, semejanza 2018-2025 mediana %.3f, %.0f %% por debajo del umbral" % (nom, v.size, np.median(v), 100 * (v < umbral).mean()))
    tabla("Tp7_embeddings_cambio.csv", ["Zona", "Pixeles de 10 m", "Semejanza 2018-2025 mediana", "Percentil 10", "%% por debajo de %.3f (percentil 10 de la ladera)" % umbral], filas)
    try:
        grieta = gpd.read_file(r"F:\HFdV COURSES\CEREGEO\2018\TelSAR\DIAMANTE\GRIETAS\grietadte.shp").to_crs(crs)
    except Exception:
        grieta = None
    x0, y0 = T.c, T.f; ext = (x0, x0 + sh[1] * T.a, y0 + sh[0] * T.e, y0)
    cx, cy = gc.union_all().centroid.x, gc.union_all().centroid.y; R_ = 700
    fig, axs = plt.subplots(1, 3, figsize=(16, 5.8))
    axs[0].imshow(leer_rgb(qg(d, "E1_DIAMANTE_BARRANCA_AlphaEarth_embeddings_2018_10m_CP1_CP2_CP3_RGB_8bit.tif"), f), extent=ext); axs[0].set_title("(a) Embeddings 2018, CP1-CP2-CP3")
    axs[1].imshow(leer_rgb(qg(d, "E1_DIAMANTE_BARRANCA_AlphaEarth_embeddings_2025_10m_CP1_CP2_CP3_RGB_8bit.tif"), f), extent=ext); axs[1].set_title("(b) Embeddings 2025, CP1-CP2-CP3")
    im = axs[2].imshow(sim, extent=ext, cmap="magma", vmin=0.4, vmax=1); axs[2].set_title("(c) Semejanza 2018-2025 (coseno)")
    cb = fig.colorbar(im, ax=axs[2], orientation="horizontal", fraction=0.05, pad=0.03); cb.set_label("1 = sin cambio; bajo = cambio")
    for ax in axs:
        gc.boundary.plot(ax=ax, color="orange", lw=1.6); gd.boundary.plot(ax=ax, color="deepskyblue", lw=1.6)
        if grieta is not None:
            grieta.plot(ax=ax, color="white", lw=5); grieta.plot(ax=ax, color="red", lw=3)
        ax.set_xlim(cx - R_, cx + R_); ax.set_ylim(cy - R_, cy + R_); ax.set_xticks([]); ax.set_yticks([]); ax.set_xlabel(""); ax.set_ylabel("")
        ax.plot([cx - R_ + 80, cx - R_ + 280], [cy - R_ + 80, cy - R_ + 80], "k", lw=4)
        ax.text(cx - R_ + 180, cy - R_ + 110, "200 m", ha="center", fontsize=10, bbox=dict(fc="w", ec="none", alpha=.8))
    fig.legend(handles=[Line2D([], [], color="orange", lw=2, label="Cicatriz (CBERS-4A)"), Line2D([], [], color="deepskyblue", lw=2, label="Depósito (CBERS-4A)"), Line2D([], [], color="red", lw=3, label="Grieta relevada en 2018")],
               loc="upper center", bbox_to_anchor=(0.5, 0.03), ncol=3, frameon=False)
    guardar("Tp7_embeddings_cambio.png", fig)
guardar_log()
