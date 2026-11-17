"""Renderiza informes y crea hojas de contacto para inspección visual."""
import json
import pymupdf as fitz
from PIL import Image, ImageOps, ImageDraw
from src.preparacion_datos import ROOT, guardar_json

def revisar():
    nombres=['Gonzalez_Coronado_Ulises_U2_AE1_Diagnostico','Gonzalez_Coronado_Ulises_U2_AE2_PreparacionDatos',
             'Gonzalez_Coronado_Ulises_U3_Informe','Gonzalez_Coronado_Ulises_U4_Informe','Informe_Final']
    out=ROOT/'tmp/pdfs';out.mkdir(parents=True,exist_ok=True)
    resultado=[]
    for nombre in nombres:
        doc=fitz.open(ROOT/'docs'/f'{nombre}.pdf'); thumbs=[]
        for i,page in enumerate(doc):
            pix=page.get_pixmap(matrix=fitz.Matrix(1.2,1.2)); ruta=out/f'{nombre}_{i+1:02}.png';pix.save(ruta)
            im=Image.open(ruta).convert('RGB');im.thumbnail((360,510))
            thumb=Image.new('RGB',(380,540),'#dde6eb');thumb.paste(im,((380-im.width)//2,10));ImageDraw.Draw(thumb).text((12,522),f'Página {i+1}',fill='black');thumbs.append(thumb)
            # No texto fuera de márgenes de la página.
            for b in page.get_text('blocks'):
                assert b[0]>=0 and b[1]>=0 and b[2]<=page.rect.width+1 and b[3]<=page.rect.height+1,(nombre,i,b)
        for inicio in range(0,len(thumbs),6):
            sheet=Image.new('RGB',(1140,540*((min(6,len(thumbs)-inicio)+2)//3)),'white')
            for j,im in enumerate(thumbs[inicio:inicio+6]):sheet.paste(im,((j%3)*380,(j//3)*540))
            sheet.save(out/f'{nombre}_contacto_{inicio//6+1}.png')
        resultado.append({'archivo':nombre+'.pdf','paginas':len(doc),'texto_dentro_pagina':True})
        print(nombre,len(doc),'páginas',flush=True)
    guardar_json(ROOT/'docs/verificacion_pdfs.json',{'informes':resultado})

if __name__=='__main__':revisar()
