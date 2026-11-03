# -*- coding: utf-8 -*-
"""
funciones_comunes.py
====================
Las funciones que comparten los once practicos. Ningun script repite este
codigo: lo importa. Si hay que corregir algo (por ejemplo, la armonizacion de
Sentinel-2), se corrige UNA vez aqui y queda corregido en todo el curso.

Contenido, por bloque
---------------------
1. Grilla de un sitio ............ grilla_sitio()
2. Catalogo del Planetary Computer buscar_stac(), fecha_item()
3. Lectura en la grilla comun .... leer_en_grilla()  (lee solo la ventana, sin
                                   bajar la escena entera: los productos son COG)
4. Lectores por sensor ........... s2_reflectancia(), s2_mascara_valida(),
                                   s1_rtc(), alos2_mosaico(), copdem(),
                                   jrc_ocurrencia()
5. Unidades del radar ............ lin_a_db(), db_a_lin(), media_lineal_db()
6. Escritura y lectura ........... guardar_tif(), leer_tif()
7. Vectores ...................... rasterizar()
8. Umbrales ...................... umbral_otsu()
9. Bitacora ...................... Bitacora (imprime y guarda lo mismo)

Regla de unidades del curso: el radar se guarda y se opera en LINEAL. El dB
sirve para ver. Promediar en dB sesga hacia valores bajos (diapositiva 14 de
la presentacion 01), por eso media_lineal_db() promedia en lineal y recien
despues convierte.
"""
import os
import sys
import datetime as _dt

import numpy as np

from configuracion_comun import EPSG, PIXEL, NODATA, SITIOS

STAC_MPC = "https://planetarycomputer.microsoft.com/api/stac/v1"
URL_MPC = "https://planetarycomputer.microsoft.com"


# ============================================================ 1. GRILLA
def grilla_sitio(nombre, pixel=PIXEL, epsg=EPSG):
    """Grilla de trabajo de un sitio: proyeccion, transformacion, filas y columnas.

    Los bordes se ajustan a multiplos exactos del pixel. Asi dos rasteres del
    mismo sitio, aunque vengan de sensores distintos, tienen los bordes de
    pixel en el mismo lugar y se apilan sin remuestrear otra vez.
    """
    from pyproj import Transformer
    from rasterio.transform import from_origin

    lon0, lat0, lon1, lat1 = SITIOS[nombre]["bbox"]
    tr = Transformer.from_crs(4326, epsg, always_xy=True)
    xmin, ymin, xmax, ymax = tr.transform_bounds(lon0, lat0, lon1, lat1, densify_pts=21)
    xmin = np.floor(xmin / pixel) * pixel
    ymin = np.floor(ymin / pixel) * pixel
    xmax = np.ceil(xmax / pixel) * pixel
    ymax = np.ceil(ymax / pixel) * pixel
    ancho = int(round((xmax - xmin) / pixel))
    alto = int(round((ymax - ymin) / pixel))
    return {
        "sitio": nombre,
        "crs": "EPSG:%d" % epsg,
        "transform": from_origin(xmin, ymax, pixel, pixel),
        "width": ancho,
        "height": alto,
        "bounds": (xmin, ymin, xmax, ymax),
        "pixel": pixel,
        "bbox_wgs84": (lon0, lat0, lon1, lat1),
    }


# ============================================== 2. CATALOGO DEL PLANETARY COMPUTER
def buscar_stac(coleccion, nombre_sitio, desde, hasta, query=None, limite=500):
    """Busca en el catalogo STAC del Planetary Computer (no pide cuenta).

    Devuelve la lista de items ordenada por fecha. Las URL vienen firmadas:
    duran aproximadamente una hora; si un script queda abierto mas tiempo,
    se vuelve a correr y se firman de nuevo.
    """
    import pystac_client
    import planetary_computer

    cat = pystac_client.Client.open(STAC_MPC, modifier=planetary_computer.sign_inplace)
    busqueda = cat.search(
        collections=[coleccion],
        bbox=SITIOS[nombre_sitio]["bbox"],
        datetime="%s/%s" % (desde, hasta),
        query=query,
        max_items=limite,
    )
    items = list(busqueda.items())
    items.sort(key=lambda it: it.datetime or _dt.datetime(1900, 1, 1))
    return items


def fecha_item(item):
    """Fecha y hora UTC de un item STAC, tomadas de los METADATOS.

    Nunca se usa la fecha del archivo en el disco: suele ser la de descarga.
    """
    d = item.datetime or _dt.datetime.fromisoformat(
        item.properties["start_datetime"].replace("Z", "+00:00"))
    return d.strftime("%Y-%m-%d"), d.strftime("%H:%M")


# =========================================== 3. LECTURA EN LA GRILLA COMUN
_ENTORNO_GDAL = dict(
    GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR",
    CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif,.TIF,.tiff,.TIFF,.jp2,.vrt",
    GDAL_HTTP_MAX_RETRY="5",
    GDAL_HTTP_RETRY_DELAY="3",
)

_REMUESTREO = {
    "average": "average",
    "bilinear": "bilinear",
    "nearest": "nearest",
    "mode": "mode",
}


