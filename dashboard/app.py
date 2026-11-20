"""Panel local del proyecto. Iniciar con python -m src.iniciar_panel."""
from pathlib import Path
import sys

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.panel_datos import (ROOT, ENTRADAS, GEOMETRIA, NOMBRES, CONSULTAS,
    archivos_faltantes, firma_archivos, cargar_resultados, cargar_modelos,
    filtrar, resumen_configuraciones, obtener_caso, predecir_caso, consultar_datamart)

st.set_page_config(page_title="Eficiencia energética | Ulises González",
                   page_icon="🌿", layout="wide")

VERDE, NARANJA, AZUL = "#12776b", "#d28330", "#5186ad"
COLORES = {"Calefacción": NARANJA, "Refrigeración": VERDE,
           "Altura 3.5": VERDE, "Altura 7": NARANJA}
PREGUNTA = ("¿Cómo cambian las cargas de calefacción y refrigeración entre "
            "edificios con distinta compacidad relativa y altura total?")

st.markdown("""<style>
 .block-container {max-width:1500px; padding-top:2rem; padding-bottom:2rem;}
 h1,h2,h3 {letter-spacing:-.035em;}
 h1 {font-size:2.4rem !important; line-height:1.12 !important;}
 h2 {font-size:1.45rem !important; margin-top:.5rem !important;}
 h3 {font-size:1.1rem !important;}
 [data-testid="stSidebar"] {border-right:1px solid #d8e3de;}
 .brand {font-weight:800; font-size:1.35rem; letter-spacing:-.04em; margin-bottom:.25rem;}
 .eyebrow {font-size:.72rem; font-weight:700; letter-spacing:.14em; color:#528075; margin-bottom:.55rem;}
 .hero {background:linear-gradient(115deg,#163e35,#23594b); border-radius:20px;
   padding:1.8rem 2rem; color:#f6fff9; margin:.2rem 0 1.4rem; position:relative; overflow:hidden;}
 .hero:after {content:""; position:absolute; right:-40px; top:-75px; height:260px;
   width:260px; border:45px solid #ffffff09; border-radius:50%; pointer-events:none;}
 .hero h1 {color:#f6fff9; margin:0 0 .7rem; font-weight:750;}
 .hero p {max-width:850px; color:#d0e5d9; margin:0; line-height:1.65;}
 .hero .eyebrow {color:#a9d4bd;}
 [data-testid="stMetric"] {background:#fff; border:1px solid #dce5df;
   border-radius:14px; padding:1rem 1.1rem; border-top:3px solid #70a493;}
 [data-testid="stMetricLabel"] {font-size:.83rem; color:#567067;}
 [data-testid="stMetricValue"] {font-weight:650; letter-spacing:-.04em;}
 .note {background:#e9f2ec; border-left:3px solid #4b8c70; padding:1rem 1.2rem;
   border-radius:0 12px 12px 0; color:#254b3b; line-height:1.65; margin:1rem 0;}
 .foot {font-size:.77rem; color:#65796e; border-top:1px solid #dce5df;
   margin-top:2rem; padding-top:1rem;}
 .subtle {font-size:.85rem; color:#62766d; line-height:1.7;}
 div[data-testid="stHorizontalBlock"] {gap:1.25rem;}
 @media (max-width:700px) {
   .block-container {padding-top:1rem;} .hero {padding:1.3rem;}
   h1 {font-size:1.8rem !important;} .hero:after {display:none;}
 }
</style>""", unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def resultados(firma):
    return cargar_resultados()


@st.cache_resource(show_spinner=False)
def modelos(firma):
    return cargar_modelos()


def encabezado(numero, titulo, detalle):
    st.markdown(f'<div class="eyebrow">ENERGY EFFICIENCY / {numero}</div>', unsafe_allow_html=True)
    st.title(titulo)
    st.caption(detalle)


def grafica(fig, clave, altura=360):
    fig.update_layout(template="plotly_white", height=altura,
        font=dict(family="Arial, sans-serif", color="#355247", size=12),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=16,r=16,t=32,b=25),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, title_text=""),
        colorway=[VERDE,NARANJA,AZUL,"#a47297"])
    if fig.data and fig.data[0].type not in ("scatter3d", "pie"):
        fig.update_xaxes(gridcolor="#e4ece7", zeroline=False)
        fig.update_yaxes(gridcolor="#e4ece7", zeroline=False)
    st.plotly_chart(fig, width="stretch", key=clave,
        config={"displaylogo":False, "toImageButtonOptions":{"format":"png","scale":2}})


