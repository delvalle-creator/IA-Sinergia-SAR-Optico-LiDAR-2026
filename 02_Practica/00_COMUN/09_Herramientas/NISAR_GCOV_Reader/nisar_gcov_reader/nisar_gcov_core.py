# -*- coding: utf-8 -*-
"""
nisar_gcov_core
===============

Lector autonomo de productos NISAR GCOV (Nivel 2, HDF5).

No depende de ningun otro plugin, no registra proveedores de datos
ni modifica opciones globales de GDAL/QGIS/SNAP: solo lee el HDF5 y
escribe archivos nuevos (GeoTIFF o BEAM-DIMAP) en la carpeta de salida.

Backends de lectura, en orden de preferencia:
  1) GDAL multidimensional (osgeo.gdal, disponible dentro de QGIS)
  2) h5py (si esta instalado)

Autor: generado para H. del Valle. Uso libre.
"""

import os
import re
import math

try:
    from osgeo import gdal, osr
    gdal.UseExceptions()
    osr.UseExceptions()
    _HAS_GDAL = True
except Exception:  # pragma: no cover
    _HAS_GDAL = False

try:
    import h5py
    _HAS_H5PY = True
except Exception:
    _HAS_H5PY = False

import numpy as np


X_NAMES = ("xCoordinates", "x_coordinates", "x", "easting", "longitude")
Y_NAMES = ("yCoordinates", "y_coordinates", "y", "northing", "latitude")

# Datasets que acompanan a las polarizaciones pero no son backscatter
AUX_NAMES = ("mask", "numberOfLooks", "rtcGammaToSigmaFactor",
             "inputDataExceptionMask",
             "rtcAreaNormalizationFactorGamma0ToBeta0",
             "rtcAreaNormalizationFactorGamma0ToSigma0")

# Terminos de covarianza tipicos de GCOV (diagonal = potencia real)
POL_RE = re.compile(r"^(HH|HV|VH|VV|RH|RV|LH|LV)(HH|HV|VH|VV|RH|RV|LH|LV)$")


class Band(object):
    """Una capa 2D exportable dentro de una grilla."""

    def __init__(self, name, path, shape, dtype, is_pol, is_aux, is_complex=False):
        self.name = name
        self.path = path            # ruta interna HDF5
        self.shape = shape          # (ny, nx)
        self.dtype = dtype          # numpy dtype string
        self.is_pol = is_pol        # termino de covarianza
        self.is_aux = is_aux        # mask / numberOfLooks / etc.
        self.is_complex = is_complex  # termino fuera de la diagonal (cuadripolar)

    @property
    def is_diagonal(self):
        m = POL_RE.match(self.name)
        return bool(m) and m.group(1) == m.group(2)

    def __repr__(self):
        return "<Band %s %s %s>" % (self.name, self.shape, self.dtype)


class Grid(object):
    """Una grilla geocodificada (p. ej. .../grids/frequencyA)."""

    def __init__(self, path, x, y, epsg, wkt, bands):
        self.path = path
        self.x = x
        self.y = y
        self.epsg = epsg
        self.wkt = wkt
        self.bands = bands
        # ventana de recorte (por defecto, la grilla entera)
        self.col0 = 0
        self.row0 = 0
        self.ncols = len(x)
        self.nrows = len(y)

    @property
    def nx(self):
        return len(self.x)

    @property
    def ny(self):
        return len(self.y)

    @property
    def geotransform(self):
        """GeoTransform de la ventana activa (coordenadas de centro de pixel)."""
        x = self.x
        y = self.y
        dx = float(x[1] - x[0]) if len(x) > 1 else 1.0
        dy = float(y[1] - y[0]) if len(y) > 1 else -1.0
        return (float(x[self.col0]) - dx / 2.0, dx, 0.0,
                float(y[self.row0]) - dy / 2.0, 0.0, dy)

    @property
    def recortada(self):
        return (self.col0, self.row0, self.ncols, self.nrows) != (0, 0, self.nx, self.ny)

    def recortar(self, minx, miny, maxx, maxy):
        """Limita la grilla a un rectangulo, en las coordenadas del producto."""
        cols = np.where((self.x >= minx) & (self.x <= maxx))[0]
        rows = np.where((self.y >= miny) & (self.y <= maxy))[0]
        if cols.size == 0 or rows.size == 0:
            raise ValueError(
                "El recorte no intersecta la grilla %s. Extension disponible: "
                "X %.0f a %.0f , Y %.0f a %.0f"
                % (self.label, float(self.x.min()), float(self.x.max()),
                   float(self.y.min()), float(self.y.max())))
        self.col0 = int(cols[0])
        self.ncols = int(cols[-1] - cols[0] + 1)
        self.row0 = int(rows[0])
        self.nrows = int(rows[-1] - rows[0] + 1)
        return self

    @property
    def label(self):
        return self.path.strip("/").split("/")[-1]

    def band(self, name):
        for b in self.bands:
            if b.name == name:
                return b
        return None

    def __repr__(self):
        return "<Grid %s %dx%d EPSG:%s %d bandas>" % (
            self.path, self.nx, self.ny, self.epsg, len(self.bands))


