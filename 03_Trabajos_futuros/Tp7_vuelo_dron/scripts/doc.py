import pickle, numpy as np, pandas as pd
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.section import WD_ORIENT
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from PIL import Image
OUT='/home/claude/dron/out'
E=pickle.load(open('plan2.pkl','rb')); X=pickle.load(open('exp.pkl','rb')); D=pickle.load(open('plan.pkl','rb'))
LN,R,G2=E['LN'],X['R'],X['G2']
d=Document()
s=d.sections[0]; s.orientation=WD_ORIENT.LANDSCAPE; s.page_width,s.page_height=Cm(29.7),Cm(21.0)
for m in ('left_margin','right_margin'): setattr(s,m,Cm(2.2))
s.top_margin=Cm(2); s.bottom_margin=Cm(2)
st=d.styles['Normal']; st.font.name='Times New Roman'; st.font.size=Pt(12)
st.element.rPr.rFonts.set(qn('w:eastAsia'),'Times New Roman')
pf=st.paragraph_format; pf.line_spacing=1.5; pf.space_after=Pt(4); pf.space_before=Pt(0)
# numero de pagina en el pie
fp=s.footer.paragraphs[0]; fp.alignment=WD_ALIGN_PARAGRAPH.CENTER
r=fp.add_run();
for t,txt in (('begin',None),(None,'PAGE'),('end',None)):
    if t: e=OxmlElement('w:fldChar'); e.set(qn('w:fldCharType'),t); r._r.append(e)
    else: e=OxmlElement('w:instrText'); e.set(qn('xml:space'),'preserve'); e.text=txt; r._r.append(e)
def par(txt,bold=False,align='j',size=12,color=None,kwn=False,italic=False,space_after=4):
    p=d.add_paragraph(); p.alignment={'j':WD_ALIGN_PARAGRAPH.JUSTIFY,'c':WD_ALIGN_PARAGRAPH.CENTER,'l':WD_ALIGN_PARAGRAPH.LEFT}[align]
    p.paragraph_format.keep_with_next=kwn; p.paragraph_format.space_after=Pt(space_after)
    # negritas con **
    parts=txt.split('**')
    for i,t in enumerate(parts):
        if not t: continue
        rr=p.add_run(t); rr.bold=bold or (i%2==1); rr.font.size=Pt(size); rr.italic=italic
        if color: rr.font.color.rgb=RGBColor(*color)
    return p
def tit(txt,lvl=1):
    p=par(txt,bold=True,align='l',size=12,kwn=True,space_after=4); p.paragraph_format.space_before=Pt(8); return p
def bullets(items):
    for it in items:
        p=par('•  '+it); p.paragraph_format.left_indent=Cm(0.8); p.paragraph_format.first_line_indent=Cm(-0.5)
def fuente(txt): par('Fuente: '+txt,align='c',size=11,color=(0,0,0xC0),space_after=6)
def interp(txt): par('**Interpretación.** '+txt)
def figura(path,cap,src,wmax=22,hmax=10.5):
    w,h=Image.open(path).size; ww=wmax; hh=ww*h/w
    if hh>hmax: hh=hmax; ww=hh*w/h
    p=d.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.keep_with_next=True; p.paragraph_format.line_spacing=1.0
    p.add_run().add_picture(path,width=Cm(ww))
    par(cap,bold=True,align='c',size=11,kwn=True); fuente(src)