def descargar(df, nombre, etiqueta="Descargar CSV", clave=None):
    st.download_button(etiqueta, df.to_csv(index=False).encode("utf-8-sig"),
        file_name=nombre, mime="text/csv", key=clave)


def tabla(df):
    st.dataframe(df, width="stretch", hide_index=True)


def largo_cargas(df, id_vars):
    d = df.melt(id_vars=id_vars, value_vars=["Y1","Y2"],
                var_name="Carga", value_name="Valor")
    d["Carga"] = d.Carga.map(NOMBRES)
    return d


def curva_compacidad(df):
    resumen = resumen_configuraciones(df)
    d = largo_cargas(resumen,["X1","X5","registros"])
    d["Altura"] = d.X5.map(lambda v:f"Altura {v:g}")
    fig = px.line(d.sort_values("X1"), x="X1", y="Valor", color="Carga",
        line_dash="Altura", markers=True, color_discrete_map=COLORES,
        labels={"X1":"Compacidad relativa", "Valor":"Carga media · escala original"},
        hover_data={"X5":True,"registros":True,"Valor":":.2f"})
    return fig


faltan = archivos_faltantes()
if faltan:
    st.title("Prepara los datos del panel")
    st.info("Primero ejecuta el análisis desde la carpeta principal del proyecto.")
    st.code(r".\.venv\Scripts\python.exe -m src.ejecutar_proyecto", language="powershell")
    with st.expander("Archivos por generar"):
        st.write(faltan)
    if st.button("Volver a comprobar"):
        st.rerun()
    st.stop()

try:
    FIRMA = firma_archivos()
    R = resultados(FIRMA)
except Exception as error:
    st.error("No se pudieron leer los resultados. Ejecuta de nuevo el análisis del proyecto.")
    st.code(str(error))
    st.stop()

DF = R["datos"]
PRUEBA = R["prueba"]

with st.sidebar:
    st.markdown('<div class="brand">◈ Eficiencia energética</div>', unsafe_allow_html=True)
    st.caption("EXPLORAR · COMPARAR · PREDECIR")
    st.divider()
    pagina = st.radio("Secciones", ["Vista general", "Pregunta principal", "Simulador",
        "Explorar variables", "Evaluación", "Datos y Data Mart"], key="pagina")
    filtros_activos = pagina in ["Vista general","Pregunta principal","Explorar variables","Datos y Data Mart"]
    if filtros_activos:
        st.divider()
        st.markdown("**Filtrar observaciones**")
        alturas = st.multiselect("Altura total", sorted(DF.X5.unique()),
            default=sorted(DF.X5.unique()), key="f_altura",format_func=lambda v:f"{v:g}")
        orientaciones = st.multiselect("Orientación (código)", sorted(DF.X6.unique()),
            default=sorted(DF.X6.unique()), key="f_orientacion")
        cristales = st.multiselect("Acristalamiento", sorted(DF.X7.unique()),
            default=sorted(DF.X7.unique()), key="f_cristal",format_func=lambda v:f"{v:.0%}")
        FILTRO = filtrar(DF, alturas, orientaciones, cristales)
        st.caption(f"{len(FILTRO)} de {len(DF)} registros seleccionados.")
    else:
        FILTRO = DF.copy()
        st.caption("El simulador utiliza los casos del dataset completo. La evaluación conserva la prueba reservada.")
    st.divider()
    st.markdown("**Ulises González Coronado**")
    st.caption("Extracción de Conocimiento en Bases de Datos\n\nRecursamiento 2026 · UCI Energy Efficiency")

if filtros_activos and FILTRO.empty:
    st.warning("No hay registros con estos filtros. Selecciona al menos una altura, orientación y proporción de cristal compatibles.")
    st.stop()


