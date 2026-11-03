from PIL import Image; import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrow
plt.rcParams['font.family']='Liberation Serif'; FS=11
a=np.array(Image.open('orig_f12.png').convert('RGB'))
R=[118,574,1030]; C=[154,481]; S=311; M=S*200/37.0
tit=[('(a) Celda 1','S2, 06/08/2021'),('(b) Celda 1','S2, 16/09/2026'),('(c) Celda 2','S2, 06/08/2021'),('(d) Celda 2','S2, 16/09/2026'),('(e) Celda 3','L8 + S2, 07/08/2021'),('(f) Celda 3','S2, 16/09/2026')]
sub=['rh98: 11,7 → 5,4 m (4 y 2 huellas)','rh98: 6,1 → 3,1 m (4 y 5 huellas)','rh98: 8,1 → 3,5 m (2 y 2 huellas)']
W,H=9.45,2.75
fig=plt.figure(figsize=(W,H)); w=0.148; h=w*W/H; gi=0.006; gp=0.03; y=0.2
x=0.01; axs=[]
for k in range(6):
    r,c=R[k//2],C[k%2]
    ax=fig.add_axes([x,y,w,h]); ax.imshow(a[r:r+S,c:c+S],extent=(0,M,0,M)); ax.set_xticks([]); ax.set_yticks([])
    ax.set_title(tit[k][0]+'\n'+tit[k][1],fontsize=FS,pad=3); axs.append(ax)
    x+=w+(gi if k%2==0 else gp)
for g in range(3):
    b0=axs[2*g].get_position(); b1=axs[2*g+1].get_position()
    fig.text((b0.x0+b1.x1)/2,y-0.03,sub[g],ha='center',va='top',fontsize=FS)
b=axs[0].get_position(); frac=500/M*b.width; ys=0.0; hb=0.035
sa=fig.add_axes([b.x0+0.01,ys,frac,hb]); sa.set_xlim(0,1); sa.set_ylim(0,1); sa.axis('off')
for i in range(2): sa.add_patch(Rectangle((i*0.5,0),0.5,1,fc=['black','white'][i],ec='black',lw=0.8))
fig.text(b.x0+0.01-0.004,ys+hb/2,'0',ha='right',va='center',fontsize=FS); fig.text(b.x0+0.01+frac+0.004,ys+hb/2,'500 m',ha='left',va='center',fontsize=FS)
bn=axs[5].get_position(); xn=bn.x1+0.02; yt=bn.y1
fig.add_artist(FancyArrow(xn,yt-0.27,0,0.22,width=0.003,head_width=0.014,head_length=0.07,length_includes_head=True,color='black',transform=fig.transFigure))
fig.text(xn,yt-0.045,'N',ha='center',va='bottom',fontsize=FS+1,fontweight='bold')
fig.savefig('Tp9_Figura_12.png',dpi=300,bbox_inches='tight',pad_inches=0.04)