def tabla(cap,df,src,widths=None,size=10):
    par(cap,bold=True,align='c',size=11,kwn=True)
    t=d.add_table(rows=1,cols=len(df.columns)); t.style='Table Grid'; t.alignment=WD_TABLE_ALIGNMENT.CENTER
    for j,cn in enumerate(df.columns):
        cell=t.rows[0].cells[j]; cell.text=''; rr=cell.paragraphs[0].add_run(str(cn)); rr.bold=True; rr.font.size=Pt(size)
        sh=OxmlElement('w:shd'); sh.set(qn('w:fill'),'D9E2F3'); cell._tc.get_or_add_tcPr().append(sh)
    for _,row in df.iterrows():
        cells=t.add_row().cells
        for j,v in enumerate(row):
            sv=str(v)
            if __import__('re').fullmatch(r'-?\d+\.\d+',sv): sv=sv.replace('.',',')
            cells[j].text=''; rr=cells[j].paragraphs[0].add_run(sv); rr.font.size=Pt(size)
    for i_,row in enumerate(t.rows):
        trp=row._tr.get_or_add_trPr(); cs=OxmlElement('w:cantSplit'); trp.append(cs)
        for j,cell in enumerate(row.cells):
            for p in cell.paragraphs:
                p.paragraph_format.line_spacing=1.0; p.paragraph_format.space_after=Pt(0); p.paragraph_format.keep_with_next=(row._index==0 or len(t.rows)<=9)
                p.alignment=WD_ALIGN_PARAGRAPH.CENTER if j>0 or len(df.columns)>3 else WD_ALIGN_PARAGRAPH.LEFT
    # anchos proporcionales al contenido
    if widths is None:
        L=[max(max(len(w) for w in str(cn).split()),len(str(cn))/2.2,*(len(str(v)) for v in df.iloc[:,j]))+2.5 for j,cn in enumerate(df.columns)]
        tot=sum(L); W=min(25.0,max(12.0,tot*0.24)); widths=[W*l/tot for l in L]
    tblPr=t._tbl.tblPr; lay=OxmlElement('w:tblLayout'); lay.set(qn('w:type'),'fixed'); tblPr.append(lay)
    t.autofit=False
    for j,col in enumerate(t.columns): col.width=Cm(widths[j])
    for row in t.rows:
        for j,cell in enumerate(row.cells): cell.width=Cm(widths[j])
    for p in t.rows[-1].cells[0].paragraphs: pass
    fuente(src)