def leer_en_grilla(origen, grilla, remuestreo="average", banda=1,
                   nodata_origen=None, tipo="float32"):
    """Lee UNA banda de un raster (local o URL) y la devuelve en la grilla comun.

    Solo se transfiere la ventana que cae dentro del sitio: los productos del
    Planetary Computer son COG y permiten esa lectura parcial.

    remuestreo:
        "average"  -> agregar a un pixel mas grueso. Es el correcto para radar
                      en LINEAL y para reflectancias (diapositiva 14 de la
                      presentacion 01: "agregar el SAR en lineal").
        "bilinear" -> llevar a un pixel igual o mas fino, variables continuas.
        "nearest"  -> clases y mascaras (SCL de Sentinel-2, mascaras de NISAR).
    Devuelve un arreglo float32 con NaN donde no hay dato.
    """
    import rasterio
    from rasterio.enums import Resampling
    from rasterio.vrt import WarpedVRT

    # Las opciones de red solo para URL: GDAL_DISABLE_READDIR_ON_OPEN impediria
    # encontrar el .hdr de los productos ENVI de SNAP (.img + .hdr) en disco.
    entorno = _ENTORNO_GDAL if str(origen).startswith(("http", "/vsi")) else {}
    with rasterio.Env(**entorno):
        with rasterio.open(origen) as src:
            nd = src.nodata if nodata_origen is None else nodata_origen
            if src.crs is None and src.gcps[0]:
                # Producto en geometria de rango en el terreno, georreferenciado solo por puntos de enlace
                # (BIOMASS L1B DGM): WarpedVRT no usa los puntos de enlace y devolveria todo sin dato.
                # Se reproyecta con los puntos de enlace (rasterio.warp.reproject). Agregado el 21/10/2026.
                from rasterio.warp import reproject
                puntos, crs_puntos = src.gcps
                a = src.read(banda).astype("float32")
                if nd is not None and not np.isnan(nd):
                    a[a == nd] = np.nan
                if tipo.startswith("float"):
                    a[a <= 0] = np.nan          # en BIOMASS L1B, 0 = sin dato
                arr = np.full((grilla["height"], grilla["width"]), np.nan, dtype="float32")
                reproject(a, arr, gcps=puntos, src_crs=crs_puntos, dst_crs=grilla["crs"],
                          dst_transform=grilla["transform"], src_nodata=np.nan, dst_nodata=np.nan,
                          resampling=getattr(Resampling, _REMUESTREO[remuestreo]))
                return arr if tipo.startswith("float") else np.nan_to_num(arr).astype(tipo)
            # UNIFIED_SRC_NODATA=NO: cada banda usa su propio sin dato. Con el valor por defecto de
            # GDAL, en un raster de varias bandas (la pila del Tp2) un pixel cuenta como sin dato solo
            # si lo es en TODAS las bandas, y el promedio mezclaba -9999 con datos validos en el borde
            # de una banda que cubre parte del sitio (NISAR S, NovaSAR): valores de -7499 en el cubo
            # del Tp3. Corregido el 21/10/2026.
            with WarpedVRT(src, crs=grilla["crs"], transform=grilla["transform"],
                           width=grilla["width"], height=grilla["height"],
                           resampling=getattr(Resampling, _REMUESTREO[remuestreo]),
                           src_nodata=nd, nodata=np.nan if tipo.startswith("float") else 0,
                           dtype=tipo, UNIFIED_SRC_NODATA="NO") as vrt:
                arr = vrt.read(banda)
    if tipo.startswith("float"):
        arr = arr.astype("float32")
        if nd is not None and not np.isnan(nd):
            arr[arr == nd] = np.nan
    return arr


def leer_db_como_lineal(origen, grilla, banda=1):
    """Lee un raster en dB, lo pasa a LINEAL en su grilla original y recien
    entonces lo promedia hacia la grilla comun (el promedio de dB no es el dB
    del promedio: promediar en dB sesga hacia abajo)."""
    import rasterio
    from rasterio.io import MemoryFile
    from rasterio.vrt import WarpedVRT
    from rasterio.enums import Resampling

    with rasterio.open(origen) as src:
        x = src.read(banda).astype("float64")
        if src.nodata is not None and not np.isnan(src.nodata):
            x[x == src.nodata] = np.nan
        lin = np.where(np.isfinite(x), 10.0 ** (x / 10.0), np.nan).astype("float32")
        perfil = src.profile
    perfil.update(dtype="float32", nodata=np.nan, count=1, compress=None)
    with MemoryFile() as mem:
        with mem.open(**perfil) as tmp:
            tmp.write(lin, 1)
        with mem.open() as tmp:
            with WarpedVRT(tmp, crs=grilla["crs"], transform=grilla["transform"],
                           width=grilla["width"], height=grilla["height"],
                           resampling=Resampling.average, src_nodata=np.nan, nodata=np.nan) as vrt:
                return vrt.read(1).astype("float32")


# ================================================== 4. LECTORES POR SENSOR
# --- Sentinel-2 L2A ---------------------------------------------------------
# Desde la linea de base de procesamiento 04.00 (25 de enero de 2022) los
# numeros digitales de L2A traen un desplazamiento de +1000. Una escena de
# 2020 y otra de 2023 NO son comparables si no se descuenta. Esta funcion lo
# hace leyendo la linea de base de los metadatos de cada escena.
CLASES_SCL_VALIDAS = (4, 5, 6, 7, 11)   # vegetacion, suelo, agua, sin clasificar, nieve
NOMBRES_SCL = {0: "sin dato", 1: "saturado", 2: "pixel oscuro", 3: "sombra de nube",
               4: "vegetacion", 5: "suelo desnudo", 6: "agua", 7: "sin clasificar",
               8: "nube media", 9: "nube alta", 10: "cirro", 11: "nieve"}


class GrupoItems:
    """Varios items STAC de la MISMA pasada (mismo dia, mismo satelite y orbita relativa) que juntos
    cubren el sitio: los cuadros consecutivos de Sentinel-1 o las teselas de Sentinel-2 de un mismo
    paso. Se usa como un item comun: los lectores (s1_rtc, s2_reflectancia, s2_mascara_valida)
    hacen el mosaico (el primero con dato manda); fecha, hora y propiedades son las del primero."""

    def __init__(self, items):
        self.items = list(items)
        self.properties = self.items[0].properties
        self.datetime = self.items[0].datetime
        self.assets = self.items[0].assets
        self.id = " + ".join(it.id for it in self.items)

    def __len__(self):
        return len(self.items)


def agrupar_por_pasada(items):
    """Agrupa items STAC por (dia, plataforma, orbita relativa) y devuelve una lista de GrupoItems
    (o items sueltos si la pasada tiene uno solo), en el orden de aparicion."""
    grupos = {}
    for it in items:
        d = fecha_item(it)[0]
        clave = (d, it.properties.get("platform", ""), it.properties.get("sat:relative_orbit",
                                                                       it.properties.get("s2:datatake_id", "")))
        grupos.setdefault(clave, []).append(it)
    return [g[0] if len(g) == 1 else GrupoItems(g) for g in grupos.values()]


def _mosaico_items(item, leer):
    """Aplica leer(it) a cada item del grupo y une: el primero con dato manda."""
    if not isinstance(item, GrupoItems):
        return leer(item)
    out = None
    for it in item.items:
        a = leer(it)
        out = a if out is None else np.where(np.isfinite(out), out, a)
    return out


def _linea_base_s2(item):
    lb = item.properties.get("s2:processing_baseline")
    try:
        return float(lb)
    except (TypeError, ValueError):
        # Sin el dato en los metadatos: se decide por la fecha del cambio.
        fecha, _ = fecha_item(item)
        return 4.0 if fecha >= "2022-01-25" else 3.0


def s2_reflectancia(item, banda, grilla, remuestreo="average"):
    """Reflectancia de superficie (0 a 1) de una banda de Sentinel-2 L2A (item o GrupoItems)."""
    def leer(it):
        dn = leer_en_grilla(it.assets[banda].href, grilla, remuestreo, nodata_origen=0)
        desplazamiento = 1000.0 if _linea_base_s2(it) >= 4.0 else 0.0
        return (dn - desplazamiento) / 10000.0
    return _mosaico_items(item, leer)


