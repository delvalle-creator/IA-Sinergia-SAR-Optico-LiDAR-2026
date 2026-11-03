import numpy as np, pickle, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MultipleLocator
plt.rcParams['font.family']='Liberation Serif'; FS=11
cur,cnt=pickle.load(open('curvas.pkl','rb'))
COL={'C':'#1f5fbf','S':'#d4a017','L':'#2a8c3a','P':'#c0392b'}
def est(k):
    b='P' if k.startswith('P_') else k[0]; cz=k[-2:] in ('HV','VH')
    anio='2021' in k
    return COL[b],('-' if cz else ':'),(2.4 if (anio or b in 'PS') else 1.4)
def lab(k):
    if k.startswith('P_'): return 'P BIOMASS 2026 '+k[-2:]
    p=k.split('_'); nm={'ALOS2':'ALOS-2','NISAR':'NISAR','S1':'Sentinel-1','NovaSAR':'NovaSAR'}
    return '%s %s %s %s'%(p[0],nm[p[1]],p[2],p[-1])
cls=['2–5','5–8','8–12','12–16','> 16']
def fmt(v,_): return ('%.0f'%v).replace('-','−')
fig=plt.figure(figsize=(24/2.54,10.2/2.54))
ax=fig.add_axes([0.075,0.36,0.50,0.57]); axp=fig.add_axes([0.655,0.36,0.345,0.57])
ordenA=['L_ALOS2_2021_HV','L_ALOS2_2021_HH','L_NISAR_2026_HV','L_NISAR_2026_HH','C_S1_2021_VH','C_S1_2021_VV','C_S1_2026_VH','C_S1_2026_VV','S_NovaSAR_2023_sigma0_HH']
ordenP=['P_Gamma0_VH','P_Gamma0_HH','P_Gamma0_VV']
for a_,orden,mk in ((ax,ordenA,'o'),(axp,ordenP,'s')):
    for k in orden:
        c,ls,lw=est(k); v=cur[k][1:]; n=cnt[k][1:]; x=np.arange(5)
        a_.plot(x,np.where(n>=100,v,np.nan),ls,color=c,lw=lw,marker=mk,ms=4.5,label=lab(k).replace('sigma0 ',''))
        a_.plot(x,np.where(n<100,v,np.nan),mk,color=c,mfc='white',ms=4.5)
    n0=cnt[orden[0]][1:]
    a_.set_xticks(range(5)); a_.set_xticklabels(['%s m\nn = %s'%(e,f'{int(q):,}'.replace(',','.')) for e,q in zip(cls,n0)],fontsize=FS)
    a_.set_xlabel('Altura del dosel GEDI rh98 (clase)',fontsize=FS); a_.yaxis.set_major_formatter(FuncFormatter(fmt))
    a_.tick_params(labelsize=FS); a_.grid(alpha=0.3); a_.set_xlim(-0.3,4.3)
ax.set_ylabel('Mediana de la retrodispersión (dB)',fontsize=FS)
ax.set_title('(a) C, L y S en Federal',fontsize=FS); axp.set_title('(b) P (BIOMASS 12/08/2026), mismas huellas',fontsize=FS)
ax.legend(fontsize=FS-1,ncol=3,loc='upper center',bbox_to_anchor=(0.5,-0.27),frameon=False,columnspacing=1.2,handlelength=2.6)
axp.legend(fontsize=FS-1,ncol=1,loc='upper center',bbox_to_anchor=(0.5,-0.27),frameon=False,handlelength=2.6)
fig.savefig('Tp9_Figura_09.png',dpi=300,bbox_inches='tight',pad_inches=0.04)