SRC='elaboración propia sobre imagen CBERS-4A pansharpened 2 m (26/09/2026, INPE/CONAE), MDE IGN 5 m y mosaico IGN 2018; grieta relevada por el municipio (grietadte.shp); cicatriz y depósito del Tp7.'
# ================= portada / encabezado =================
par('Plan de vuelo con dron sobre la barranca de Diamante (Entre Ríos)',bold=True,align='c',size=16,space_after=2)
par('Relevamiento fotogramétrico de la grieta, la cicatriz y el depósito. Documento para los operadores',align='c',size=13,space_after=2)
par('Equipo: DJI Mavic 2 Pro (cámara Hasselblad L1D-20c). Aplicación de vuelo: Litchi. Fecha del plan: 23/10/2026',align='c',size=12,space_after=10)
tit('1. Objetivo')
par('El vuelo busca obtener un ortomosaico de unos 2 cm de píxel y un modelo digital de superficie y de terreno de la barranca de Diamante en el sector de la grieta. Con esos productos se medirá la longitud, la apertura y el escalón de la grieta, el contorno de la cicatriz y el volumen del depósito. El último modelo de elevación oficial disponible para el sitio es el del IGN de 2018, anterior a la grieta: este vuelo aporta el modelo actual que falta para medir el cambio, y repitiendo exactamente el mismo plan en el futuro se podrá monitorear si la barranca sigue moviéndose.')
tit('2. Área de vuelo y misiones')
par('El área es un rectángulo de 800 m a lo largo de la barranca por 340 m de ancho (27,2 ha), orientado con un rumbo de 38,4° (paralelo a la barranca) y centrado en la grieta. Incluye la meseta urbana, el borde, el talud, el pie y la orilla del río Paraná. El relevamiento se divide en siete misiones de Litchi: cuatro de fotos verticales a 80 m (misiones 1 a 4), una pasada oblicua sobre el río mirando la cara de la barranca (misión 5) y dos misiones de detalle a 40 m sobre la grieta (misiones 6 y 7). La Figura 1 muestra el conjunto y la Tabla 1 da los vértices del área.')
cor=[ (lambda lo,la:(la,lo))(*__import__('pyproj').Transformer.from_crs(32721,4326,always_xy=True).transform(*p)) for p in list(D['aoi'].exterior.coords)[:4]]
dfc=pd.DataFrame([dict(Vértice=n,Latitud='%.6f'%a,Longitud='%.6f'%b,**{'Este UTM 21S (m)':'%.1f'%p[0],'Norte UTM 21S (m)':'%.1f'%p[1]}) for n,(a,b),p in zip(['SO (sur, lado ciudad)','E (norte, lado ciudad)','N (norte, lado río)','O (sur, lado río)'],cor,list(D['aoi'].exterior.coords)[:4])])
tabla('Tabla 1. Vértices del área de vuelo (WGS 84 y UTM zona 21 Sur, EPSG:32721)',dfc,'elaboración propia.')
interp('Estos cuatro vértices permiten cargar o controlar el área en cualquier aplicación. El archivo KML que acompaña el plan contiene el mismo polígono y todas las líneas, de modo que los operadores pueden verificarlo en Google Earth antes de ir al campo.')
figura(OUT+'/f_plan_general.png','Figura 1. Plan general del vuelo: líneas de cada misión, pasada oblicua, recuadro de detalle, puntos de control y de chequeo, y despegue sugerido',SRC,hmax=12.5)
interp('Las líneas corren paralelas a la barranca, así cada pasada se mantiene casi a la misma cota de terreno y la altura sobre el suelo es pareja. Los puntos de control rodean la grieta por la meseta y por el pie, sin quedar sobre el bloque que se mueve: el más cercano está a 82 m de la grieta. La pasada oblicua (magenta) va sobre el agua, a 30 m del límite del área, para fotografiar de frente la cara de la barranca, que las fotos verticales ven muy de costado.')
tit('3. Parámetros de cámara y de vuelo')
cam=pd.DataFrame([
 ('Sensor','1" CMOS, 13,2 × 8,8 mm, 5472 × 3648 píxeles (20 Mpx)'),('Distancia focal real','10,26 mm (28 mm equivalente)'),
 ('Altura de vuelo (misiones 1 a 4)','80 m sobre el terreno (siguiendo el terreno, ver punto 4)'),('Tamaño de píxel en el terreno (GSD)','%.2f cm a 80 m; %.2f cm a 40 m'%(E['gsd'],E['gsd']/2)),
 ('Huella de cada foto a 80 m','%.0f m (transversal) × %.0f m (en el sentido del vuelo)'%(E['fw'],E['fh'])),
 ('Solape longitudinal / lateral','80 % / 70 %'),('Separación entre líneas','%.1f m'%E['sp']),('Distancia entre fotos','%.1f m'%E['ph']),
 ('Velocidad','4 m/s (una foto cada %.1f s)'%(E['ph']/4)),('Cámara','vertical (gimbal −90°), formato JPEG solamente, sin DNG'),
 ('Exposición','prioridad de obturación 1/1000 s o más rápida, ISO 100 a 400, balance de blancos fijo'),
 ('Enfoque','fijo en infinito (enfocar en tierra sobre un objeto lejano y bloquear)'),
 ('Corrección de distorsión de la cámara','desactivada (la calcula el programa de procesamiento)')],columns=['Parámetro','Valor'])
