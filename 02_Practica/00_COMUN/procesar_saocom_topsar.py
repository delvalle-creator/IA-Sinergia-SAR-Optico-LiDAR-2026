# -*- coding: utf-8 -*-
"""
procesar_saocom_topsar.py - SAOCOM-1A/1B L1A TOPSAR (catalogo de CONAE) -> gamma0 con SNAP (gpt), por sitio.

Las escenas L1A TOPSAR Narrow (TNA, TNB) que pidio el docente al catalogo de CONAE
(https://catalog.saocom.conae.gov.ar) llegan de dos maneras:

  - "merg": CONAE ya unio las rafagas (bursts) y las subfranjas (subswaths): un SLC por polarizacion
    (slc-...-merg-hh) y un mapa de angulos de incidencia (idm-...-merg-hh). SNAP lo lee como un SLC.
    El mapa de angulos se deja aparte porque el lector de SNAP lo confunde con la imagen.
  - por subfranja: un SLC por subfranja y polarizacion (slc-...-s1qp-hh ... s5qp-hh), cada uno con
    sus rafagas superpuestas. SNAP 14 no tiene TOPSAR-Deburst para SAOCOM (solo Sentinel-1). Este
    programa hace el "deburst" y la union ("merge") como lo hace CONAE: corta cada superposicion de
    rafagas y de subfranjas por la mitad (las rafagas y las subfranjas comparten la misma grilla de
    tiempo de azimut y de rango: los desfases son lineas y muestras enteras) y escribe un SLC unido
    con el mismo formato del producto "merg" (BigTIFF complejo, XML anotado y puntos de enlace).

Despues cada escena va por esta cadena (grafo de SNAP, se guarda en Grafos_SNAP):
  Read -> Subset del sitio (+25 km) -> Calibration (sigma0) -> Multilook (pixel cuadrado en el terreno)
       -> Speckle-Filter (Refined Lee) -> Range-Doppler Terrain-Correction (Copernicus DEM 30 m, 20 m,
       EPSG:32721, con el angulo de incidencia sobre el elipsoide) -> Subset del sitio -> BEAM-DIMAP
Los L1A de CONAE ya vienen calibrados (|DN|^2 = sigma0; el Calibration de SNAP los deja iguales).
gamma0 = sigma0 / cos(angulo de incidencia sobre el elipsoide). No se usa el Terrain-Flattening de
SNAP 14: con SAOCOM da unos 5 dB menos que NISAR GCOV de la misma semana sobre Federal.

Salida, en cada practico de la escena: <Tp>\\02_Subsets_SNAP_QGIS\\SAOCOM_gamma0\\
  SNAP_DIMAP (lineal + virtuales dB + cociente), QGIS_GeoTIFF (todas las bandas y una banda por
  polarizacion), RGB_copol_cruzada_cociente (HH-HV-HH/HV), Grafos_SNAP, LEEME_SAOCOM_gamma0.md

USO (Miniforge Prompt, entorno sar):
    python procesar_saocom_topsar.py                       (todas las escenas)
    python procesar_saocom_topsar.py --solo EOL1ASARSAO1B15520854 EOL1ASARSAO1B15543480
    python procesar_saocom_topsar.py --origen D:\\CURSOS_CEREGEO_2026\\02_Practica\\00_COMUN\\08_Originales_crudos\\SAOCOM --trabajo D:\\TEMP\\_saocom_trabajo --rehacer
"""
import argparse
import datetime as _dt
import glob
import os
import re
import shutil
import struct
import subprocess
import sys
import time
import zipfile

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import armar_subsets as A                                          # noqa: E402
from configuracion_comun import ruta_tp, SITIOS                     # noqa: E402
from procesar_s1_crudo import DEM, nodo                             # noqa: E402

PROGRAMA = "00_COMUN/procesar_saocom_topsar.py"
POLS = ["HH", "HV", "VH", "VV"]
PIXEL = 20.0

# id de descarga: (fecha, sitios, practicos, para que)
ESCENAS = {
    "EOL1ASARSAO1B15725893": ("2023-10-10", ["B_CONCORDIA"], ["Tp6", "Tp1"], "antes de la crecida de noviembre de 2023 (referencia)"),
    "EOL1ASARSAO1B15725957": ("2023-10-31", ["B_CONCORDIA"], ["Tp6", "Tp1"], "crecida del rio Uruguay"),
    "EOL1ASARSAO1A15725877": ("2023-11-08", ["B_CONCORDIA"], ["Tp6", "Tp1"], "crecida del rio Uruguay"),
    "EOL1ASARSAO1B15725921": ("2023-11-11", ["B_CONCORDIA"], ["Tp6", "Tp1"], "crecida del rio Uruguay"),
    "EOL1ASARSAO1B15543480": ("2026-09-16", ["B_CONCORDIA"], ["Tp10", "Tp1"], "ciudad de Concordia, septiembre de 2026"),
    "EOL1ASARSAO1B15571913": ("2026-09-22", ["E_PARANA_DIAMANTE"], ["Tp10"], "Parana - Diamante, septiembre de 2026"),
    "EOL1ASARSAO1B15520854": ("2026-09-11", ["C_FEDERAL"], ["Tp9"], "monte de Federal, 2026"),
    "EOL1ASARSAO1A15725989": ("2021-08-04", ["C_FEDERAL"], ["Tp9"], "monte de Federal, 2021"),
    "EOL1ASARSAO1A15725942": ("2023-09-11", ["F_BOVRIL"], ["Tp8"], "suelo de Bovril, septiembre de 2023"),
    "EOL1ASARSAO1A15583751": ("2026-09-24", ["A2_IBICUY", "DELTA_NISAR"], ["Tp2", "Tp3"], "humedales del Delta, septiembre de 2026"),
}


def log(*a):
    print(*a, flush=True)