# ---------------------------------------------------------------------------
# Backend GDAL multidimensional
# ---------------------------------------------------------------------------

def _md_read(arr):
    """
    Lee un MDArray como arreglo de numpy.

    GDAL 3.8 devuelve un arreglo desde Read(); las versiones mas nuevas (las que
    trae QGIS) devuelven un bytearray crudo, que hay que interpretar con
    ReadAsArray. Se prueban las dos formas.
    """
    try:
        a = arr.ReadAsArray()
        if a is not None:
            return np.asarray(a)
    except Exception:
        pass
    a = arr.Read()
    if isinstance(a, (bytes, bytearray, memoryview)):
        raise ValueError("lectura cruda no interpretable")
    return np.asarray(a)


def _gdal_attr(obj, names):
    """Devuelve el primer atributo cuyo nombre coincida (sin distinguir mayusculas)."""
    try:
        attrs = obj.GetAttributes()
    except Exception:
        return None
    low = dict((a.GetName().lower(), a) for a in attrs)
    for n in names:
        a = low.get(n.lower())
        if a is not None:
            try:
                if a.GetDataType().GetClass() == gdal.GEDTC_STRING:
                    return a.ReadAsString()
                return a.ReadAsDouble()
            except Exception:
                try:
                    return a.ReadAsString()
                except Exception:
                    return None
    return None


def _crs_from_gdal_group(grp):
    """Busca EPSG/WKT en el dataset 'projection' o en atributos del grupo."""
    epsg, wkt = None, None
    names = []
    try:
        names = list(grp.GetMDArrayNames())
    except Exception:
        pass
    for nm in names:
        if nm.lower() in ("projection", "crs", "spatial_ref", "grid_mapping"):
            try:
                arr = grp.OpenMDArray(nm)
            except Exception:
                continue
            v = _gdal_attr(arr, ["epsg_code", "epsg", "EPSG"])
            if v is not None:
                try:
                    epsg = int(float(v))
                except Exception:
                    pass
            w = _gdal_attr(arr, ["spatial_ref", "crs_wkt", "wkt", "esri_pe_string"])
            if isinstance(w, str) and len(w) > 20:
                wkt = w
            if epsg is None:
                # el valor del propio array suele ser el codigo EPSG
                try:
                    v2 = _md_read(arr).ravel()[0]
                    if 1000 < float(v2) < 40000:
                        epsg = int(v2)
                except Exception:
                    pass
            break
    if epsg is None:
        v = _gdal_attr(grp, ["epsg_code", "epsg", "EPSG"])
        if v is not None:
            try:
                epsg = int(float(v))
            except Exception:
                pass
    return epsg, wkt


def _walk_gdal(grp, path, out):
    out.append((path, grp))
    try:
        for sub in grp.GetGroupNames():
            _walk_gdal(grp.OpenGroup(sub), path.rstrip("/") + "/" + sub, out)
    except Exception:
        pass


