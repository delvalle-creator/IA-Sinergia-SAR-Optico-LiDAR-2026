"""Figura 23 del Desarrollo del Tp3 (antes fig_cci_emb.py, Figura 21): CCI Biomass v7 AGB 2024 e incertidumbre relativa.
Mismo contenido; escala y norte fuera del mapa."""
import sys; sys.path.insert(0, '/tmp/claude-0/-home-claude/12ab2d2f-e8dc-5c55-a3b2-d0b4e2a90d27/scratchpad/tp3/sc')
from com import *
import rasterio
with rasterio.open(Q + 'A2_IBICUY_CCI_Biomass_v7_AGB.tif') as s:
    d = list(s.descriptions); agb = s.read(d.index('AGB_2024') + 1).astype(float); sd = s.read(d.index('AGB_SD_2024') + 1).astype(float)
    b = s.bounds
    if s.nodata is not None: agb[agb == s.nodata] = np.nan; sd[sd == s.nodata] = np.nan
ext = [b.left, b.right, b.bottom, b.top]
rel = np.where(agb > 0, sd / agb, np.nan)
asp = 1 / np.cos(np.radians(33.75))
FW, FH = 8.75, 4.85
pw = 2.85; ph = pw * (ext[3] - ext[2]) / (ext[1] - ext[0]) * asp
fig = plt.figure(figsize=(FW, FH))
x0s = [0.72, 0.72 + pw + 1.38]; y0 = 0.95
axs = [fig.add_axes([x / FW, y0 / FH, pw / FW, ph / FH]) for x in x0s]
cm = plt.get_cmap('YlGn').copy(); cm.set_under('#d9d9d9')
im = axs[0].imshow(np.where(agb == 0, -1, agb), extent=ext, cmap=cm, vmin=0.01, vmax=100)
im2 = axs[1].imshow(rel, extent=ext, cmap='magma_r', vmin=0, vmax=1)
axs[0].set_title('(a) CCI Biomass v7, AGB 2024'); axs[1].set_title('(b) Incertidumbre relativa 2024')
for k, a in enumerate(axs):
    a.set_xlabel('Longitud (°)'); a.xaxis.set_major_formatter(FuncFormatter(lambda v, p: num(v, 2))); a.yaxis.set_major_formatter(FuncFormatter(lambda v, p: num(v, 2)))
    a.set_xticks([-59.25, -59.2, -59.15]); a.set_yticks([-33.8, -33.75, -33.7, -33.65]); a.set_aspect(asp)
    a.set_xlim(ext[0], ext[1]); a.set_ylim(ext[2], ext[3])
axs[0].set_ylabel('Latitud (°)')
# barras de color fuera del mapa, a la derecha de cada panel y por debajo de la flecha norte
ch = ph - 0.85
c1 = fig.add_axes([(x0s[0] + pw + 0.12) / FW, y0 / FH, 0.13 / FW, ch / FH])
c2 = fig.add_axes([(x0s[1] + pw + 0.12) / FW, y0 / FH, 0.13 / FW, ch / FH])
cb = fig.colorbar(im, cax=c1, extend='min'); cb.set_label('AGB 2024 (Mg/ha); gris: 0'); cb.ax.yaxis.set_major_formatter(fmt(0))
cb2 = fig.colorbar(im2, cax=c2); cb2.set_label('Desvío / AGB\n(incertidumbre relativa)'); cb2.ax.yaxis.set_major_formatter(fmt(1))
dx5 = 5 / (111.32 * np.cos(np.radians(33.75)))   # 5 km en grados de longitud
escala_norte(fig, axs[0], dx5, '5 km', axn=axs[1])
guardar(fig, 'F23.png')
