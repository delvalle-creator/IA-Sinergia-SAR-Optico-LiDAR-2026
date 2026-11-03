# -*- coding: utf-8 -*-
"""Tp2_06_saocom_pauli_y_fase.py - PARA PROFUNDIZAR (lo corre el docente; el alumno mira el resultado).

Descomposicion de Pauli y fase HH-VV del SAOCOM-1A cuadripolar del 24/09/2026 (TOPSAR Narrow B,
EOL1ASARSAO1A15583751) sobre los 28 poligonos sorteados de A2_IBICUY. Lo que la intensidad dual no
puede decir: la fase HH-VV cercana a 180 grados confirma el doble rebote; cercana a 0, superficie o
volumen. Se trabaja sobre el SLC complejo (no sobre el gamma0 en intensidad).

Como funciona:
  - lee el zip L1A de CONAE por partes (no lo descomprime) y une las rafagas (deburst) por la mitad
    de su solapamiento;
  - ubica cada linea con la orbita del producto (tiepoints_orbita de 00_COMUN/procesar_saocom_topsar.py):
    los puntos de enlace del GeoTIFF estan en la geometria de rafaga y no sirven despues del deburst;
  - modo "pol": por poligono (110 x 110 m), potencias HH, HV, VH, VV, Pauli P1 = |HH+VV|^2/2
    (superficie), P2 = |HH-VV|^2/2 (doble rebote), P3 = 2|HV|^2 (volumen), fase y coherencia HH-VV;
  - modo "grilla": las mismas magnitudes en una grilla de 100 m (salida comprimida en base64).

Uso (en la carpeta del zip, con 00_COMUN al lado como ~/mnt/02_Practica/00_COMUN):
    python Tp2_06_saocom_pauli_y_fase.py pol    > A2_IBICUY_SAOCOM_pauli_por_poligono.json
    python Tp2_06_saocom_pauli_y_fase.py grilla > A2_IBICUY_SAOCOM_pauli_100m.b64
Tiempo: unos 20 a 40 minutos (lee 3,2 GB). Subfranja 6 (SW); las coordenadas UTM se aproximan con
una transformacion afin local alrededor de Ibicuy (error menor que 1 m en el sitio).
"""
import zipfile, struct, io, numpy as np, re, sys, json, zlib, base64
import datetime as _dt, os
SRC=open(os.path.expanduser('~/mnt/02_Practica/00_COMUN/procesar_saocom_topsar.py'),encoding='utf-8').read()
exec(SRC[SRC.index('A_WGS, B_WGS'):SRC.index('# ------------------------------------------------------------------ deburst')])
MODO=sys.argv[1]   # 'pol' (por poligono) o 'grilla' (100 m)
z=zipfile.ZipFile('S1A_OPER_SAR_EOSSP__CORE_L1A_OLVF_20260925T100212.zip')
SW=6
def abrir(p):
    f=z.open('Data/slc-acqId0002080261-a-tnb-2609251044-s%dqp-%s'%(SW,p)); h=f.read(189050)
    b=io.BytesIO(h); b.seek(8); off=struct.unpack('<Q',b.read(8))[0]; b.seek(off); n=struct.unpack('<Q',b.read(8))[0]; T={}
    for _ in range(n):
        tag,typ,cnt,val=struct.unpack('<HHQQ',b.read(20)); T[tag]=(typ,cnt,val)
    typ,cnt,val=T[33922]; tp=np.frombuffer(h[val:val+8*cnt],'<f8').reshape(-1,6)
    return f,tp,T[256][2],T[257][2]
def _t(s):
    d=_dt.datetime.strptime(s.strip()[:20],"%d-%b-%Y %H:%M:%S")
    return (d-_dt.datetime(2000,1,1)).total_seconds()+float("0."+s.strip().split(".")[1])