def _grids_gdal(h5file):
    ds = gdal.OpenEx(h5file, gdal.OF_MULTIDIM_RASTER)
    if ds is None:
        raise IOError("GDAL no pudo abrir %s" % h5file)
    root = ds.GetRootGroup()
    groups = []
    _walk_gdal(root, "/", groups)

    grids = []
    for path, grp in groups:
        try:
            names = list(grp.GetMDArrayNames())
        except Exception:
            continue
        low = dict((n.lower(), n) for n in names)
        xn = next((low[n.lower()] for n in X_NAMES if n.lower() in low), None)
        yn = next((low[n.lower()] for n in Y_NAMES if n.lower() in low), None)
        if not xn or not yn:
            continue
        try:
            x = _md_read(grp.OpenMDArray(xn)).ravel()
            y = _md_read(grp.OpenMDArray(yn)).ravel()
        except Exception:
            continue
        if x.size < 2 or y.size < 2:
            continue
        ny, nx = int(y.size), int(x.size)
        epsg, wkt = _crs_from_gdal_group(grp)

        bands = []
        for nm in names:
            if nm in (xn, yn) or nm.lower() in ("projection", "crs", "spatial_ref"):
                continue
            try:
                arr = grp.OpenMDArray(nm)
                dims = arr.GetDimensions()
            except Exception:
                continue
            if len(dims) != 2:
                continue
            if int(dims[0].GetSize()) != ny or int(dims[1].GetSize()) != nx:
                continue
            dt = arr.GetDataType()
            cplx = (dt.GetClass() == gdal.GEDTC_COMPOUND)
            if cplx:
                tname = "complex"
            else:
                num = dt.GetNumericDataType()
                cplx = bool(gdal.DataTypeIsComplex(num))
                tname = gdal.GetDataTypeName(num)
            is_pol = bool(POL_RE.match(nm))
            bands.append(Band(nm, path.rstrip("/") + "/" + nm, (ny, nx),
                              tname, is_pol, nm in AUX_NAMES, cplx))
        if bands:
            grids.append(Grid(path, x, y, epsg, wkt, bands))
    ds = None
    return grids


# ---------------------------------------------------------------------------
# Backend h5py
# ---------------------------------------------------------------------------

def _grids_h5py(h5file):
    grids = []
    f = h5py.File(h5file, "r")

    def visit(name, obj):
        if not isinstance(obj, h5py.Group):
            return
        keys = list(obj.keys())
        low = dict((k.lower(), k) for k in keys)
        xn = next((low[n.lower()] for n in X_NAMES if n.lower() in low), None)
        yn = next((low[n.lower()] for n in Y_NAMES if n.lower() in low), None)
        if not xn or not yn:
            return
        try:
            x = np.asarray(obj[xn][()]).ravel()
            y = np.asarray(obj[yn][()]).ravel()
        except Exception:
            return
        if x.size < 2 or y.size < 2:
            return
        ny, nx = int(y.size), int(x.size)

        epsg, wkt = None, None
        for cand in ("projection", "crs", "spatial_ref"):
            if cand in low:
                d = obj[low[cand]]
                for a in ("epsg_code", "epsg", "EPSG"):
                    if a in d.attrs:
                        try:
                            epsg = int(np.array(d.attrs[a]).ravel()[0])
                        except Exception:
                            pass
                for a in ("spatial_ref", "crs_wkt", "wkt"):
                    if a in d.attrs:
                        v = d.attrs[a]
                        if isinstance(v, bytes):
                            v = v.decode("utf-8", "ignore")
                        if isinstance(v, str) and len(v) > 20:
                            wkt = v
                if epsg is None:
                    try:
                        v = np.array(d[()]).ravel()[0]
                        if 1000 < float(v) < 40000:
                            epsg = int(v)
                    except Exception:
                        pass
                break

        bands = []
        for k in keys:
            if k in (xn, yn) or k.lower() in ("projection", "crs", "spatial_ref"):
                continue
            d = obj[k]
            if not isinstance(d, h5py.Dataset) or d.ndim != 2:
                continue
            if d.shape != (ny, nx):
                continue
            cplx = bool(d.dtype.names and len(d.dtype.names) == 2)
            if not cplx:
                try:
                    cplx = np.iscomplexobj(np.zeros(1, dtype=d.dtype))
                except Exception:
                    cplx = False
            bands.append(Band(k, "/" + name.strip("/") + "/" + k, (ny, nx),
                              "complex" if cplx else str(d.dtype),
                              bool(POL_RE.match(k)), k in AUX_NAMES, cplx))
        if bands:
            grids.append(Grid("/" + name.strip("/"), x, y, epsg, wkt, bands))

    f.visititems(visit)
    f.close()
    return grids


# ---------------------------------------------------------------------------
# API publica
# ---------------------------------------------------------------------------

def _solo_imagen(grids):
    """Descarta las grillas de metadatos (calibracion, ruido, parametros)."""
    reales = [g for g in grids if "/grids/" in (g.path.rstrip("/") + "/")]
    return reales or grids


