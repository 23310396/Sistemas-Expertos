'use strict';

const $ = id => document.getElementById(id);
const SVG_NS = 'http://www.w3.org/2000/svg';
const LETRAS = 'pqrstuvwxyzabcdefghijklmno';
function letra(id) {
  const n=Number(String(id).slice(1))-1;
  return Number.isInteger(n)&&n>=0 ? LETRAS[n%26]+(n>=26?String(Math.floor(n/26)):'') : id;
}
function simbolizar(formula) {
  return String(formula).replace(/\bX[1-9]\d*\b/g, letra);
}

const ejemplo = 'Si Juan estudia, entonces aprueba. Juan estudia.';
const estado = { data:null, textoAnalizado:null, modo:'simbolica', vista:'arbol', cerradas:true, pasos:0, zoom:1, panX:0, panY:0, centroRaiz:null, seleccionado:null, dominio:null, revision:null, textoGuardado:'', guardando:null, analizando:false, conflicto:false, cargando:false };
let relojGuardado=null;

function crearSvg(etiqueta, atributos={}, texto=null) {
  const elemento = document.createElementNS(SVG_NS, etiqueta);
  for (const [clave, valor] of Object.entries(atributos)) elemento.setAttribute(clave, valor);
  if (texto !== null) elemento.textContent = texto;
  return elemento;
}
function crear(etiqueta, clase='', contenido='') {
  const e=document.createElement(etiqueta);
  if (clase) e.className=clase;
  e.textContent=contenido;
  return e;
}
function estadoEtiqueta(texto, clase) {
  const e=$('arbol-estado'); e.textContent=texto; e.className='state-inline '+(clase||'');
}
function cortarTexto(texto, ancho=43, maxLineas=7) {
  const palabras=String(texto).trim().split(/\s+/);
  const partes=[];
  for (const palabra of palabras) {
    if (palabra.length<=ancho) {partes.push(palabra);continue;}
    for(let i=0;i<palabra.length;i+=ancho) partes.push(palabra.slice(i,i+ancho));
  }
  const salida=[];
  let linea='';
  for(const palabra of partes){
    if(linea && (linea.length+1+palabra.length)>ancho){salida.push(linea);linea=palabra;}
    else linea=(linea?linea+' ':'')+palabra;
  }
  if(linea)salida.push(linea);
  if(salida.length>maxLineas){
    salida.length=maxLineas;
    salida[maxLineas-1]=salida[maxLineas-1].slice(0,ancho-1).trimEnd()+'…';
  }
  return salida.length?salida:[''];
}

