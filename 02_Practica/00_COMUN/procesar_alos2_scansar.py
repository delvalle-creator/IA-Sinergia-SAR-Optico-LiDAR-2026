# -*- coding: utf-8 -*-
"""
procesar_alos2_scansar.py - ALOS-2 PALSAR-2 ScanSAR WBD L1.1 (CEOS, JAXA) -> sigma0 y gamma0 a 20 m sobre un sitio.
==================================================================================================================
Docente (00_COMUN). SNAP 14 no trae un operador para quitar las rafagas del ScanSAR L1.1 de ALOS-2 (no hay
ALOS-Deburst), asi que el programa hace la cadena a mano, con las mismas formulas de JAXA:

  1. Lee cada subfranja (F1 a F5) que toca el sitio, linea por linea, del archivo CEOS IMG (SLC complejo,
     float32 I y Q). Las lineas entre rafagas vienen en cero: no se usan.
  2. Calibra: sigma0 = (I^2 + Q^2) * 10^(CF / 10), con CF = -83,0 dB (registro radiometrico del LED). La
     forma con "- 32 dB" (la de los L1.1 de ALOS-1) da en este producto un HH de -46 dB de mediana, por debajo
     del piso de ruido del instrumento (unos -28 dB): no corresponde a estos datos.
  3. Ubica cada muestra con los puntos de enlace que trae cada linea (latitud y longitud del primer pixel, del
     central y del ultimo; interpolacion cuadratica en rango) y la proyecta a EPSG:32721.
  4. Calcula el angulo de incidencia sobre el elipsoide con la distancia oblicua de cada muestra (la del primer
     pixel de la linea mas el paso en rango del LED, 8,58 m) y el radio de la orbita (vectores de estado del LED).
  5. Promedia en LINEAL todas las muestras que caen en cada pixel de 20 m de la grilla del sitio (multilook por
     agregacion, unas 10 a 20 muestras no nulas por pixel) y aplica un promedio 3 x 3 (filtro de moteado simple).
  6. gamma0 = sigma0 / cos(incidencia), sobre el elipsoide (relieve llano de Entre Rios).
Salidas como las de SAOCOM: SNAP_DIMAP (sigma0 lineal, incidencia, gamma0 virtual, dB y cociente virtuales,
metadatos de JAXA), QGIS_GeoTIFF (todas las bandas y una por gamma0) y RGB HH-HV-HH/HV.

Uso:  python procesar_alos2_scansar.py --carpeta <IMG/LED/VOL descomprimidos> --sitio B_CONCORDIA --tp Tp6 Tp1
"""
import os, sys, glob, struct, argparse, time, datetime as _dt
import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import armar_subsets as A                                   # noqa: E402
from configuracion_comun import ruta_tp, SITIOS             # noqa: E402
from funciones_comunes import grilla_sitio                  # noqa: E402

PROGRAMA = "00_COMUN/procesar_alos2_scansar.py"
A.PROGRAMA = PROGRAMA


def log(*a):
    print(*a); sys.stdout.flush()


def leer_led(ruta):
    d = open(ruta, "rb").read()
    i, recs = 0, []
    while i < len(d):
        L = int.from_bytes(d[i + 8:i + 12], "big")
        if L <= 0:
            break
        recs.append(d[i:i + L]); i += L
    cf = None
    for r in recs:
        k = r.find(b"-83.0")
        if k > 0 and cf is None:
            try:
                cf = float(r[k:k + 16])
            except ValueError:
                pass
    pp = recs[2]                                            # registro de posicion de la plataforma
    n = int(pp[140:144])
    radios = []
    for j in range(n):
        o = 386 + j * 132
        x, y, z = (float(pp[o + 22 * q:o + 22 * (q + 1)]) for q in range(3))
        radios.append((x * x + y * y + z * z) ** 0.5)
    inc_centro = float(recs[1][484:492]) if len(recs) > 1 else float("nan")
    paso_rango = float(recs[1][1702:1718])                  # espaciado de pixel en rango oblicuo (m)
    return (cf if cf is not None else -83.0), float(np.mean(radios)), inc_centro, paso_rango