def s2_mascara_valida(item, grilla):
    """Mascara de pixeles utiles segun la SCL, y la nubosidad DENTRO del sitio.

    La nubosidad que declara el catalogo (eo:cloud_cover) es la de la tesela
    entera de 110 x 110 km. Esta funcion cuenta dentro del sitio, que es lo
    que importa. Se informan las dos cifras, una al lado de la otra.
    """
    scl = _mosaico_items(item, lambda it: leer_en_grilla(it.assets["SCL"].href, grilla, "nearest",
                                                         nodata_origen=0).astype("float32"))
    scl = np.nan_to_num(scl, nan=0).astype("uint8")
    con_dato = scl > 0
    valido = np.isin(scl, CLASES_SCL_VALIDAS)
    n_dato = int(con_dato.sum())
    cobertura = 100.0 * n_dato / scl.size
    nubes = 100.0 * (con_dato & ~valido).sum() / n_dato if n_dato else float("nan")
    return valido, cobertura, nubes


def s2_escena_mas_limpia(nombre_sitio, fecha, grilla, dias=10, nube_max=20.0):
    """La pasada Sentinel-2 L2A con MENOS nube DENTRO del sitio en +/- dias de la fecha.

    Las teselas del mismo dia y la misma orbita se unen (GrupoItems): un sitio que cae
    en dos teselas se lee entero, no solo la parte de una.
    Devuelve (item o GrupoItems, mascara_valida, nubosidad_en_el_sitio) o (None, None, None).
    La nubosidad se cuenta en el sitio con la SCL, no con la de la tesela.
    """
    f = np.datetime64(fecha)
    items = buscar_stac("sentinel-2-l2a", nombre_sitio, str(f - dias), str(f + dias),
                        query={"eo:cloud_cover": {"lt": 80}})
    mejor = (None, None, None)
    for it in agrupar_por_pasada(items):
        valido, cobertura, nubes = s2_mascara_valida(it, grilla)
        if cobertura < 50 or not np.isfinite(nubes) or nubes > nube_max:
            continue
        if mejor[0] is None or nubes < mejor[2]:
            mejor = (it, valido, nubes)
    return mejor


def s1_rtc_mas_cercana(nombre_sitio, fecha, dias=6, orbita=None, grilla=None, cobertura_min=90.0):
    """La pasada Sentinel-1 RTC mas cercana a la fecha (+/- dias), o None.

    Devuelve un item o un GrupoItems con TODOS los cuadros de esa pasada (mismo dia
    y orbita), que se leen unidos.
    orbita: si se da (sat:relative_orbit), solo se aceptan escenas de esa
    orbita relativa: para comparar fechas la geometria de vision debe ser la
    misma (el doble rebote depende de la direccion de vuelo).
    grilla: si se da, se prefiere la pasada mas cercana que cubra al menos
    cobertura_min % del sitio (una orbita vecina puede tocar solo un borde);
    si ninguna llega, la de mayor cobertura.
    """
    f = np.datetime64(fecha)
    items = buscar_stac("sentinel-1-rtc", nombre_sitio, str(f - dias), str(f + dias))
    if orbita is not None:
        items = [it for it in items if it.properties.get("sat:relative_orbit") == orbita]
    if not items:
        return None
    dist = lambda it: abs((np.datetime64(fecha_item(it)[0]) - f).astype(int))   # noqa: E731
    pasadas = sorted(agrupar_por_pasada(items), key=dist)
    if grilla is None:
        return pasadas[0]
    mejor, mejor_cob = None, -1.0
    for p in pasadas:
        cob = 100.0 * float(np.isfinite(s1_rtc(p, "vv", grilla)).mean())
        if cob >= cobertura_min:
            return p
        if cob > mejor_cob:
            mejor, mejor_cob = p, cob
    return mejor


# --- Sentinel-1 RTC (Planetary Computer) -----------------------------------
def s1_rtc(item, pol, grilla, remuestreo="average"):
    """gamma0 LINEAL de Sentinel-1 RTC del Planetary Computer ("vv" o "vh"); item o GrupoItems."""
    def leer(it):
        g = leer_en_grilla(it.assets[pol.lower()].href, grilla, remuestreo)
        g[(g <= 0) | ~np.isfinite(g)] = np.nan
        return g
    return _mosaico_items(item, leer)


# --- ALOS-2 PALSAR-2: mosaico anual de JAXA ---------------------------------
def alos2_mosaico(item, pol, grilla, remuestreo="average"):
    """gamma0 LINEAL del mosaico anual ALOS-2 (JAXA), polarizacion "HH" o "HV".

    JAXA entrega numeros digitales. La conversion publicada es
        gamma0 [dB] = 10*log10(DN^2) - 83
    y en lineal  gamma0 = DN^2 * 10^(-8,3).
    El cuadrado se calcula ANTES de remuestrear, para promediar potencia.
    """
    import rasterio
    from rasterio.enums import Resampling
    from rasterio.vrt import WarpedVRT

    with rasterio.Env(**_ENTORNO_GDAL):
        with rasterio.open(item.assets[pol].href) as src:
            dn = src.read(1).astype("float64")
            pot = np.where(dn > 0, dn * dn * 10 ** (-8.3), np.nan).astype("float32")
            perfil = src.profile
    from rasterio.io import MemoryFile
    perfil.update(dtype="float32", nodata=np.nan, count=1, compress=None)
    with MemoryFile() as mem:
        with mem.open(**perfil) as tmp:
            tmp.write(pot, 1)
        with mem.open() as tmp:
            with WarpedVRT(tmp, crs=grilla["crs"], transform=grilla["transform"],
                           width=grilla["width"], height=grilla["height"],
                           resampling=getattr(Resampling, remuestreo),
                           src_nodata=np.nan, nodata=np.nan) as vrt:
                return vrt.read(1).astype("float32")


# --- NovaSAR-1 (banda S) del archivo del curso -------------------------------
def novasar_carpeta_grd(escena):
    """Carpeta del producto GRD de una escena NovaSAR (por numero de escena)."""
    import glob
    from configuracion_comun import NOVASAR

    patron = os.path.join(NOVASAR, "NovaSAR_01_%s_grd_*_HH" % escena, "NovaSAR_01_%s_grd_*" % escena)
    cands = [c for c in glob.glob(patron) if os.path.isdir(c)]
    if not cands:
        raise FileNotFoundError("No encuentro el GRD de la escena %s en %s" % (escena, NOVASAR))
    return cands[0]


