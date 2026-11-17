// Requiere @oai/artifact-tool y el runtime de presentaciones de Codex.
import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
const root=process.cwd();
const runtime=process.env.ARTIFACT_RUNTIME || 'C:/Users/DELL/.cache/codex-runtimes/codex-primary-runtime/dependencies';
const skill=process.env.PRESENTATIONS_SKILL || 'C:/Users/DELL/.codex/plugins/cache/openai-primary-runtime/presentations/26.1112.11217/skills/presentations';
const {Presentation,PresentationFile}=await import(pathToFileURL(path.join(runtime,'node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs')));
const {finalizePresentation,applyPresentationChartFont}=await import(pathToFileURL(path.join(skill,'container_tools/artifact_tool_utils.mjs')));
const tmp=path.join(root,'tmp/presentacion'); await fs.mkdir(tmp,{recursive:true});
const deck=Presentation.create({slideSize:{width:1280,height:720}});
const font='Arial', ink='#14384A', teal='#008C86';
function text(s,t,x,y,w,h,size=28,bold=false,color=ink){const a=s.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});a.text=t;a.text.style={fontFamily:font,fontSize:size,bold,color};return a;}
function slide(title,notes){const s=deck.slides.add();s.background.fill='#F7FAFC';text(s,title,65,45,1145,105,42,true);s.speakerNotes.text=notes;return s;}
function para(s,t,y=190){text(s,t,75,y,1110,410,30);}
function chart(s,categories,series,opt={}){const c=s.charts.add('bar',{position:{left:70,top:165,width:750,height:400},categories,series:series.map(s=>({...s,values:s.values.map(v=>Number(v.toFixed(6)))})),barOptions:{direction:'column',grouping:'clustered'},hasLegend:series.length>1,legend:{position:'bottom'},xAxis:{textStyle:{fontFamily:font,fontSize:20}},yAxis:{minimumScale:0,textStyle:{fontFamily:font,fontSize:20},numberFormatCode:opt.format||'0.0'},dataLabels:{showValue:true,position:'outEnd',numberFormatCode:opt.format||'0.0',textStyle:{fontFamily:font,fontSize:19}},...opt});applyPresentationChartFont(c,{fontFamily:font});return c;}
async function csv(file){let [head,...rows]=(await fs.readFile(path.join(root,file),'utf8')).trim().split(/\r?\n/).map(x=>x.split(','));return rows.map(r=>Object.fromEntries(head.map((h,i)=>[h,Number.isNaN(Number(r[i]))?r[i]:Number(r[i])])));}
const altura=await csv('data/processed/resumen_altura.csv'), reg=await csv('docs/metricas_regresion.csv'), pca=await csv('docs/varianza_pca.csv');
let s=slide('Eficiencia energética de edificios','Fuente: UCI Energy Efficiency, https://doi.org/10.24432/C51307. Proyecto de Ulises González Coronado, recursamiento ECBD 2026.');
text(s,'Geometría, predicción y patrones',75,255,1110,90,46,false,teal);
text(s,'Ulises González Coronado\nProyecto Integrador de Recursamiento 2026',75,480,1110,110,28);
s=slide('Problema y datos','Fuente: data/raw/ENB2012_data.xlsx y docs/diccionario_datos.md. UCI: https://doi.org/10.24432/C51307. Cada registro es una simulación. Las unidades de Y1/Y2 no se declaran en la ficha consultada.');
para(s,'¿Cómo cambian las cargas de calefacción y refrigeración entre geometrías y alturas?\n\n768 simulaciones, 12 geometrías y 8 variables predictoras.\nY1 representa calefacción y Y2 refrigeración.\n\nEl análisis busca comparar diseños y anticipar cargas dentro del alcance del dataset.');
s=slide('Preparación y almacenamiento','Fuentes: notebooks U2_AE1 y U2_AE2, src/etl_sqlserver.py, sql/datamart.sql, docs/verificacion_sqlserver.json. En la demostración abrir dbo.HECHOS y ejecutar sql/consulta_defensa.sql.');
para(s,'Extracción: Excel original conservado con su huella SHA-256.\n\nTransformación: tipos, claves dimensionales y atributos de análisis. No hay nulos ni duplicados que justifiquen eliminar filas.\n\nCarga: SQL Server REC_ECBD_Energia, 768 hechos y 9 relaciones. Geometría depende de altura. Acristalamiento depende de porcentaje y distribución.');
s=slide('Las cargas medias difieren entre alturas','Fuente: data/processed/resumen_altura.csv. Altura y compacidad están confundidas: ningún valor de compacidad aparece en ambas alturas. Esta comparación no identifica causalidad.');
chart(s,altura.map(r=>String(r.X5)),[{name:'Calefacción Y1',values:altura.map(r=>r.calefaccion_media),fill:teal},{name:'Refrigeración Y2',values:altura.map(r=>r.refrigeracion_media),fill:'#375A75'}]);
text(s,'Los diseños de altura 7 presentan cargas mayores.\n\nTambién cambia la geometría. No se puede atribuir la diferencia solo a la altura.',860,200,335,340,28);
text(s,'Altura total en el eje horizontal. Cargas en la escala original del dataset.',75,605,1110,60,23);
s=slide('Regresión sobre geometrías no vistas','Fuente: docs/metricas_regresion.csv y docs/resultados_modelos.json. 576 registros de nueve geometrías para entrenamiento y 192 de tres geometrías para prueba. GridSearchCV usa GroupKFold de tres particiones solo en entrenamiento. Random Forest: max_depth=8, min_samples_leaf=1.');
chart(s,['Y1 calefacción','Y2 refrigeración'],[{name:'Referencia media',values:reg.filter(r=>r.modelo==='Referencia_media').map(r=>r.MAE),fill:'#9EADB8'},{name:'Random Forest',values:reg.filter(r=>r.modelo==='RandomForest').map(r=>r.MAE),fill:teal}]);
text(s,'MAE menor significa menos error.\n\nY1: 3.33\nY2: 4.33\n\nR²: 0.806 y 0.696.',860,185,335,370,28);
text(s,'Prueba: 192 simulaciones. Ninguna geometría de prueba aparece en entrenamiento.',75,605,1110,65,23);
s=slide('Clasificación y errores relevantes','Fuentes: docs/reporte_clasificacion.json y docs/metricas_clasificacion.csv. Regresión logística C=1. Umbral didáctico de carga alta: Y1 >=25. Matriz con filas reales baja/alta y columnas predichas baja/alta: [[72,0],[40,80]].');
text(s,'79.17%',75,180,450,100,72,true,teal);
text(s,'Accuracy en prueba',75,290,500,55,28);
text(s,'F1 macro: 0.7913\nPrecision macro: 0.8214\nRecall macro: 0.8333',75,395,520,160,29);
text(s,'40 de 120 casos de carga alta se clasifican como baja.\n\nEse error limita el uso del modelo para detectar todos los diseños exigentes.\n\nLa clase alta es didáctica: Y1 ≥ 25.',660,185,535,385,30);
s=slide('Dos grupos describen patrones geométricos','Fuente: docs/resultados_no_supervisados.json, docs/evaluacion_clusters.csv y data/processed/perfiles_clusters.csv. KMeans sobre X1-X5 y X7 tras StandardScaler. Y1/Y2 y códigos nominales excluidos. Se comparan k=2..8.');
text(s,'k = 2',75,190,480,100,72,true,teal);
text(s,'Silhouette: 0.5244\n384 simulaciones por grupo',75,325,500,130,31);
text(s,'Los clusters separan alturas de 3.5 y 7 junto con sus geometrías.\n\nEl agrupamiento permite comparar diseños semejantes. La correlación geométrica domina el resultado.',660,195,535,330,30);
s=slide('PCA conserva 82.38% en dos componentes','Fuente: docs/varianza_pca.csv y docs/cargas_pca.csv. PCA sobre las mismas seis variables estandarizadas del clustering. PC3 eleva la varianza acumulada a 99.05%.');
chart(s,pca.map(r=>r.componente),[{name:'Varianza explicada',values:pca.map(r=>r.varianza_explicada),fill:teal}],{format:'0%'});
text(s,'PC1: 61.72%\nPC2: 20.66%\n\nTres componentes superan el 95%.\n\nLa proyección 2D simplifica los datos y pierde parte de la información.',860,180,335,390,27);
s=slide('Conclusiones y decisiones','Fuentes: docs/Informe_Final.pdf y docs/guia_revision_proyecto.md. Demostración final: recorrer cuatro páginas en Power BI, filtrar altura y mostrar Vista de modelo. Las recomendaciones requieren validación externa antes de aplicarse a edificios reales.');
text(s,'Conclusiones',75,170,500,60,30,true,teal);
text(s,'1. Altura y geometría se asocian con las cargas observadas.\n\n2. Random Forest mejora la referencia, pero la clasificación omite casos de carga alta.\n\n3. Dos grupos y PCA resumen gran parte de la estructura geométrica.',75,245,535,360,28);
text(s,'Recomendaciones',685,170,500,60,30,true,teal);
text(s,'Comparar alternativas dentro de grupos geométricos similares.\n\nValidar con consumos reales y revisar falsos negativos antes de usar las predicciones para decisiones de construcción.',685,245,510,340,29);
for(let i=0;i<deck.slides.items.length;i++){let b=await deck.export({slide:deck.slides.items[i],format:'png',scale:1});await fs.writeFile(path.join(tmp,`slide-${i+1}.png`),new Uint8Array(await b.arrayBuffer()));}
const candidatePath=path.join(tmp,'candidate.pptx');await (await PresentationFile.exportPptx(deck)).save(candidatePath);
const result=await finalizePresentation({workspaceDir:root,candidatePath,finalPath:path.join(root,'docs/Defensa_Proyecto.pptx'),pythonExecutable:path.join(runtime,'python/python.exe'),integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-heading-fit'],requiredNativeChartOwnerSlides:[4,5,8],requiredNativeTableOwnerSlides:[],materializeLiteralChartWorkbooks:true,fontPolicy:{basis:'design',families:[font]},verifyArtifactToolImport:true,receiptPath:path.join(tmp,'validation.json')});
console.log(JSON.stringify(result));

