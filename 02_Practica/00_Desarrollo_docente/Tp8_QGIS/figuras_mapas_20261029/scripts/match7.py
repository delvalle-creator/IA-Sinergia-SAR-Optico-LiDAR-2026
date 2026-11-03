import numpy as np, rasterio, cv2
from PIL import Image
G='/mnt/user-data/uploads/02_Practica/Tp8_Erosion_suelos/02_Subsets_SNAP_QGIS/QGIS_GeoTIFF/'
r=rasterio.open(G+'F_BOVRIL_CBERS4A_BOVRIL_20230615_pansharpened_2m.tif')
a=r.read([4,3,2]).astype('f4')
F=2
g=a.sum(0); g=cv2.resize(g,(g.shape[1]//F,g.shape[0]//F),interpolation=cv2.INTER_AREA)
im=np.array(Image.open('F7_orig.png').convert('RGB')).astype('f4')
X=[32,559,1086,1613,2140]; Y=[86,683]; P=494
pan=[(0,0,240),(0,1,240),(0,2,240),(0,3,240),(0,4,240),(1,0,240),(1,1,600),(1,2,600),(1,3,600)]
res=[]
for k,(i,j,L) in enumerate(pan):
    c=im[Y[i]+3:Y[i]+P-3, X[j]+3:X[j]+P-3].sum(2)
    n=int(round(L/2/F*(P-6)/P))
    t=cv2.resize(c,(n,n),interpolation=cv2.INTER_AREA)
    h=int(n*(0.5 if k==4 else 0.7))
    t=t[:h]
    m=cv2.matchTemplate(g,t.astype('f4'),cv2.TM_CCOEFF_NORMED)
    _,mx,_,loc=cv2.minMaxLoc(m)
    # top-left of panel interior in pixels of g
    x0=r.transform.c+loc[0]*F*2 - 3/P*L; y0=r.transform.f-loc[1]*F*2 + 3/P*L
    m2=m.copy(); yy,xx=loc[1],loc[0]; m2[max(0,yy-20):yy+20,max(0,xx-20):xx+20]=-1
    print(k,L,round(mx,3),'2nd',round(m2.max(),3),'UL',round(x0),round(y0),'centro',round(x0+L/2),round(y0-L/2))

# refinamiento a 2 m
g1=a.sum(0)
out=[]
for k,(i,j,L) in enumerate(pan):
    c=im[Y[i]+3:Y[i]+P-3, X[j]+3:X[j]+P-3].sum(2)
    n=int(round(L/2*(P-6)/P)); t=cv2.resize(c,(n,n),interpolation=cv2.INTER_AREA)
    t=t[:int(n*(0.5 if k==4 else 0.7))].astype('f4')
    print(k)