x=z.read('Data/slc-acqId0002080261-a-tnb-2609251044-s%dqp-hh.xml'%SW).decode()
dt=float(re.search(r'<LinesStep unit="s">(.*?)<',x).group(1)); lpb=int(re.search(r'<LinesPerBurst>(.*?)<',x).group(1))
bt=[_t(s) for s in re.findall(r'<AzimuthStartTime unit="Utc">(.*?)<', x)]
o=[int(round((b-bt[0])/dt)) for b in bt]; nb=len(o)
fs={p:abrir(p) for p in ('hh','hv','vh','vv')}
f,tp,W,H=fs['hh']
tau0=float(re.search(r'<SamplesStart unit="s">(.*?)<',x).group(1)); dtau=float(re.search(r'<SamplesStep unit="s">(.*?)<',x).group(1))
Lm=o[-1]+lpb
cs=np.r_[np.arange(0,W,250),W-1].astype(float); rs=np.r_[np.arange(0,Lm,60),Lm-1].astype(float)
TO=tiepoints_orbita(x,bt[0],dt,tau0,dtau,rs,cs)
L=TO[:,3].reshape(len(rs),len(cs)); A=TO[:,4].reshape(len(rs),len(cs))
cols=np.arange(W); j=np.clip(np.searchsorted(cs,cols)-1,0,len(cs)-2); fc=(cols-cs[j])/(cs[j+1]-cs[j])
lon0,lat0=-59.2,-33.72; x0,y0=296151.23,6266715.93; ax=[92676.018,-2364.866,1971.934,110904.502]
def utm(lo,la): return x0+ax[0]*(lo-lon0)+ax[1]*(la-lat0), y0+ax[2]*(lo-lon0)+ax[3]*(la-lat0)
POL=json.loads('''[{"c":"agua_calma","n":1,"lon":-59.24213223368893,"lat":-33.7608170795692,"A":[92633.06,-2412.814,2011.035,110906.346]},{"c":"agua_calma","n":2,"lon":-59.174876002009235,"lat":-33.78212836817564,"A":[92608.472,-2341.635,1951.084,110904.741]},{"c":"agua_calma","n":3,"lon":-59.18794041019252,"lat":-33.73960881241369,"A":[92654.612,-2353.095,1961.641,110904.458]},{"c":"agua_calma","n":4,"lon":-59.18044628131886,"lat":-33.754799451080665,"A":[92638.066,-2345.958,1955.327,110904.478]},{"c":"agua_rizada","n":1,"lon":-59.293718854488986,"lat":-33.72380275008497,"A":[92674.215,-2466.022,2056.382,110907.309]},{"c":"agua_rizada","n":2,"lon":-59.227666670301225,"lat":-33.71491375286115,"A":[92682.162,-2394.333,1996.681,110905.224]},{"c":"agua_rizada","n":3,"lon":-59.233884314684445,"lat":-33.71335873475008,"A":[92683.987,-2400.928,2002.23,110905.382]},{"c":"agua_rizada","n":4,"lon":-59.23478015457343,"lat":-33.71045718181336,"A":[92687.132,-2401.709,2002.951,110905.363]},{"c":"pajonal","n":1,"lon":-59.24492637016225,"lat":-33.710633779253904,"A":[92687.19,-2412.642,2012.085,110905.663]},{"c":"pajonal","n":2,"lon":-59.14718969289333,"lat":-33.65042589659129,"A":[92749.606,-2303.788,1922.468,110901.927]},{"c":"pajonal","n":3,"lon":-59.2094905201042,"lat":-33.78448864827065,"A":[92606.748,-2379.109,1982.324,110905.763]},{"c":"pajonal","n":4,"lon":-59.23067369146968,"lat":-33.739384825219304,"A":[92655.879,-2399.113,2000.097,110905.685]},{"c":"monte_o_bosque","n":1,"lon":-59.21085444495896,"lat":-33.66093498483946,"A":[92739.829,-2372.86,1979.995,110903.911]},{"c":"monte_o_bosque","n":2,"lon":-59.14738711969228,"lat":-33.69740072142748,"A":[92699.097,-2306.853,1923.964,110902.659]},{"c":"monte_o_bosque","n":3,"lon":-59.14439009772386,"lat":-33.672295557356136,"A":[92726.031,-2302.106,1920.565,110902.186]},{"c":"monte_o_bosque","n":4,"lon":-59.134769003840944,"lat":-33.684454747515275,"A":[92712.73,-2292.496,1912.255,110902.105]},{"c":"suelo_desnudo","n":1,"lon":-59.18281970203158,"lat":-33.6908283977518,"A":[92707.006,-2344.569,1955.645,110903.562]},{"c":"suelo_desnudo","n":2,"lon":-59.18365197094588,"lat":-33.69387940837622,"A":[92703.743,-2345.653,1956.481,110903.632]},{"c":"suelo_desnudo","n":3,"lon":-59.18296171790221,"lat":-33.69217841297481,"A":[92705.557,-2344.805,1955.811,110903.586]},{"c":"suelo_desnudo","n":4,"lon":-59.110193356609784,"lat":-33.75566022718717,"A":[92635.504,-2270.314,1892.114,110902.529]},{"c":"estable","n":1,"lon":-59.154938335360924,"lat":-33.74487822134059,"A":[92648.156,-2317.869,1932.088,110903.605]},{"c":"estable","n":2,"lon":-59.15806708182421,"lat":-33.744823547832695,"A":[92648.289,-2321.236,1934.902,110903.692]},{"c":"estable","n":3,"lon":-59.15654085600733,"lat":-33.7442190497924,"A":[92648.904,-2319.555,1933.512,110903.639]},{"c":"estable","n":4,"lon":-59.166368941871255,"lat":-33.740169686679145,"A":[92653.497,-2329.894,1942.243,110903.854]},{"c":"urbano","n":1,"lon":-59.15979554336776,"lat":-33.74488347789783,"A":[92648.265,-2323.101,1936.46,110903.741]},{"c":"urbano","n":2,"lon":-59.1564551064938,"lat":-33.74079415178059,"A":[92652.592,-2319.254,1933.339,110903.584]},{"c":"urbano","n":3,"lon":-59.15497406046481,"lat":-33.741992210329734,"A":[92651.266,-2317.731,1932.039,110903.561]},{"c":"urbano","n":4,"lon":-59.14753224923174,"lat":-33.74654018760975,"A":[92646.193,-2309.992,1925.469,110903.423]}]''') if MODO=='pol' else None
P=100.0; X0,Y1=277750.0,6282950.0; NX,NY=190,226
acc={k:np.zeros(NX*NY) for k in ('n','p1','p2','p3','cr','ci')}
st={k:{q:[] for q in ('hh','hv','vh','vv','x','f')} for k in range(len(POL))} if POL else None
ch=58              # lineas que se leen por vez (memoria acotada)
fin=False
for b in range(nb):
    if fin: break
    a0=0 if b==0 else (o[b]+o[b-1]+lpb)//2-o[b]
    e0=lpb if b==nb-1 else (o[b+1]+o[b]+lpb)//2-o[b]
    for l0 in range(0,lpb,ch):
        nr=min(ch,lpb-l0)
        blk={p:np.frombuffer(fs[p][0].read(W*8*nr),'<c8').reshape(-1,W).astype('c8') for p in fs}
        ls=np.arange(l0,l0+nr); keep=(ls>=a0)&(ls<e0)
        if not keep.any(): continue
        q=(o[b]+ls[keep]).astype('f8')
        i=np.clip(np.searchsorted(rs,q)-1,0,len(rs)-2); fr=((q-rs[i])/(rs[i+1]-rs[i]))[:,None]; I=i[:,None]
        bil=lambda M: M[I,j]*(1-fr)*(1-fc)+M[I,j+1]*(1-fr)*fc+M[I+1,j]*fr*(1-fc)+M[I+1,j+1]*fr*fc
        lo=bil(L); la=bil(A)
        # el sitio va de -33,60 a -33,90 de latitud: fuera de eso no se acumula
        if la.max()<-33.90:
            fin=True; break
        if la.min()>-33.60:
            continue
        hh,hv,vh,vv=[blk[p][keep] for p in ('hh','hv','vh','vv')]
        xx,yy=utm(lo,la)
        if MODO=='grilla':
            cx=np.floor((xx-X0)/P).astype(int); cy=np.floor((Y1-yy)/P).astype(int)
            ok=(cx>=0)&(cx<NX)&(cy>=0)&(cy<NY)&(np.abs(hh)>0)
            k=cy[ok]*NX+cx[ok]; H_,V_,X_=hh[ok],vv[ok],(hv[ok]+vh[ok])/2
            acc['n']+=np.bincount(k,minlength=NX*NY)
            acc['p1']+=np.bincount(k,np.abs(H_+V_)**2/2,minlength=NX*NY)
            acc['p2']+=np.bincount(k,np.abs(H_-V_)**2/2,minlength=NX*NY)
            acc['p3']+=np.bincount(k,2*np.abs(X_)**2,minlength=NX*NY)
            c=H_*np.conj(V_); acc['cr']+=np.bincount(k,c.real,minlength=NX*NY); acc['ci']+=np.bincount(k,c.imag,minlength=NX*NY)
        else:
            for kk,p in enumerate(POL):
                a=p['A']; dx=a[0]*(lo-p['lon'])+a[1]*(la-p['lat']); dy=a[2]*(lo-p['lon'])+a[3]*(la-p['lat'])
                m=(np.abs(dx)<=55)&(np.abs(dy)<=55)&(np.abs(hh)>0)
                if m.any():
                    for nm,arr in (('hh',hh),('hv',hv),('vh',vh),('vv',vv)): st[kk][nm].append(arr[m])
                    st[kk]['x'].append(np.nonzero(m)[1])