def novasar_constante_calibracion(carpeta_grd):
    """Lee CalibrationConstant del metadata.xml (en las escenas del curso: 1E+05)."""
    import re

    with open(os.path.join(carpeta_grd, "metadata.xml"), encoding="utf-8", errors="ignore") as f:
        t = f.read()
    m = re.search(r"<CalibrationConstant>([^<]+)<", t)
    if not m:
        raise ValueError("El metadata.xml no trae CalibrationConstant: no se puede calibrar")
    return float(m.group(1))


def novasar_puntos_enlace(carpeta_grd):
    """Los puntos de enlace (TiePoint) del metadata.xml del GRD: Line, Pixel, Latitude, Longitude, Height.

    En las escenas del curso son 6 x 14 = 84 puntos repartidos en toda la franja, contra los 4 de
    esquina que trae el image_HH.tif. Devuelve una lista de GroundControlPoint (fila, columna, lon, lat).
    """
    import xml.etree.ElementTree as ET
    from rasterio.control import GroundControlPoint

    raiz = ET.parse(os.path.join(carpeta_grd, "metadata.xml")).getroot()
    gc = []
    for i, e in enumerate(raiz.iter("TiePoint")):
        gc.append(GroundControlPoint(row=float(e.findtext("Line")), col=float(e.findtext("Pixel")),
                                     x=float(e.findtext("Longitude")), y=float(e.findtext("Latitude")),
                                     z=float(e.findtext("Height") or 0), id=str(i + 1)))
    return gc


def novasar_sigma0(escena, grilla, desplazamiento_m=(0.0, 0.0), puntos_enlace="esquinas"):
    """sigma0 LINEAL de NovaSAR-1 GRD HH en la grilla comun.

    El GRD viene georreferenciado por puntos de enlace (GCP), sin
    transformacion afin. GDAL proyecta con esos puntos.

    El remuestreo usa la media cuadratica ("rms") de los numeros digitales:
        rms(DN)^2 = media(DN^2) = media de la POTENCIA.
    Asi el pixel de 10 m promedia potencia, que es lo correcto, y despues se
    calibra con sigma0 = media(DN^2) / CalibrationConstant.

    puntos_enlace: "esquinas" (por defecto, los 4 GCP del image_HH.tif: ajuste afin de toda la
    franja, con desplazamientos de cientos de metros y error de escala) o "todos" (los 84 puntos de
    enlace del metadata.xml; agregado el 23/10/2026 para el Tp8: deja un corrimiento chico y rigido).

    desplazamiento_m = (dx, dy): correccion de la georreferencia en metros,
    medida en el Tp3 (Tp3_02). En la presentacion 02 se midieron desfases de
    hasta 1120 m en estas escenas: no se usan sin medirlo.
    """
    import rasterio
    from rasterio.enums import Resampling
    from rasterio.transform import from_origin

    carpeta = novasar_carpeta_grd(escena)
    tif = os.path.join(carpeta, "image_HH.tif")
    k = novasar_constante_calibracion(carpeta)
    xmin, ymin, xmax, ymax = grilla["bounds"]
    dx, dy = desplazamiento_m
    # Desplazar el producto (dx, dy) equivale a leer la ventana desplazada (-dx, -dy).
    t = from_origin(xmin - dx, ymax - dy, grilla["pixel"], grilla["pixel"])
    from rasterio.warp import reproject

    dn = np.zeros((grilla["height"], grilla["width"]), dtype="float32")
    with rasterio.open(tif) as src:
        gcps, crs_gcp = src.gcps
        if puntos_enlace == "todos":
            gcps = novasar_puntos_enlace(carpeta)
        if not gcps:
            raise ValueError("El GRD %s no trae puntos de enlace (GCP)" % escena)
        # El image_HH.tif trae solo las 4 esquinas como GCP: la proyeccion es
        # un ajuste afin de la franja. Por eso hay desplazamientos de cientos
        # de metros que se miden y corrigen en el Tp3.
        # Con una banda del archivo como origen, rasterio usa los GCP del archivo e ignora gcps=:
        # para usar los puntos de enlace del metadata.xml se pasa el arreglo.
        origen = src.read(1) if puntos_enlace == "todos" else rasterio.band(src, 1)
        reproject(origen, dn, gcps=gcps, src_crs=crs_gcp,
                  dst_transform=t, dst_crs=grilla["crs"],
                  resampling=Resampling.rms, src_nodata=0, dst_nodata=0,
                  num_threads=2)
    dn = dn.astype("float64")
    sigma0 = np.where(dn > 0, dn * dn / k, np.nan).astype("float32")
    return sigma0, k