function ponerTextoLista(id, items, tipo) {
  const cont=$(id); cont.replaceChildren();
  if(!items.length){cont.textContent='Sin elementos.';return;}
  for(const item of items){
    const fila=crear('div','data-item');
    const clave=crear('b','',tipo==='regla'?item.id:letra(item.id));
    const valor=crear('span','',item.texto);
    if(tipo==='regla') valor.append(crear('small','',simbolizar(item.expresion)));
    fila.append(clave,valor);cont.append(fila);
  }
}
function mostrarMundos(d) {
  const cont=$('mundos'); cont.replaceChildren();
  const mundos=d.arbol.mundos;
  if(!mundos.length) {
    cont.textContent='No hay mundos posibles: todas las ramas están cerradas.';
  }else{
    mundos.forEach((m,i)=>{
      const caja=crear('div','world-item');
      caja.append(crear('strong','','Mundo '+(i+1)));
      const tokens=crear('div','world-tokens');
      Object.entries(m).forEach(([atom,valor])=>tokens.append(crear('span',valor?'true':'false',letra(atom)+' = '+(valor?'V':'F'))));
      caja.append(tokens); cont.append(caja);
    });
  }
  $('mundos-alerta').hidden=!d.arbol.mundos_truncados;
}
function cambiarVista(vista) {
  if (!['arbol', 'fnc', 'sat', 'consultas'].includes(vista)) return;
  estado.vista = vista;
  for (const nombre of ['arbol', 'fnc', 'sat', 'consultas']) {
    const activo = nombre === vista;
    $('vista-' + nombre).hidden = !activo;
    $('tab-' + nombre).classList.toggle('selected', activo);
    $('tab-' + nombre).setAttribute('aria-selected', String(activo));
  }
  if (vista === 'arbol' && estado.data) dibujar();
}
function mostrarFnc(d) {
  const f = d.fnc;
  $('fnc-info').textContent = f.num_variables + ' variables · ' + f.clausulas.length + ' cláusulas';
  $('fnc-completa').textContent = simbolizar(f.expresion);
  $('fnc-clausulas').textContent = JSON.stringify(f.clausulas);
  $('fnc-dimacs').textContent = f.dimacs;
  const cont = $('fnc-reglas'); cont.replaceChildren();
  for (const regla of f.reglas) {
    const fila = crear('div', 'conversion-row');
    const cabecera = crear('div', 'conversion-head');
    cabecera.append(crear('strong', '', regla.id), crear('span', '', '→ FNC'));
    fila.append(cabecera);
    fila.append(crear('div', 'conversion-original', simbolizar(regla.original)));
    fila.append(crear('div', 'conversion-result', simbolizar(regla.fnc)));
    cont.append(fila);
  }
}
function mostrarSat(d) {
  const s = d.sat;
  for (const [id, valor] of [['sat-resultado', s.estado], ['sat-arbol', s.arbol], ['sat-coincide', s.coincide_arbol ? 'Sí' : 'NO']]) {
    const elemento = $(id);
    elemento.textContent = valor;
    elemento.classList.remove('sat-ok', 'sat-bad');
    if (id === 'sat-coincide') elemento.classList.add(s.coincide_arbol ? 'sat-ok' : 'sat-bad');
    else elemento.classList.add(valor === 'SAT' ? 'sat-ok' : 'sat-bad');
  }
  $('sat-motor').textContent = s.motor;
  const mensaje = $('sat-mensaje');
  mensaje.className = 'result-message ' + (s.compatible ? 'compatible' : 'incompatible');
  mensaje.textContent = s.compatible
    ? 'SAT · Existe al menos una asignación que satisface todas las reglas.'
    : 'UNSAT · No existe ninguna asignación que satisfaga todas las reglas.';
  const cont = $('sat-soluciones'); cont.replaceChildren();
  if (!s.soluciones.length) {
    cont.textContent = 'No hay soluciones: el conjunto es incompatible.';
  } else {
    s.soluciones.forEach((solucion, indice) => {
      const caja = crear('div', 'sat-model');
      caja.append(crear('strong', '', 'Mundo ' + (indice + 1)));
      const tokens = crear('div', 'world-tokens');
      for (const [atomo, valor] of Object.entries(solucion)) {
        const etiqueta = crear('span', valor ? 'true' : 'false', letra(atomo) + ' = ' + (valor ? 'V' : 'F'));
        etiqueta.title = d.atomos[atomo] || atomo;
        tokens.append(etiqueta);
      }
      caja.append(tokens);
      cont.append(caja);
    });
  }
  $('sat-cuenta').textContent = s.soluciones.length + (s.soluciones.length === 1 ? ' visible' : ' visibles');
  $('sat-truncado').hidden = !s.hay_mas;
  $('sat-explicacion').textContent = !s.coincide_arbol
    ? 'Advertencia: el árbol y el solver no coinciden. Revisa el análisis antes de usarlo.'
    : s.compatible
      ? 'Ambos métodos coinciden: el problema es satisfacible. Cada mundo mostrado es una combinación que cumple todas las reglas. Puede haber más soluciones si la lista está limitada.'
      : 'Ambos métodos coinciden: todas las ramas del árbol están cerradas y el solver determina UNSAT. No hay mundos que cumplan todas las reglas simultáneamente.';
}
function limpiarCalculos() {
  $('fnc-info').textContent = 'Sin analizar';
  $('fnc-completa').textContent = 'Analiza un problema para ver su FNC.';
  $('fnc-reglas').replaceChildren();
  $('fnc-clausulas').textContent = '—';
  $('fnc-dimacs').textContent = '—';
  $('sat-resultado').textContent = '—';
  $('sat-arbol').textContent = '—';
  $('sat-coincide').textContent = '—';
  $('sat-motor').textContent = 'Sin analizar';
  $('sat-mensaje').className = 'result-message';
  $('sat-mensaje').textContent = 'Analiza un problema para ver el resultado de SAT.';
  $('sat-soluciones').textContent = 'Todavía no hay soluciones.';
  $('sat-cuenta').textContent = '0 visibles';
  $('sat-truncado').hidden = true;
  $('sat-explicacion').textContent = 'El programa indicará si existe al menos un mundo posible que cumpla todas las reglas.';
}
function inspeccionar(nodo) {
  estado.seleccionado=nodo.id;
  $('detalle-vacio').hidden=true; $('detalle').hidden=false;
  $('detalle-id').textContent='Nodo N'+nodo.id;
  const status=$('detalle-estado'); status.className='inspect-status '+nodo.estado;
  status.textContent=nodo.estado==='normal' && nodo.aplicada ? '✓ Fórmula desarrollada' : (({'abierta':'✓ Rama abierta','cerrada':'✕ Contradicción','normal':'Pendiente / literal'})[nodo.estado]||'Desarrollo');
  $('detalle-formula').textContent=simbolizar(nodo.expresion);
  $('detalle-natural').textContent=nodo.natural;
  $('detalle-origen').textContent=nodo.origen;
  $('detalle-metodo').textContent=({'raiz':'Reglas iniciales','Y':'Conjunción','O':'Disyunción','NO':'Negación','IMPLICA':'Implicación','BICONDICIONAL':'Bicondicional'})[nodo.metodo]||nodo.metodo;
  const c=$('detalle-contradiccion'); c.hidden=!nodo.contradiccion;
  if(nodo.contradiccion){
    const d=nodo.contradiccion;
    c.textContent=`Contradicción en ${letra(d.atomo)}: la misma rama contiene la afirmación y la negación. Ocurre entre N${d.nodos[0]} y N${d.nodos[1]}.`;
  }
  document.querySelectorAll('.node-group').forEach(el=>el.classList.toggle('selected',Number(el.dataset.id)===nodo.id));
}
function construirNodosVisibles() {
  if(!estado.data) return [];
  const nodos=estado.data.arbol.nodos;
  const permitidos=new Set(nodos.map(n=>n.id));
  if(!estado.cerradas){
    const originales=new Map(nodos.map(n=>[n.id,n]));
    const abiertos=estado.data.arbol.hojas.filter(h=>h.estado==='abierta');
    const conservar=new Set([estado.data.arbol.raiz]);
    for(const hoja of abiertos){
      let id=hoja.nodo;
      while(id!==null && originales.has(id) && !conservar.has(id)){
        conservar.add(id); id=originales.get(id).padre;
      }
    }
    for(const id of permitidos) if(!conservar.has(id)) permitidos.delete(id);
  }
  return nodos.filter(n=>permitidos.has(n.id)&&n.id<=estado.pasos);
}
function dibujar() {
  if(!estado.data)return;
  const todos=construirNodosVisibles();
  const svg=$('tree-svg'); svg.replaceChildren();
  const placeholder=$('placeholder');
  if(!todos.length){svg.setAttribute('hidden',''); placeholder.hidden=false;return;}
  placeholder.hidden=true; svg.removeAttribute('hidden');
  const actual=new Map(todos.map(n=>[n.id,n]));
  const hijos=new Map(todos.map(n=>[n.id,[]]));
  for(const n of todos) if(hijos.has(n.padre)) hijos.get(n.padre).push(n.id);
  const natural=estado.modo==='natural';
  const medidas=new Map();
  const alturas=[];
  const separacionHorizontal=52;
  const separacionVertical=70;
  for(const n of todos){
    const etiqueta=natural?n.natural:simbolizar(n.expresion);
    const lineas=cortarTexto(etiqueta,natural?48:48,7);
    const ancho=Math.min(natural?480:440,Math.max(natural?310:250,
      Math.max(...lineas.map(x=>x.length))*7.3+36));
    const alto=Math.max(natural?108:92,lineas.length*20+57);
    medidas.set(n.id,{ancho,alto,lineas});
  }
  const amplitudes=new Map();
  function medirSubarbol(id, profundidad=0){
    const m=medidas.get(id);
    alturas[profundidad]=Math.max(alturas[profundidad]||0,m.alto);
    const ramas=hijos.get(id)||[];
    const hijosAncho=ramas.reduce((total,h)=>total+medirSubarbol(h,profundidad+1),0);
    const requerido=Math.max(m.ancho+separacionHorizontal,hijosAncho);
    amplitudes.set(id,requerido);
    return requerido;
  }
  const raiz=estado.data.arbol.raiz;
  if(!actual.has(raiz))return;
  const total=medirSubarbol(raiz);
  const niveles=[];
  let siguienteY=24;
  for(const alto of alturas){niveles.push(siguienteY+alto/2);siguienteY+=alto+separacionVertical;}
  const posiciones=new Map();
  function ubicar(id,prof,izquierda){
    const espacio=amplitudes.get(id);
    posiciones.set(id,{x:izquierda+espacio/2,y:niveles[prof]});
    const ramas=hijos.get(id)||[];
    const anchoRamas=ramas.reduce((total,h)=>total+amplitudes.get(h),0);
    let comienzo=izquierda+(espacio-anchoRamas)/2;
    for(const h of ramas){ubicar(h,prof+1,comienzo);comienzo+=amplitudes.get(h);}
  }
  const anchoVista=Math.max(total+100,$('viewport').clientWidth-20);
  ubicar(raiz,0,(anchoVista-total)/2);
  const altoVista=siguienteY+30;
  svg.setAttribute('viewBox',`0 0 ${anchoVista} ${altoVista}`);
  svg.setAttribute('width',Math.ceil(anchoVista));
  svg.setAttribute('height',Math.ceil(altoVista));
  const centro=posiciones.get(raiz);
  estado.centroRaiz={x:centro.x,y:centro.y-medidas.get(raiz).alto/2};

  for(const n of todos){
    if(!actual.has(n.padre))continue;
    const origen=posiciones.get(n.padre), destino=posiciones.get(n.id);
    const desde=origen.y+medidas.get(n.padre).alto/2, hasta=destino.y-medidas.get(n.id).alto/2;
    const medio=(desde+hasta)/2;
    svg.append(crearSvg('path',{class:'node-edge',d:`M ${origen.x} ${desde} C ${origen.x} ${medio} ${destino.x} ${medio} ${destino.x} ${hasta}`}));
  }
  for(const n of todos){
    const p=posiciones.get(n.id);
    const m=medidas.get(n.id);
    const grupo=crearSvg('g',{class:'node-group '+n.estado+(estado.seleccionado===n.id?' selected':''),tabindex:'0',role:'button','aria-label':`Nodo N${n.id}: ${simbolizar(n.expresion)}`});
    grupo.dataset.id=String(n.id);
    grupo.append(crearSvg('rect',{class:'node-card '+n.estado,x:p.x-m.ancho/2,y:p.y-m.alto/2,width:m.ancho,height:m.alto,rx:12}));
    grupo.append(crearSvg('circle',{class:'node-dot',cx:p.x-m.ancho/2+14,cy:p.y-m.alto/2+17,r:4}));
    grupo.append(crearSvg('text',{class:'node-small',x:p.x-m.ancho/2+25,y:p.y-m.alto/2+21},'N'+n.id+' · '+String(n.origen).slice(0,35)));
    const primerY=p.y-(m.lineas.length-1)*10+4;
    m.lineas.forEach((linea,i)=>grupo.append(crearSvg('text',{class:'node-label',x:p.x,y:primerY+i*20,'text-anchor':'middle'},linea)));
    const estadoTexto=n.estado==='cerrada'?'✕ CONTRADICCIÓN':n.estado==='abierta'?'✓ ABIERTA':n.aplicada?'✓ DESARROLLADA':n.metodo==='raiz'?'REGLAS':'LITERAL';
    grupo.append(crearSvg('text',{class:'node-small',x:p.x,'text-anchor':'middle',y:p.y+m.alto/2-11},estadoTexto));
    grupo.append(crearSvg('title',{},simbolizar(n.expresion)+'\n'+n.natural+(n.aplicada?'\n✓ Fórmula desarrollada':'')));
    grupo.addEventListener('click',()=>inspeccionar(n));
    grupo.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();inspeccionar(n);}});
    svg.append(grupo);
  }
  if(estado.seleccionado){const n=actual.get(estado.seleccionado);if(n)inspeccionar(n);}
  aplicarTransformacion();
}

