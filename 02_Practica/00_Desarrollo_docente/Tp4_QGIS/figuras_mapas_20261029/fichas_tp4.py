# 30/10/2026: fichas armadas al tamaño de impresión (15,5 cm la Figura 9, 22 cm la Figura 10), letra de 11 pt
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrow
from PIL import Image
import numpy as np, sys
plt.rcParams['font.family']='Liberation Serif'; plt.rcParams['font.size']=11
C='/mnt/user-data/uploads/02_Practica/00_COMUN/09_Herramientas/desarrollo_docente/Tp4P/chips/'
OUT='/tmp/claude-0/-home-claude/12ab2d2f-e8dc-5c55-a3b2-d0b4e2a90d27/scratchpad/tp4m/maps/'
def ficha(nombre, pts, Wcm):
    W=Wcm/2.54; g=0.04; gg=0.16; x0=0.10; hdr=0.40; lab=0.22; sc=0.62; c=(W-x0-0.42-5*g-(gg-g))/6
    H=hdr+3*(lab+c)+sc
    fig=plt.figure(figsize=(W,H))
    def ax_at(col,row):
        x=x0+col*(c+g)+(gg-g if col>=3 else 0); y=H-hdr-(row+1)*(lab+c)+0
        return fig.add_axes([x/W,y/H,c/W,c/H]), x, y
    heads=['Esri\n300 m','Google\n300 m','Esri\n1.200 m']*2
    axes={}
    for k,p in enumerate(pts):
        col0=3*(k//3); row=k%3
        for j,s in enumerate('egw'):
            ax,x,y=ax_at(col0+j,row); axes[(col0+j,row)]=ax
            im=np.asarray(Image.open(C+'%s_%s.png'%(p,s)).convert('RGB')); n=im.shape[0]
            ax.imshow(im,extent=(0,n,0,n)); ax.set_xticks([]); ax.set_yticks([])
            for sp in ax.spines.values(): sp.set_visible(False)
            def sq(L,Lt,col,lw):
                a=n*L/Lt; ax.add_patch(Rectangle((n/2-a/2,n/2-a/2),a,a,fill=False,ec=col,lw=lw))
            if s in 'eg': sq(20,300,'#ffe600',1.4)
            else: sq(300,1200,'#22d3ee',1.4); sq(20,1200,'#ffe600',0.9)
            if j==0: fig.text(x/W,(y+c+0.03)/H,p,fontsize=11,va='bottom',ha='left')
    for col in range(6):
        ax=axes[(col,0)]; b=ax.get_position()
        fig.text((b.x0+b.x1)/2,(H-0.06)/H,heads[col],ha='center',va='top',fontsize=11,fontweight='bold')
    # escala FUERA, bajo el primer panel (chips de 300 m); flecha N FUERA, a la derecha del panel superior derecho
    b=axes[(0,2)].get_position(); L=100; frac=L/300*b.width; y=0.24/H; h=0.05/H
    sa=fig.add_axes([b.x0,y,frac,h]); sa.axis('off'); sa.set_xlim(0,1); sa.set_ylim(0,1)
    sa.add_patch(Rectangle((0,0),0.5,1,fc='k',ec='k',lw=0.8)); sa.add_patch(Rectangle((0.5,0),0.5,1,fc='w',ec='k',lw=0.8))
    fig.text(b.x0,y+h+0.03/H,'0',ha='center',va='bottom',fontsize=11); fig.text(b.x0+frac,y+h+0.03/H,'100 m',ha='center',va='bottom',fontsize=11)
    fig.text(b.x0+frac+0.35/W,y+h/2,'(vistas de 300 m; la de 1.200 m\nes cuatro veces menor)',va='center',fontsize=11)
    bn=axes[(5,0)].get_position(); xn=bn.x1+0.17/W; yt=bn.y1
    fig.add_artist(FancyArrow(xn,yt-0.42/H,0,0.28/H,width=0.016/W,head_width=0.11/W,head_length=0.12/H,length_includes_head=True,color='black',transform=fig.transFigure))
    fig.text(xn,yt-0.10/H,'N',ha='center',va='bottom',fontsize=11,fontweight='bold')
    fig.savefig(OUT+nombre,dpi=300); plt.close(fig); print(nombre, W, H)
ficha('F09.png',['P001','P002','P003','P004','P005','P006'],15.5)
ficha('F10.png',['P031','P032','P033','P034','P035','P036'],22)