tabla('Tabla 2. Parámetros de la cámara del Mavic 2 Pro y del vuelo fotogramétrico',cam,'especificaciones del DJI Mavic 2 Pro (DJI) y elaboración propia.',widths=[8.5,15.5])
interp('Con 80 m de altura cada píxel cubre menos de 2 cm, suficiente para ver la grieta y sus bordes. Los solapes de 80 % y 70 % son los habituales para reconstruir relieve con buena calidad. La cámara del Mavic 2 Pro tiene obturador electrónico de barrido (rolling shutter): por eso la velocidad se limita a 4 m/s y en el procesamiento hay que activar la corrección de rolling shutter. El intervalo de 3,4 s entre fotos está por encima del mínimo que admite la cámara en JPEG; si se guardara también en DNG ese mínimo crece y se perderían fotos.')
tit('4. Alturas: el punto más delicado del plan')
par('La barranca tiene unos 45 m de desnivel entre la meseta (≈ 55 a 60 m de cota) y la orilla del río (≈ 10 m). Si el dron volara a una altura fija sobre el despegue, sobre el río quedaría a más de 120 m del suelo y sobre la meseta a 80 m, con fotos de escala muy distinta. Por eso cada línea lleva waypoints cada 40 m (cada 30 m en el detalle) y la altura de cada waypoint se calculó como 80 m (o 40 m) por encima del punto más alto del terreno en su entorno, según el MDE del IGN. Litchi guarda esas alturas **relativas al punto de despegue**: el plan supone despegar en el punto sugerido, en la meseta, a %.1f m de cota IGN (latitud %.6f, longitud %.6f), a %d m de la grieta.'%(E['Z0'],E['hl'][1],E['hl'][0],127))
par('**Si se despega desde otro lugar**, hay que corregir todas las alturas de la misión en Litchi Mission Hub por la diferencia de cota: si el nuevo despegue está 5 m más bajo, sumar 5 m a todos los waypoints; si está más alto, restar. No despegar desde el pie de la barranca sin hacer esa corrección: el dron chocaría contra la meseta.')
tl=LN[['n','rumbo','alt_min','alt_max','agl_min','agl_max']].copy()
tl.insert(1,'Misión',[[k+1 for k,mm in enumerate(E['mis']) if n in mm][0] for n in tl.n])
tl=tl.rename(columns={'n':'Línea','rumbo':'Rumbo (°)','alt_min':'Altura mín. sobre despegue (m)','alt_max':'Altura máx. sobre despegue (m)','agl_min':'Altura mín. sobre terreno (m)','agl_max':'Altura máx. sobre terreno (m)'})
tl['Altura mín. sobre terreno (m)']=tl['Altura mín. sobre terreno (m)'].round(0).astype(int); tl['Altura máx. sobre terreno (m)']=tl['Altura máx. sobre terreno (m)'].round(0).astype(int)
tabla('Tabla 3. Alturas de vuelo por línea (misiones 1 a 4)',tl,'elaboración propia con el MDE IGN 5 m.')
interp('Sobre el terreno el dron queda siempre entre unos 79 y 103 m, por debajo de 120 m. Los valores más altos aparecen donde la línea cruza en diagonal el borde de la barranca en los extremos del área: allí el dron se mantiene a la altura de la meseta mientras el terreno baja. Las líneas 8 a 12, sobre el pie y la orilla, vuelan entre 28 y 64 m por encima del despegue, es decir más bajo que el punto donde está parado el piloto.')
figura(OUT+'/f_perfil_alturas.png','Figura 2. Perfil transversal por la grieta con la altura de cada línea, la pasada oblicua y su campo visual',SRC.replace('imagen CBERS-4A pansharpened 2 m (26/09/2026, INPE/CONAE), ','')+' El despegue se dibuja proyectado sobre el perfil.',hmax=9)
interp('El perfil muestra el escalón de la barranca a unos 25 a 40 m de la grieta hacia el río, el pie casi plano a 25-30 m de cota y la orilla. Las líneas siguen la forma del terreno con unos 80 m de separación. En la pasada oblicua el centro de la foto apunta al pie y la parte superior del cuadro alcanza el borde y la meseta, así la cara de la barranca queda cubierta de frente.')
tit('5. Pasada oblicua (misión 5)')
par('Una línea de 800 m paralela a la barranca, sobre el agua, 200 m hacia el río desde la grieta y a 70 m sobre el nivel del río (%d m sobre el despegue). El dron avanza de costado con la nariz apuntando a la barranca (rumbo %.1f°), la cámara inclinada a −35° y una foto cada 10 m. Esas fotos completan la cara empinada de la barranca, donde las fotos verticales tienen poca resolución. Conviene volarla a la tarde, cuando el sol ilumina de frente la cara de la barranca, que mira al noroeste.'%(E['alt_ob'],E['rumbo_ob']))
tit('6. Detalle de la grieta (misiones 6 y 7)')
par('Un recuadro de unos 220 × 190 m centrado en la grieta, a 40 m sobre el terreno, con el mismo solape. El píxel baja a %.2f cm, lo que permite medir la apertura y el escalón de la grieta con más precisión. Al volar a 40 m sobre la zona urbana hay que revisar antes, en el lugar, que no haya antenas, tanques de agua, torres o árboles altos sobre las líneas (Figura 3).'%(E['gsd']/2))
figura(OUT+'/f_detalle_grieta.png','Figura 3. Misiones 6 y 7: líneas, waypoints y puntos de foto del vuelo de detalle a 40 m',SRC,hmax=7.6)
interp('Las diez líneas cubren la grieta, la cicatriz completa y la parte alta del depósito, con unos 60 m de margen a cada lado. Las fotos se toman cada %.1f m; en el centro del recuadro cada punto del terreno aparece en más de diez fotos, lo que da un modelo de superficie muy denso justo donde están los bordes de la grieta.'%E['phd'])
par('La Tabla 4 resume las siete misiones con el archivo de Litchi que corresponde a cada una.',kwn=True)
tabla('Tabla 4. Resumen de las misiones (un archivo CSV de Litchi por misión)',R.assign(**{'Archivo':['Litchi_M%d_*.csv'%m for m in R.mision]}).rename(columns={'mision':'Misión','tipo':'Tipo','lineas':'Líneas','dist_km':'Recorrido (km)','vel':'Velocidad (m/s)','tiempo_min':'Duración aprox. (min)','fotos':'Fotos','waypoints':'Waypoints'}),'elaboración propia.',widths=[1.5,4.4,3.3,2.5,2.4,2.6,1.5,2.2,4.4])
interp('Cada misión dura entre 11 y 17 minutos incluyendo el ascenso, el regreso y el aterrizaje, por debajo de la autonomía real del Mavic 2 Pro (unos 20 a 25 minutos útiles con viento moderado). En total son unos %d minutos de vuelo y %d fotos: hacen falta al menos tres baterías y una forma de recargarlas en el campo, o repartir el trabajo en dos jornadas. Ninguna misión supera los 99 waypoints que admite Litchi.'%(R.tiempo_min.sum(),R.fotos.sum()))
tit('7. Puntos de control y de chequeo')
par('Se proponen diez puntos de control (GCP), que entran en el ajuste del modelo, y cinco de chequeo (CHK), que no entran en el ajuste y sirven para medir el error real. Están repartidos entre la meseta y el pie, sobre terreno de pendiente baja (menos de 10 %), lejos del borde y a más de 80 m de la grieta, para que no queden sobre el bloque que se puede estar moviendo. Las coordenadas de la Tabla 5 son la ubicación ideal: en el terreno el blanco puede correrse hasta unos 20 m buscando un lugar abierto y firme (vereda, calle de tierra, plaza), siempre que no quede bajo árboles o cables.')
g=G2[['id','tipo','posicion','lat','lon','E_UTM21S','N_UTM21S','cota_IGN_aprox_m','dist_grieta_m']].copy()
g['lat']=g.lat.map('%.6f'.__mod__); g['lon']=g.lon.map('%.6f'.__mod__); g['E_UTM21S']=g.E_UTM21S.map('%.1f'.__mod__); g['N_UTM21S']=g.N_UTM21S.map('%.1f'.__mod__)
g=g.rename(columns={'id':'Punto','tipo':'Tipo','posicion':'Posición','lat':'Latitud','lon':'Longitud','E_UTM21S':'Este UTM 21S (m)','N_UTM21S':'Norte UTM 21S (m)','cota_IGN_aprox_m':'Cota IGN aprox. (m)','dist_grieta_m':'Distancia a la grieta (m)'})
tabla('Tabla 5. Ubicación prevista de los puntos de control (GCP) y de chequeo (CHK)',g,'elaboración propia; las cotas son aproximadas, tomadas del MDE IGN 5 m.')
interp('Siete GCP en la meseta y tres en el pie encierran la zona de la grieta por los dos niveles de la barranca, de modo que el modelo no se incline ni se deforme entre la meseta y el río. Los cinco puntos de chequeo quedan intercalados y permiten informar el error del producto con datos independientes. Las cotas del IGN sirven sólo para orientarse: la cota válida será la que se mida con GNSS.')
figura(OUT+'/f_blanco_gcp.png','Figura 4. Blanco recomendado para los puntos de control',"elaboración propia.",wmax=12,hmax=5.2)
interp('Un damero de 60 cm se ve con unos 32 píxeles por lado a 80 m, lo que permite marcar el centro con precisión de un píxel. El número del punto escrito sobre el blanco evita confusiones al procesar.')
par('**Cómo medir los puntos:**',kwn=True)
bullets(['Colocar los blancos antes del primer vuelo y no moverlos hasta terminar todas las misiones.',
 'Medir el centro de cada blanco con GNSS de doble frecuencia en modo RTK (dos registros de 30 s con solución fija) o estático para posprocesar (al menos 5 minutos por punto).',
 'Marco de referencia POSGAR 2007. Entregar coordenadas en UTM 21 Sur (EPSG:32721) y altura elipsoidal; convertir a altura sobre el nivel medio del mar (SRVN16) con el modelo de geoide GEOIDE-Ar 16 del IGN.',
 'Anotar en una planilla el número del punto, las coordenadas medidas, la hora y sacar una foto del blanco con su entorno.',
 'Para el monitoreo futuro: fijar pares de clavos o mojones a ambos lados de la grieta, cada 20 m aproximadamente, y medir la distancia entre ellos con cinta. Esa medida simple se puede repetir sin dron.'])