function etiquetaDominio(mensaje, alerta=false) {
  $('estado-dominio').textContent=mensaje;
  $('estado-dominio').classList.toggle('warn', alerta);
}
async function apiDominio(url, metodo='GET', cuerpo=null) {
  const opciones={method:metodo};
  if(cuerpo!==null){opciones.headers={'Content-Type':'application/json'};opciones.body=JSON.stringify(cuerpo);}
  const r=await fetch(url,opciones);
  const d=await r.json();
  if(!r.ok||!d.ok){
    const e=new Error(d.error||'No se pudo completar la operación.');
    e.conflicto=!!d.conflicto;e.datos=d;throw e;
  }
  return d;
}
function linkCalculos(info) {
  const enlace=$('abrir-calculos');
  enlace.hidden=!info.tiene_calculos;
  if(info.tiene_calculos) enlace.href='/api/dominio/calculos?nombre='+encodeURIComponent(info.nombre);
}
function asignarTexto(texto) {
  $('editor').value=texto;
  $('contador').textContent=texto.length+' caracteres';
  estado.data=null;estado.textoAnalizado=null;estado.seleccionado=null;
  limpiarResultados();estadoEtiqueta('Sin generar','');
  $('errores').hidden=true;$('tree-svg').replaceChildren();$('tree-svg').setAttribute('hidden','');
  $('placeholder').hidden=false;$('detalle').hidden=true;$('detalle-vacio').hidden=false;
}
async function opcionesDominios() {
  const r=await apiDominio('/api/dominios');
  const selector=$('dominio'), anterior=estado.dominio;
  selector.replaceChildren();
  for(const d of r.dominios){const op=document.createElement('option');op.value=d.nombre;op.textContent=d.nombre;selector.append(op);}
  if(anterior&&r.dominios.some(d=>d.nombre===anterior)) selector.value=anterior;
  return r.dominios;
}
async function cargarDominio(nombre, forzar=false) {
  if(!nombre)return;
  if(forzar && $('editor').value!==estado.textoGuardado && !confirm('Tienes cambios locales. ¿Quieres descartarlos y recuperar el TXT?'))return;
  estado.cargando=true;
  try {
    const {dominio:d}=await apiDominio('/api/dominio?nombre='+encodeURIComponent(nombre));
    estado.dominio=d.nombre;estado.revision=d.revision;estado.textoGuardado=d.texto;
    estado.conflicto=false;$('dominio').value=d.nombre;
    asignarTexto(d.texto);linkCalculos(d);
    etiquetaDominio('TXT cargado · '+(d.calculado?'Cálculos vigentes':d.tiene_calculos?'Cálculos pendientes de actualizar':'Sin cálculos guardados'));
    if(d.texto.trim()) await analizar();
  } catch(e) {etiquetaDominio(e.message,true);} finally {estado.cargando=false;}
}
async function guardarEdicion() {
  if(!estado.dominio||estado.conflicto||estado.cargando)return;
  if(estado.guardando) {await estado.guardando;}
  const texto=$('editor').value;
  if(texto===estado.textoGuardado)return;
  const nombre=estado.dominio;
  const version=estado.revision;
  const proceso=apiDominio('/api/dominio/guardar','POST',{nombre,texto,revision:version});
  estado.guardando=proceso;
  try {
    const {dominio:d}=await proceso;
    if(estado.dominio!==nombre)return;
    estado.revision=d.revision;estado.textoGuardado=texto;
    linkCalculos(d);
    etiquetaDominio('TXT guardado · '+(d.calculado?'Cálculos vigentes':'Presiona Analizar para actualizar cálculos'));
  } catch(e) {
    if(e.conflicto)estado.conflicto=true;
    etiquetaDominio(e.message,true);
    throw e;
  } finally {if(estado.guardando===proceso) estado.guardando=null;}
}
async function completarGuardado() {
  clearTimeout(relojGuardado);relojGuardado=null;
  if(estado.guardando)await estado.guardando;
  await guardarEdicion();
  if(estado.conflicto)throw new Error('Primero debes recargar el TXT externo.');
}
async function iniciarDominios() {
  try {
    let todos=await opcionesDominios();
    if(!todos.length){await apiDominio('/api/dominios','POST',{nombre:'entrada'});todos=await opcionesDominios();}
    const inicial=todos.some(d=>d.nombre==='entrada')?'entrada':todos[0].nombre;
    await cargarDominio(inicial);
  } catch(e){etiquetaDominio('Error al cargar los dominios: '+e.message,true);}
}
async function verificarCambiosExternos() {
  if(!estado.dominio||estado.cargando||estado.analizando||estado.guardando||estado.conflicto)return;
  try {
    await opcionesDominios();
    const {dominio:d}=await apiDominio('/api/dominio?nombre='+encodeURIComponent(estado.dominio));
    if(d.nombre!==estado.dominio||d.revision===estado.revision)return;
    if($('editor').value!==estado.textoGuardado){
      estado.conflicto=true;
      etiquetaDominio('El TXT cambió fuera y hay cambios locales. Pulsa ↻ para resolver el conflicto.',true);
    }else{
      etiquetaDominio('Se detectó una edición externa; recargando TXT…');
      await cargarDominio(d.nombre);
    }
  }catch(e){etiquetaDominio('No se pudo verificar el TXT: '+e.message,true);}
}