def vista_general():
    st.markdown('<div class="hero"><div class="eyebrow">PROYECTO INTEGRADOR / ANÁLISIS DE EDIFICIOS</div>'
        '<h1>Del diseño a la demanda energética.</h1>'
        f'<p>{PREGUNTA}</p></div>', unsafe_allow_html=True)
    a,b,c,d = st.columns(4)
    a.metric("Simulaciones seleccionadas",f"{len(FILTRO):,}", help="Cada fila es una simulación, no un edificio medido en campo.")
    b.metric("Geometrías disponibles",str(FILTRO.grupo_geometria.nunique()))
    c.metric("Calefacción media",f"{FILTRO.Y1.mean():.2f}",help="Y1, en la escala original del dataset.")
    d.metric("Refrigeración media",f"{FILTRO.Y2.mean():.2f}",help="Y2, en la escala original del dataset.")
    st.write("")
    izquierda,derecha = st.columns([1.65,1])
    with izquierda:
        st.subheader("Cómo cambian las cargas")
        st.caption("Media de cada configuración. Las líneas separan los grupos de altura.")
        grafica(curva_compacidad(FILTRO),"inicio_curva")
    with derecha:
        st.subheader("Comparación por altura")
        st.caption("Los grupos también tienen geometrías diferentes.")
        grupos = FILTRO.groupby("X5",as_index=False)[["Y1","Y2"]].mean()
        grupos["Altura"] = grupos.X5.map(lambda v:f"{v:g}")
        grafica(px.bar(largo_cargas(grupos,["Altura"]),x="Altura",y="Valor",color="Carga",
            barmode="group",text_auto=".2f", color_discrete_map=COLORES,
            labels={"Valor":"Carga media · escala original"}),"inicio_altura")
    st.markdown('<div class="note"><strong>Qué podemos concluir.</strong> Las configuraciones de '
        'compacidad y altura tienen cargas distintas. Cada compacidad aparece con una sola altura: '
        'estos datos permiten comparar diseños, pero no aislar el efecto de cada característica.</div>',unsafe_allow_html=True)
    st.subheader("Un recorrido para presentar el proyecto")
    c1,c2,c3 = st.columns(3)
    c1.markdown("**01 / Entender la pregunta**\n\nCompara configuraciones y revisa sus valores medios y su variación.")
    c2.markdown("**02 / Hacer una predicción**\n\nElige dos casos y contrasta las estimaciones con los valores registrados.")
    c3.markdown("**03 / Revisar los errores**\n\nMira el desempeño en geometrías reservadas y compáralo con una referencia simple.")


def pregunta_principal():
    encabezado("01", "Compacidad, altura y cargas", PREGUNTA)
    st.info("Las comparaciones de esta sección usan observaciones del dataset, con los filtros de la izquierda. Son asociaciones entre configuraciones, no efectos causales.")
    por_altura=FILTRO.groupby("X5")[["Y1","Y2"]].mean()
    frases=[f"Para altura {h:g}, la carga media es {fila.Y1:.2f} en calefacción y {fila.Y2:.2f} en refrigeración"
            for h,fila in por_altura.iterrows()]
    st.markdown("**Lo que muestran los registros seleccionados:** "+". ".join(frases)+".")
    grafica(curva_compacidad(FILTRO),"pregunta_curva",410)
    izquierda,derecha = st.columns(2)
    with izquierda:
        st.subheader("Variación dentro de cada altura")
        d=largo_cargas(FILTRO,["X5"])
        d["Altura"]=d.X5.map(lambda v:f"{v:g}")
        grafica(px.box(d,x="Altura",y="Valor",color="Carga",color_discrete_map=COLORES,
            labels={"Valor":"Carga · escala original"}),"pregunta_box")
    with derecha:
        st.subheader("Dónde están los registros")
        objetivo=st.selectbox("Carga a observar",["Y1","Y2"],format_func=NOMBRES.get,key="pregunta_obj")
        d=FILTRO.copy()
        d["Altura"]=d.X5.map(lambda v:f"Altura {v:g}")
        grafica(px.scatter(d,x="X1",y=objetivo,color="Altura",opacity=.6,
            color_discrete_map=COLORES,hover_data=["id_registro","X7","X6"],
            labels={**NOMBRES,objetivo:f"{NOMBRES[objetivo]} · escala original"}),"pregunta_scatter")
    st.subheader("Comparar dos configuraciones observadas")
    resumen=resumen_configuraciones(FILTRO)
    etiqueta=lambda i:f"Compacidad {resumen.iloc[i].X1:.2f} · altura {resumen.iloc[i].X5:g}"
    a,b=st.columns(2)
    ia=a.selectbox("Configuración A",range(len(resumen)),format_func=etiqueta,key="comparar_a")
    ib=b.selectbox("Configuración B",range(len(resumen)),index=len(resumen)-1,format_func=etiqueta,key="comparar_b")
    fila_a,fila_b=resumen.iloc[ia],resumen.iloc[ib]
    a,b,c=st.columns(3)
    a.metric("Cambio en calefacción: B − A",f"{fila_b.Y1-fila_a.Y1:+.2f}")
    b.metric("Cambio en refrigeración: B − A",f"{fila_b.Y2-fila_a.Y2:+.2f}")
    c.metric("Registros por configuración",f"{int(fila_a.registros)} / {int(fila_b.registros)}")
    st.caption("Diferencia positiva: B tiene mayor carga media. También cambian otras propiedades de la geometría.")
    st.subheader("Resumen de configuraciones")
    tabla(resumen.rename(columns={"X1":"Compacidad","X5":"Altura","registros":"Registros",
        "Y1":"Calefacción media","Y2":"Refrigeración media", "Y1_min":"Calefacción mínima",
        "Y1_max":"Calefacción máxima","Y2_min":"Refrigeración mínima","Y2_max":"Refrigeración máxima"}).round(3))
    descargar(resumen,"comparacion_compacidad_altura.csv",clave="desc_pregunta")


