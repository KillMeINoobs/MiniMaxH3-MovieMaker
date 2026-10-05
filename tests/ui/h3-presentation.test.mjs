import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import vm from 'node:vm';
import {test} from 'node:test';

async function harness() {
  const context=vm.createContext({console});
  const modules=new Map();
  async function load(url) {
    if(modules.has(url.href)) return modules.get(url.href);
    const module=new vm.SourceTextModule(await fs.readFile(url,'utf8'),{context,identifier:url.href});
    modules.set(url.href,module);
    await module.link((path,parent)=>load(new URL(path,parent.identifier)));
    return module;
  }
  const entry=await load(new URL('../../web/h3/presentation.mjs',import.meta.url));
  await entry.evaluate();
  return {h3:entry.namespace,shared:modules.get(new URL('../../web/common/presentation.js',import.meta.url).href).namespace};
}

function node(id,title='') {
  return {type:id,comfyClass:id,title,inputs:[{name:'control',type:'KVD_CONTROL',link:12}],
    outputs:[{name:'images',type:'IMAGE',links:[15]}],widgets:[
      {name:'prompt',value:'Authored action.\nРусский текст.',options:{}},
      {name:'structural_control',value:'off',options:{}},
      {name:'model_file',value:'minimax_h3_ref2va_pruned_int8_convrot.safetensors',options:{}}],
    setDirtyCanvas(){}};
}
function semantics(n) {
  return JSON.stringify({type:n.type,inputs:n.inputs.map(({name,type,link})=>({name,type,link})),
    outputs:n.outputs.map(({name,type,links})=>({name,type,links})),widgets:n.widgets.map(({name,value})=>({name,value}))});
}

test('EN default and all owned nodes have complete RU presentation without semantic edits',async()=>{
  const {h3,shared}=await harness();
  assert.equal(shared.getLanguage(),'en');
  assert.equal(h3.OWN_IDS.length,13);
  for(const id of h3.OWN_IDS) {
    const n=node(id);
    const before=semantics(n);
    shared.applyPresentation(n);
    const english=n.title;
    assert.ok(english.startsWith('KVD '));
    assert.ok(shared.presentationFor(n).help.length>20);
    shared.setLanguage('ru');
    shared.applyPresentation(n);
    assert.notEqual(n.title,english);
    assert.match(shared.presentationFor(n).help,/[А-Яа-я]/);
    assert.equal(semantics(n),before);
    shared.setLanguage('en'); shared.applyPresentation(n);
    assert.equal(n.title,english);
  }
});

test('custom titles, prompt contents, off values and foreign nodes remain intact',async()=>{
  const {shared}=await harness();
  const owned=node('KVD_CompileWindowPrompt','My Shot / Мой план');
  const foreign=node('Foreign_Sampler','Foreign Sampler');
  const original=JSON.stringify(foreign);
  const before=semantics(owned);
  for(const language of ['en','ru','en']) {
    shared.setLanguage(language); shared.applyPresentation(owned); shared.applyPresentation(foreign);
    assert.equal(owned.title,'My Shot / Мой план');
    assert.equal(semantics(owned),before);
    assert.equal(JSON.stringify(foreign),original);
  }
});

test('source/schema status and dependency failures never claim GPU or generated acceptance',async()=>{
  const {h3,shared}=await harness();
  const en=h3.reportText({code:'PROFILE_SOURCE_CHECKED'});
  assert.match(en,/source|metadata/i); assert.match(en,/unverified|not performed/i);
  assert.match(h3.reportText({code:'CONTROL_OFF'}),/off/i);
  assert.match(h3.reportText({code:'USEFUL_FINALIZED',useful_frames:180,width:24,height:16}),/180.*24.*16/);
  shared.setLanguage('ru');
  assert.match(h3.reportText({code:'DEPENDENCY_MISSING'}),/зависим|бэкенд/i);
  assert.match(h3.reportText({code:'MODEL_INCOMPATIBLE'}),/несовместим/i);
});

test('native helper fields and reports localize while their real semantic keys remain stable',async()=>{
  const {shared}=await harness();
  const n=node('KVD_ControlImage');
  n.inputs=[{name:'gate',type:'KVD_GATE',link:7}];
  n.widgets=['manifest','asset_root','working_set_bytes','project_id','plan_revision','ordinal','useful_start','graph_report']
    .map(name=>({name,value:name==='manifest'?'{}':'unchanged',options:{}}));
  const before=semantics(n);
  shared.applyPresentation(n);
  assert.equal(n.inputs[0].label,'Window gate');
  shared.setLanguage('ru');shared.applyPresentation(n);
  for(const field of [...n.inputs,...n.outputs,...n.widgets]) assert.match(field.label,/[А-Яа-я]/);
  assert.equal(semantics(n),before);
});