# --- NISAR GCOV (.h5) ----------------------------------------------------------
def nisar_gcov_en_grilla(ruta_h5, grilla, termino="HHHH", banda="LSAR", frecuencia="A"):
    """gamma0 LINEAL de un GCOV de NISAR, recortado y llevado a la grilla comun.

    Lee del .h5 solo la ventana del sitio (h5py) y despues la proyecta.
    termino: HHHH (copolarizada) o HVHV (cruzada).
    banda  : LSAR (banda L, NASA) o SSAR (banda S, ISRO).
    Se usa SOLO la frecuencia A: la B (80 m en los GCOV de banda L del curso)
    no se usa.
    """
    import h5py
    from rasterio.enums import Resampling
    from rasterio.transform import from_origin
    from pyproj import Transformer

    base = "/science/%s/GCOV/grids/frequency%s/" % (banda, frecuencia)
    with h5py.File(ruta_h5, "r") as h:
        x = h[base + "xCoordinates"][:]
        y = h[base + "yCoordinates"][:]
        proy = h[base + "projection"]
        # El codigo EPSG es el VALOR del dataset "projection" (tambien figura
        # como atributo epsg_code en algunas versiones del producto).
        epsg = int(np.array(proy[()]).ravel()[0]) if proy.shape is not None else 0
        if epsg < 1000 and "epsg_code" in proy.attrs:
            epsg = int(np.array(proy.attrs["epsg_code"]).ravel()[0])
        tr = Transformer.from_crs(grilla["crs"], epsg, always_xy=True)
        x0, y0, x1, y1 = tr.transform_bounds(*grilla["bounds"], densify_pts=21)
        if x1 < x.min() or x0 > x.max() or y1 < y.min() or y0 > y.max():
            raise ValueError("El granulo %s no cubre el sitio %s"
                             % (os.path.basename(ruta_h5), grilla["sitio"]))
        dx = float(x[1] - x[0])
        dy = float(y[1] - y[0])          # negativo: las filas van de norte a sur
        margen = 3
        c0 = max(int(np.searchsorted(x, x0)) - margen, 0)
        c1 = min(int(np.searchsorted(x, x1)) + margen, x.size)
        if dy < 0:
            f0 = max(int(np.searchsorted(-y, -y1)) - margen, 0)
            f1 = min(int(np.searchsorted(-y, -y0)) + margen, y.size)
        else:
            f0 = max(int(np.searchsorted(y, y0)) - margen, 0)
            f1 = min(int(np.searchsorted(y, y1)) + margen, y.size)
        if c1 <= c0 or f1 <= f0:
            raise ValueError("El granulo no cubre el sitio %s" % grilla["sitio"])
        bloque = h[base + termino][f0:f1, c0:c1].astype("float32")
        # Mascara del producto (dataset "mask"): 1..n = numero de subfranja,
        # muestra VALIDA; 0 = muestra parcialmente enfocada o invalida;
        # 255 = fuera de la adquisicion. Sin esta mascara, el borde de la
        # franja entra con valores minusculos (del orden de 1e-14: -130 a -140 dB; en los GCOV del Delta, alrededor de -133 dB) que arruinan cualquier
        # promedio.
        if (base + "mask") in h:
            m = h[base + "mask"][f0:f1, c0:c1]
            bloque[(m == 0) | (m == 255)] = np.nan
    bloque[(bloque <= 0) | ~np.isfinite(bloque)] = np.nan
    if not np.isfinite(bloque).any():
        raise ValueError("El granulo %s no tiene muestras validas sobre %s"
                         % (os.path.basename(ruta_h5), grilla["sitio"]))
    from rasterio.warp import reproject

    origen_x = float(x[c0]) - dx / 2.0
    origen_y = float(y[f0]) - dy / 2.0
    t_origen = from_origin(origen_x, origen_y, abs(dx), abs(dy))
    salida = np.full((grilla["height"], grilla["width"]), np.nan, dtype="float32")
    # Pixel de origen mas fino que la grilla: se promedia (potencia, lineal).
    # Pixel de origen igual o mas grueso (20 m -> 10 m): bilineal.
    rem = Resampling.average if abs(dx) < grilla["pixel"] else Resampling.bilinear
    reproject(bloque, salida, src_transform=t_origen, src_crs="EPSG:%d" % epsg,
              src_nodata=np.nan, dst_transform=grilla["transform"],
              dst_crs=grilla["crs"], dst_nodata=np.nan, resampling=rem)
    return salida


# --- Modelos de elevacion y agua permanente ---------------------------------
def copdem(nombre_sitio, grilla):
    """Copernicus DEM GLO-30 (alturas sobre el geoide EGM2008) en la grilla."""
    items = buscar_stac("cop-dem-glo-30", nombre_sitio, "2000-01-01", "2030-01-01")
    if not items:
        raise RuntimeError("El Planetary Computer no devolvio teselas GLO-30 para %s" % nombre_sitio)
    acum = np.full((grilla["height"], grilla["width"]), np.nan, dtype="float32")
    for it in items:
        a = leer_en_grilla(it.assets["data"].href, grilla, "bilinear")
        acum = np.where(np.isnan(acum), a, acum)
    return acum, items


def jrc_ocurrencia(nombre_sitio, grilla):
    """Ocurrencia de agua 1984-2021 (JRC Global Surface Water), 0 a 100 %."""
    items = buscar_stac("jrc-gsw", nombre_sitio, "1984-01-01", "2030-01-01")
    if not items:
        raise RuntimeError("El Planetary Computer no devolvio teselas JRC-GSW para %s" % nombre_sitio)
    acum = np.full((grilla["height"], grilla["width"]), np.nan, dtype="float32")
    for it in items:
        a = leer_en_grilla(it.assets["occurrence"].href, grilla, "nearest", nodata_origen=255)
        acum = np.where(np.isnan(acum), a, acum)
    return acum, items


# ================================================ 5. UNIDADES DEL RADAR
def lin_a_db(x):
    """Lineal -> dB. Ceros y negativos quedan sin dato (NaN), no en -inf."""
    x = np.asarray(x, dtype="float64")
    out = np.full(x.shape, np.nan)
    ok = np.isfinite(x) & (x > 0)
    out[ok] = 10.0 * np.log10(x[ok])
    return out.astype("float32")


def db_a_lin(x):
    """dB -> lineal."""
    return (10.0 ** (np.asarray(x, dtype="float64") / 10.0)).astype("float32")


def media_lineal_db(valores_lineales):
    """Promedio CORRECTO de radar: se promedia en lineal y se informa en dB."""
    v = np.asarray(valores_lineales, dtype="float64")
    v = v[np.isfinite(v) & (v > 0)]
    if v.size == 0:
        return float("nan")
    return float(10.0 * np.log10(v.mean()))


# ================================================ 6. ESCRITURA Y LECTURA
def unidad_de_banda(nombre):
    """Unidad probable de una banda segun su nombre (se escribe en la etiqueta UNIDAD de cada banda)."""
    n = nombre.lower()
    if ("clase" in n or n.startswith(("mascara", "agua_", "veredicto", "version", "votos", "severidad", "n_"))
            or "votaron" in n or "codigo" in n):
        return "sin unidad (codigo o conteo)"
    if "dias" in n:
        return "dias"
    if "meses" in n:
        return "meses"
    if "_cv_" in n or n.startswith("cv"):
        return "sin unidad (coeficiente de variacion)"
    if "importancia" in n or "susceptib" in n:
        return "sin unidad (valor relativo)"
    if "prob" in n:
        return "probabilidad 0-1"
    if n.endswith("_db") or "_db_" in n or n.endswith("db"):
        return "dB"
    if "coh" in n:
        return "coherencia 0-1"
    if "sigma0" in n:
        return "sigma0 lineal"
    if "beta0" in n:
        return "beta0 lineal"
    if "gamma0" in n or n.startswith(("c_v", "c_h", "l_h", "l_v", "s_h", "x_h", "x_v", "p_h", "p_v")) \
            or n in ("vv", "vh", "hh", "hv"):
        return "gamma0 lineal"
    if n.startswith(("opt_", "b0", "b1", "b8")) or "reflect" in n:
        return "reflectancia 0-1"
    if n.startswith(("ndvi", "nbr", "dnbr", "rdnbr", "mndwi", "ndwi", "dndvi")):
        return "indice (sin unidad)"
    if n.endswith("_m") or "altura" in n or "profundidad" in n or "cota" in n or n.startswith(("h_", "mde", "dem")):
        return "m"
    if "agb" in n or "biomasa" in n:
        return "Mg/ha"
    if "vel" in n and "mm" in n:
        return "mm/ano"
    return "ver PROCESO"


