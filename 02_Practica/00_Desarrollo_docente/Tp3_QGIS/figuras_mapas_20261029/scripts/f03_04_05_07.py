"""Figuras 3, 4, 5 y 7 del Desarrollo del Tp3 (antes fig345.py y fig07.py): mismo contenido, escala y norte afuera."""
import sys; sys.path.insert(0, '/tmp/claude-0/-home-claude/12ab2d2f-e8dc-5c55-a3b2-d0b4e2a90d27/scratchpad/tp3/sc')
from com import *
cap, T = cubo()
H, Wd = cap['OPT_S2_B08'].shape; ext = [T.c, T.c + Wd * 20, T.f - H * 20, T.f]


def rgbsar(co, cx):
    r = np.dstack([st(db(co)), st(db(cx)), st(db(co) - db(cx))]); return np.nan_to_num(r, nan=0)


def marco(ax, ylab=True, paso=5):
    ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3]); ejes_utm(ax, paso, ylab)
    if not ylab: ax.set_yticklabels([])


s2 = np.nan_to_num(np.dstack([st(cap['OPT_S2_B04']), st(cap['OPT_S2_B03']), st(cap['OPT_S2_B02'])]), nan=1)

# ---- Figura 3
fig, axs = plt.subplots(1, 2, figsize=(8.6, 5.75)); fig.subplots_adjust(left=0.085, right=0.95, top=0.9, bottom=0.2, wspace=0.05)
axs[0].imshow(s2, extent=ext); axs[0].set_title('(a) Sentinel-2 16/09/2026,\ncolor natural (B04, B03, B02)'); marco(axs[0])
axs[1].imshow(rgbsar(cap['L_NISAR_gamma0_HH_20260930'], cap['L_NISAR_gamma0_HV_20260930']), extent=ext)
axs[1].set_title('(b) NISAR L 30/09/2026:\nR = HH, G = HV, B = HH/HV (dB)'); marco(axs[1], False)
escala_norte(fig, axs[0], 5000, '5 km', axn=axs[1]); guardar(fig, 'F03.png')

# ---- Figura 4
fig, axs = plt.subplots(1, 2, figsize=(8.8, 5.85)); fig.subplots_adjust(left=0.085, right=0.95, top=0.9, bottom=0.2, wspace=0.05)
axs[0].imshow(rgbsar(cap['C_S1_gamma0_VV'], cap['C_S1_gamma0_VH']), extent=ext)
axs[0].set_title('(a) Sentinel-1 RTC 26/09/2026:\nR = VV, G = VH, B = VV/VH (dB)'); marco(axs[0])
sS = rgbsar(cap['S_NISAR_gamma0_HH_20260930'], cap['S_NISAR_gamma0_HV_20260930'])
sS[~np.isfinite(cap['S_NISAR_gamma0_HH_20260930'])] = 0.85
axs[1].imshow(sS, extent=ext); axs[1].set_title('(b) NISAR S 30/09/2026:\nR = HH, G = HV, B = HH/HV (dB)'); marco(axs[1], False)
axs[1].text(ext[0] + 9500, ext[3] - 4500, 'Sin cobertura de la banda S', ha='center', fontsize=10.5, color='0.25')
escala_norte(fig, axs[0], 5000, '5 km', axn=axs[1]); guardar(fig, 'F04.png')

# ---- Figura 5 (ancho en el Word: 9,6 cm)
plt.rcParams.update({"font.size": 10, "axes.titlesize": 10, "axes.labelsize": 10, "xtick.labelsize": 9.5, "ytick.labelsize": 9.5})
fig = plt.figure(figsize=(3.9, 6.0))
ax = fig.add_axes([0.2, 0.36, 0.66, 0.56])
im = ax.imshow(cap['MDE_GLO30_m'], extent=ext, cmap='terrain', vmin=0, vmax=9); marco(ax)
ax.set_title('Copernicus DEM GLO-30\nllevado a la grilla de 20 m')
yb = escala_norte(fig, ax, 5000, '5 km', fs=10)
b = ax.get_position()
cax = fig.add_axes([b.x0, yb - 0.075, b.width, 0.022])
cb = fig.colorbar(im, cax=cax, orientation='horizontal'); cb.set_label('m sobre EGM2008'); cb.ax.xaxis.set_major_formatter(fmt(0))
guardar(fig, 'F05.png', dpi=300)
plt.rcParams.update({"font.size": 11, "axes.titlesize": 11, "axes.labelsize": 11, "xtick.labelsize": 10.5, "ytick.labelsize": 10.5})

# ---- Figura 7: detalle de 5 x 5 km
c0 = int((293700 - T.c) / 20); c1 = c0 + 250; f0 = int((T.f - 6267680) / 20); f1 = f0 + 250
x0 = T.c + c0 * 20; y1 = T.f - f0 * 20; e7 = [x0, x0 + 5000, y1 - 5000, y1]
rgb = np.dstack([st(cap['OPT_S2_B0%d' % b_][f0:f1, c0:c1]) for b_ in (4, 3, 2)])
fig, axs = plt.subplots(1, 2, figsize=(8.4, 4.95)); fig.subplots_adjust(left=0.09, right=0.95, top=0.9, bottom=0.22, wspace=0.05)
for k, (ax, cr, tit) in enumerate(((axs[0], 'L_NISAR_gamma0_HV_20260930', '(a) NISAR L HV 30/09/2026\nal 50 % sobre Sentinel-2'),
                                   (axs[1], 'C_S1_gamma0_VV', '(b) Sentinel-1 RTC VV 26/09/2026\nal 50 % sobre Sentinel-2'))):
    g = np.nan_to_num(st(db(cap[cr][f0:f1, c0:c1])))
    ax.imshow(0.5 * rgb + 0.5 * np.dstack([g, g, g]), extent=e7); ax.set_title(tit)
    ax.set_xlim(e7[0], e7[1]); ax.set_ylim(e7[2], e7[3]); ejes_utm(ax, 1, k == 0)
    if k: ax.set_yticklabels([])
escala_norte(fig, axs[0], 1000, '1 km', axn=axs[1]); guardar(fig, 'F07.png')
