from PIL import Image; import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrow
plt.rcParams['font.family']='Liberation Serif'; FS=11
a=np.array(Image.open('orig_f06.png').convert('RGB'))
C=[(65,124),(65,859),(872,124),(872,859)]; S=704; M=482.0
pan=[a[r:r+S,c:c+S] for r,c in C]
tit=['(a) Aceptado, 02/08/2021','(b) Aceptado, 05/09/2026','(c) Descartado, 02/08/2021','(d) Descartado, 05/09/2026']
W,H=9.6,2.85
fig=plt.figure(figsize=(W,H)); w=0.21; h=w*W/H; gx=0.026; x0=0.02; y=0.12
axs=[]
for k in range(4):
    x=x0+k*(w+gx)+(0.02 if k>=2 else 0)
    ax=fig.add_axes([x,y,w,h]); ax.imshow(pan[k],extent=(0,M,0,M)); ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values(): s.set_linewidth(0.8)
    ax.set_title(tit[k],fontsize=FS,pad=3); axs.append(ax)
b=axs[0].get_position(); frac=100/M*b.width; ys=0.02; hb=0.035
sa=fig.add_axes([b.x0+0.02,ys,frac,hb]); sa.set_xlim(0,1); sa.set_ylim(0,1); sa.axis('off')
for i in range(2): sa.add_patch(Rectangle((i*0.5,0),0.5,1,fc=['black','white'][i],ec='black',lw=0.8))
fig.text(b.x0+0.02-0.005,ys+hb/2,'0',ha='right',va='center',fontsize=FS); fig.text(b.x0+0.02+frac+0.005,ys+hb/2,'100 m',ha='left',va='center',fontsize=FS)
bn=axs[3].get_position(); xn=bn.x1+0.022; yt=bn.y1
fig.add_artist(FancyArrow(xn,yt-0.25,0,0.2,width=0.003,head_width=0.014,head_length=0.07,length_includes_head=True,color='black',transform=fig.transFigure))
fig.text(xn,yt-0.04,'N',ha='center',va='bottom',fontsize=FS+1,fontweight='bold')
fig.savefig('Tp9_Figura_06.png',dpi=300,bbox_inches='tight',pad_inches=0.04)