# ------------------------------------------------------------------ lectura de los XML de CONAE
def _t(s):
    d = _dt.datetime.strptime(s.strip()[:20], "%d-%b-%Y %H:%M:%S")
    frac = s.strip().split(".")[1] if "." in s else "0"
    return (d - _dt.datetime(2000, 1, 1)).total_seconds() + float("0." + frac)


def _t_txt(sec):
    d = _dt.datetime(2000, 1, 1) + _dt.timedelta(seconds=int(sec))
    return d.strftime("%d-%b-%Y %H:%M:%S").upper() + ("%.12f" % (sec - int(sec)))[1:]


def _g(x, tag, attr=""):
    m = re.search(r"<%s%s>(.*?)</%s>" % (tag, attr, tag), x, re.S)
    return m.group(1).strip() if m else None


def leer_swath(xml):
    x = open(xml, encoding="utf-8", errors="ignore").read()
    d = dict(xml=xml, texto=x,
             archivo=os.path.join(os.path.dirname(xml), _g(x, "FileName")),
             L=int(_g(x, "Lines")), S=int(_g(x, "Samples")), hdr=int(_g(x, "HeaderOffsetBytes")),
             dt=float(_g(x, "LinesStep", ' unit="s"')), dtau=float(_g(x, "SamplesStep", ' unit="s"')),
             tau=float(_g(x, "SamplesStart", ' unit="s"')), lpb=int(_g(x, "LinesPerBurst")))
    d["bt"] = [_t(s) for s in re.findall(r'<AzimuthStartTime unit="Utc">(.*?)<', x)]
    return d


# ------------------------------------------------------------------ BigTIFF (como los de CONAE)
def _ifd(fn):
    f = open(fn, "rb")
    f.seek(8)
    off = struct.unpack("<Q", f.read(8))[0]
    f.seek(off)
    n = struct.unpack("<Q", f.read(8))[0]
    T = {}
    for _ in range(n):
        tag, typ, cnt, val = struct.unpack("<HHQQ", f.read(20))
        T[tag] = (typ, cnt, val)
    def leer(tag):
        typ, cnt, val = T[tag]
        size = {2: 1, 3: 2, 4: 4, 12: 8, 16: 8}[typ] * cnt
        if size <= 8:
            return struct.pack("<Q", val)[:size]
        f.seek(val)
        return f.read(size)
    return T, leer


def escribir_bigtiff(ruta, arr, tiepoints, plantilla):
    """SLC complejo (CFloat32) en BigTIFF, una fila por tira y datos contiguos, con los mismos rotulos
    GeoTIFF que el archivo de CONAE (plantilla). Devuelve el desplazamiento de los datos."""
    T, leer = _ifd(plantilla)
    L, S = arr.shape
    tags = []                                                   # (tag, tipo, cuenta, bytes)
    def add(tag, typ, cnt, data):
        tags.append((tag, typ, cnt, data))
    add(256, 4, 1, struct.pack("<I", S))
    add(257, 4, 1, struct.pack("<I", L))
    add(258, 3, 1, struct.pack("<H", 64))
    add(259, 3, 1, struct.pack("<H", 1))
    add(262, 3, 1, struct.pack("<H", 1))
    desc = leer(270) if 270 in T else b"SAOCOM\x00"
    add(270, 2, len(desc), desc)
    add(273, 16, L, None)                                       # offsets: se completan despues
    add(274, 3, 1, struct.pack("<H", 1))
    add(277, 3, 1, struct.pack("<H", 1))
    add(278, 3, 1, struct.pack("<H", 1))
    add(279, 16, L, struct.pack("<%dQ" % L, *([S * 8] * L)))
    add(284, 3, 1, struct.pack("<H", 1))
    fecha = _dt.datetime.now().strftime("%Y:%m:%d %H:%M:%S").encode() + b"\x00"
    add(306, 2, len(fecha), fecha)
    add(339, 3, 1, struct.pack("<H", 6))
    tp = tiepoints.astype("<f8").tobytes()
    add(33922, 12, tiepoints.size, tp)
    for tag in (34735, 34736, 34737):
        if tag in T:
            typ, cnt, _ = T[tag]
            add(tag, typ, cnt, leer(tag))
    n = len(tags)
    pos = 16 + 8 + n * 20 + 8
    extra = []
    entradas = []
    for tag, typ, cnt, data in tags:
        size = {2: 1, 3: 2, 4: 4, 12: 8, 16: 8}[typ] * cnt
        if size <= 8 and data is not None:
            entradas.append((tag, typ, cnt, int.from_bytes(data.ljust(8, b"\x00"), "little")))
        else:
            if pos % 2:
                extra.append(b"\x00")
                pos += 1
            entradas.append((tag, typ, cnt, pos))
            extra.append((tag, data, size))
            pos += size
    datos0 = pos + (8 - pos % 8) % 8
    with open(ruta, "wb") as f:
        f.write(b"II" + struct.pack("<HHHQ", 43, 8, 0, 16))
        f.write(struct.pack("<Q", n))
        for tag, typ, cnt, val in entradas:
            f.write(struct.pack("<HHQQ", tag, typ, cnt, val))
        f.write(struct.pack("<Q", 0))
        for e in extra:
            if isinstance(e, bytes):
                f.write(e)
                continue
            tag, data, size = e
            if tag == 273:
                data = struct.pack("<%dQ" % L, *[datos0 + i * S * 8 for i in range(L)])
            f.write(data)
        f.write(b"\x00" * (datos0 - f.tell()))
        for i0 in range(0, L, 512):
            f.write(np.ascontiguousarray(arr[i0:i0 + 512]).astype("<c8").tobytes())
    return datos0


def tiepoints_swath(fn):
    T, leer = _ifd(fn)
    return np.frombuffer(leer(33922), "<f8").reshape(-1, 6)