def seleccionar_escenario(titulo, prefijo, indice):
    st.subheader(titulo)
    geometrias=DF[["grupo_geometria"]+GEOMETRIA].drop_duplicates().sort_values("X1")
    opciones=geometrias.grupo_geometria.tolist()
    def etiqueta(g):
        r=geometrias.loc[geometrias.grupo_geometria==g].iloc[0]
        return f"Compacidad {r.X1:.2f} · altura {r.X5:g}"
    g=st.selectbox("Diseño del edificio",opciones,index=indice,format_func=etiqueta,key=f"{prefijo}_g")
    sub=DF[DF.grupo_geometria==g]
    o=st.selectbox("Orientación (código)",sorted(sub.X6.unique()),key=f"{prefijo}_o")
    v=st.selectbox("Proporción de acristalamiento",sorted(sub.X7.unique()),
        index=2,format_func=lambda x:f"{x:.0%}",key=f"{prefijo}_v")
    distribuciones=sorted(sub.loc[(sub.X6==o)&np.isclose(sub.X7,v),"X8"].unique())
    # La clave incluye el dominio para evitar conservar una distribución inválida al cambiar el cristal.
    dist=st.selectbox("Distribución del cristal (código)",distribuciones,
        key=f"{prefijo}_d_{v}")
    caso=obtener_caso(DF,g,o,v,dist)
    r=caso.iloc[0]
    st.caption(f"Superficie: {r.X2:g} · Muros: {r.X3:g} · Techo: {r.X4:g}. La geometría se mantiene coherente con el diseño elegido.")
    conjunto=R["division"].set_index("id_registro").loc[int(r.id_registro),"conjunto"]
    st.caption(f"Registro {int(r.id_registro)} · conjunto de {conjunto}.")
    return caso


