import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';
import vm from 'node:vm';
import { pathToFileURL } from 'node:url';

const source = await readFile('web/kvd.js','utf8');
const fixture = JSON.parse(await readFile('workflows/foundation_project.json','utf8'));

async function harness({storedLanguage='en',writeOutcomes=[],readStatus=200,deferWrites=false}={}) {
  let extension, cached = storedLanguage ?? 'en', persisted = storedLanguage;
  const writes = [], reads = [], waiters = [], messages = [];
  function element() {
    return {children:[],listeners:{},style:{},textContent:'',
      append(...children) { this.children.push(...children); },
      setAttribute(key,value) { this[key]=value; },
      addEventListener(key,callback) { this.listeners[key]=callback; }};
  }
  const nodes = fixture.nodes.map(data=>({
    ...structuredClone(data),comfyClass:data.type,
    widgets:(data.widgets_values || []).map((value,index)=>({
      name:data.type === 'KVD_ProjectJSON' ? 'project_json' : ['project_root','project_file','overwrite'][index],value,options:{}})),
    addDOMWidget(){return {};},setDirtyCanvas(){},
  }));
  nodes[1].title = 'Personal title / Моя сцена';
  const foreign = {type:'OtherPack',title:'Unchanged',widgets:[{name:'x',value:9}]};
  nodes.push(foreign);
  const originalForeign = JSON.stringify(foreign);
  const semantics = () => JSON.stringify({links:fixture.links,nodes:nodes.map(n=>({
    type:n.type,inputs:n.inputs?.map(({name,type,link})=>({name,type,link})),
    outputs:n.outputs?.map(({name,type,links})=>({name,type,links})),
    values:n.widgets.map(({name,value})=>({name,value})),
  }))});
  const before = semantics();
  function store(key,value) {
    assert.equal(key,'KVD.Language');
    if (value === cached) return Promise.resolve();
    cached = value;
    extension.settings[0].onChange(value); // Pinned native store applies onChange before saving.
    const outcome = writeOutcomes[writes.length] || 'saved';
    return new Promise((resolve,reject)=>{
      const write = {value,resolve(){persisted=value;resolve();},reject};
      writes.push(write);
      for (const wake of waiters.splice(0)) wake();
      if (!deferWrites) {
        if (outcome === 'rejected') reject(new Error('Preference write rejected'));
        else if (outcome === 'http_error') resolve();
        else write.resolve();
      }
    });
  }
  const app = {
    graph:{_nodes:nodes,getNodeById:id=>nodes.find(n=>n.id===id)},
    registerExtension(value){extension=value;},
    ui:{settings:{getSettingValue(key){assert.equal(key,'KVD.Language');return cached;},
      setSettingValue(key,value){store(key,value).catch(error=>messages.push(error.message));},
      async setSettingValueAsync(key,value){await store(key,value);}}},
  };
  const api = {
    addEventListener(key){assert.equal(key,'execution_error');},
    async fetchApi(route,options){
      assert.equal(route,'/settings/KVD.Language');
      assert.ok(!options?.method || options.method === 'GET');
      reads.push(persisted);
      const status = typeof readStatus === 'function' ? readStatus(reads.length) : readStatus;
      return {ok:status===200,status,json:async()=>persisted};
    },
  };
  const context = vm.createContext({URL,document:{createElement:element,head:element()},
    console:{error:(...args)=>messages.push(args)}});
  const appModule = new vm.SyntheticModule(['app'],function(){this.setExport('app',app);},{context});
  const apiModule = new vm.SyntheticModule(['api'],function(){this.setExport('api',api);},{context});
  const presentation = new vm.SourceTextModule(await readFile('web/common/presentation.js','utf8'),{context});
  const main = new vm.SourceTextModule(source,{context,
    initializeImportMeta:meta=>{meta.url=pathToFileURL(process.cwd()+'/web/kvd.js').href;}});
  await main.link(async specifier=>{
    if (specifier.endsWith('/app.js')) return appModule;
    if (specifier.endsWith('/api.js')) return apiModule;
    if (specifier.endsWith('/presentation.js')) return presentation;
    assert.equal(specifier,'./common/language-settings.js');
    return new vm.SourceTextModule(await readFile('web/common/language-settings.js','utf8'),{context});
  });
  await main.evaluate();
  await extension.setup();
  for (const node of nodes) extension.nodeCreated(node);
  return {nodes,writes,reads,messages,language:()=>presentation.namespace.getLanguage(),persisted:()=>persisted,
    async select(value){const selector=nodes[0]._kvdPanel.selector;selector.value=value;return selector.listeners.change();},
    async whenWrite(count){while(writes.length<count)await new Promise(resolve=>waiters.push(resolve));return writes[count-1];},
    assertSemantics(){assert.equal(semantics(),before);assert.equal(nodes[1].title,'Personal title / Моя сцена');assert.equal(JSON.stringify(foreign),originalForeign);},
  };
}

