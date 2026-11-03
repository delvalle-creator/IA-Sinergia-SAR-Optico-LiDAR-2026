# Cambio AlphaEarth 2021-2025 a 20 m para la Figura 20 del Desarrollo del Tp9 (herramienta docente).
# Embeddings de 10 m: se descuantizan (sign*(q/127.5)^2), se promedian los 4 vectores de cada 2 x 2
# y se renormalizan a largo 1; cambio = 1 - coseno entre 2021 y 2025. Grilla de salida: origen (306310, 6614720), 20 m.
import sys, numpy as np, rasterio
from rasterio.windows import Window
base = sys.argv[1]; out = sys.argv[2]
f21 = base + "/C_FEDERAL_AlphaEarth_embeddings_2021_10m.tif"; f25 = base + "/C_FEDERAL_AlphaEarth_embeddings_2025_10m.tif"
r1, r2 = rasterio.open(f21), rasterio.open(f25)
assert r1.transform == r2.transform and r1.shape == r2.shape
print(r1.transform, r1.shape)
H, W = r1.height // 2, r1.width // 2
res = np.full((H, W), np.nan, np.float32)
def prom(r, i0, n):
    a = r.read(window=Window(0, 2 * i0, 2 * W, 2 * n)).astype(np.float32)
    nod = (a == -128).any(0)
    v = np.sign(a) * (a / 127.5) ** 2
    v[:, nod] = np.nan
    v = v.reshape(64, n, 2, W, 2)
    m = np.nanmean(v, axis=(2, 4))
    nn = np.linalg.norm(m, axis=0); nn[nn == 0] = np.nan
    return m / nn
for i0 in range(0, H, 128):
    n = min(128, H - i0)
    a, b = prom(r1, i0, n), prom(r2, i0, n)
    res[i0:i0 + n] = 1 - np.sum(a * b, axis=0)
    print(i0, flush=True)
np.save(out, res)
print("listo", out, res.shape, np.nanpercentile(res, [1, 50, 99]))