tit('8. Seguridad, permisos y vecinos')
par('El Mavic 2 Pro pesa unos 907 g y el área incluye zona urbana. Según la Resolución ANAC 550/2025 (vigente desde agosto de 2025, Partes 100 a 102 de las RAAC), los vuelos en zona urbana corresponden a la categoría específica (Parte 102), que requiere autorización previa, licencia del piloto, certificado de operador y seguro obligatorio de responsabilidad civil. Los operadores deben confirmar con el texto vigente qué les corresponde y tramitarlo con anticipación. Además:')
bullets(['Pedir permiso a la Municipalidad de Diamante y avisar a Defensa Civil; el vuelo sobre el río conviene comunicarlo a Prefectura Naval.',
 'Avisar a los vecinos de la barranca con un día de anticipación; muchos ya colaboraron con datos sobre las fisuras y pueden indicar el estado de la grieta.',
 'No volar sobre reuniones de personas. Mantener siempre la línea de vista: el punto más lejano está a unos 620 m del despegue, por eso se recomiendan dos observadores con radio, uno en cada extremo del área.',
 'Altura de regreso automático (RTH): 60 m sobre el despegue. Con ese valor el dron pasa sobre los edificios de la meseta y sobre el río queda por debajo de 120 m del agua. Acción al perder señal: regresar. Regreso por batería: 30 %.',
 'Calibrar la brújula lejos de autos y estructuras metálicas, actualizar el firmware y la base de datos de zonas restringidas, y hacer un vuelo corto de prueba antes de la primera misión.',
 'Viento: no volar con viento sostenido mayor de 7 m/s en superficie o ráfagas fuertes en el borde de la barranca, donde el viento del río sube por el talud. No volar con lluvia, llovizna ni niebla.'])