async function analizar() {
  const texto=$('editor').value.trim();
  if(!texto){
    estado.data=null;estado.textoAnalizado=null;estado.seleccionado=null;
    limpiarResultados();estadoEtiqueta('Sin generar','');
    $('tree-svg').replaceChildren();$('tree-svg').setAttribute('hidden','');
    $('placeholder').hidden=false;$('detalle').hidden=true;$('detalle-vacio').hidden=false;
    mostrarError('Introduce un problema antes de generar el árbol.');
    return;
  }
  $('analizar').disabled=true; estado.analizando=true; $('estado-analisis').textContent='Analizando…'; $('errores').hidden=true;
  try{
    await completarGuardado();
    const respuesta=await fetch('/api/dominio/analizar',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({nombre:estado.dominio,texto,revision:estado.revision})});
    const datos=await respuesta.json();
    if(datos.dominio){estado.revision=datos.dominio.revision;estado.textoGuardado=datos.dominio.texto;linkCalculos(datos.dominio);}
    if(respuesta.status===409){estado.conflicto=true;throw new Error(datos.error||'El TXT cambió fuera del programa.');}
    if(!respuesta.ok||!datos.ok){
      estado.data=null;estado.textoAnalizado=null;mostrarError(datos.error||'No se pudo analizar el problema.',datos.errores||[]);
      $('estado-analisis').textContent='Revisar entrada';estadoEtiqueta('No generado','bad');
      $('placeholder').hidden=false; $('tree-svg').setAttribute('hidden',''); $('tree-svg').replaceChildren();
      $('detalle').hidden=true; $('detalle-vacio').hidden=false;
      limpiarResultados();
      return;
    }
    estado.data=datos;estado.textoAnalizado=texto;estado.pasos=datos.arbol.nodos.length;estado.seleccionado=null;
    etiquetaDominio('TXT y cálculos actualizados · '+datos.dominio.archivo_calculos);
    limpiarConsulta();
    $('estado-analisis').textContent='Correcto';estadoEtiqueta(datos.arbol.compatible?'SAT · Compatible':'UNSAT · Contradicción',datos.arbol.compatible?'ok':'bad');
    $('total-atomos').textContent=Object.keys(datos.atomos).length;
    $('total-reglas').textContent=datos.reglas.length;
    $('count-atomos').textContent=Object.keys(datos.atomos).length;
    $('count-reglas').textContent=datos.reglas.length;
    ponerTextoLista('lista-atomos',Object.entries(datos.atomos).map(([id,texto])=>({id,texto})),'atomo');
    ponerTextoLista('lista-reglas',datos.reglas,'regla');
    $('ramas-abiertas').innerHTML=`<i class="dot green"></i> ${datos.resumen.abiertas} abiertas`;
    $('ramas-cerradas').innerHTML=`<i class="dot red"></i> ${datos.resumen.cerradas} cerradas`;
    const pasos=$('pasos'); pasos.disabled=false;pasos.max=estado.pasos;pasos.value=estado.pasos;
    $('pasos-etiqueta').textContent=`${estado.pasos} de ${estado.pasos} nodos`;
    $('detalle').hidden=true; $('detalle-vacio').hidden=false;
    estado.zoom=1;
    mostrarMundos(datos);mostrarFnc(datos);mostrarSat(datos);dibujar();centrarRaiz();
  }catch(error){mostrarError('Error de conexión con Python: '+error.message);$('estado-analisis').textContent='Error';estado.data=null;estado.textoAnalizado=null;limpiarResultados();$('tree-svg').setAttribute('hidden','');$('placeholder').hidden=false;}
  finally{$('analizar').disabled=false;estado.analizando=false;}
}
function limpiarResultados(){
  $('total-atomos').textContent='—'; $('total-reglas').textContent='—';
  $('count-atomos').textContent='0'; $('count-reglas').textContent='0';
  $('lista-atomos').textContent='Esperando un problema válido.';
  $('lista-reglas').textContent='Esperando un problema válido.';
  $('ramas-abiertas').textContent='— abiertas'; $('ramas-cerradas').textContent='— cerradas';
  $('mundos').textContent='Sin resultados válidos.'; $('mundos-alerta').hidden=true;
  $('pasos').disabled=true; $('pasos-etiqueta').textContent='Sin nodos';
  limpiarCalculos();
  limpiarConsulta();
}
function mostrarError(mensaje,oraciones=[]){
  const caja=$('errores');caja.hidden=false;
  caja.textContent=mensaje+(oraciones.length?'\n'+oraciones.map(e=>`\n${e.numero}. ${e.texto}\n   ${e.motivo}`).join('\n'):'');
}
function actualizarPasos(v){estado.pasos=Number(v);$('pasos-etiqueta').textContent=`${v} de ${estado.data.arbol.nodos.length} nodos`;dibujar();}
function aplicarTransformacion(){
  $('tree-svg').style.transform=`translate(${estado.panX}px, ${estado.panY}px) scale(${estado.zoom})`;
  $('zoom-text').textContent=Math.round(estado.zoom*100)+'%';
}
function cambiarZoom(valor, x=$('viewport').clientWidth/2, y=$('viewport').clientHeight/2){
  const nuevo=Math.max(.2,Math.min(3,valor));
  const relacion=nuevo/estado.zoom;
  estado.panX=x-(x-estado.panX)*relacion;
  estado.panY=y-(y-estado.panY)*relacion;
  estado.zoom=nuevo;
  aplicarTransformacion();
}
function centrarRaiz(){
  if(!estado.centroRaiz)return;
  const vista=$('viewport');
  estado.panX=vista.clientWidth/2-estado.centroRaiz.x*estado.zoom;
  estado.panY=28-estado.centroRaiz.y*estado.zoom;
  aplicarTransformacion();
}
function ajustarArbol(){
  const svg=$('tree-svg');
  if(svg.hasAttribute('hidden') || !estado.data)return;
  const vista=$('viewport');
  const ancho=Number(svg.getAttribute('width'));
  const alto=Number(svg.getAttribute('height'));
  const factor=Math.min((vista.clientWidth-40)/ancho,(vista.clientHeight-40)/alto);
  estado.zoom=Math.max(.2,Math.min(1.35,factor));
  estado.panX=(vista.clientWidth-ancho*estado.zoom)/2;
  estado.panY=(vista.clientHeight-alto*estado.zoom)/2;
  aplicarTransformacion();
}
function habilitarNavegacionArbol(){
  const vista=$('viewport');
  let arrastre=null;
  let ultimoArrastre=0;
  vista.addEventListener('pointerdown',e=>{
    if(e.button!==0 || !estado.data || $('tree-svg').hasAttribute('hidden'))return;
    arrastre={id:e.pointerId,x:e.clientX,y:e.clientY,panX:estado.panX,panY:estado.panY,movido:false};
    vista.classList.add('drag-ready');
  });
  window.addEventListener('pointermove',e=>{
    if(!arrastre || e.pointerId!==arrastre.id)return;
    const dx=e.clientX-arrastre.x, dy=e.clientY-arrastre.y;
    if(!arrastre.movido && Math.hypot(dx,dy)<5)return;
    arrastre.movido=true;
    vista.classList.add('dragging');
    estado.panX=arrastre.panX+dx;
    estado.panY=arrastre.panY+dy;
    aplicarTransformacion();
    e.preventDefault();
  });
  function terminar(e){
    if(!arrastre || e.pointerId!==arrastre.id)return;
    if(arrastre.movido)ultimoArrastre=performance.now();
    arrastre=null;
    vista.classList.remove('drag-ready','dragging');
  }
  window.addEventListener('pointerup',terminar);
  window.addEventListener('pointercancel',terminar);
  vista.addEventListener('click',e=>{
    if(performance.now()-ultimoArrastre < 300){e.preventDefault();e.stopPropagation();}
  },true);
  vista.addEventListener('wheel',e=>{
    if(!estado.data || $('tree-svg').hasAttribute('hidden'))return;
    e.preventDefault();
    const r=vista.getBoundingClientRect();
    const factor=Math.exp(-e.deltaY*.0015);
    cambiarZoom(estado.zoom*factor,e.clientX-r.left,e.clientY-r.top);
  },{passive:false});
}