def guardar_tif(ruta, capas, grilla, fuente, proceso, script=None, unidades=None):
    """Escribe un GeoTIFF float32 con una banda por capa y su documentacion.

    capas   : dict ordenado {nombre_de_banda: arreglo}
    fuente  : la cita de los datos (organismo, sensor, fecha, URL). Queda dentro
              del archivo, en los metadatos, para que viaje con el raster.
    proceso : que se hizo, en una frase.
    unidades: dict opcional {nombre_de_banda: unidad}. Si falta, la unidad se deduce
              del nombre (unidad_de_banda) y queda en la etiqueta UNIDAD de cada banda.
    """
    import rasterio

    os.makedirs(os.path.dirname(os.path.abspath(ruta)), exist_ok=True)
    nombres = list(capas.keys())
    perfil = dict(driver="GTiff", dtype="float32", count=len(nombres),
                  width=grilla["width"], height=grilla["height"],
                  crs=grilla["crs"], transform=grilla["transform"],
                  nodata=NODATA, compress="deflate", predictor=3,
                  tiled=True, blockxsize=256, blockysize=256, BIGTIFF="IF_SAFER")
    with rasterio.open(ruta, "w", **perfil) as dst:
        for i, n in enumerate(nombres, start=1):
            a = np.asarray(capas[n], dtype="float32").copy()
            a[~np.isfinite(a)] = NODATA
            dst.write(a, i)
            dst.set_band_description(i, n)
            dst.update_tags(i, UNIDAD=(unidades or {}).get(n) or unidad_de_banda(n))
        dst.update_tags(
            FUENTE=fuente,
            PROCESO=proceso,
            SCRIPT=script or os.path.basename(sys.argv[0]),
            FECHA_PROCESO=_dt.datetime.now().strftime("%Y-%m-%d %H:%M"),
            UNIDADES="por banda: ver la etiqueta UNIDAD de cada banda (gdalinfo o QGIS > Propiedades > Informacion)",
        )
    return ruta


def leer_tif(ruta):
    """Devuelve ({nombre_de_banda: arreglo con NaN}, perfil, etiquetas)."""
    import rasterio

    with rasterio.open(ruta) as src:
        capas = {}
        for i in range(1, src.count + 1):
            a = src.read(i).astype("float32")
            if src.nodata is not None:
                a[a == src.nodata] = np.nan
            nombre = src.descriptions[i - 1] or "banda_%d" % i
            capas[nombre] = a
        return capas, src.profile, src.tags()


def grilla_de_tif(ruta):
    """La grilla de un GeoTIFF existente, en el mismo formato que grilla_sitio()."""
    import rasterio

    with rasterio.open(ruta) as src:
        return {"sitio": os.path.basename(ruta), "crs": src.crs.to_string(),
                "transform": src.transform, "width": src.width,
                "height": src.height, "bounds": tuple(src.bounds),
                "pixel": src.transform.a}


# ==================================================== 7b. MASCARA DE AGUA PARA LA ALTURA FH (22/10/2026)
# La altura del bosque FH de BIOMASS L2A da valores (10 a 30 m) sobre rios, lagunas y el embalse: no son
# altura de bosque. Toda medicion de FH (medianas por clase, comparacion con GEDI o ATL08, mapas) se hace
# con el agua enmascarada.
AGUA_MAPBIOMAS = (26, 31, 33)       # cuerpo de agua, acuicultura, rios, lagunas, lagos y oceano
UMBRAL_JRC_AGUA = 50.0              # ocurrencia JRC 1984-2021 (%): agua habitual


def mascara_agua(carpeta_qg, sitio, grilla, umbral_jrc=UMBRAL_JRC_AGUA):
    """True donde hay agua en la grilla dada: mas de la mitad del pixel con agua en MapBiomas (ultimo anio,
    clases 26, 31 y 33) o una ocurrencia JRC media de umbral_jrc % o mas. Devuelve (mascara, texto)."""
    import glob
    import rasterio
    from rasterio.enums import Resampling
    from rasterio.warp import reproject

    agua = np.zeros((grilla["height"], grilla["width"]), bool)
    usadas = []
    fm = sorted(glob.glob(os.path.join(carpeta_qg, "%s_MapBiomas_cobertura_*.tif" % sitio)))
    if fm:
        with rasterio.open(fm[0]) as s:
            c = s.read(s.count)
            anio = (s.descriptions[-1] or "").split("_")[-1]
            fr = np.full(agua.shape, np.nan, "float32")
            reproject(np.where(c > 0, np.isin(c, AGUA_MAPBIOMAS), np.nan).astype("float32"), fr,
                      src_transform=s.transform, src_crs=s.crs, src_nodata=np.nan,
                      dst_transform=grilla["transform"], dst_crs=grilla["crs"], dst_nodata=np.nan,
                      resampling=Resampling.average)
        agua |= np.nan_to_num(fr) > 0.5
        usadas.append("MapBiomas %s (clases 26, 31 y 33)" % anio)
    fj = sorted(glob.glob(os.path.join(carpeta_qg, "%s_JRC_GSW_ocurrencia.tif" % sitio)))
    if fj:
        j = leer_en_grilla(fj[0], grilla, "average", nodata_origen=255)
        agua |= np.nan_to_num(j) >= umbral_jrc
        usadas.append("JRC ocurrencia >= %g %%" % umbral_jrc)
    texto = "agua de %s" % " o ".join(usadas) if usadas else "SIN mascara de agua (no hay MapBiomas ni JRC)"
    return agua, texto


def fh_sin_agua(ruta_fh, carpeta_qg, sitio):
    """Lee la altura FH y su calidad en su grilla propia y las deja en NaN sobre el agua.
    Devuelve (fh, calidad, agua, grilla, texto)."""
    import rasterio

    g = grilla_de_tif(ruta_fh)
    with rasterio.open(ruta_fh) as s:
        fh = s.read(1).astype("float32")
        cal = s.read(2).astype("float32") if s.count > 1 else np.full(fh.shape, np.nan, "float32")
    agua, texto = mascara_agua(carpeta_qg, sitio, g)
    fh[agua] = np.nan
    cal[agua] = np.nan
    return fh, cal, agua, g, texto