tit('9. Cuándo volar')
bullets(['Misiones 1 a 4 y 6 a 7 (verticales): entre las 10 y las 14 horas, con sol alto para que las sombras de la barranca y de los árboles sean cortas; un día nublado parejo es todavía mejor.',
 'Misión 5 (oblicua): a la tarde, entre las 14 y las 17 horas, cuando el sol da de frente sobre la cara de la barranca.',
 'Evitar días después de lluvias fuertes, por la seguridad del personal en el borde y porque el suelo mojado cambia de color entre fotos.',
 'Hacer todas las misiones en el mismo día o en días consecutivos, sin mover los blancos.'])
tit('10. Productos que se esperan')
bullets(['Ortomosaico de 2 cm (sector general) y 1 cm (sector de la grieta), GeoTIFF en EPSG:32721.',
 'Modelo digital de superficie y modelo digital de terreno (filtrando vegetación y edificios), GeoTIFF de 5 cm, alturas SRVN16.',
 'Nube de puntos clasificada en LAS o LAZ.',
 'Informe de procesamiento con el error en los puntos de control y en los de chequeo. Se espera un error del orden de 2 a 3 cm en planimetría y de 3 a 5 cm en altura.',
 'Planilla de los puntos medidos con GNSS y las fotos de cada blanco.'])
