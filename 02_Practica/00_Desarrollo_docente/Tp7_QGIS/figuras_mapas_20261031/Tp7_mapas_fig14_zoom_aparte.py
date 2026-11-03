# Tp7 Figura 14 (31/10/2026): cotas 10-90 m como la Figura 7 y el detalle de la grieta como panel (d) aparte
import sys; sys.path.insert(0, '.')
from comun import *
E = BAR; DEM = plt.get_cmap('RdYlGn_r')
Z = (155150, 155650, 6446150, 6446650)
LEGF = [lin(C_CIC, 'cicatriz'), lin(C_DEP, 'depósito'), lin('red', 'grieta relevada en 2018', 3.5)]
W = 25.6; L, g, gz, Rn = 1.45, 0.3, 0.75, 1.1
asp = (E[3]-E[2])/(E[1]-E[0])
pw = (W - L - 2*g - gz - Rn) / (3 + asp)       # el detalle es cuadrado, de la altura del mapa
ph = pw*asp; zw = ph
T, XL, ZS, ZC, ZL = 0.65, 1.0, 0.85, 1.45, 0.7
H = T + ph + XL + ZS + ZC + ZL + 0.15
fig = plt.figure(figsize=(W*CM, H*CM)); yb = (H - T - ph)/H
axs = [fig.add_axes([(L + k*(pw+g))/W, yb, pw/W, ph/H]) for k in range(3)]
az = fig.add_axes([(L + 3*pw + 2*g + gz)/W, yb, zw/W, ph/H])
ign = warp(Q + 'IGN_MDE_5m.tif', 1, E, 5)
im0 = axs[0].imshow(ign, extent=E, cmap=DEM, vmin=10, vmax=90, interpolation='bilinear')
axs[1].imshow(warp(Q + 'CopernicusDEM30.tif', 1, E, 10, rs=Resampling.nearest), extent=E, cmap=DEM, vmin=10, vmax=90, interpolation='nearest')
dz = -warp(FIG + 'E1_dz_GLO30_menos_IGN5m_30m.tif', 1, E, 10, rs=Resampling.nearest)
im2 = axs[2].imshow(dz, extent=E, cmap='RdBu', vmin=-10, vmax=10, interpolation='nearest')
axs[2].add_patch(Rectangle((Z[0], Z[2]), Z[1]-Z[0], Z[3]-Z[2], fill=False, ec='black', lw=1.4, zorder=9))
for k, (ax, t) in enumerate(zip(axs, ['(a) IGN 5 m (2013), «después»', '(b) GLO-30 (2011–2015), «antes»', '(c) IGN menos GLO-30, 30 m'])):
    capas(ax, formas=True, lw=1.6, gw=(4, 2.3)); marco(ax, E, 1000, left=k == 0); ax.set_title(t, fontsize=10.5, pad=4)
axs[0].set_ylabel('Norte (m), EPSG:32721')
az.imshow(dz, extent=E, cmap='RdBu', vmin=-10, vmax=10, interpolation='nearest'); capas(az, formas=True, lw=2.0, gw=(5, 3))
az.set_xlim(Z[0], Z[1]); az.set_ylim(Z[2], Z[3]); az.set_aspect('auto')
az.xaxis.set_major_locator(MultipleLocator(200)); az.yaxis.set_major_locator(MultipleLocator(200)); az.set_xticks([155200, 155400, 155600])
az.xaxis.set_major_formatter(miles); az.yaxis.set_major_formatter(miles); az.tick_params(labelsize=9, length=3)
for l in az.get_yticklabels(): l.set_rotation(90); l.set_va('center')
az.set_ylabel(""); az.set_xlabel("Este (m)", fontsize=10, labelpad=2); az.set_title('(d) Detalle de la grieta', fontsize=10.5, pad=4)
for s_ in az.spines.values(): s_.set_lw(1.4)
lay = dict(W=W, H=H, y_esc=(H - T - ph - XL - ZS + 0.18)/H, y_cb=(H - T - ph - XL - ZS - 0.55)/H, y_leg=(ZL + 0.15)/H)
escala_norte(fig, lay, axs[0], az, 500, '500 m')
cbar(fig, lay, im0, axs[:2], 'cota (m, SRVN16)', ticks=[10, 20, 30, 40, 50, 60, 70, 80, 90], frac=0.96)
cbar(fig, lay, im2, [axs[2], az], 'dZ = IGN − GLO-30 (m); rojo = el IGN más bajo', ticks=[-10, -5, 0, 5, 10], fmt=coma(), frac=0.9)
leyenda(fig, lay, LEGF + [Patch(facecolor='none', edgecolor='black', lw=1.4, label='zona del detalle (d)')], 4)
fig.savefig('F14_zoom_aparte.png', dpi=300); print('W x H', W, round(H, 2), 'pw', round(pw, 2))
