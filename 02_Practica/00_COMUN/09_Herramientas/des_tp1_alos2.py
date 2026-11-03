# -*- coding: utf-8 -*-
"""
des_tp1_alos2.py  (docente)  Consulta el catalogo G-Portal de JAXA (sin cuenta) por escenas
ALOS-2 PALSAR-2 sobre un sitio y una ventana de fechas, y por si acaso tambien ASF.
Deja la respuesta cruda y una tabla en Tp1_Convergencia/05_Resultados/04_Tablas/alos2_consulta_<SITIO>.csv

USO  python des_tp1_alos2.py --sitio B_CONCORDIA --desde 2023-10-20 --hasta 2023-11-20
"""
import argparse, os, sys, re, json
_d = os.path.dirname(os.path.abspath(__file__))
while not os.path.isdir(os.path.join(_d, "00_COMUN")) and _d != os.path.dirname(_d):
    _d = os.path.dirname(_d)
sys.path.insert(0, os.path.join(_d, "00_COMUN"))
import requests, pandas as pd
from configuracion_comun import SITIOS, ruta_tp

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sitio", default="B_CONCORDIA"); ap.add_argument("--desde", default="2023-10-20"); ap.add_argument("--hasta", default="2023-11-20")
    a = ap.parse_args()
    x0, y0, x1, y1 = SITIOS[a.sitio]["bbox"]
    filas = []
    crudo = ruta_tp("Tp1", "05_Resultados", "06_Control_calidad", "alos2_gportal_%s.xml" % a.sitio)
    url = "https://gportal.jaxa.jp/csw/csw"
    total = None
    for start in range(1, 2001, 100):
        p = {"service": "CSW", "version": "3.0.0", "request": "GetRecords", "bbox": "%s,%s,%s,%s" % (x0, y0, x1, y1),
             "startDate": a.desde + "T00:00:00Z", "endDate": a.hasta + "T23:59:59Z", "maxRecords": 100, "startPosition": start, "outputFormat": "application/json"}
        try:
            r = requests.get(url, params=p, timeout=120)
        except Exception as e:
            print("G-Portal no respondio:", e); break
        print("G-Portal", r.status_code, r.url[:160])
        if "maintenance" in r.text.lower():
            print("G-Portal: el sitio respondio 'down for maintenance': consulta no realizada"); break
        if start == 1:
            open(crudo, "wb").write(r.content)
        txt = r.text
        try:
            js = r.json(); feats = js.get("features", [])
            total = js.get("properties", {}).get("totalResults", total)
            for f in feats:
                pr = f.get("properties", {})
                ident = pr.get("identifier") or f.get("id") or ""
                filas.append({"fuente": "G-Portal", "identificador": ident, "titulo": pr.get("title", ""),
                              "inicio": pr.get("beginPosition", pr.get("date", "")), "producto": pr.get("productType", ""),
                              "json": json.dumps(pr)[:300]})
            if not feats: break
        except ValueError:
            ids = re.findall(r"<dc:identifier>([^<]+)</dc:identifier>", txt)
            tit = re.findall(r"<dc:title>([^<]+)</dc:title>", txt)
            dts = re.findall(r"<dc:date>([^<]+)</dc:date>", txt)
            m = re.search(r'numberOfRecordsMatched="(\d+)"', txt); total = m.group(1) if m else total
            for i, ident in enumerate(ids):
                filas.append({"fuente": "G-Portal", "identificador": ident, "titulo": tit[i] if i < len(tit) else "",
                              "inicio": dts[i] if i < len(dts) else "", "producto": "", "json": ""})
            if not ids: break
    print("G-Portal: registros declarados", total, "leidos", len(filas))
    try:
        import asf_search as asf
        res = asf.geo_search(platform=["ALOS-2"], intersectsWith="POLYGON((%s %s,%s %s,%s %s,%s %s,%s %s))" % (x0, y0, x1, y0, x1, y1, x0, y1, x0, y0),
                             start=a.desde, end=a.hasta)
        print("ASF ALOS-2:", len(res))
        for g in res:
            pr = g.properties
            print("ASF propiedades:", json.dumps(pr, default=str)[:3000])
            try:
                from shapely.geometry import shape, box
                hu = shape(g.geometry); sit = box(x0, y0, x1, y1)
                cob = 100.0 * hu.intersection(sit).area / sit.area
            except Exception:
                cob = float("nan")
            print("ASF %s: huella sobre el sitio %.1f %%" % (pr.get("sceneName", ""), cob))
            filas.append({"fuente": "ASF", "identificador": pr.get("sceneName", ""), "titulo": pr.get("beamModeType", ""),
                          "inicio": pr.get("startTime", ""), "producto": pr.get("processingLevel", ""),
                          "json": "huella %.1f %%; %s" % (cob, json.dumps(pr, default=str)[:400])})
    except Exception as e:
        print("ASF ALOS-2 no disponible:", str(e)[:200])
    t = pd.DataFrame(filas, columns=["fuente", "identificador", "titulo", "inicio", "producto", "json"])
    alos = t[t.apply(lambda f: bool(re.search(r"ALOS-?2|PALSAR-?2|ALOS2", " ".join(map(str, f.values)), re.I)), axis=1)]
    print("Registros ALOS-2 / PALSAR-2:", len(alos))
    print(alos[["fuente", "identificador", "inicio", "producto"]].to_string(index=False))
    print("Productos de todos los registros:", t.producto.value_counts().head(20).to_dict())
    print("Ejemplos de titulos:", list(t.titulo.head(15)))
    salida = ruta_tp("Tp1", "05_Resultados", "04_Tablas", "alos2_consulta_%s.csv" % a.sitio)
    t.to_csv(salida, index=False, encoding="utf-8-sig"); print("->", salida)

if __name__ == "__main__":
    main()