# ==================================================== 7. VECTORES
def rasterizar(ruta_vector, grilla, campo=None, valor=1, capa=None, todos_los_tocados=False):
    """Pasa poligonos (GeoPackage o shapefile) a la grilla. 0 = fuera.

    todos_los_tocados=True marca todo pixel que el poligono toca (no solo
    aquellos cuyo centro cae adentro): sirve cuando los poligonos son mas
    chicos que el pixel (por ejemplo, edificios en una grilla de 80 m).
    """
    import geopandas as gpd
    from rasterio import features

    gdf = gpd.read_file(ruta_vector, layer=capa) if capa else gpd.read_file(ruta_vector)
    gdf = gdf.to_crs(grilla["crs"])
    if campo:
        formas = ((g, int(v)) for g, v in zip(gdf.geometry, gdf[campo]))
    else:
        formas = ((g, valor) for g in gdf.geometry)
    return features.rasterize(formas, out_shape=(grilla["height"], grilla["width"]),
                              transform=grilla["transform"], fill=0, dtype="int32",
                              all_touched=todos_los_tocados)


def capa_vacia(ruta, capa, campos, tipo="Polygon", crs=None):
    """Crea un GeoPackage con una capa VACIA para digitalizar en QGIS.

    campos: {nombre: "int32" | "str" | "float64"}. tipo: "Polygon" o "Point".
    El tipo de geometria se declara explicitamente: una capa vacia creada sin
    tipo queda como "Unknown" y QGIS no habilita la herramienta de dibujo.
    """
    import geopandas as gpd
    import pandas as pd
    from configuracion_comun import EPSG

    crs = crs or EPSG
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    gdf = gpd.GeoDataFrame({k: pd.Series(dtype=v) for k, v in campos.items()},
                           geometry=gpd.GeoSeries([], crs=crs), crs=crs)
    gdf.to_file(ruta, layer=capa, driver="GPKG", engine="pyogrio", geometry_type=tipo)
    return ruta


# ==================================================== 8. UMBRALES
def umbral_otsu(valores, n_bins=256):
    """Umbral de Otsu sobre los valores finitos. Devuelve (umbral, n_usados).

    Otsu supone un histograma con DOS modas (por ejemplo agua y tierra). Si el
    sitio casi no tiene agua, el umbral cae en cualquier lado: por eso cada
    practico muestra el histograma y pide justificar el valor elegido.
    """
    from skimage.filters import threshold_otsu

    v = np.asarray(valores, dtype="float64")
    v = v[np.isfinite(v)]
    if v.size < 100:
        raise ValueError("Muy pocos valores validos para Otsu (%d)" % v.size)
    # Corregido el 22/10/2026 (Tp5, SAOCOM): unos pocos valores extremos (bordes de escena, cocientes
    # contra pixeles casi nulos, de +-60 dB) estiran el rango del histograma y Otsu cae en la cola
    # (19 dB en vez de 3 dB). Se calcula sobre el 99 % central, el mismo rango que muestra el histograma.
    lo, hi = np.percentile(v, [0.5, 99.5])
    v = v[(v >= lo) & (v <= hi)]
    return float(threshold_otsu(v, nbins=n_bins)), int(v.size)


# ==================================================== 9. BITACORA
class Bitacora:
    """Imprime en pantalla y guarda lo mismo en un archivo .log.

    Uso:
        log = Bitacora(ruta_tp("Tp5", "05_Resultados", "06_Control_calidad"), "Tp5_02")
        log("Busco escenas...")
        log.cerrar()
    """

    def __init__(self, carpeta, nombre):
        os.makedirs(carpeta, exist_ok=True)
        self.ruta = os.path.join(carpeta, nombre + ".log")
        self._f = open(self.ruta, "w", encoding="utf-8")
        self("=" * 72)
        self("%s   %s" % (nombre, _dt.datetime.now().strftime("%Y-%m-%d %H:%M")))
        self("Python %s   %s" % (sys.version.split()[0], sys.executable))
        self("=" * 72)

    def __call__(self, *partes):
        s = " ".join(str(p) for p in partes)
        print(s, flush=True)
        self._f.write(s + "\n")
        self._f.flush()

    def titulo(self, texto):
        self("")
        self("-" * 72)
        self(texto)
        self("-" * 72)

    def cerrar(self, siguiente=None):
        if siguiente:
            self("")
            self("SIGUIENTE PASO: " + siguiente)
        self("Bitacora guardada en: " + self.ruta)
        self._f.close()


def fuente_mpc(organismo, producto, fecha, hora=None, detalle=""):
    """Cita uniforme para datos tomados del Planetary Computer."""
    h = (", %s UTC" % hora) if hora else ""
    d = (" " + detalle) if detalle else ""
    return "%s. %s, %s%s.%s Microsoft Planetary Computer: %s" % (
        organismo, producto, fecha, h, d, URL_MPC)


# ============================================ 4b. COMPUESTOS DE TEMPORADA (24/10/2026)
# Una escena suelta mezcla en el mapa la humedad del suelo de ese dia, el riego, la cosecha y el
# moteado (speckle) del radar. La practica habitual para mapas de cobertura y de cambio con
# Sentinel-1 y Sentinel-2 es trabajar con COMPUESTOS: la media de todas las pasadas de radar de una
# misma orbita (en LINEAL) y la mediana de todas las escenas opticas sin nube de una ventana.
# Las dos funciones devuelven tambien cuantas observaciones entraron en cada pixel.
def _orbita_por_huella(items, nombre_sitio):
    """La orbita relativa cuyas pasadas cubren mas del sitio, segun la HUELLA del catalogo (sin leer imagenes)."""
    from shapely.geometry import box, shape
    sitio = box(*SITIOS[nombre_sitio]["bbox"])
    cob = {}
    for it in items:
        o = it.properties.get("sat:relative_orbit")
        a = shape(it.geometry).intersection(sitio).area / sitio.area
        d = fecha_item(it)[0]
        cob.setdefault(o, {}).setdefault(d, 0.0)
        cob[o][d] += a
    return max(cob, key=lambda o: np.median([min(v, 1.0) for v in cob[o].values()]))