if MODO=='grilla':
    n=np.maximum(acc['n'],1)
    def q8(v,lo,hi): return np.clip(np.round((v-lo)/(hi-lo)*254)+1,1,255).astype('u1')
    db=lambda v: 10*np.log10(np.maximum(v/n,1e-9))
    fase=np.degrees(np.arctan2(acc['ci'],acc['cr']))
    out=np.stack([q8(db(acc['p1']),-35,5),q8(db(acc['p2']),-35,5),q8(db(acc['p3']),-35,5),q8(fase,-180,180)])
    out[:,acc['n']==0]=0
    sys.stderr.write('celdas %d\n'%(acc['n']>0).sum())
    print(base64.b64encode(zlib.compress(out.tobytes(),9)).decode())
else:
    res=[]
    for kk,p in enumerate(POL):
        if not st[kk]['hh']: res.append(dict(k=kk,c=p['c'],n=p['n'],npx=0)); continue
        g={nm:np.concatenate(st[kk][nm]).astype('c16') for nm in ('hh','hv','vh','vv')}
        cc=np.concatenate(st[kk]['x'])
        hh,hv,vh,vv=g['hh'],g['hv'],g['vh'],g['vv']; xx=(hv+vh)/2
        rho=np.mean(hh*np.conj(vv))/np.sqrt(np.mean(np.abs(hh)**2)*np.mean(np.abs(vv)**2))
        res.append(dict(k=kk,c=p['c'],n=p['n'],npx=int(hh.size),col_min=int(cc.min()),col_max=int(cc.max()),
            HH=float(np.mean(np.abs(hh)**2)),HV=float(np.mean(np.abs(hv)**2)),VH=float(np.mean(np.abs(vh)**2)),VV=float(np.mean(np.abs(vv)**2)),
            P1=float(np.mean(np.abs(hh+vv)**2)/2),P2=float(np.mean(np.abs(hh-vv)**2)/2),P3=float(2*np.mean(np.abs(xx)**2)),
            fase=float(np.degrees(np.angle(rho))),coh=float(abs(rho))))
    print(json.dumps(res))
