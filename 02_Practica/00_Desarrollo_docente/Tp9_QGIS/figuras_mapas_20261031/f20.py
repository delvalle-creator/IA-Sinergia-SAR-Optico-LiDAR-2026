import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MultipleLocator
from matplotlib.patches import Rectangle, FancyArrow, Patch
plt.rcParams['font.family']='Liberation Serif'; FS=11
z=np.load('../emb/grupos.npz'); ch=z['ch']; E=(306310,306310+1950*20,6614720-2248*20,6614720)
def fk(v,_): return f'{v/1000:,.0f}'.replace(',','.')
def fc(v,_): return ('%.2f'%v).replace('.',',')
W,H=10.2,4.6
fig=plt.figure(figsize=(W,H)); h=0.72; w=h*H/W*(E[1]-E[0])/(E[3]-E[2]); y=0.2
ax1=fig.add_axes([0.055,y,w,h]); ax2=fig.add_axes([0.055+w+0.075,y,w,h]); ax3=fig.add_axes([0.055+2*w+0.25,y,0.995-(0.055+2*w+0.25),h])
cm=plt.get_cmap('magma_r').copy(); cm.set_bad('white')
im=ax1.imshow(ch,extent=E,cmap=cm,vmin=0,vmax=0.25,interpolation='nearest')
f21=z['f21']; loss=z['loss']; alto=z['alto']
rgb=np.ones(ch.shape+(3,))
rgb[f21]=matplotlib.colors.to_rgb('#c7e9c0')
rgb[f21&alto&~loss]=matplotlib.colors.to_rgb('#e66101'); rgb[f21&loss&~alto]=matplotlib.colors.to_rgb('#5e3c99'); rgb[f21&loss&alto]=(0,0,0)
ax2.imshow(rgb,extent=E,interpolation='nearest')
for k,(ax,t) in enumerate([(ax1,'(a) Cambio AlphaEarth 2021 a 2025\n(1 − coseno entre los dos vectores)'),(ax2,'(b) Bosque 2021 con cambio > p99 del bosque\nestable, frente a la pérdida MapBiomas 2022–2025')]):
    ax.set_xlim(E[0],E[1]); ax.set_ylim(E[2],E[3])
    for a_ in (ax.xaxis,ax.yaxis): a_.set_major_locator(MultipleLocator(10000)); a_.set_major_formatter(FuncFormatter(fk))
    ax.tick_params(labelsize=FS,length=3,pad=2); ax.set_xlabel('Este (km, UTM 21 S)',fontsize=FS)
    if k==0: ax.set_ylabel('Norte (km)',fontsize=FS)
    else: ax.set_yticklabels([])
    ax.set_title(t,fontsize=FS,pad=3)
b1=ax1.get_position(); cax=fig.add_axes([b1.x1+0.006,b1.y0,0.01,b1.height]); cb=fig.colorbar(im,cax=cax,ticks=[0,0.05,0.1,0.15,0.2,0.25],format=FuncFormatter(fc)); cb.ax.tick_params(labelsize=FS-1)
# panel c
data=[z['bosque'],z['perdida'],z['cultivo'],z['herb'],z['ptl'],z['ptn']]
ns=[len(d) for d in data]
lab=['Bosque estable','Pérdida MapBiomas\n2022–2025','Cultivo estable','Herbáceas estables','Puntos: pérdida\no degradación','Puntos: no']
lab=[l+'\n(n = %s)'%f'{n:,}'.replace(',','.') for l,n in zip(lab,ns)]
pos=np.arange(6,0,-1)
ax3.boxplot(data,positions=pos,vert=False,whis=(5,95),showfliers=False,widths=0.55,medianprops=dict(color='#e66101',lw=1.5))
ax3.axvline(float(z['p99']),color='#d7191c',ls='--',lw=1)
ax3.text(float(z['p99'])+0.005,6.55,'p99 del bosque\nestable = 0,122',ha='left',va='center',fontsize=FS-1,color='#d7191c')
ax3.set_yticks(pos); ax3.set_yticklabels(lab,fontsize=FS-1); ax3.xaxis.set_major_formatter(FuncFormatter(fc)); ax3.tick_params(axis='x',labelsize=FS)
ax3.set_xlabel('1 − coseno',fontsize=FS); ax3.set_title('(c) Cambio por grupo',fontsize=FS,pad=3); ax3.set_xlim(0,0.32); ax3.set_ylim(0.4,7.1)
ax3.xaxis.set_major_locator(MultipleLocator(0.1))
for s_ in ('top','right'): ax3.spines[s_].set_visible(False)
# escala, norte, leyenda
b0=ax1.get_position(); frac=10000/(E[1]-E[0])*b0.width; ys=0.02; hb=0.025
sa=fig.add_axes([b0.x0,ys,frac,hb]); sa.set_xlim(0,1); sa.set_ylim(0,1); sa.axis('off')
for i in range(2): sa.add_patch(Rectangle((i*0.5,0),0.5,1,fc=['black','white'][i],ec='black',lw=0.8))
fig.text(b0.x0-0.005,ys+hb/2,'0',ha='right',va='center',fontsize=FS); fig.text(b0.x0+frac+0.005,ys+hb/2,'10 km',ha='left',va='center',fontsize=FS)
b2=ax2.get_position()
hs=[Patch(fc='#c7e9c0',ec='k',lw=0.5,label='Bosque MapBiomas 2021'),Patch(fc='#e66101',ec='k',lw=0.5,label='Sólo AlphaEarth'),Patch(fc='#5e3c99',ec='k',lw=0.5,label='Sólo MapBiomas 2022–2025'),Patch(fc='black',ec='k',lw=0.5,label='Los dos')]
fig.legend(handles=hs,loc='lower center',bbox_to_anchor=((b2.x0+b2.x1)/2+0.08,-0.04),ncol=2,fontsize=FS-1,frameon=False)
xn=b2.x1+0.022; yt=b2.y1
fig.add_artist(FancyArrow(xn,yt-0.17,0,0.14,width=0.003,head_width=0.013,head_length=0.045,length_includes_head=True,color='black',transform=fig.transFigure))
fig.text(xn,yt-0.025,'N',ha='center',va='bottom',fontsize=FS+1,fontweight='bold')
fig.savefig('Tp9_Figura_20.png',dpi=300,bbox_inches='tight',pad_inches=0.04); print(ns)