def simulador():
    encabezado("02", "Prueba dos diseños", "Cambia las características y compara las cargas estimadas al instante.")
    st.info("Elige combinaciones existentes en las simulaciones. Compacidad, altura y áreas se seleccionan juntas para conservar una geometría válida. No se reentrenan los modelos al mover los controles.")
    try:
        reg,cls=modelos(FIRMA)
        a,b=st.columns(2)
        with a:
            caso_a=seleccionar_escenario("Escenario A","a",0)
        with b:
            caso_b=seleccionar_escenario("Escenario B","b",DF.grupo_geometria.nunique()-1)
        pred_a,pred_b=predecir_caso(caso_a,reg,cls),predecir_caso(caso_b,reg,cls)
    except Exception as error:
        st.error("No se pudieron usar los modelos. Vuelve a ejecutar el análisis con las bibliotecas de tu entorno.")
        st.code(r".\.venv\Scripts\python.exe -m src.ejecutar_proyecto",language="powershell")
        with st.expander("Detalle del problema"):
            st.code(str(error))
        return
    st.divider()
    a,b,c,d=st.columns(4)
    a.metric("A · Calefacción estimada",f"{pred_a['Y1']:.2f}")
    b.metric("A · Refrigeración estimada",f"{pred_a['Y2']:.2f}")
    c.metric("B · Calefacción estimada",f"{pred_b['Y1']:.2f}")
    d.metric("B · Refrigeración estimada",f"{pred_b['Y2']:.2f}")
    st.caption(f"B − A: calefacción {pred_b['Y1']-pred_a['Y1']:+.2f}; refrigeración {pred_b['Y2']-pred_a['Y2']:+.2f}. Todos los valores usan la escala original.")
    a,b=st.columns([1.5,1])
    filas=[]
    for nombre,caso,pred in [("A",caso_a,pred_a),("B",caso_b,pred_b)]:
        for y in ["Y1","Y2"]:
            filas.append({"Escenario":nombre,"Carga":NOMBRES[y],"Registrado":float(caso.iloc[0][y]),
                "Predicción":pred[y],"Error absoluto":abs(pred[y]-caso.iloc[0][y]),
                "Clase predicha":pred["clase"]})
    comparacion=pd.DataFrame(filas)
    with a:
        st.subheader("Predicción frente al valor registrado")
        dibujo=comparacion.melt(id_vars=["Escenario","Carga"],value_vars=["Registrado","Predicción"],var_name="Tipo",value_name="Valor")
        dibujo["Caso"]=dibujo.Escenario+" · "+dibujo.Carga
        grafica(px.bar(dibujo,x="Caso",y="Valor",color="Tipo",barmode="group",text_auto=".2f",
            color_discrete_map={"Registrado":"#9cafa4","Predicción":VERDE},
            labels={"Valor":"Carga · escala original","Caso":""}),"sim_comparacion")
    with b:
        st.subheader("Clasificación de calefacción")
        st.write(f"**Escenario A:** carga {pred_a['clase']} · **Escenario B:** carga {pred_b['clase']}.")
        umbral=R["modelos"]["clasificacion"]["umbral_Y1"]
        st.caption(f"Clases de entrenamiento: baja si Y1 < {umbral:g}; alta desde {umbral:g}. Es una regla didáctica, no una certificación energética.")
        st.caption("La clasificación es un modelo independiente; su resultado puede diferir de aplicar el corte a la regresión.")
        mr=R["regresion"]
        mr=mr[mr.modelo==R["modelos"]["regresion"]["modelo"]].set_index("objetivo")
        st.markdown(f"**Error medio en prueba**\n\nCalefacción: **{mr.loc['Y1','MAE']:.2f}** · Refrigeración: **{mr.loc['Y2','MAE']:.2f}**")
        st.caption("Este error resume 231 casos de prueba futura simulada; no es un intervalo de confianza para cada predicción. Un caso de entrenamiento no sirve para demostrar generalización.")
    st.subheader("Otros diseños con la misma orientación y cristal que A")
    base=DF[(DF.X6==caso_a.X6.iloc[0]) & np.isclose(DF.X7,caso_a.X7.iloc[0]) & (DF.X8==caso_a.X8.iloc[0])].copy()
    pred=reg.predict(base[ENTRADAS])
    base["Y1_estimada"],base["Y2_estimada"]=pred[:,0],pred[:,1]
    d=base.melt(id_vars=["X1","X5"],value_vars=["Y1_estimada","Y2_estimada"],var_name="Carga",value_name="Valor")
    d["Carga"]=d.Carga.map({"Y1_estimada":"Calefacción","Y2_estimada":"Refrigeración"})
    d["Altura"]=d.X5.map(lambda x:f"Altura {x:g}")
    grafica(px.line(d.sort_values("X1"),x="X1",y="Valor",color="Carga",line_dash="Altura",markers=True,
        color_discrete_map=COLORES,labels={"X1":"Compacidad relativa","Valor":"Carga predicha · escala original"}),"sim_curva")
    st.caption("Cambian las geometrías completas. La curva no representa el efecto aislado de modificar únicamente la compacidad o la altura.")
    with st.expander("Ver entradas, predicciones y errores de A y B"):
        entradas=pd.concat([caso_a.assign(escenario="A"),caso_b.assign(escenario="B")])
        tabla(entradas[["escenario","id_registro"]+ENTRADAS].rename(columns=NOMBRES))
        tabla(comparacion.round(3))
    exportar=pd.concat([caso_a.assign(escenario="A",Y1_predicha=pred_a["Y1"],Y2_predicha=pred_a["Y2"],clase_predicha=pred_a["clase"]),
                       caso_b.assign(escenario="B",Y1_predicha=pred_b["Y1"],Y2_predicha=pred_b["Y2"],clase_predicha=pred_b["clase"])])
    descargar(exportar,"predicciones_escenarios.csv",clave="desc_sim")