def open_grids(h5file):
    """Devuelve las grillas de imagen geocodificadas del producto."""
    if not os.path.isfile(h5file):
        raise IOError("No existe el archivo: %s" % h5file)
    last = None
    if _HAS_GDAL:
        try:
            g = _grids_gdal(h5file)
            if g:
                return _solo_imagen(g)
        except Exception as e:
            last = e
    if _HAS_H5PY:
        try:
            g = _grids_h5py(h5file)
            if g:
                return _solo_imagen(g)
        except Exception as e:
            last = e
    if last:
        raise IOError("No se pudo leer la estructura del HDF5: %s" % last)
    raise IOError("No se encontraron grillas geocodificadas en %s" % h5file)


def _srs(grid):
    if not _HAS_GDAL:
        return None
    srs = osr.SpatialReference()
    if grid.epsg:
        srs.ImportFromEPSG(int(grid.epsg))
    elif grid.wkt:
        srs.SetFromUserInput(grid.wkt)
    else:
        return None
    return srs


_WKT_UTM = ('PROJCS["WGS 84 / UTM zone %d%s",GEOGCS["WGS 84",DATUM["WGS_1984",'
            'SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],'
            'AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0],'
            'UNIT["degree",0.0174532925199433],AUTHORITY["EPSG","4326"]],'
            'PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],'
            'PARAMETER["central_meridian",%d],PARAMETER["scale_factor",0.9996],'
            'PARAMETER["false_easting",500000],PARAMETER["false_northing",%d],'
            'UNIT["metre",1,AUTHORITY["EPSG","9001"]],AXIS["Easting",EAST],'
            'AXIS["Northing",NORTH],AUTHORITY["EPSG","%d"]]')


def wkt_de(grid):
    """WKT del CRS de la grilla. Funciona tambien sin GDAL (caso UTM/WGS84)."""
    srs = _srs(grid)
    if srs is not None:
        return srs.ExportToWkt()
    if grid.wkt:
        return grid.wkt
    e = int(grid.epsg or 0)
    if 32600 < e < 32661 or 32700 < e < 32761:
        zona = e % 100
        norte = e < 32700
        return _WKT_UTM % (zona, "N" if norte else "S", zona * 6 - 183,
                           0 if norte else 10000000, e)
    return None


def _read_block(h5file, band, row0, nrows, col0=0, ncols=None):
    """Lee un bloque rectangular del dataset, con el backend disponible."""
    if ncols is None:
        ncols = band.shape[1] - col0
    if _HAS_H5PY:
        with h5py.File(h5file, "r") as f:
            a = np.asarray(f[band.path][row0:row0 + nrows, col0:col0 + ncols])
        if a.dtype.names and len(a.dtype.names) == 2:
            r, i = a.dtype.names
            a = a[r].astype("float64") + 1j * a[i].astype("float64")
        return a
    sub = 'HDF5:"%s"://%s' % (h5file, band.path.lstrip("/"))
    ds = gdal.Open(sub)
    if ds is None:
        raise IOError("No se pudo abrir el subdataset %s" % sub)
    arr = ds.GetRasterBand(1).ReadAsArray(col0, row0, ncols, nrows)
    ds = None
    return arr


def recortar_lonlat(grid, minlon, minlat, maxlon, maxlat):
    """Recorta la grilla con un rectangulo dado en longitud/latitud (WGS84)."""
    if not _HAS_GDAL:
        raise RuntimeError("Se necesita GDAL para convertir lon/lat al CRS del producto")
    src = osr.SpatialReference()
    src.ImportFromEPSG(4326)
    try:
        src.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
    except Exception:
        pass
    dst = _srs(grid)
    if dst is None:
        raise ValueError("El producto no declara CRS: use un recorte en coordenadas del producto")
    try:
        dst.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
    except Exception:
        pass
    tr = osr.CoordinateTransformation(src, dst)
    xs, ys = [], []
    for lon in (minlon, maxlon):
        for lat in (minlat, maxlat):
            x, y = tr.TransformPoint(lon, lat)[:2]
            xs.append(x)
            ys.append(y)
    return grid.recortar(min(xs), min(ys), max(xs), max(ys))