function limpiarConsulta() {
  $('consulta-error').hidden = true;
  $('consulta-resultado').replaceChildren(crear('p','muted','Analiza un problema y después escribe una consulta.'));
}
function pintarMundo(titulo, solucion) {
  const caja = crear('div', 'query-world');
  caja.append(crear('strong', '', titulo));
  const linea = crear('div', 'world-tokens');
  for (const [atomo, valor] of Object.entries(solucion)) {
    const tag = crear('span', valor ? 'true' : 'false', letra(atomo) + '=' + (valor ? 'V' : 'F'));
    linea.append(tag);
  }
  caja.append(linea);
  return caja;
}
function mostrarConsulta(respuesta) {
  const cont = $('consulta-resultado');
  cont.replaceChildren();
  const c = respuesta.consulta;
  const cabecera = crear('div','query-head');
  const clase = c.estado === 'DEMOSTRADA' ? 'query-yes' : c.estado === 'REFUTADA' || c.estado === 'INCONSISTENTE' ? 'query-no' : 'query-maybe';
  cabecera.append(crear('span', 'query-status ' + clase, c.estado));
  cabecera.append(crear('span', 'muted tiny', c.motor));
  const razon=crear('section','query-reason');
  razon.append(crear('strong','','¿Por qué se obtuvo este resultado?'), crear('p','explanation',c.explicacion));
  cont.append(cabecera, crear('p','query-formula','Consulta: ' + simbolizar(c.expresion)), razon);
  const nuevas = Object.entries(c.nuevos_atomos);
  if (nuevas.length) cont.append(crear('p','hint','Proposiciones no presentes en las reglas: ' + nuevas.map(([id, texto])=>letra(id)+' = '+texto).join('; ')));
  if (c.ejemplo_verdadero) cont.append(pintarMundo('Ejemplo donde la consulta es verdadera',c.ejemplo_verdadero));
  if (c.contraejemplo) cont.append(pintarMundo('Mundo donde la consulta es falsa (contraejemplo)',c.contraejemplo));
}
async function consultarPregunta() {
  const pregunta = $('pregunta').value.trim();
  const error = $('consulta-error'); error.hidden = true;
  if (!estado.data || $('editor').value.trim() !== estado.textoAnalizado) {
    error.textContent = 'Analiza las reglas actuales antes de hacer una consulta.';
    error.hidden = false;
    return;
  }
  if (!pregunta) { error.textContent = 'Escribe una consulta.'; error.hidden = false; return; }
  const boton = $('enviar-consulta'); boton.disabled = true;
  try {
    const peticion = await fetch('/api/consultar', {
      method:'POST', headers:{'Content-Type':'application/json'},
      body:JSON.stringify({texto:estado.textoAnalizado,pregunta})
    });
    const respuesta = await peticion.json();
    if (!peticion.ok || !respuesta.ok) throw new Error(respuesta.error || 'No se pudo evaluar la consulta.');
    mostrarConsulta(respuesta);
  } catch (e) {
    error.textContent = e.message;
    error.hidden = false;
    $('consulta-resultado').replaceChildren();
  } finally { boton.disabled = false; }
}
async function agregarRegla() {
  const adicional = $('nueva-regla').value.trim();
  if (!adicional) { $('consulta-error').textContent = 'Escribe primero una regla nueva.'; $('consulta-error').hidden = false; return; }
  const texto = $('editor').value.trim();
  const separador = texto && !/[.!?;]$/.test(texto) ? '.\n' : '\n';
  $('editor').value = texto ? texto + separador + adicional : adicional;
  $('editor').dispatchEvent(new Event('input', {bubbles:true}));
  $('nueva-regla').value = '';
  await analizar();
}