def explorar_variables():
    encabezado("03","Explora las relaciones","Distribuciones, asociaciones y una vista 3D de los registros seleccionados.")
    objetivo=st.selectbox("Variable que quieres analizar",["Y1","Y2"],format_func=NOMBRES.get,key="explorar_obj")
    t1,t2,t3=st.tabs(["Distribuciones y relaciones","Correlaciones","Vista 3D"])
    with t1:
        a,b=st.columns(2)
        with a:
            st.subheader("Distribución de la carga")
            grafica(px.histogram(FILTRO,x=objetivo,nbins=24,color_discrete_sequence=[VERDE],
                labels={objetivo:f"{NOMBRES[objetivo]} · escala original"}),"exp_hist")
        with b:
            st.subheader("Compara con otra característica")
            variable=st.selectbox("Característica",ENTRADAS,format_func=NOMBRES.get,key="explorar_x")
            datos=FILTRO.copy()
            datos["Altura"]=datos.X5.map(lambda v:f"Altura {v:g}")
            if variable in ["X6","X7","X8"]:
                datos["Categoría"]=datos[variable].map(lambda v:f"{v:g}")
                figura=px.box(datos,x="Categoría",y=objetivo,color="Altura",color_discrete_map=COLORES,
                    labels={"Categoría":NOMBRES[variable],objetivo:f"{NOMBRES[objetivo]} · escala original"})
            else:
                figura=px.scatter(datos,x=variable,y=objetivo,color="Altura",opacity=.65,
                    color_discrete_map=COLORES,hover_data=["id_registro"],labels=NOMBRES)
            grafica(figura,"exp_relacion")
        st.caption("Las diferencias observadas no demuestran que una característica cause por sí sola el cambio de carga. Orientación y distribución se conservan como códigos.")
    with t2:
        st.subheader("Asociación entre variables numéricas")
        cols=["X1","X2","X3","X4","X5","X7","Y1","Y2"]
        corr=FILTRO[cols].rename(columns=NOMBRES).corr()
        fig=px.imshow(corr,zmin=-1,zmax=1,color_continuous_scale="BrBG",text_auto=".2f",aspect="auto",
            labels={"color":"Correlación"})
        grafica(fig,"exp_correlacion",520)
        st.caption("Correlación de Pearson: de −1 a 1. No implica causalidad. Las casillas vacías corresponden a variables sin variación con los filtros actuales. Se excluyen los códigos de categorías X6 y X8.")
    with t3:
        st.subheader("Compacidad y las dos cargas")
        d=FILTRO.copy()
        d["Altura"]=d.X5.map(lambda v:f"Altura {v:g}")
        fig=px.scatter_3d(d,x="X1",y="Y1",z="Y2",color="Altura",opacity=.65,
            color_discrete_map=COLORES,hover_data=["id_registro","X7"],labels=NOMBRES)
        fig.update_traces(marker_size=4)
        grafica(fig,"exp_3d",540)
        st.caption("Arrastra para girar, usa la rueda para acercarte y pasa el cursor para consultar un registro.")