# ------------------------------------------------------------------ geolocalizacion por la orbita (doppler cero, elipsoide WGS84)
A_WGS, B_WGS = 6378137.0, 6356752.314245
def orbita(x):
    blk = x[x.find("<StateVectorData"):x.find("</StateVectorData>")]
    def vals(tag):
        b = blk[blk.find("<%s>" % tag):blk.find("</%s>" % tag)]
        return np.array([float(v) for v in re.findall(r">([-0-9.eE+]+)</val>", b)])
    p = vals("pSV_m").reshape(-1, 3); v = vals("vSV_mOs").reshape(-1, 3)
    t0 = _t(re.search(r"<t_ref_Utc>(.*?)</t_ref_Utc>", blk).group(1))
    dt = float(re.search(r"<dtSV_s>(.*?)</dtSV_s>", blk).group(1))
    return t0 + dt * np.arange(len(p)), p, v
def interp(ts, P, V, t, grado=8):
    i = np.clip(np.searchsorted(ts, t) - grado // 2, 0, len(ts) - grado - 1)
    sl = slice(i, i + grado + 1); tt = ts[sl] - t
    S = np.array([np.polyval(np.polyfit(tt, P[sl, k], grado), 0) for k in range(3)])
    W = np.array([np.polyval(np.polyfit(tt, V[sl, k], grado), 0) for k in range(3)])
    return S, W
def punto(S, W, R, derecha=True):
    up = S / np.linalg.norm(S); f = W / np.linalg.norm(W)
    n = -up - np.dot(-up, f) * f; n /= np.linalg.norm(n)
    r = np.cross(f, up); r -= np.dot(r, f) * f; r /= np.linalg.norm(r)
    if not derecha: r = -r
    def g(a):
        P = S + R * (np.cos(a) * n + np.sin(a) * r)
        return (P[0]**2 + P[1]**2) / A_WGS**2 + P[2]**2 / B_WGS**2 - 1, P
    lo, hi = 0.0, np.radians(70)
    for _ in range(60):
        m = (lo + hi) / 2
        if g(m)[0] < 0: lo = m
        else: hi = m
    return g((lo + hi) / 2)[1]
def ecef_a_geo(P):
    x, y, z = P; e2 = 1 - B_WGS**2 / A_WGS**2; lon = np.degrees(np.arctan2(y, x)); p = np.hypot(x, y)
    lat = np.arctan2(z, p * (1 - e2))
    for _ in range(5):
        N = A_WGS / np.sqrt(1 - e2 * np.sin(lat)**2); lat = np.arctan2(z + e2 * N * np.sin(lat), p)
    return lon, np.degrees(lat)
def tiepoints_orbita(x, t_ini, dt, tau_ini, dtau, filas, cols, derecha=True):
    ts, P, V = orbita(x); out = []
    for f in filas:
        S, W = interp(ts, P, V, t_ini + f * dt)
        for c in cols:
            R = 299792458.0 * (tau_ini + c * dtau) / 2
            lon, lat = ecef_a_geo(punto(S, W, R, derecha))
            out.append((c, f, 0.0, lon, lat, 0.0))
    return np.array(out)


# ------------------------------------------------------------------ deburst y union de subfranjas
def unir_subfranjas(carpeta_data, salida_data, base_nombre):
    """Devuelve las polarizaciones escritas."""
    os.makedirs(salida_data, exist_ok=True)
    hechas = []
    for pol in POLS:
        xmls = sorted(x for x in glob.glob(os.path.join(carpeta_data, "slc-*-s*qp-%s.xml" % pol.lower()))
                      if re.search(r"-s\d+qp-\w\w\.xml$", x))
        if not xmls:
            continue
        sw = [leer_swath(x) for x in xmls]
        # el tiempo entre lineas es el mismo en todas las subfranjas; el muestreo en rango NO (60, 40 o 30 MHz
        # segun el haz): todas se llevan al muestreo mas fino, por vecino mas cercano en rango
        dt = sw[0]["dt"]
        assert all(abs(s["dt"] - dt) < 1e-12 for s in sw), "subfranjas con distinto tiempo entre lineas"
        dtau = min(s["dtau"] for s in sw)
        t0 = min(s["bt"][0] for s in sw)
        tau0 = min(s["tau"] for s in sw)
        for s in sw:
            s["o"] = [int(round((b - t0) / dt)) for b in s["bt"]]
            s["fin"] = s["tau"] + (s["S"] - 1) * s["dtau"]
            assert s["L"] == len(s["bt"]) * s["lpb"], (s["xml"], s["L"], len(s["bt"]), s["lpb"])
        Lo = max(s["o"][-1] + s["lpb"] for s in sw)
        So = int(np.floor((max(s["fin"] for s in sw) - tau0) / dtau)) + 1
        sw.sort(key=lambda s: s["tau"])
        cortes = [0]
        for a, b in zip(sw[:-1], sw[1:]):
            cortes.append(int(round(((b["tau"] + min(a["fin"], b["fin"])) / 2 - tau0) / dtau)))
        cortes.append(So)
        out = np.zeros((Lo, So), dtype="complex64")
        for k, s in enumerate(sw):
            src = np.memmap(s["archivo"], dtype="<c8", mode="r", offset=s["hdr"], shape=(s["L"], s["S"]))
            j = np.arange(cortes[k], cortes[k + 1])
            idx = np.rint((tau0 + j * dtau - s["tau"]) / s["dtau"]).astype(int)
            ok = (idx >= 0) & (idx < s["S"])
            j, idx = j[ok], idx[ok]
            if j.size == 0:
                continue
            j0, j1 = int(j[0]), int(j[-1]) + 1
            nb, lpb, o = len(s["bt"]), s["lpb"], s["o"]
            for b in range(nb):
                a0 = 0 if b == 0 else (o[b] + o[b - 1] + lpb) // 2 - o[b]
                e0 = lpb if b == nb - 1 else (o[b + 1] + o[b] + lpb) // 2 - o[b]
                blq = np.asarray(src[b * lpb + a0:b * lpb + e0, idx[0]:idx[-1] + 1])
                out[o[b] + a0:o[b] + e0, j0:j1] = blq[:, idx - idx[0]]
            del src
        # puntos de enlace del producto unido, calculados con la orbita (cada 500 columnas y 66 filas,
        # como el producto merg de CONAE; altura 0 sobre el elipsoide)
        cols = np.r_[np.arange(0, So, 500), So - 1]
        filas = np.r_[np.arange(0, Lo, 66), Lo - 1]
        tie = tiepoints_orbita(sw[len(sw) // 2]["texto"], t0, dt, tau0, dtau, filas, cols)
        nombre = "%s-merg-%s" % (base_nombre, pol.lower())
        ruta = os.path.join(salida_data, nombre)
        off = escribir_bigtiff(ruta, out, tie, sw[0]["archivo"])
        valido = float((out[::20, ::20] != 0).mean())
        del out
        # XML anotado: el de la subfranja de rango cercano (su tiempo de rango inicial, trg0 de SlantToGround
        # y GroundToSlant, es el del producto unido), con la geometria del producto unido
        x = sw[0]["texto"]
        x = re.sub(r"<FileName>.*?</FileName>", "<FileName>%s</FileName>" % nombre, x, count=1)
        x = re.sub(r"<Lines>.*?</Lines>", "<Lines>%d</Lines>" % Lo, x, count=1)
        x = re.sub(r"<Samples>.*?</Samples>", "<Samples>%d</Samples>" % So, x, count=1)
        x = re.sub(r"<HeaderOffsetBytes>.*?</HeaderOffsetBytes>", "<HeaderOffsetBytes>%d</HeaderOffsetBytes>" % off, x, count=1)
        x = re.sub(r'<LinesStart unit="Utc">.*?</LinesStart>', '<LinesStart unit="Utc">%s</LinesStart>' % _t_txt(t0), x, count=1)
        x = re.sub(r'<SamplesStart unit="s">.*?</SamplesStart>', '<SamplesStart unit="s">%.18f</SamplesStart>' % tau0, x, count=1)
        x = re.sub(r"<ImageType>.*?</ImageType>", "<ImageType>MERGED SLC</ImageType>", x, count=1)
        x = re.sub(r"<Swath>(\w+?)\d+</Swath>", r"<Swath>\1</Swath>", x, count=1)
        x = re.sub(r"<EchoesPerBurst>.*?</EchoesPerBurst>", "<EchoesPerBurst>%d</EchoesPerBurst>" % Lo, x, count=1)
        x = re.sub(r"<trg0_s>.*?</trg0_s>", "<trg0_s>%.18f</trg0_s>" % tau0, x)
        x = re.sub(r'<SamplesStep unit="s">.*?</SamplesStep>', '<SamplesStep unit="s">%.15g</SamplesStep>' % dtau, x, count=1)
        x = re.sub(r'<frg_hz unit="Hz">.*?</frg_hz>', '<frg_hz unit="Hz">%.6f</frg_hz>' % (1.0 / dtau), x, count=1)
        x = re.sub(r'<PSrg_m unit="m">.*?</PSrg_m>', '<PSrg_m unit="m">%.12f</PSrg_m>' % (299792458.0 * dtau / 2), x, count=1)
        for bloque in ("AcquisitionTimeLine", "DataStatistics", "BurstInfo", "DopplerCentroid", "DopplerRate", "Pulse"):
            x = re.sub(r"\n\s*<%s>.*?</%s>" % (bloque, bloque), "", x, flags=re.S)
        with open(ruta + ".xml", "w", encoding="utf-8") as f:
            f.write(x)
        log("    %s: %d x %d, %d subfranjas, con dato %.0f %%, %d puntos de enlace calculados con la orbita"
            % (pol, Lo, So, len(sw), 100 * valido, len(tie)))
        hechas.append(pol)
        xm = sw[len(sw) // 2]["texto"]
        if "ASCENDING" in (re.search(r"<OrbitDirection>(.*?)</OrbitDirection>", xm) or [None, ""])[1]:
            pares = [(0, 0), (Lo - 1, 0), (Lo - 1, So - 1), (0, So - 1)]      # convencion del lector, ascendente
        else:
            pares = [(Lo - 1, So - 1), (0, So - 1), (0, 0), (Lo - 1, 0)]      # descendente, mirada a la derecha
        esq = [tiepoints_orbita(xm, t0, dt, tau0, dtau, [f], [c])[0] for f, c in pares]
        geo = dict(t0=t0, t1=t0 + (Lo - 1) * dt, esquinas=esq, Lo=Lo, So=So, dt=dt, dtau=dtau, tau0=tau0)
    return hechas, geo


# ------------------------------------------------------------------ preparar el producto que lee SNAP
def preparar(id_, origen, trabajo):
    carpeta = os.path.join(origen, id_)
    zips = glob.glob(os.path.join(carpeta, "*.zip"))
    xemt = glob.glob(os.path.join(carpeta, "*.xemt"))
    if not zips or not xemt:
        raise RuntimeError("No encuentro el .zip y el .xemt en %s" % carpeta)
    destino = os.path.join(trabajo, id_ + "_snap")
    lista = os.path.join(destino, xemt[0].split(os.sep)[-1])
    marca = os.path.join(destino, "_union_v8.txt")
    if os.path.exists(lista) and os.path.exists(marca):
        return lista, open(marca, encoding="utf-8").read()
    shutil.rmtree(destino, ignore_errors=True)
    z = zipfile.ZipFile(zips[0])
    nombres = [i.filename for i in z.infolist()]
    merg = [n for n in nombres if re.search(r"Data/slc-.*-merg-\w\w(\.xml)?$", n)]
    os.makedirs(os.path.join(destino, "Data"), exist_ok=True)
    if merg:
        for n in merg:
            with z.open(n) as a, open(os.path.join(destino, "Data", n.split("/")[-1]), "wb") as b:
                shutil.copyfileobj(a, b, 64 << 20)
        modo = "CONAE ya unio rafagas y subfranjas (merg); se deja aparte el mapa de angulos (idm)"
    else:
        crudo = os.path.join(trabajo, id_ + "_subfranjas")
        os.makedirs(crudo, exist_ok=True)
        for n in nombres:
            if n.startswith("Data/slc-"):
                d = os.path.join(crudo, n.split("/")[-1])
                if not os.path.exists(d):
                    with z.open(n) as a, open(d, "wb") as b:
                        shutil.copyfileobj(a, b, 64 << 20)
        base = re.sub(r"-s\d+qp-\w\w$", "", os.path.basename(sorted(x for x in glob.glob(os.path.join(crudo, "slc-*-s*qp-hh"))
                                                                   if not x.endswith(".xml"))[0]))
        pols, geo = unir_subfranjas(crudo, os.path.join(destino, "Data"), base)
        shutil.rmtree(crudo, ignore_errors=True)
        modo = "rafagas y subfranjas unidas por este programa (%s)" % " ".join(pols)
        # El lector de SNAP toma del .xemt el tiempo de la primera y la ultima linea (y de ahi el intervalo
        # entre lineas) y las cuatro esquinas: se reescriben con la geometria del producto unido.
        xt = open(xemt[0], encoding="utf-8", errors="ignore").read()
        iso = lambda sec: (_dt.datetime(2000, 1, 1) + _dt.timedelta(seconds=sec)).strftime("%Y-%m-%dT%H:%M:%S.%f")
        xt = re.sub(r"(<timePeriod>\s*<startTime>).*?(</startTime>\s*<endTime>).*?(</endTime>)",
                    lambda m: m.group(1) + iso(geo["t0"]) + m.group(2) + iso(geo["t1"]) + m.group(3), xt, count=1, flags=re.S)
        # orden de los vertices de CONAE (descendente, mirada a la derecha): ultima-lejana, primera-lejana,
        # primera-cercana, ultima-cercana
        vert = "".join("\n          <vertex>\n            <lat>%.10f</lat>\n            <lon>%.10f</lon>\n          </vertex>"
                       % (e[4], e[3]) for e in geo["esquinas"])
        xt = re.sub(r"<frame>.*?</frame>", "<frame>%s\n        </frame>" % vert, xt, count=1, flags=re.S)
        # y el tamano de la imagen y el tiempo de rango inicial salen de imageAttributes: se escribe como
        # el de un producto merg de CONAE
        haz = (re.search(r"<beamID>(.*?)</beamID>", xt) or [None, "TNAQP"])[1]
        bandas = "".join("""
          <band>
            <bandIndex>%d</bandIndex>
            <bandName>Merged %s Beams %s polarization samples</bandName>
            <nCols>%d</nCols>
            <nRows>%d</nRows>
          </band>""" % (i + 1, haz, p, geo["So"], geo["Lo"]) for i, p in enumerate(pols))
        franjas = "".join("""
        <SwathInfo>
          <Swath>%s</Swath>
          <Polarization>%s</Polarization>
          <ProcessedBandwidths>
            <Brg_hz>0</Brg_hz>
            <Baz_hz>0</Baz_hz>
          </ProcessedBandwidths>
          <DopplerCentroid>
            <pol>
              <val>0</val>
              <val>0</val>
              <val>0</val>
              <val>0</val>
              <val>0</val>
              <val>0</val>
              <val>0</val>
            </pol>
            <trg0_s>0</trg0_s>
            <taz0_Utc>1970-01-01T00:00:00.000000</taz0_Utc>
          </DopplerCentroid>
          <RasterInfo>
            <SamplesStep>%.15g</SamplesStep>
            <LinesStep>%.15g</LinesStep>
            <LinesStart>%s</LinesStart>
            <SamplesStart>%.18f</SamplesStart>
          </RasterInfo>
        </SwathInfo>""" % (haz, p, geo["dtau"], geo["dt"], _t_txt(geo["t0"]), geo["tau0"]) for p in pols)
        bloque = "<imageAttributes>\n        <bands>%s\n        </bands>%s\n      </imageAttributes>" % (bandas, franjas)
        xt = re.sub(r"<imageAttributes>.*?</imageAttributes>", lambda m: bloque, xt, count=1, flags=re.S)
        with open(lista, "w", encoding="utf-8") as f:
            f.write(xt)
        with open(marca, "w", encoding="utf-8") as f:
            f.write(modo)
        return lista, modo
    shutil.copy2(xemt[0], lista)
    with open(marca, "w", encoding="utf-8") as f:
        f.write(modo)
    return lista, modo


# ------------------------------------------------------------------ SNAP
def grafo(entrada, salida, wkt, wkt_final):
    g = "<graph id=\"SAOCOM_TOPSAR_a_sigma0\">\n  <version>1.0</version>\n"
    g += nodo("Read", "Read", [], {"file": entrada, "copyMetadata": "true"})
    pasos = [
        ("Recorte_del_sitio", "Subset", {"geoRegion": wkt, "copyMetadata": "true"}),
        ("Calibracion", "Calibration", {"selectedPolarisations": ",".join(POLS),
                                        "outputSigmaBand": "true", "outputBetaBand": "false",
                                        "outputImageInComplex": "false", "outputImageScaleInDb": "false"}),
        ("Multilook", "Multilook", {"nRgLooks": 6, "outputIntensity": "true", "grSquarePixel": "true"}),
        ("Filtro_speckle", "Speckle-Filter", {"filter": "Refined Lee"}),
        ("Correccion_geometrica", "Terrain-Correction", {"demName": DEM, "demResamplingMethod": "BILINEAR_INTERPOLATION",
                                                         "imgResamplingMethod": "BILINEAR_INTERPOLATION",
                                                         "pixelSpacingInMeter": PIXEL, "mapProjection": "EPSG:32721",
                                                         "nodataValueAtSea": "false", "saveSelectedSourceBand": "true",
                                                         "saveIncidenceAngleFromEllipsoid": "true",
                                                         "saveLocalIncidenceAngle": "true"}),
        ("Recorte_final", "Subset", {"geoRegion": wkt_final, "copyMetadata": "true"}),
    ]
    prev = "Read"
    for id_, op, par in pasos:
        g += nodo(id_, op, [prev], par)
        prev = id_
    g += nodo("Write", "Write", [prev], {"file": salida, "formatName": "BEAM-DIMAP"})
    return g + "</graph>\n"


def wkt_sitio(sitio, margen=0.02):
    o, s, e, n = SITIOS[sitio]["bbox"]
    o, s, e, n = o - margen, s - margen, e + margen, n + margen
    return "POLYGON((%f %f, %f %f, %f %f, %f %f, %f %f))" % (o, n, e, n, e, s, o, s, o, n)


def correr(gpt, xml, dim, reg):
    r = subprocess.run([gpt, xml, "-c", "8G", "-q", "16"], capture_output=True, text=True, errors="replace")
    with open(reg, "w", encoding="utf-8") as f:
        f.write("CODIGO: %s\nSALIDA:\n%s\nERRORES:\n%s\n" % (r.returncode, r.stdout, r.stderr))
    return r.returncode == 0 and os.path.exists(dim), (r.stderr or r.stdout)[-800:]


def normalizar_bandas(dim):
    """SNAP llama Gamma0_DA_HH a las bandas del SLC unido: se renombran a Gamma0_HH (como el Tp5)."""
    datos = os.path.splitext(dim)[0] + ".data"
    txt = open(dim, encoding="utf-8").read()
    for f in glob.glob(os.path.join(datos, "*.*")):
        m = re.match(r"^((?:Gamma0|Sigma0|Beta0))_[A-Za-z0-9]+_(HH|HV|VH|VV)\.(img|hdr)$", os.path.basename(f))
        if not m:
            continue
        viejo = os.path.basename(f)[:-4]
        nuevo = "%s_%s" % (m.group(1), m.group(2))
        if m.group(3) == "hdr":
            h = open(f, encoding="utf-8", errors="ignore").read().replace(viejo, nuevo)
            open(f, "w", encoding="utf-8").write(h)
        os.replace(f, os.path.join(datos, nuevo + "." + m.group(3)))
        txt = txt.replace(viejo, nuevo)
    open(dim, "w", encoding="utf-8").write(txt)


def a_producto(dim, nombre, sitio, cita, fecha):
    """gamma0 = sigma0 / cos(angulo de incidencia sobre el elipsoide).
    Los L1A de CONAE ya estan calibrados: |DN|^2 = sigma0 (el Calibration de SNAP da Sigma0 = Beta0 =
    intensidad). El Terrain-Flattening de SNAP 14 da con SAOCOM valores unos 5 dB por debajo de lo
    esperado (se comprobo contra NISAR GCOV), asi que no se usa: la normalizacion es la del elipsoide,
    valida en el relieve llano de Entre Rios."""
    import rasterio
    datos = os.path.splitext(dim)[0] + ".data"
    p = A.Producto(nombre)
    inc = glob.glob(os.path.join(datos, "incidenceAngleFromEllipsoid.img"))
    with rasterio.open(inc[0]) as r:
        th = r.read(1).astype("float32")
    cos = np.cos(np.radians(np.where((th > 0) & (th < 90), th, np.nan)))
    gam = []
    for pol in POLS:
        img = os.path.join(datos, "Sigma0_%s.img" % pol)
        if not os.path.exists(img):
            continue
        with rasterio.open(img) as r:
            s0 = r.read(1).astype("float32")
            p.transform, p.crs_wkt = r.transform, A._wkt(r.crs)
        g = s0 / cos
        g[~np.isfinite(g) | (s0 <= 0)] = 0.0
        p.banda("Gamma0_%s" % pol, g.astype("float32"), "intensity",
                "gamma0 %s LINEAL sobre el elipsoide (sigma0 / cos del angulo de incidencia; Refined Lee + "
                "Terrain-Correction en SNAP, desde el SLC SAOCOM L1A TOPSAR)" % pol)
        gam.append(dict(nombre="Gamma0_%s" % pol,
                        expr="(Sigma0_%s > 0 && incidenceAngleFromEllipsoid > 0) ? Sigma0_%s / cos(rad(incidenceAngleFromEllipsoid)) : NaN" % (pol, pol),
                        funcion=None, unidad="intensity",
                        desc="gamma0 %s lineal sobre el elipsoide = sigma0 / cos(angulo de incidencia) (banda virtual)" % pol,
                        valida="Sigma0_%s > 0" % pol))
    A.agregar_db_y_cociente(p, "Gamma0_HH", "Gamma0_HV", "HH", "HV", "gamma0")
    for pol in ("VH", "VV"):
        b = "Gamma0_%s" % pol
        p.virtual(b + "_db", "%s > 0 ? 10*log10(%s) : NaN" % (b, b),
                  (lambda nb: (lambda pr: A.db(pr.datos(nb))))(b), "dB", "gamma0 %s en dB (banda virtual)" % pol, "%s > 0" % b)
    p.gamma_virtuales = gam
    try:
        p.metadatos = A.xml_a_arbol(dim)
    except Exception:                                    # noqa: BLE001
        p.metadatos = {}
    p.inicio = p.fin = fecha
    p.tipo = "SAOCOM_L1A_TOPSAR_sigma0_y_gamma0_elipsoide_SNAP"
    p.cita = cita
    p.recorte = A._doc_recorte(sitio, "pixel %.0f m, EPSG:32721 (SNAP Terrain-Correction)" % PIXEL)
    return p


def una_banda(p, banda, carpeta):
    import rasterio
    from rasterio.crs import CRS
    ruta = os.path.join(carpeta, "%s_%s.tif" % (p.nombre, banda))
    a = np.where(p.datos(banda) > 0, p.datos(banda), np.nan).astype("float32")
    with rasterio.open(ruta, "w", driver="GTiff", width=p.ancho, height=p.alto, count=1, dtype="float32",
                       crs=CRS.from_wkt(p.crs_wkt), transform=p.transform, nodata=np.nan, compress="deflate",
                       predictor=3, tiled=True, blockxsize=512, blockysize=512) as d:
        d.write(a, 1)
        d.set_band_description(1, banda)
        d.update_tags(FUENTE=p.cita, UNIDAD="lineal (potencia); dB = 10*log10", PROGRAMA=PROGRAMA)
    return ruta


def copiar_arbol(src, dst):
    if os.path.isdir(src):
        if os.path.exists(dst):
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
    else:
        shutil.copy2(src, dst)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--origen", default=r"D:\CURSOS_CEREGEO_2026\02_Practica\00_COMUN\08_Originales_crudos\SAOCOM")
    ap.add_argument("--trabajo", default=r"D:\TEMP\_saocom_trabajo")
    ap.add_argument("--solo", nargs="*")
    ap.add_argument("--rehacer", action="store_true")
    ap.add_argument("--conservar", action="store_true", help="no borrar el producto unido intermedio")
    a = ap.parse_args()
    gpt = A.gpt_snap()
    if not gpt:
        sys.exit("No se encontro gpt.exe de SNAP. Definir SNAP_GPT.")
    log("SNAP gpt: %s" % gpt)
    os.makedirs(a.trabajo, exist_ok=True)
    resumen = []
    for id_, (fecha, sitios, tps, para) in ESCENAS.items():
        if a.solo and id_ not in a.solo:
            continue
        log("\n=== %s (%s) -> %s, %s ===" % (id_, fecha, ", ".join(sitios), ", ".join(tps)))
        t0 = time.time()
        try:
            xemt, modo = preparar(id_, a.origen, a.trabajo)
        except Exception as e:                              # noqa: BLE001
            log("  NO se pudo preparar: %s" % e)
            continue
        xt = open(glob.glob(os.path.join(a.origen, id_, "*.xemt"))[0], encoding="utf-8", errors="ignore").read()
        sat = _g(xt, "platform") or "SAO1"
        haz = _g(xt, "beamID") or "TN"
        log("  Producto para SNAP: %s (%s, %.0f min)" % (xemt, modo, (time.time() - t0) / 60))
        for sitio in sitios:
            tp0 = tps[0]
            base = ruta_tp(tp0, "02_Subsets_SNAP_QGIS", "SAOCOM_gamma0")
            c_dim, c_tif, c_rgb, c_g = [os.path.join(base, x) for x in
                                        ("SNAP_DIMAP", "QGIS_GeoTIFF", "RGB_copol_cruzada_cociente", "Grafos_SNAP")]
            for c in (c_dim, c_tif, c_rgb, c_g):
                os.makedirs(c, exist_ok=True)
            etiqueta = "SAOCOM_L_%s_QP" % fecha.replace("-", "")
            hecho = None
            magnitud = "gamma0"
            nombre = "%s_%s_%s" % (sitio, etiqueta, magnitud)
            dim = os.path.join(c_dim, nombre + ".dim")
            xml = os.path.join(c_g, "Grafo_%s.xml" % nombre)
            with open(xml, "w", encoding="utf-8") as f:
                f.write(grafo(xemt, dim, wkt_sitio(sitio, 0.25), wkt_sitio(sitio, 0.0)))
            if os.path.exists(dim) and not a.rehacer:
                hecho = (nombre, dim, xml, magnitud)
                log("  Ya estaba: %s" % dim)
            else:
                t1 = time.time()
                ok, err = correr(gpt, xml, dim, os.path.join(c_dim, "_registro_gpt_%s.txt" % nombre))
                if ok:
                    log("  SNAP: sigma0 en %.0f min" % ((time.time() - t1) / 60))
                    hecho = (nombre, dim, xml, magnitud)
                else:
                    log("  SNAP no pudo:\n  %s" % err.replace("\n", "\n  "))
            if not hecho:
                continue
            nombre, dim, xml, magnitud = hecho
            normalizar_bandas(dim)
            dd = fecha.split("-")
            cita = ("CONAE. %s (SAOCOM-%s) SAR banda L, L1A SLC TOPSAR Narrow %s, cuadripolar HH HV VH VV, %s/%s/%s "
                    "(%s). Catalogo SAOCOM, https://catalog.saocom.conae.gov.ar, producto %s. Procesado a %s con "
                    "ESA SNAP 14 (Copernicus DEM GLO-30): sigma0 y gamma0 sobre el elipsoide."
                    % (sat, sat[-2:], haz, dd[2], dd[1], dd[0], para, id_, magnitud))
            p = a_producto(dim, nombre, sitio, cita, fecha)
            if not p.bandas:
                log("  El .dim no tiene bandas: revisar %s" % dim)
                continue
            rec = dict(p.recorte)
            rec.update(programa=PROGRAMA, fecha=_dt.datetime.now().strftime("%d/%m/%Y %H:%M"), fuente=cita,
                       grafo=os.path.basename(xml), entrada=id_, union=modo)
            A.agregar_virtuales_a_dim(dim, p.gamma_virtuales + p.virtuales, rec)
            tif = A.escribir_geotiff(p, c_tif)
            sueltos = [una_banda(p, b["nombre"], c_tif) for b in p.bandas]
            rgb = A.escribir_rgb(p, c_rgb)
            ctrl = A.control_snap(gpt, [dim], os.path.join(base, "_control_snap_tmp"), sitio).get(dim, "")
            validos = [round(100.0 * float((b["datos"] > 0).mean()), 1) for b in p.bandas]
            med = {b["nombre"]: round(float(np.nanmedian(A.db(b["datos"][b["datos"] > 0]))), 1) for b in p.bandas}
            log("  .dim: %s\n  GeoTIFF: %s (+ %d de una banda)\n  RGB: %s\n  Control SNAP: %s\n  Con dato: %s %%; mediana dB: %s"
                % (dim, tif, len(sueltos), rgb, ctrl, validos, med))
            for tp in tps[1:]:
                otro = ruta_tp(tp, "02_Subsets_SNAP_QGIS", "SAOCOM_gamma0")
                for sub, archivos in (("SNAP_DIMAP", [dim, os.path.splitext(dim)[0] + ".data"]),
                                      ("QGIS_GeoTIFF", glob.glob(os.path.join(c_tif, nombre + "*"))),
                                      ("RGB_copol_cruzada_cociente", glob.glob(os.path.join(c_rgb, nombre + "*"))),
                                      ("Grafos_SNAP", [xml])):
                    os.makedirs(os.path.join(otro, sub), exist_ok=True)
                    for s in archivos:
                        copiar_arbol(s, os.path.join(otro, sub, os.path.basename(s)))
                log("  Copiado a %s" % otro)
            resumen.append(dict(id=id_, fecha=fecha, sitio=sitio, tps=tps, para=para, nombre=nombre, magnitud=magnitud,
                                modo=modo, validos=validos, mediana=med, ctrl=ctrl, cita=cita))
        if not a.conservar:
            shutil.rmtree(os.path.join(a.trabajo, id_ + "_snap"), ignore_errors=True)
        log("  Escena terminada en %.0f min" % ((time.time() - t0) / 60))
    # LEEME por practico
    por_tp = {}
    for r in resumen:
        for tp in r["tps"]:
            por_tp.setdefault(tp, []).append(r)
    for tp, filas in por_tp.items():
        leeme = os.path.join(ruta_tp(tp, "02_Subsets_SNAP_QGIS", "SAOCOM_gamma0"), "LEEME_SAOCOM_gamma0.md")
        previo = open(leeme, encoding="utf-8").read() if os.path.exists(leeme) else ""
        with open(leeme, "w", encoding="utf-8") as f:
            if "# SAOCOM banda L" not in previo:
                f.write("# SAOCOM banda L (catalogo de CONAE) procesado a gamma0 en SNAP\n\n"
                        "Hecho con `00_COMUN\\procesar_saocom_topsar.py` desde los L1A SLC TOPSAR Narrow cuadripolares "
                        "(HH, HV, VH, VV). Las rafagas y subfranjas vienen unidas por CONAE (merg) o las une el programa "
                        "cortando cada superposicion por la mitad. Cadena en SNAP: recorte del sitio, calibracion a "
                        "sigma0 (los L1A de CONAE ya vienen calibrados: |DN|^2 = sigma0), multilook a pixel cuadrado, Refined Lee "
                        "y Range-Doppler Terrain-Correction a %.0f m en EPSG:32721 (Copernicus DEM 30 m), con el angulo de "
                        "incidencia sobre el elipsoide. gamma0 = sigma0 / cos(angulo de incidencia): normalizacion sobre el "
                        "elipsoide, no Terrain-Flattening (con SAOCOM, el Terrain-Flattening de SNAP 14 da unos 5 dB menos "
                        "que lo esperado al compararlo con NISAR GCOV de la misma semana). En el relieve llano de Entre Rios "
                        "la diferencia con un gamma0 aplanado es chica; en las barrancas no. Grafos en `Grafos_SNAP` "
                        "(SNAP: Tools > Graph Builder > Load).\n\n"
                        "| Carpeta | Que hay |\n|---|---|\n"
                        "| `SNAP_DIMAP` | sigma0 LINEAL de HH, HV, VH y VV, angulos de incidencia, gamma0 (virtual) + bandas virtuales en dB y cociente HH/HV en dB; metadatos completos |\n"
                        "| `QGIS_GeoTIFF` | `<nombre>.tif`: todas las bandas (lineal y dB). `<nombre>_Gamma0_<POL>.tif`: una banda lineal |\n"
                        "| `RGB_copol_cruzada_cociente` | R = HH, G = HV, B = HH/HV, en dB y en 8 bits |\n"
                        "| `Grafos_SNAP` | El grafo XML de cada producto |\n\n" % PIXEL)
            else:
                f.write(previo.split("\n## ")[0].rstrip() + "\n\n")
            secciones = {}
            for sec in ("\n" + previo).split("\n## ")[1:]:
                secciones[sec.split("\n", 1)[0].strip()] = "## " + sec.rstrip() + "\n"
            for r in filas:
                secciones[r["nombre"]] = ("## %s\n\n- Fecha: %s (%s). Sitio: %s. Magnitud: **%s**.\n- Union: %s.\n"
                        "- Pixeles con dato en el recorte (HH, HV, VH, VV): %s %%. Mediana en dB: %s\n"
                        "- Control SNAP: %s\n- Fuente: %s\n"
                        % (r["nombre"], r["fecha"], r["para"], r["sitio"], r["magnitud"], r["modo"],
                           " / ".join(str(v) for v in r["validos"]),
                           ", ".join("%s %s" % kv for kv in r["mediana"].items()), r["ctrl"].split("\n")[0][:200], r["cita"]))
            orden = sorted(secciones, key=lambda n: (re.search(r"_(\d{8})_", n) or [None, n])[1])
            f.write("\n".join(secciones[n] for n in orden))
        log("LEEME: %s" % leeme)
    log("\nFIN")


if __name__ == "__main__":
    main()