for (const vista of ['arbol', 'fnc', 'sat', 'consultas']) {
  $('tab-' + vista).addEventListener('click', () => cambiarVista(vista));
}
$('enviar-consulta').addEventListener('click', consultarPregunta);
$('pregunta').addEventListener('keydown', e => { if (e.key === 'Enter') { e.preventDefault(); consultarPregunta(); } });
$('agregar-regla').addEventListener('click', agregarRegla);
$('copiar-dimacs').addEventListener('click', async () => {
  if (!estado.data) return;
  const boton = $('copiar-dimacs');
  try {
    await navigator.clipboard.writeText(estado.data.fnc.dimacs);
    boton.textContent = 'Copiado';
  } catch (e) {
    boton.textContent = 'No se pudo copiar';
  }
  setTimeout(() => { boton.textContent = 'Copiar DIMACS'; }, 1700);
});
$('editor').addEventListener('input',e=>{
  $('contador').textContent=e.target.value.length+' caracteres';
  $('estado-analisis').textContent='Cambios sin analizar';limpiarConsulta();
  clearTimeout(relojGuardado);
  relojGuardado=setTimeout(()=>guardarEdicion().catch(()=>{}),900);
});
$('dominio').addEventListener('change',async e=>{
  const anterior=estado.dominio;
  try{await completarGuardado();await cargarDominio(e.target.value);}
  catch(error){e.target.value=anterior;etiquetaDominio(error.message,true);}
});
$('nuevo-dominio').addEventListener('click',async()=>{
  const nombre=prompt('Nombre del nuevo dominio (letras, números, guion o guion bajo):');
  if(!nombre)return;
  try{
    await completarGuardado();
    await apiDominio('/api/dominios','POST',{nombre:nombre.trim()});
    await opcionesDominios();await cargarDominio(nombre.trim());
  }catch(e){etiquetaDominio(e.message,true);}
});
$('recargar-dominio').addEventListener('click',()=>cargarDominio(estado.dominio,true));
setInterval(verificarCambiosExternos,4000);
window.addEventListener('focus',verificarCambiosExternos);

$('analizar').addEventListener('click',analizar);
$('editor').addEventListener('keydown',e=>{if((e.ctrlKey||e.metaKey)&&e.key==='Enter'){e.preventDefault();analizar();}});
for(const modo of ['simbolica','natural'])$(''+modo).addEventListener('click',()=>{estado.modo=modo;for(const m of ['simbolica','natural']){$(m).classList.toggle('selected',m===modo);$(m).setAttribute('aria-pressed',String(m===modo));}dibujar();centrarRaiz();});
$('mostrar-cerradas').addEventListener('change',e=>{estado.cerradas=e.target.checked;dibujar();});
$('pasos').addEventListener('input',e=>{if(estado.data)actualizarPasos(e.target.value);});
$('mostrar-todo').addEventListener('click',()=>{if(estado.data){$('pasos').value=estado.data.arbol.nodos.length;actualizarPasos($('pasos').value);}});
$('zoom-in').addEventListener('click',()=>cambiarZoom(estado.zoom+.15));
$('zoom-out').addEventListener('click',()=>cambiarZoom(estado.zoom-.15));
$('zoom-reset').addEventListener('click',ajustarArbol);
habilitarNavegacionArbol();
iniciarDominios();