def evaluacion():
    encabezado("04","Qué tan bien predicen los modelos","Evaluación sobre geometrías completas reservadas. Esta sección no cambia con los filtros de observaciones.")
    meta=R["modelos"]
    seleccion=R["regresion"][R["regresion"].modelo==meta["regresion"]["modelo"]].set_index("objetivo")
    mc=R["clasificacion"][R["clasificacion"].modelo==meta["clasificacion"]["modelo"]].iloc[0]
    a,b,c,d=st.columns(4)
    a.metric("MAE · Calefacción",f"{seleccion.loc['Y1','MAE']:.2f}")
    b.metric("MAE · Refrigeración",f"{seleccion.loc['Y2','MAE']:.2f}")
    c.metric("Exactitud de clasificación",f"{mc.accuracy:.2%}")
    d.metric("Casos reservados",str(len(PRUEBA)))
    st.caption("MAE: diferencia absoluta media, en la escala original; un valor menor es mejor. No es un porcentaje.")
    t1,t2,t3=st.tabs(["Regresión","Clasificación","Cómo se evaluó"])
    with t1:
        y=st.selectbox("Carga a evaluar",["Y1","Y2"],format_func=NOMBRES.get,key="eval_obj")
        a,b=st.columns(2)
        with a:
            st.subheader("Valores registrados y predichos")
            fig=px.scatter(PRUEBA,x=y,y=f"{y}_predicha",hover_data=["id_registro","X1","X5"],
                opacity=.7,color_discrete_sequence=[VERDE],labels={y:"Valor registrado",f"{y}_predicha":"Predicción"})
            limite=[min(PRUEBA[y].min(),PRUEBA[f"{y}_predicha"].min()),max(PRUEBA[y].max(),PRUEBA[f"{y}_predicha"].max())]
            fig.add_trace(go.Scatter(x=limite,y=limite,mode="lines",name="Predicción perfecta",line=dict(dash="dash",color=NARANJA)))
            grafica(fig,"eval_reales")
        with b:
            st.subheader("Dónde se concentran los errores")
            errores=PRUEBA.assign(error=PRUEBA[y]-PRUEBA[f"{y}_predicha"])
            fig=px.scatter(errores,x=f"{y}_predicha",y="error",hover_data=["id_registro","X1","X5"],opacity=.7,
                labels={f"{y}_predicha":"Predicción","error":"Registrado − predicho"},color_discrete_sequence=[AZUL])
            fig.add_hline(y=0,line_dash="dash",line_color=NARANJA)
            grafica(fig,"eval_errores")
        st.caption("Un error positivo indica que el modelo subestimó la carga. Los resultados corresponden a una sola separación.")
        a,b=st.columns([1,1.2])
        with a:
            st.subheader("Comparación con la media")
            mr=R["regresion"].copy()
            mr["Carga"]=mr.objetivo.map(NOMBRES)
            grafica(px.bar(mr,x="Carga",y="MAE",color="modelo",barmode="group",text_auto=".2f",
                labels={"MAE":"Error absoluto medio","modelo":"Modelo"}),"eval_base")
        with b:
            st.subheader("Métricas completas")
            tabla(R["regresion"].rename(columns={"objetivo":"Carga"}).round(4))
            st.caption("Referencia_media predice siempre el promedio del entrenamiento. RMSE penaliza más los errores grandes. R² puede ser negativo y no representa un porcentaje de aciertos.")
        descargar(PRUEBA,"predicciones_geometrias_prueba.csv",clave="desc_prueba")
    with t2:
        a,b=st.columns([1.1,1])
        cm=np.array(meta["clasificacion"]["matriz_confusion_baja_alta"])
        with a:
            st.subheader("Matriz de confusión")
            fig=px.imshow(cm,x=["Baja","Alta"],y=["Baja","Alta"],text_auto=True,
                color_continuous_scale="Greens",labels={"x":"Clase predicha","y":"Clase registrada","color":"Casos"},aspect="auto")
            grafica(fig,"eval_confusion")
        with b:
            st.subheader("Aciertos y equivocaciones")
            aciertos=int(np.trace(cm))
            st.markdown(f"**{aciertos} aciertos de {int(cm.sum())} casos.**")
            st.write(f"Cargas bajas predichas como altas: {int(cm[0,1])}. Cargas altas predichas como bajas: {int(cm[1,0])}.")
            st.caption(f"Clase alta: Y1 ≥ {meta['clasificacion']['umbral_Y1']:g}. Esta regla didáctica no indica una certificación energética.")
            tabla(R["clasificacion"].round(4))
            st.caption("F1 macro pondera por igual las dos clases. Referencia_mayoria usa siempre la clase más frecuente del entrenamiento.")
        fallos=PRUEBA[PRUEBA.clase_real!=PRUEBA.clase_predicha]
        with st.expander(f"Ver los {len(fallos)} errores de clasificación"):
            tabla(fallos[["id_registro","X1","X5","Y1","clase_real","clase_predicha"]].rename(columns=NOMBRES))
    with t3:
        st.subheader("Separación por geometría")
        st.write(f"Entrenamiento: {meta['entrenamiento_filas']} registros en {len(meta['geometrias_entrenamiento'])} geometrías. Prueba: {meta['prueba_filas']} registros en {len(meta['geometrias_prueba'])} geometrías. Geometrías compartidas: {meta['geometrias_compartidas']}.")
        div=R["division"].groupby(["grupo_geometria","conjunto"]).size().reset_index(name="Registros")
        div["Geometría"]=div.grupo_geometria.map(str)
        grafica(px.bar(div,x="Geometría",y="Registros",color="conjunto",color_discrete_map={"entrenamiento":VERDE,"prueba":NARANJA}),"eval_division",300)
        st.write("Todas las variantes de una geometría permanecen en el mismo conjunto. Dentro del entrenamiento se comparan modelos y parámetros con GroupKFold de tres particiones; el preprocesamiento se ajusta dentro de cada partición.")
        st.write(f"Modelos elegidos: {meta['regresion']['modelo']} para las dos cargas y {meta['clasificacion']['modelo']} para la clase de calefacción.")
        st.info("Solo entran X1–X8 a los modelos. Los identificadores, el grupo geométrico y los objetivos quedan fuera. Son 12 geometrías simuladas: el resultado no acredita desempeño en edificios reales.")
        with st.expander("Parámetros y versiones de la ejecución"):
            st.json(meta)