test('actual selector starts EN without modifying any preference',async()=>{
  const host = await harness({storedLanguage:null});
  assert.equal(host.language(),'en');
  assert.equal(host.nodes[0]._kvdPanel.selector.value,'en');
  assert.equal(host.nodes[0]._kvdPanel.heading.textContent,'Portable project');
  assert.equal(host.writes.length,0);
  host.assertSemantics();
});

test('actual selector awaits verified RU and EN with unchanged data and foreign nodes',async()=>{
  const host = await harness({storedLanguage:null});
  await host.select('ru');
  assert.equal(host.language(),'ru');
  assert.equal(host.persisted(),'ru');
  assert.ok(host.reads.includes('ru'),'must verify the server value');
  assert.equal(host.nodes[0]._kvdPanel.heading.textContent,'Переносимый проект');
  await host.select('en');
  assert.equal(host.persisted(),'en');
  assert.equal(host.nodes[0]._kvdPanel.selector.value,'en');
  host.assertSemantics();
});

test('actual selector exposes localized save errors for rejection and fulfilled HTTP failure',async()=>{
  for (const outcome of ['rejected','http_error']) {
    const host = await harness({storedLanguage:'ru',writeOutcomes:[outcome]});
    await host.select('en');
    assert.equal(host.nodes[0]._kvdLanguageStatus,'SETTINGS_ERROR');
    assert.equal(host.language(),'ru');
    assert.equal(host.persisted(),'ru');
    assert.match(host.nodes[0]._kvdPanel.status.textContent,/Не удалось сохранить/);
    assert.equal(host.nodes[0]._kvdLanguageEvidence.restored,true);
    host.assertSemantics();
  }
});

test('unavailable persistence readback leaves preference untouched and reports uncertainty',async()=>{
  const host = await harness({readStatus:503});
  await host.select('ru');
  assert.equal(host.nodes[0]._kvdLanguageStatus,'SETTINGS_ERROR');
  assert.equal(host.writes.length,0);
  assert.equal(host.nodes[0]._kvdLanguageEvidence.persisted,undefined);
  assert.match(host.nodes[0]._kvdPanel.status.textContent,/Unverified/);
});

test('failed recovery distinguishes displayed EN from verified stored RU',async()=>{
  const host = await harness({writeOutcomes:['saved','rejected'],readStatus:count=>count===2 ? 503 : 200});
  await host.select('ru');
  assert.equal(host.nodes[0]._kvdLanguageStatus,'SETTINGS_ERROR');
  assert.equal(host.language(),'en');
  assert.equal(host.persisted(),'ru');
  assert.equal(host.nodes[0]._kvdLanguageEvidence.restored,false);
  assert.equal(host.nodes[0]._kvdLanguageEvidence.persisted,'ru');
  assert.match(host.nodes[0]._kvdPanel.status.textContent,/English.*Русский/);
});

test('a pending ordinary save is not shown as saved and completes only after confirmation',async()=>{
  const host = await harness({deferWrites:true});
  const running = host.select('ru');
  const write = await host.whenWrite(1);
  await new Promise(resolve=>setImmediate(resolve));
  assert.equal(host.nodes[0]._kvdLanguageStatus,'SETTINGS_SAVING');
  assert.equal(host.nodes[0]._kvdPanel.selector.disabled,true);
  assert.match(host.nodes[0]._kvdPanel.status.textContent,/Сейчас: Русский/,'pending state must show the actual displayed locale');
  assert.equal(host.persisted(),'en');
  write.resolve();
  await running;
  assert.equal(host.nodes[0]._kvdLanguageStatus,undefined);
  assert.equal(host.nodes[0]._kvdPanel.selector.disabled,false);
  assert.equal(host.persisted(),'ru');
  host.assertSemantics();
});