def radio_local(lat):
    a, b = 6378137.0, 6356752.3142
    la = np.radians(lat)
    return np.sqrt(((a * a * np.cos(la)) ** 2 + (b * b * np.sin(la)) ** 2) / ((a * np.cos(la)) ** 2 + (b * np.sin(la)) ** 2))


class Subfranja:
    def __init__(self, ruta):
        self.ruta = ruta
        with open(ruta, "rb") as h:
            fd = h.read(720)
        self.nlin = int(fd[180:186]); self.lrec = int(fd[186:192]); self.npix = (self.lrec - 544) // 8

    def prefijos(self, lineas):
        out = []
        with open(self.ruta, "rb") as h:
            for l in lineas:
                h.seek(720 + int(l) * self.lrec)
                r = h.read(216)
                sr = struct.unpack(">3i", r[116:128])
                la = struct.unpack(">3i", r[192:204]); lo = struct.unpack(">3i", r[204:216])
                out.append((sr, [x / 1e6 for x in la], [x / 1e6 for x in lo]))
        return out

    def bloque(self, l0, n):
        with open(self.ruta, "rb") as h:
            h.seek(720 + l0 * self.lrec)
            raw = np.frombuffer(h.read(n * self.lrec), dtype=np.uint8).reshape(n, self.lrec)
        iq = raw[:, 544:].copy().view(">f4").astype("float32").reshape(n, self.npix, 2)
        return iq[..., 0] ** 2 + iq[..., 1] ** 2, raw[:, :216]