def datos_datamart():
    encabezado("05","Datos y trazabilidad","Revisa el archivo procesado, su calidad y las consultas del almacén analítico local.")
    t1,t2,t3=st.tabs(["Datos seleccionados","Calidad y variables","Data Mart local"])
    with t1:
        st.caption(f"{len(FILTRO)} registros con los filtros actuales. El CSV descargado conserva los códigos originales.")
        tabla(FILTRO.rename(columns=NOMBRES))
        descargar(FILTRO,"eficiencia_energetica_filtrada.csv",clave="desc_datos")
        with st.expander("Estadísticas de los registros seleccionados"):
            tabla(FILTRO[ENTRADAS+["Y1","Y2"]].describe().T.reset_index().rename(columns={"index":"Variable"}).round(3))
    with t2:
        q=R["calidad"]
        a,b,c,d=st.columns(4)
        a.metric("Registros originales",str(q["filas_originales"]))
        b.metric("Valores faltantes",str(q["faltantes"]))
        c.metric("Filas duplicadas",str(q["duplicados_completos"]))
        d.metric("Filas eliminadas",str(q["filas_eliminadas"]))
        st.write("Se validaron los datos sin eliminar filas ni rellenar valores. El archivo original se conserva en data/raw; los derivados se guardan en data/processed.")
        definiciones={"X1":"Compacidad del diseño; variable central de la pregunta.",
            "X2":"Superficie total del diseño.","X3":"Superficie de sus muros.","X4":"Superficie del techo.",
            "X5":"Altura total; aparecen dos valores: 3.5 y 7.",
            "X6":"Categoría codificada: 2, 3, 4 o 5; no es una escala de intensidad.",
            "X7":"Proporción de acristalamiento: 0, 0.1, 0.25 o 0.4.",
            "X8":"Categoría de distribución del cristal: códigos de 0 a 5.",
            "Y1":"Carga de calefacción; objetivo numérico de la regresión.",
            "Y2":"Carga de refrigeración; segundo objetivo numérico."}
        tabla(pd.DataFrame([{"Código":k,"Variable":NOMBRES[k],"Descripción":v} for k,v in definiciones.items()]))
        st.caption("Las cargas se muestran en su escala original; no se asignan unidades ni direcciones cardinales ausentes de la documentación usada en el avance.")
        with st.expander("Registro completo de calidad y huella del original"):
            st.json(q)
    with t3:
        st.info("Las consultas de esta pestaña usan el Data Mart completo, sin los filtros laterales. Se ejecutan en SQLite y solo leen datos. La validación en SQL Server sigue pendiente.")
        st.markdown("**Una tabla de hechos, tres dimensiones**\n\nhecho_simulacion relaciona cada registro con dim_geometria, dim_orientacion y dim_acristalamiento mediante sus llaves foráneas.")
        consulta=st.selectbox("Consulta preparada",list(CONSULTAS),key="consulta_sql")
        try:
            datos=consultar_datamart(consulta)
            tabla(datos.round(3))
            descargar(datos,"consulta_datamart_panel.csv",clave="desc_sql")
        except Exception as error:
            st.error("No se pudo consultar el Data Mart. Vuelve a ejecutar el análisis para reconstruirlo.")
            st.code(str(error))
        with st.expander("Ver la consulta SQL"):
            st.code(CONSULTAS[consulta],language="sql")
        st.caption("Este panel es un apoyo local para la revisión. El dashboard final de Power BI previsto en la guía continúa pendiente.")


{"Vista general":vista_general,"Pregunta principal":pregunta_principal,
 "Simulador":simulador,"Explorar variables":explorar_variables,
 "Evaluación":evaluacion,"Datos y Data Mart":datos_datamart}[pagina]()

st.markdown('<div class="foot">Energy Efficiency · Tsanas y Xifara / UCI · 768 simulaciones · '
    'Cargas en escala original · Proyecto de Ulises González Coronado</div>',unsafe_allow_html=True)