def out_geometry(grid, step=1, metodo="promedio"):
    """
    Tamano y GeoTransform de salida para un factor de submuestreo dado.

    Al promediar solo se emiten bloques completos, asi que el tamano se
    redondea hacia abajo; al decimar, hacia arriba.
    """
    step = max(1, int(step))
    if step > 1 and metodo != "decimar":
        nxo = grid.ncols // step
        nyo = grid.nrows // step
    else:
        nxo = int(math.ceil(grid.ncols / float(step)))
        nyo = int(math.ceil(grid.nrows / float(step)))
    gt = grid.geotransform
    return nxo, nyo, (gt[0], gt[1] * step, 0.0, gt[3], 0.0, gt[5] * step)


def _read_out_block(h5file, band, j0, nb, step, nxo, grid=None, metodo="promedio"):
    """
    Lee las filas de salida j0..j0+nb-1, aplicando ventana y submuestreo.

    metodo="promedio": promedia bloques de step x step (multilooking; reduce el
    moteado, que es lo que conviene en radar).
    metodo="decimar":  toma una celda de cada step (mas rapido, conserva el ruido).
    """
    col0 = grid.col0 if grid is not None else 0
    ncols = grid.ncols if grid is not None else band.shape[1]
    fila0 = grid.row0 if grid is not None else 0

    if step == 1:
        a = _read_block(h5file, band, fila0 + j0, nb, col0, ncols)
        return a[:, :nxo]

    if metodo == "decimar":
        row0 = fila0 + j0 * step
        nr = min((nb - 1) * step + 1, band.shape[0] - row0)
        a = _read_block(h5file, band, row0, nr, col0, ncols)
        return a[::step, ::step][:, :nxo]

    # promedio de bloques step x step
    row0 = fila0 + j0 * step
    nr = min(nb * step, band.shape[0] - row0, (fila0 + grid.nrows - row0) if grid is not None else nb * step)
    a = _read_block(h5file, band, row0, nr, col0, ncols)
    fil = (a.shape[0] // step) * step
    col = (a.shape[1] // step) * step
    if fil == 0 or col == 0:
        return a[:1, :nxo]
    b = a[:fil, :col].astype("float64")
    b = b.reshape(fil // step, step, col // step, step)
    with np.errstate(invalid="ignore"):
        b = np.nanmean(np.nanmean(b, axis=3), axis=1)
    return b[:, :nxo]


def export_bands(h5file, grid, band_names, outdir, to_db=False,
                 prefix=None, block=512, progress=None, creation=None, step=1,
                 metodo="promedio"):
    """
    Exporta las bandas elegidas a GeoTIFF (uno por banda).

    to_db  : aplica 10*log10 a los terminos de la diagonal (gamma0 lineal -> dB)
    step   : submuestreo (1 = resolucion completa, 4 = una de cada 4 celdas)
    return : lista de rutas escritas
    """
    step = max(1, int(step))
    nxo, nyo, gto = out_geometry(grid, step, metodo)
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    if prefix is None:
        prefix = os.path.splitext(os.path.basename(h5file))[0]

    srs = _srs(grid)
    creation = creation or ["COMPRESS=DEFLATE", "PREDICTOR=3", "TILED=YES",
                            "BIGTIFF=IF_SAFER", "NUM_THREADS=ALL_CPUS"]
    drv = gdal.GetDriverByName("GTiff")
    written = []

    total = len(band_names)
    for i, name in enumerate(band_names):
        b = grid.band(name)
        if b is None:
            continue
        db = to_db and b.is_diagonal and not b.is_complex
        partes = [("real",), ("imag",)] if b.is_complex else [(None,)]
        salidas = []
        for (parte,) in partes:
            suf = ("_" + parte) if parte else ""
            if db:
                suf += "_db"
            if step > 1:
                suf += "_sub%d" % step
            out = os.path.join(outdir, "%s_%s_%s%s.tif" % (prefix, grid.label, name, suf))
            ds = drv.Create(out, nxo, nyo, 1, gdal.GDT_Float32, creation)
            ds.SetGeoTransform(gto)
            if srs is not None:
                ds.SetProjection(srs.ExportToWkt())
            rb = ds.GetRasterBand(1)
            rb.SetNoDataValue(float("nan"))
            rb.SetDescription(name + ((" " + parte) if parte else "") + (" [dB]" if db else ""))
            if b.is_pol:
                rb.SetMetadataItem("POLARIZATION", name)
                rb.SetMetadataItem("UNIT", "dB" if db else
                                   ("covarianza (lineal)" if b.is_complex else "gamma0 (lineal)"))
            salidas.append([out, ds, rb, parte])

        cancelado = False
        for r0 in range(0, nyo, block):
            nr = min(block, nyo - r0)
            a = _read_out_block(h5file, b, r0, nr, step, nxo, grid, metodo)
            for s_out, s_ds, s_rb, parte in salidas:
                v = a
                if parte == "real":
                    v = np.real(a)
                elif parte == "imag":
                    v = np.imag(a)
                v = np.asarray(v, dtype="float32")
                if db:
                    with np.errstate(divide="ignore", invalid="ignore"):
                        v = np.where(v > 0, 10.0 * np.log10(v), np.nan).astype("float32")
                s_rb.WriteArray(v, 0, r0)
            if progress:
                frac = (i + (r0 + nr) / float(nyo)) / float(total)
                if progress(frac, "%s  fila %d/%d" % (name, r0 + nr, nyo)) is False:
                    cancelado = True
                    break

        for s_out, s_ds, s_rb, parte in salidas:
            s_rb.FlushCache()
            if not cancelado:
                try:
                    s_ds.BuildOverviews("AVERAGE", [2, 4, 8, 16])
                except Exception:
                    pass
        for fila in salidas:
            fila[1] = None
            fila[2] = None
        if cancelado:
            for s_out, _, _, _ in salidas:
                try:
                    os.remove(s_out)
                except Exception:
                    pass
            return written
        written.extend([s_out for s_out, _, _, _ in salidas])
    return written


def _escribir_hdr(ruta, nx, ny, gt, epsg):
    """Cabecera ENVI del .img. BEAM-DIMAP guarda big-endian (byte order = 1)."""
    lineas = ["ENVI",
              "description = {NISAR GCOV}",
              "samples = %d" % nx,
              "lines   = %d" % ny,
              "bands   = 1",
              "header offset = 0",
              "file type = ENVI Standard",
              "data type = 4",
              "interleave = bsq",
              "byte order = 1"]
    if epsg and (32600 < int(epsg) < 32661 or 32700 < int(epsg) < 32761):
        zona = int(epsg) % 100
        hemi = "North" if int(epsg) < 32700 else "South"
        lineas.append("map info = {UTM, 1, 1, %.3f, %.3f, %.3f, %.3f, %d, %s, WGS-84}"
                      % (gt[0], gt[3], abs(gt[1]), abs(gt[5]), zona, hemi))
    with open(ruta, "w") as fh:
        fh.write("\n".join(lineas) + "\n")


_DIM_TPL = u"""<?xml version="1.0" encoding="ISO-8859-1"?>
<Dimap_Document name="{name}.dim">
    <Metadata_Id>
        <METADATA_FORMAT version="2.12.1">DIMAP</METADATA_FORMAT>
        <METADATA_PROFILE>BEAM-DATAMODEL-V1</METADATA_PROFILE>
    </Metadata_Id>
    <Dataset_Id>
        <DATASET_SERIES>BEAM-PRODUCT</DATASET_SERIES>
        <DATASET_NAME>{name}</DATASET_NAME>
    </Dataset_Id>
    <Production>
        <DATASET_PRODUCER_NAME />
        <PRODUCT_TYPE>NISAR_GCOV</PRODUCT_TYPE>
    </Production>
{crs}
    <Raster_Dimensions>
        <NCOLS>{nx}</NCOLS>
        <NROWS>{ny}</NROWS>
        <NBANDS>{nb}</NBANDS>
    </Raster_Dimensions>
    <Data_Access>
        <DATA_FILE_FORMAT>ENVI</DATA_FILE_FORMAT>
        <DATA_FILE_FORMAT_DESC>ENVI File Format</DATA_FILE_FORMAT_DESC>
        <DATA_FILE_ORGANISATION>BAND_SEPARATE</DATA_FILE_ORGANISATION>
{files}
    </Data_Access>
    <Image_Interpretation>
{bands}
    </Image_Interpretation>
</Dimap_Document>
"""


def export_dimap(h5file, grid, band_names, outdir, to_db=False, product_name=None,
                 block=512, progress=None, step=1, nombres=None, metodo="promedio"):
    """
    Exporta a BEAM-DIMAP (.dim + .data), el formato nativo de SNAP.

    SNAP lo abre con File > Open Product y conserva los nombres de banda.
    QGIS tambien puede abrir los .img que quedan dentro de la carpeta .data.
    """
    step = max(1, int(step))
    nxo, nyo, gt = out_geometry(grid, step, metodo)
    if product_name is None:
        product_name = "%s_%s" % (os.path.splitext(os.path.basename(h5file))[0], grid.label)
        if step > 1:
            product_name += "_sub%d" % step
    root = os.path.join(outdir, product_name + ".data")
    if not os.path.isdir(root):
        os.makedirs(root)

    drv = None
    files, infos = [], []
    total = len(band_names)
    nombres = nombres or {}

    for i, name in enumerate(band_names):
        b = grid.band(name)
        if b is None:
            continue
        db = to_db and b.is_diagonal and not b.is_complex
        partes = ["real", "imag"] if b.is_complex else [None]

        salidas = []
        for parte in partes:
            base = name + (("_" + parte) if parte else "") + ("_db" if db else "")
            bname = nombres.get(base, base)
            img = os.path.join(root, bname + ".img")
            salidas.append([bname, open(img, "wb"), parte])

        for r0 in range(0, nyo, block):
            nr = min(block, nyo - r0)
            a = _read_out_block(h5file, b, r0, nr, step, nxo, grid, metodo)
            for bname, fh, parte in salidas:
                v = a
                if parte == "real":
                    v = np.real(a)
                elif parte == "imag":
                    v = np.imag(a)
                v = np.asarray(v, dtype="float32")
                if db:
                    with np.errstate(divide="ignore", invalid="ignore"):
                        v = np.where(v > 0, 10.0 * np.log10(v), np.nan).astype("float32")
                v.astype(">f4").tofile(fh)     # big-endian, como exige BEAM-DIMAP
            if progress:
                frac = (i + (r0 + nr) / float(nyo)) / float(total)
                if progress(frac, "%s  fila %d/%d" % (name, r0 + nr, nyo)) is False:
                    for fila in salidas:
                        fila[1].close()
                    return None

        for fila in salidas:
            fila[1].close()
            _escribir_hdr(os.path.join(root, fila[0] + ".hdr"), nxo, nyo, gt, grid.epsg)

        for bname, _, parte in salidas:
            idx = len(files)
            files.append('        <Data_File>\n'
                         '            <DATA_FILE_PATH href="%s.data/%s.hdr" />\n'
                         '            <BAND_INDEX>%d</BAND_INDEX>\n'
                         '        </Data_File>' % (product_name, bname, idx))
            if db:
                unit = "dB"
            elif b.is_complex:
                unit = "covarianza"
            elif b.is_pol:
                unit = "gamma0"
            else:
                unit = ""
            infos.append(
                '        <Spectral_Band_Info>\n'
                '            <BAND_INDEX>%d</BAND_INDEX>\n'
                '            <BAND_NAME>%s</BAND_NAME>\n'
                '            <BAND_DESCRIPTION>NISAR GCOV %s%s</BAND_DESCRIPTION>\n'
                '            <BAND_RASTER_WIDTH>%d</BAND_RASTER_WIDTH>\n'
                '            <BAND_RASTER_HEIGHT>%d</BAND_RASTER_HEIGHT>\n'
                '            <DATA_TYPE>float32</DATA_TYPE>\n'
                '            <PHYSICAL_UNIT>%s</PHYSICAL_UNIT>\n'
                '            <SCALING_FACTOR>1.0</SCALING_FACTOR>\n'
                '            <SCALING_OFFSET>0.0</SCALING_OFFSET>\n'
                '            <LOG10_SCALED>false</LOG10_SCALED>\n'
                '            <NO_DATA_VALUE_USED>true</NO_DATA_VALUE_USED>\n'
                '            <NO_DATA_VALUE>NaN</NO_DATA_VALUE>\n'
                '        </Spectral_Band_Info>' % (idx, bname, name,
                                                   (" " + parte) if parte else "",
                                                   nxo, nyo, unit))

    wkt = wkt_de(grid)
    crs = ""
    if wkt:
        crs = ("    <Coordinate_Reference_System>\n"
               "        <WKT>%s</WKT>\n"
               "    </Coordinate_Reference_System>\n"
               "    <Geoposition>\n"
               "        <IMAGE_TO_MODEL_TRANSFORM>%.10f,0.0,0.0,%.10f,%.6f,%.6f"
               "</IMAGE_TO_MODEL_TRANSFORM>\n"
               "    </Geoposition>" % (wkt, gt[1], gt[5], gt[0], gt[3]))

    dim = os.path.join(outdir, product_name + ".dim")
    with open(dim, "w") as fh:
        fh.write(_DIM_TPL.format(name=product_name, crs=crs, nx=nxo, ny=nyo,
                                 nb=len(infos), files="\n".join(files),
                                 bands="\n".join(infos)))
    return dim


# Correspondencia entre los terminos del GCOV lexicografico y la matriz C3
# que esperan las herramientas polarimetricas de SNAP (vector [HH, HV, VV]).
C3_MAP = [
    ("HHHH", None, "C11"),
    ("HHHV", "real", "C12_real"), ("HHHV", "imag", "C12_imag"),
    ("HHVV", "real", "C13_real"), ("HHVV", "imag", "C13_imag"),
    ("HVHV", None, "C22"),
    ("HVVV", "real", "C23_real"), ("HVVV", "imag", "C23_imag"),
    ("VVVV", None, "C33"),
]
C3_ALT = {"HHHV": "HHVH", "HVVV": "VHVV"}   # nombres alternativos del producto


def c3_disponible(grid):
    """Devuelve los terminos necesarios para armar C3, o None si no estan todos."""
    elegidos = {}
    for termino, _, _ in C3_MAP:
        if grid.band(termino) is not None:
            elegidos[termino] = termino
        elif C3_ALT.get(termino) and grid.band(C3_ALT[termino]) is not None:
            elegidos[termino] = C3_ALT[termino]
        else:
            return None
    return elegidos


def export_c3(h5file, grid, outdir, product_name=None, block=512, progress=None, step=1):
    """
    Escribe un BEAM-DIMAP con los nombres de banda de una matriz de covarianza C3
    (C11, C12_real, C12_imag, ... C33), que es la nomenclatura que reconocen las
    herramientas polarimetricas de SNAP. Solo para productos cuadripolares.

    Los valores se escriben en potencia lineal, sin conversion a decibeles.
    """
    elegidos = c3_disponible(grid)
    if not elegidos:
        raise ValueError(
            "La grilla %s no es cuadripolar: faltan terminos de la matriz de covarianza. "
            "Terminos presentes: %s" % (grid.label,
                                        ", ".join(b.name for b in grid.bands if b.is_pol)))
    nombres = {}
    for termino, parte, destino in C3_MAP:
        real = elegidos[termino]
        nombres[real + (("_" + parte) if parte else "")] = destino
    orden = []
    for termino, _, _ in C3_MAP:
        if elegidos[termino] not in orden:
            orden.append(elegidos[termino])
    if product_name is None:
        product_name = "%s_%s_C3" % (
            os.path.splitext(os.path.basename(h5file))[0], grid.label)
        if step > 1:
            product_name += "_sub%d" % step
    return export_dimap(h5file, grid, orden, outdir, to_db=False,
                        product_name=product_name, block=block,
                        progress=progress, step=step, nombres=nombres)


def describe(h5file):
    """Texto de diagnostico: estructura detectada en el archivo."""
    lines = ["Archivo: %s" % h5file,
             "Backend: %s" % ("GDAL multidim" if _HAS_GDAL else "h5py")]
    for g in open_grids(h5file):
        lines.append("")
        lines.append("Grilla %s" % g.path)
        lines.append("  tamano  : %d col x %d fil" % (g.nx, g.ny))
        if g.recortada:
            lines.append("  recorte : %d col x %d fil desde (%d, %d)"
                         % (g.ncols, g.nrows, g.col0, g.row0))
        lines.append("  CRS     : EPSG:%s" % (g.epsg if g.epsg else "no declarado"))
        gt = g.geotransform
        lines.append("  pixel   : %.3f x %.3f" % (gt[1], abs(gt[5])))
        lines.append("  origen  : %.3f , %.3f" % (gt[0], gt[3]))
        for b in g.bands:
            tag = "pol" if b.is_pol else ("aux" if b.is_aux else "   ")
            extra = "  (complejo -> real + imag)" if b.is_complex else ""
            lines.append("  [%s] %-28s %s %s%s" % (tag, b.name, b.shape, b.dtype, extra))
        lines.append("  matriz C3 para SNAP: %s" %
                     ("disponible (producto cuadripolar)" if c3_disponible(g)
                      else "no (producto dual o compacto)"))
    return "\n".join(lines)


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("uso: python nisar_gcov_core.py archivo_GCOV.h5")
        raise SystemExit(1)
    print(describe(sys.argv[1]))
