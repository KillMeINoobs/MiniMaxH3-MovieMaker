import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';
import vm from 'node:vm';
import { pathToFileURL } from 'node:url';

const fixture = JSON.parse(await readFile('workflows/foundation_project.json', 'utf8'));
const checkerSource = await readFile('web/zz_verification.js', 'utf8');
const presentationSource = await readFile('web/common/presentation.js', 'utf8');

async function harness({query='?kvd-check=foundation&phase=display', outcomes=[], changeInitialGraph, changeLoadedGraph, readyAtSetup=false, unavailableCanvas=false, settingLanguage='en', savedWorkflow}={}) {
  const scheduled = [], loads = [], messages = [], elements = [], stored = new Map();
  let extension, current, graphReady = readyAtSetup, language = settingLanguage;
  if (savedWorkflow) stored.set('KVD.FoundationVerification.saved',JSON.stringify(savedWorkflow));
  const app = {
    registerExtension(value) { extension = value; },
    ui: { settings: {
      getSettingValue() { return language; },
      async setSettingValue(key, value) {
        assert.equal(key, 'KVD.Language'); language = value;
      },
    } },
    canvas: unavailableCanvas ? null : {ds:{}, setDirty() {}},
    async loadGraphData(data, ...options) {
      loads.push({data:structuredClone(data), options});
      current = structuredClone(data);
      if (loads.length === 1) changeInitialGraph?.(current);
      changeLoadedGraph?.(current, loads.length);
      await extension.afterLoadGraph?.();
      const outcome = (loads.length - 1) in outcomes ? outcomes[loads.length - 1] : true;
      return graphReady ? outcome : false;
    },
  };
  Object.defineProperty(app,'isGraphReady',{get:()=>graphReady});
  Object.defineProperty(app, 'graph', {get() {
    assert.ok(graphReady, 'checker accessed the graph before initialization');
    const nodes = current.nodes.map(data => {
      const node = {...data, _kvdPanel:{}, widgets:[{name:'project_json', value:data.widgets_values?.[0]}]};
      Object.defineProperty(node,'title',{get:()=>data.title,set:value=>{data.title=value;}});
      return node;
    });
    return {_nodes:nodes, links:current.links, serialize:()=>structuredClone(current),
      getNodeById:id=>nodes.find(node=>node.id === id)};
  }});
  const context = vm.createContext({
    URL, URLSearchParams, structuredClone,
    location:{search:query},
    document:{
      createElement() { const element = {style:{}, setAttribute(){}, textContent:''}; elements.push(element); return element; },
      body:{append(){}},
    },
    sessionStorage:{getItem:key=>stored.get(key) ?? null, setItem:(key,value)=>stored.set(key,value)},
    setTimeout:callback=>scheduled.push(callback),
    console:{info:(...values)=>messages.push({level:'info',values}), error:(...values)=>messages.push({level:'error',values})},
  });
  const appModule = new vm.SyntheticModule(['app'], function() { this.setExport('app',app); }, {context});
  const presentation = new vm.SourceTextModule(presentationSource,{context});
  const checker = new vm.SourceTextModule(checkerSource,{context,
    initializeImportMeta:meta=>{meta.url=pathToFileURL(process.cwd() + '/web/zz_verification.js').href;},
  });
  // Imports remain actual production modules; only the native host is synthetic.
  await checker.link(specifier=>specifier.endsWith('/app.js') ? appModule : presentation);
  context.fetch = async(url, options)=>{
    assert.ok(String(url).endsWith('/examples/foundation_project.json'));
    assert.ok(!options?.method || options.method === 'GET','checker must not submit a request');
    return {ok:true,json:async()=>structuredClone(fixture)};
  };
  await checker.evaluate();
  presentation.namespace.setLanguage(language);
  await extension.setup();
  return {extension, loads, scheduled, messages, elements,
    setGraphReady() { graphReady = true; },
    async flush() { while (scheduled.length) await scheduled.shift()(); },
    receipt() { const entry = messages.findLast(message=>message.values[0] === '[KVD verification]'); return entry && JSON.parse(entry.values[1]); },
    language:()=>language,
    saved:()=>stored.get('KVD.FoundationVerification.saved'),
  };
}

test('ordinary pages never load a graph or alter a preference', async()=>{
  const host = await harness({query:''});
  await host.extension.afterLoadGraph?.();
  await host.flush();
  assert.equal(host.loads.length,0);
  assert.equal(host.elements.length,0);
  assert.equal(host.language(),'en');
});

test('opt-in setup waits for native initial graph loading and starts once', async()=>{
  const host = await harness();
  assert.equal(host.loads.length,0);
  assert.equal(host.scheduled.length,0);
  assert.equal(typeof host.extension.afterLoadGraph,'function');
  host.setGraphReady();
  await host.extension.afterLoadGraph();
  await host.extension.afterLoadGraph();
  assert.equal(host.loads.length,0,'a lifecycle hook must not recursively await a graph load');
  assert.equal(host.scheduled.length,1);
  await host.flush();
  assert.equal(host.loads.length,1,'fixture loads must not recursively schedule checks');
  assert.equal(host.receipt().status,'PASS');
  assert.equal(host.loads[0].options[3].skipAssetScans,true);
  assert.doesNotMatch(host.elements[0].textContent,/EN\/RU/,'display must not imply a language roundtrip');
});