def s1_rtc_compuesto(nombre_sitio, desde, hasta, grilla, orbita=None, pols=("vv", "vh"), cobertura_min=50.0,
                     max_pasadas=5):
    """Media en LINEAL de las pasadas Sentinel-1 RTC entre desde y hasta, de UNA orbita relativa.

    orbita: sat:relative_orbit. Si es None, la que mas cubre el sitio segun la huella del catalogo.
    max_pasadas: se usan las pasadas mas cercanas al centro de la ventana (5 alcanzan para bajar el
    moteado y la humedad de un dia; leer mas solo alarga la corrida).
    Devuelve ({pol: media lineal}, n_pasadas por pixel, lista de fechas, orbita) o (None, None, [], None).
    """
    import time
    items = buscar_stac("sentinel-1-rtc", nombre_sitio, desde, hasta)
    if not items:
        return None, None, [], None
    if orbita is None:
        orbita = _orbita_por_huella(items, nombre_sitio)
    items = [it for it in items if it.properties.get("sat:relative_orbit") == orbita]
    centro = np.datetime64(desde) + (np.datetime64(hasta) - np.datetime64(desde)) // 2
    pasadas = sorted(agrupar_por_pasada(items), key=lambda p: abs((np.datetime64(fecha_item(p)[0]) - centro).astype(int)))
    suma = {p: None for p in pols}
    n = None
    fechas = []
    for p in pasadas:
        if len(fechas) >= max_pasadas:
            break
        t0 = time.time()
        capas = {pol: s1_rtc(p, pol, grilla) for pol in pols}
        ok = np.isfinite(capas[pols[0]])
        print("    Sentinel-1 %s orbita %s: cubre %.0f %% del sitio (%.0f s)"
              % (fecha_item(p)[0], orbita, 100.0 * ok.mean(), time.time() - t0), flush=True)
        if 100.0 * ok.mean() < cobertura_min:
            continue
        fechas.append(fecha_item(p)[0])
        for pol in pols:
            x = np.where(np.isfinite(capas[pol]), capas[pol], 0.0)
            suma[pol] = x if suma[pol] is None else suma[pol] + x
        n = ok.astype("float32") if n is None else n + ok
    if n is None:
        return None, None, [], orbita
    fechas.sort()
    media = {pol: np.where(n > 0, suma[pol] / np.maximum(n, 1), np.nan).astype("float32") for pol in pols}
    return media, n, fechas, orbita


def s2_compuesto(nombre_sitio, desde, hasta, grilla, bandas=("B02", "B03", "B04", "B08", "B11"),
                 nube_max_sitio=60.0, nube_max_tesela=70.0, max_escenas=5, excluir=()):
    """Mediana por pixel de las escenas Sentinel-2 L2A entre desde y hasta, usando solo los pixeles
    validos de la SCL (sin nube, sombra ni cirros).

    Se recorren las pasadas de menos a mas nube de la tesela; se descartan las que tienen mas de
    nube_max_sitio % de nube DENTRO del sitio, y se usan hasta max_escenas.
    excluir: fechas (AAAA-MM-DD) que NO entran al compuesto, por ejemplo la imagen que se usa como
    referencia para validar: la referencia tiene que ser independiente del mapa.
    Devuelve ({banda: mediana de reflectancia}, n_validas por pixel, lista de (fecha, nube %)) o (None, None, []).
    """
    import time
    import warnings
    items = buscar_stac("sentinel-2-l2a", nombre_sitio, desde, hasta,
                        query={"eo:cloud_cover": {"lt": nube_max_tesela}})
    pasadas = sorted(agrupar_por_pasada(items), key=lambda p: p.properties.get("eo:cloud_cover", 100))
    usadas = []
    for it in pasadas:
        if len(usadas) >= max_escenas:
            break
        if fecha_item(it)[0] in excluir:
            print("    Sentinel-2 %s: EXCLUIDA (referencia de la validacion)" % fecha_item(it)[0], flush=True)
            continue
        t0 = time.time()
        valido, cobertura, nubes = s2_mascara_valida(it, grilla)
        print("    Sentinel-2 %s: nube en el sitio %.1f %%, cubre %.0f %% (%.0f s)"
              % (fecha_item(it)[0], nubes, cobertura, time.time() - t0), flush=True)
        if cobertura < 50 or not np.isfinite(nubes) or nubes > nube_max_sitio:
            continue
        usadas.append((it, valido, fecha_item(it)[0], nubes))
    if not usadas:
        return None, None, []
    usadas.sort(key=lambda u: u[2])
    n = np.sum([u[1] for u in usadas], axis=0).astype("float32")
    med = {}
    for b in bandas:
        t0 = time.time()
        pila = np.stack([np.where(v, s2_reflectancia(it, b, grilla), np.nan) for it, v, _, _ in usadas])
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            med[b] = np.nanmedian(pila, axis=0).astype("float32")
        del pila
        print("    Sentinel-2 banda %s: mediana de %d escenas (%.0f s)" % (b, len(usadas), time.time() - t0), flush=True)
    return med, n, [(f, round(float(nb), 1)) for _, _, f, nb in usadas]


# ============================================ 4c. ENTRENAMIENTO CON MAPBIOMAS (24/10/2026)
# Clases del Tp10 a partir de la leyenda oficial de MapBiomas Argentina (Coleccion 3).
CLASES_URBANO_MB = {1: ("urbano", (24,)),
                    2: ("vegetacion lenosa", (3, 4, 5, 6, 9, 35, 36)),
                    3: ("herbaceas y cultivos", (11, 12, 13, 15, 18, 19, 20, 21, 39, 40, 41, 46, 47, 48, 62, 63)),
                    4: ("agua", (26, 31, 33)),
                    5: ("suelo desnudo y otras no vegetadas", (22, 23, 25, 29, 30))}


def entrenamiento_mapbiomas(ruta_mb, anio, grilla, anios_estables=3, n_total=20000, minimo=600, semilla=2026,
                            clases=CLASES_URBANO_MB, anio_inicial=1985):
    """Pixeles de entrenamiento tomados de MapBiomas: solo los ESTABLES (la misma clase en los
    anios_estables anios que terminan en anio) y en PROPORCION a la superficie de cada clase
    (con un minimo por clase). Devuelve (raster de codigos, 0 = no es entrenamiento; tabla de conteos).

    Por que proporcional: un Random Forest entrenado con clases equilibradas supone que todas las
    clases ocupan lo mismo y sobrestima las clases chicas (la ciudad es menos del 5 % del sitio).
    """
    mb = [leer_en_grilla(ruta_mb, grilla, "nearest", banda=a - anio_inicial + 1) for a in range(anio - anios_estables + 1, anio + 1)]
    estable = np.all([m == mb[-1] for m in mb], axis=0)
    cod = np.zeros(mb[-1].shape, "int32")
    for k, (_, valores) in clases.items():
        cod[estable & np.isin(mb[-1], valores)] = k
    cuenta = {k: int((cod == k).sum()) for k in clases}
    total = sum(cuenta.values())
    rng = np.random.default_rng(semilla)
    salida = np.zeros_like(cod)
    filas = []
    for k in clases:
        idx = np.flatnonzero(cod.ravel() == k)
        n = min(idx.size, max(minimo, int(round(n_total * cuenta[k] / total)))) if total else 0
        if n:
            salida.ravel()[rng.choice(idx, n, replace=False)] = k
        filas.append({"codigo": k, "clase": clases[k][0], "pixeles_estables": cuenta[k],
                      "porcentaje_del_sitio_con_dato": round(100.0 * cuenta[k] / total, 2) if total else 0,
                      "pixeles_de_entrenamiento": int(n)})
    return salida, filas