def coef(f0, f5, f1):
    return f0, -3 * f0 + 4 * f5 - f1, 2 * f0 - 4 * f5 + 2 * f1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--carpeta", required=True)
    ap.add_argument("--sitio", default="B_CONCORDIA")
    ap.add_argument("--tp", nargs="+", default=["Tp6", "Tp1"])
    ap.add_argument("--pixel", type=float, default=20.0)
    ap.add_argument("--bloque", type=int, default=1500)
    a = ap.parse_args()
    from pyproj import Transformer
    g = grilla_sitio(a.sitio, a.pixel)
    W, H = g["width"], g["height"]; T = g["transform"]
    xmin, ymax = T.c, T.f
    lon0, lat0, lon1, lat1 = SITIOS[a.sitio]["bbox"]
    tr = Transformer.from_crs(4326, 32721, always_xy=True)
    led = glob.glob(os.path.join(a.carpeta, "LED-*"))[0]
    escena = os.path.basename(led)[4:].split("-WBD")[0]
    cf, Rs, inc_c, dr = leer_led(led)
    k_cal = 10 ** (cf / 10.0)
    log("Escena %s; CF %.1f dB; radio de la orbita %.1f km; incidencia en el centro de la escena (LED) %.2f grados;"
        " paso en rango oblicuo %.4f m" % (escena, cf, Rs / 1000, inc_c, dr))
    suma = {p: np.zeros(W * H) for p in ("HH", "HV")}
    nn = {p: np.zeros(W * H) for p in ("HH", "HV")}
    sth = np.zeros(W * H); nth = np.zeros(W * H)
    usadas = []
    for f in range(1, 6):
        rutas = {p: glob.glob(os.path.join(a.carpeta, "IMG-%s-*-F%d" % (p, f))) for p in ("HH", "HV")}
        if not rutas["HH"]:
            continue
        sh = Subfranja(rutas["HH"][0])
        paso = 200
        muestra = np.arange(0, sh.nlin, paso)
        pre = sh.prefijos(muestra)
        lats = np.array([p[1] for p in pre]); lons = np.array([p[2] for p in pre])
        dentro = [(lats[i].min() <= lat1 + 0.05) and (lats[i].max() >= lat0 - 0.05) and
                  (lons[i].min() <= lon1 + 0.05) and (lons[i].max() >= lon0 - 0.05) for i in range(len(muestra))]
        if not any(dentro):
            log("F%d: no toca el sitio" % f); continue
        idx = np.nonzero(dentro)[0]
        la0 = max(0, int(muestra[idx[0]]) - paso); la1 = min(sh.nlin, int(muestra[idx[-1]]) + paso)
        log("F%d: %d lineas x %d pixeles; lineas %d a %d tocan el sitio" % (f, sh.nlin, sh.npix, la0, la1))
        usadas.append("F%d" % f)
        t0 = time.time()
        u = np.linspace(0, 1, sh.npix)
        for l in range(la0, la1, a.bloque):
            n = min(a.bloque, la1 - l)
            pot = {}
            for p in ("HH", "HV"):
                pw, cab = Subfranja(rutas[p][0]).bloque(l, n)
                pot[p] = pw
            sr = np.array([struct.unpack(">3i", c[116:128].tobytes()) for c in cab], dtype="float64")
            la = np.array([struct.unpack(">3i", c[192:204].tobytes()) for c in cab], dtype="float64") / 1e6
            lo = np.array([struct.unpack(">3i", c[204:216].tobytes()) for c in cab], dtype="float64") / 1e6
            ok_l = (la[:, 1] != 0) & (sr[:, 0] > 0)
            sr = sr.astype("float64")
            if not ok_l.any():
                continue
            pot = {p: v[ok_l] for p, v in pot.items()}; sr, la, lo = sr[ok_l], la[ok_l], lo[ok_l]
            a0, b0, c0 = coef(la[:, 0:1], la[:, 1:2], la[:, 2:3]); LAT = a0 + b0 * u + c0 * u * u
            a0, b0, c0 = coef(lo[:, 0:1], lo[:, 1:2], lo[:, 2:3]); LON = a0 + b0 * u + c0 * u * u
            R = sr[:, 0:1] + np.arange(sh.npix)[None, :] * dr
            Rt = radio_local(LAT)
            look = np.arccos(np.clip((R * R + Rs * Rs - Rt * Rt) / (2 * R * Rs), -1, 1))
            th = np.degrees(np.arcsin(np.clip(Rs / Rt * np.sin(look), -1, 1)))
            caja = (LON >= lon0 - 0.02) & (LON <= lon1 + 0.02) & (LAT >= lat0 - 0.02) & (LAT <= lat1 + 0.02)
            if not caja.any():
                continue
            x, y = tr.transform(LON[caja], LAT[caja])
            col = np.floor((x - xmin) / a.pixel).astype(int); fil = np.floor((ymax - y) / a.pixel).astype(int)
            ok = (col >= 0) & (col < W) & (fil >= 0) & (fil < H)
            k = (fil * W + col)[ok]
            for p in ("HH", "HV"):
                v = pot[p][caja][ok] * k_cal
                nz = v > 0
                suma[p] += np.bincount(k[nz], weights=v[nz], minlength=W * H)
                nn[p] += np.bincount(k[nz], minlength=W * H)
            sth += np.bincount(k, weights=th[caja][ok], minlength=W * H); nth += np.bincount(k, minlength=W * H)
        log("   F%d procesada en %.0f s" % (f, time.time() - t0))
    from scipy.ndimage import uniform_filter
    s0 = {}
    for p in ("HH", "HV"):
        m = np.where(nn[p] > 0, suma[p] / np.maximum(nn[p], 1), np.nan).reshape(H, W)
        ok = np.isfinite(m)
        num = uniform_filter(np.where(ok, m, 0), 3); den = uniform_filter(ok.astype(float), 3)
        s0[p] = np.where(ok & (den > 0), num / np.maximum(den, 1e-9), 0.0).astype("float32")
    th = np.where(nth > 0, sth / np.maximum(nth, 1), 0.0).reshape(H, W).astype("float32")
    nmed = np.median(nn["HH"][nn["HH"] > 0])
    log("Muestras no nulas por pixel de %.0f m (mediana): %.0f; pixeles con dato: %.1f %% del sitio"
        % (a.pixel, nmed, 100.0 * (s0["HH"] > 0).mean()))
    log("Incidencia en el sitio: %.1f a %.1f grados" % (np.nanmin(th[th > 0]), np.nanmax(th[th > 0])))
    # ---------------- producto
    fecha = "2023-11-16"
    nombre = "%s_ALOS2_L_20231116_WBD_gamma0" % a.sitio
    cita = ("JAXA. ALOS-2 PALSAR-2, banda L, ScanSAR WBD nivel 1.1 (CEOS), HH y HV, 16/11/2023 15:11 UTC, "
            "orbita descendente, pasada 123, escena %s; distribuido por ASF DAAC, "
            "https://search.asf.alaska.edu. Procesado a sigma0 y gamma0 sobre el elipsoide con %s "
            "(subfranjas %s; CF %.1f dB)." % (escena, PROGRAMA, "+".join(usadas), cf))
    p = A.Producto(nombre)
    p.crs_wkt = A._wkt(g["crs"]); p.transform = T
    for pol in ("HH", "HV"):
        p.banda("Sigma0_%s" % pol, s0[pol], "intensity",
                "sigma0 %s LINEAL (|DN|^2 * 10^(CF/10), promedio de las muestras en el pixel y 3 x 3)" % pol)
    p.banda("incidenceAngleFromEllipsoid", th, "deg", "angulo de incidencia sobre el elipsoide (grados)")
    gam = []
    for pol in ("HH", "HV"):
        nb = "Gamma0_%s" % pol
        f_g = (lambda q: (lambda pr: np.where((pr.datos("Sigma0_%s" % q) > 0) & (pr.datos("incidenceAngleFromEllipsoid") > 0),
                                              pr.datos("Sigma0_%s" % q) / np.cos(np.radians(pr.datos("incidenceAngleFromEllipsoid"))),
                                              0.0).astype("float32")))(pol)
        p.virtual(nb, "(Sigma0_%s > 0 && incidenceAngleFromEllipsoid > 0) ? Sigma0_%s / cos(rad(incidenceAngleFromEllipsoid)) : NaN"
                  % (pol, pol), f_g, "intensity", "gamma0 %s lineal sobre el elipsoide (banda virtual)" % pol, "Sigma0_%s > 0" % pol)
        gam.append(f_g)
    p.virtual("Gamma0_HH_db", "Gamma0_HH > 0 ? 10*log10(Gamma0_HH) : NaN", lambda pr: A.db(gam[0](pr)), "dB", "gamma0 HH en dB (banda virtual)", "Gamma0_HH > 0")
    p.virtual("Gamma0_HV_db", "Gamma0_HV > 0 ? 10*log10(Gamma0_HV) : NaN", lambda pr: A.db(gam[1](pr)), "dB", "gamma0 HV en dB (banda virtual)", "Gamma0_HV > 0")
    p.virtual("HH_HV_cociente_db", "(Gamma0_HH > 0 && Gamma0_HV > 0) ? 10*log10(Gamma0_HH/Gamma0_HV) : NaN",
              lambda pr: A.db(A._cociente(gam[0](pr), gam[1](pr))), "dB", "Cociente HH/HV en dB", "Gamma0_HH > 0 && Gamma0_HV > 0")
    p.rgb = ("Gamma0_HH_db", "Gamma0_HV_db", "HH_HV_cociente_db", "HH", "HV")
    md = {}
    for ln in open(os.path.join(a.carpeta, "summary.txt"), encoding="latin-1"):
        if "=" in ln:
            k_, v_ = ln.split("=", 1); md[k_.strip()] = v_.strip().strip('"')
    md["Calibracion_CF_dB"] = cf; md["Radio_orbita_m"] = round(Rs, 1); md["Incidencia_centro_escena_LED"] = inc_c
    p.metadatos = {"JAXA_summary": md}
    p.inicio = p.fin = fecha
    p.tipo = "ALOS2_PALSAR2_ScanSAR_WBD_L11_sigma0_gamma0_elipsoide"
    p.cita = cita
    p.recorte = A._doc_recorte(a.sitio, "pixel %.0f m, EPSG:32721 (agregacion de muestras + promedio 3 x 3)" % a.pixel)
    base = ruta_tp(a.tp[0], "02_Subsets_SNAP_QGIS", "ALOS2_gamma0")
    c_dim, c_tif, c_rgb = (os.path.join(base, s) for s in ("SNAP_DIMAP", "QGIS_GeoTIFF", "RGB_copol_cruzada_cociente"))
    dim = A.escribir_dim(p, c_dim)
    tif = A.escribir_geotiff(p, c_tif)
    import rasterio
    from rasterio.crs import CRS
    for pol, fg in zip(("HH", "HV"), gam):
        r_ = os.path.join(c_tif, "%s_Gamma0_%s.tif" % (nombre, pol))
        arr = np.where(fg(p) > 0, fg(p), np.nan).astype("float32")
        with rasterio.open(r_, "w", driver="GTiff", width=W, height=H, count=1, dtype="float32", crs=CRS.from_wkt(p.crs_wkt),
                           transform=T, nodata=np.nan, compress="deflate", predictor=3, tiled=True) as d:
            d.write(arr, 1); d.set_band_description(1, "Gamma0_%s" % pol)
            d.update_tags(FUENTE=cita, UNIDAD="lineal (potencia); dB = 10*log10", PROGRAMA=PROGRAMA)
    rgb = A.escribir_rgb(p, c_rgb)
    for pol, fg in zip(("HH", "HV"), gam):
        v = fg(p); log("gamma0 %s mediana en el sitio: %.1f dB" % (pol, np.nanmedian(A.db(v[v > 0]))))
    # control: SAOCOM-1B del 11/11/2023 (TNA, 100 % del sitio), cinco dias antes, misma banda L
    try:
        from funciones_comunes import leer_en_grilla
        for pol, fg in zip(("HH", "HV"), gam):
            sao = glob.glob(os.path.join(ruta_tp("Tp6", "02_Subsets_SNAP_QGIS", "SAOCOM_gamma0", "QGIS_GeoTIFF"),
                                         "*SAOCOM_L_20231111_QP_gamma0_Gamma0_%s.tif" % pol))
            if not sao:
                continue
            s_ = leer_en_grilla(sao[0], g, "average")
            v = fg(p); ok = (v > 0) & np.isfinite(s_) & (s_ > 0)
            dif = A.db(v[ok]) - A.db(s_[ok])
            r = np.corrcoef(A.db(v[ok]), A.db(s_[ok]))[0, 1]
            log("Control con SAOCOM 11/11/2023 %s: ALOS-2 %.1f dB, SAOCOM %.1f dB (medianas); diferencia mediana %+.1f dB; r %.2f; %d pixeles"
                % (pol, np.median(A.db(v[ok])), np.median(A.db(s_[ok])), np.median(dif), r, ok.sum()))
    except Exception as e:                                      # noqa: BLE001
        log("Control con SAOCOM no realizado: %s" % e)
    log(".dim: %s\nGeoTIFF: %s\nRGB: %s" % (dim, tif, rgb))
    import shutil
    for tp in a.tp[1:]:
        otro = ruta_tp(tp, "02_Subsets_SNAP_QGIS", "ALOS2_gamma0")
        if os.path.exists(otro):
            shutil.rmtree(otro)
        shutil.copytree(base, otro)
        log("Copiado a %s" % otro)


if __name__ == "__main__":
    main()