test('a caught native configure failure returning false cannot produce PASS', async()=>{
  for (const outcome of [false,undefined,null,1]) {
    const host = await harness({outcomes:[outcome],readyAtSetup:true});
    host.setGraphReady();
    await host.extension.afterLoadGraph?.();
    await host.flush();
    assert.equal(host.receipt().status,'FAIL');
    assert.match(host.receipt().reason,/native.*load/i);
    assert.equal(host.language(),'en');
  }
});

test('first-load widget corruption rejects even when later serialization is stable', async()=>{
  const host = await harness({readyAtSetup:true,changeInitialGraph:graph=>{graph.nodes[2].widgets_values[2] = true;}});
  host.setGraphReady();
  await host.extension.afterLoadGraph?.();
  await host.flush();
  assert.equal(host.receipt().status,'FAIL');
  assert.match(host.receipt().reason,/fixture.*data/i);
});

test('roundtrip configure failure rejects and restores the original own language', async()=>{
  const host = await harness({query:'?kvd-check=foundation&phase=roundtrip',outcomes:[true,false],readyAtSetup:true});
  host.setGraphReady();
  await host.extension.afterLoadGraph?.();
  await host.flush();
  assert.equal(host.loads.length,2);
  assert.equal(host.receipt().status,'FAIL');
  assert.equal(host.language(),'en');
  assert.equal(host.saved() === undefined,true,'an aborted roundtrip must not seed a persistence receipt');
});

test('unavailable canvas rejects without a successful receipt', async()=>{
  const host = await harness({readyAtSetup:true,unavailableCanvas:true});
  await host.extension.afterLoadGraph?.();
  await host.flush();
  assert.equal(host.receipt().status,'FAIL');
  assert.match(host.receipt().reason,/canvas/i);
});

test('completed native roundtrip checks preserve fixture data and persist RU', async()=>{
  const host = await harness({query:'?kvd-check=foundation&phase=roundtrip'});
  host.setGraphReady();
  await host.extension.afterLoadGraph?.();
  await host.flush();
  assert.equal(host.receipt().status,'PASS');
  assert.equal(host.receipt().language_roundtrip,'passed');
  assert.equal(host.receipt().native_serialization,'passed');
  assert.equal(host.receipt().links,2);
  assert.equal(host.receipt().custom_titles,'passed');
  assert.equal(host.language(),'ru');
  const expected = structuredClone(fixture);
  expected.nodes[1].title = 'KVD check · custom / Сцена';
  assert.deepEqual(host.loads[1].data,expected);
});

test('custom titles must survive native configure and saved-graph loading', async()=>{
  const roundtrip = await harness({query:'?kvd-check=foundation&phase=roundtrip',
    changeLoadedGraph(graph, count) { if (count === 2) graph.nodes[1].title = 'Changed by configure'; }});
  roundtrip.setGraphReady();
  await roundtrip.extension.afterLoadGraph();
  await roundtrip.flush();
  assert.equal(roundtrip.receipt().status,'FAIL');
  assert.match(roundtrip.receipt().reason,/custom title/i);
  assert.equal(roundtrip.language(),'en');

  const saved = structuredClone(fixture);
  saved.nodes[1].title = 'My saved title / Моя сцена';
  const persist = await harness({query:'?kvd-check=foundation&phase=persist',settingLanguage:'ru',savedWorkflow:saved,
    changeInitialGraph:graph=>{delete graph.nodes[1].title;}});
  persist.setGraphReady();
  await persist.extension.afterLoadGraph();
  await persist.flush();
  assert.equal(persist.receipt().status,'FAIL');
  assert.match(persist.receipt().reason,/custom title/i);
});

test('a premature host hook with an uninitialized graph fails before loading', async()=>{
  const host = await harness();
  await host.extension.afterLoadGraph();
  await host.flush();
  assert.equal(host.loads.length,0);
  assert.equal(host.receipt().status,'FAIL');
  assert.match(host.receipt().reason,/initialization/i);
});

test('persist phase requires the saved native graph and existing RU preference', async()=>{
  const host = await harness({query:'?kvd-check=foundation&phase=persist',settingLanguage:'ru',savedWorkflow:fixture});
  host.setGraphReady();
  await host.extension.afterLoadGraph();
  await host.flush();
  assert.equal(host.receipt().status,'PASS');
  assert.equal(host.receipt().page_reload_persistence,'passed');
  assert.equal(host.receipt().initial_language,'ru');
  const missing = await harness({query:'?kvd-check=foundation&phase=persist'});
  missing.setGraphReady();
  await missing.extension.afterLoadGraph();
  await missing.flush();
  assert.equal(missing.receipt().status,'FAIL');
  assert.match(missing.receipt().reason,/persist/i);
});
