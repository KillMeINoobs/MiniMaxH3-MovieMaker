import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import vm from 'node:vm';
import {test} from 'node:test';

async function harness() {
  let stored=null,cached='en';
  const writes=[],listeners={},extensions=[];
  function element(){return {children:[],listeners:{},style:{},textContent:'',
    append(...children){this.children.push(...children);},setAttribute(k,v){this[k]=v;},
    addEventListener(k,fn){this.listeners[k]=fn;}};}
  const node={id:1,type:'KVD_CompileWindowPrompt',comfyClass:'KVD_CompileWindowPrompt',title:'KVD Window Prompt',size:[375,200],
    inputs:[{name:'window',type:'KVD_WINDOW',link:9}],outputs:[{name:'compiled_prompt',type:'KVD_PROMPT',links:[11]}],
    widgets:[{name:'prompt',value:'Authored text / Авторский текст',options:{}}],
    addDOMWidget(){return {};},setDirtyCanvas(){},onExecuted(){return 'preserved callback';}};
  const custom={...structuredClone({...node,onExecuted:undefined,addDOMWidget:undefined,setDirtyCanvas:undefined}),id:2,
    title:'Personal / Личный',addDOMWidget(){return {};},setDirtyCanvas(){}};
  const foreign={id:3,type:'Foreign',title:'Foreign',widgets:[{name:'value',value:5}]};
  const nodes=[node,custom,foreign];
  const originalForeign=JSON.stringify(foreign);
  const semantics=()=>JSON.stringify(nodes.map(n=>({type:n.type,inputs:n.inputs?.map(({name,type,link})=>({name,type,link})),
    outputs:n.outputs?.map(({name,type,links})=>({name,type,links})),widgets:n.widgets.map(({name,value})=>({name,value}))})));
  const before=semantics();
  const app={graph:{_nodes:nodes,getNodeById:id=>nodes.find(n=>n.id===id)},registerExtension:e=>extensions.push(e),
    ui:{settings:{getSettingValue:k=>cached,async setSettingValueAsync(k,v){
      assert.equal(k,'KVD.Language');cached=v;writes.push(v);extensions.find(e=>e.name==='KVD.Foundation').settings[0].onChange(v);stored=v;}}}};
  const api={addEventListener(k,fn){(listeners[k]??=[]).push(fn);},async fetchApi(route){
    assert.equal(route,'/settings/KVD.Language');return {ok:true,json:async()=>stored};}};
  const context=vm.createContext({URL,console,document:{createElement:element,head:element()}});
  const appModule=new vm.SyntheticModule(['app'],function(){this.setExport('app',app);},{context});
  const apiModule=new vm.SyntheticModule(['api'],function(){this.setExport('api',api);},{context});
  const cache=new Map();
  async function load(url){
    if(cache.has(url.href))return cache.get(url.href);
    const module=new vm.SourceTextModule(await fs.readFile(url,'utf8'),{context,identifier:url.href,initializeImportMeta:m=>{m.url=url.href;}});
    cache.set(url.href,module);
    await module.link((specifier,parent)=>specifier.endsWith('/app.js')?appModule:specifier.endsWith('/api.js')?apiModule:load(new URL(specifier,parent.identifier)));
    return module;
  }
  for(const path of ['../../web/kvd.js','../../web/h3/h3.js']){const module=await load(new URL(path,import.meta.url));await module.evaluate();}
  for(const e of extensions)await e.setup();
  for(const n of nodes)for(const e of extensions)e.nodeCreated?.(n);
  return {node,custom,writes,persisted:()=>stored,async select(v){node._kvdPanel.selector.value=v;await node._kvdPanel.selector.listeners.change();},
    error(code){for(const fn of listeners.execution_error)fn({detail:{node_id:node.id,exception_message:code+': native operation unavailable'}});},
    assertStable(){assert.equal(semantics(),before);assert.equal(custom.title,'Personal / Личный');assert.equal(JSON.stringify(foreign),originalForeign);}};
}

test('owned H3 uses the actual shared persisted EN/RU selector and preserves graph data',async()=>{
  const h=await harness();
  assert.equal(h.node._kvdPanel.selector.value,'en');assert.deepEqual(h.writes,[]);
  await h.select('ru');
  assert.equal(h.persisted(),'ru');assert.equal(h.node.title,'KVD Промпт окна');
  assert.match(h.node._h3Panel.textContent,/не выполнена/);
  await h.select('en');assert.equal(h.persisted(),'en');assert.equal(h.node.title,'KVD Window Prompt');h.assertStable();
});

test('owned actual status/error hooks are scoped and preserve earlier callback returns',async()=>{
  const h=await harness();
  assert.equal(h.node.onExecuted({h3_report:[{code:'PROMPT_AUTHORED'}]}),'preserved callback');
  assert.match(h.node._h3Panel.textContent,/authored/i);
  await h.select('ru');h.error('DEPENDENCY_MISSING');
  assert.match(h.node._h3Panel.textContent,/бэкенд/);h.assertStable();
});