par('Para procesar sirven Agisoft Metashape, Pix4D o WebODM (gratuito). En todos los casos hay que activar la corrección de rolling shutter, importar los GCP y dejar los CHK sólo como control. El modelo de superficie resultante se podrá restar al MDE IGN de 2018 para medir el cambio desde la formación de la grieta.')
tit('11. Archivos que acompañan este plan')
bullets(['Plan_vuelo_dron_Diamante.kml: área, líneas de las siete misiones, despegue, puntos de control, puntos de foto (capa apagada), grieta, cicatriz y depósito. Se abre con Google Earth o QGIS.',
 'Litchi_M1 a Litchi_M7 (.csv): una misión por archivo, para importar en Litchi Mission Hub (Missions › Import). Al importar, revisar que las alturas queden “relativas al despegue” y la velocidad en 4 m/s (3 m/s en las misiones 5 a 7).',
 'Puntos_de_control_GCP.csv: coordenadas de los quince puntos en WGS 84, UTM 21 Sur y POSGAR 2007 faja 5.',
 'Puntos_de_foto.csv: los %d puntos donde se toma cada foto, con misión, línea, altura y ángulo de la cámara.'%len(X['F2']),
 'Figuras del plan en PNG.'])
par('**Antes de salir al campo**, abrir cada misión en Litchi Mission Hub con la vista 3D del terreno y recorrerla completa para confirmar que ningún tramo pasa cerca de obstáculos. Las alturas se calcularon con el MDE del IGN de 2018; construcciones o árboles crecidos después no están en ese modelo.')
tit('Fuentes')
for t in ['DJI (2018). Mavic 2 Pro: especificaciones técnicas. https://www.dji.com/mavic-2/info',
 'ANAC (2025). Resolución 550/2025, Partes 100, 101 y 102 de las RAAC. Boletín Oficial de la República Argentina, 8/08/2025.',
 'Marval O’Farrell Mairal (2025). Operaciones de aeronaves pilotadas a distancia. https://www.marval.com/Publicacion/operaciones-de-aeronaves-pilotadas-a-distancia-17321',
 'Litchi (VC Technology). Mission Hub: formato CSV de misiones. https://flylitchi.com/hub',
 'Instituto Geográfico Nacional. MDE-Ar 5 m y modelo de geoide GEOIDE-Ar 16. https://www.ign.gob.ar',
 'INPE / CONAE. Imagen CBERS-4A WPM del 26/09/2026 (pansharpened 2 m).']:
    p=par(t,align='l',size=11); p.paragraph_format.left_indent=Cm(0.8); p.paragraph_format.first_line_indent=Cm(-0.8)
d.save(OUT+'/Plan_de_vuelo_dron_Diamante.docx'); print('ok')
