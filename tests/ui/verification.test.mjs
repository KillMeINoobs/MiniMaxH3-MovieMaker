import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';
import vm from 'node:vm';
import { pathToFileURL } from 'node:url';
import { randomUUID } from 'node:crypto';

const fixture = JSON.parse(await readFile('workflows/foundation_project.json', 'utf8'));
const checkerSource = await readFile('web/zz_verification.js', 'utf8');
const presentationSource = await readFile('web/common/presentation.js', 'utf8');

async function harness({query='?kvd-check=foundation&phase=display', outcomes=[], changeInitialGraph, changeLoadedGraph,
  readyAtSetup=false, unavailableCanvas=false, settingLanguage='en', storedLanguage=settingLanguage,
  savedWorkflow, deferWrites=false, writeOutcomes=[], readStatus=200, losePanelsOnReload=false,
  loseCanvasOnReload=false, losePanelsAfterFinalRead=false, malformedRead=false,
  dropLoadReturn=false, loadHookSequences=[], returnedOutcomes=[], rejections=[],
  staleConfigureData=false, staleCompletionGraph=false, deferLoads=false, deferLoadNumber,
  pauseBeforeConfigureNumber, rejectionAfterPause, deferReadNumber, diagnosticParseError, serializeError,
  fixtureForTest=fixture}={}) {
  const scheduled = [], loads = [], messages = [], elements = [], stored = new Map();
  const writes = [], writeWaiters = [], reads = [], warnings = [];
  const loadResumers = [], loadWaiters = [];
  const readResumers = [], readWaiters = [];
  const timers = new Map();
  let timerId = 0;
  let extension, current, graphReady = readyAtSetup, language = settingLanguage;
  let persisted = storedLanguage;
  let panelsLost = false;
  const settingStore = {
    set(key, value) {
      assert.equal(key,'KVD.Language');
      if (value === language) return Promise.resolve(); // Native store skips unchanged cached values.
      language = value;
      presentation.namespace.setLanguage(value); // Native onChange precedes persistence.
      const outcome = writeOutcomes[writes.length] || 'saved';
      return new Promise((resolve,reject)=>{
        const write = {value, resolve(){persisted=value;resolve();}, reject};
        writes.push(write);
        for (const waiter of writeWaiters.splice(0)) waiter();
        if (!deferWrites) {
          if (outcome === 'rejected') reject(new Error('Setting save rejected'));
          else if (outcome === 'http_error') resolve(); // Native store does not reject an HTTP-error response.
          else write.resolve();
        }
      });
    },
  };
  if (savedWorkflow) stored.set('KVD.FoundationVerification.saved',JSON.stringify(savedWorkflow));
  const pauseLoad = () => new Promise(resolve=>{
    loadResumers.push(resolve);
    for (const waiter of loadWaiters.splice(0)) waiter();
  });
  const app = {
    registerExtension(value) { extension = value; },
    ui: { settings: {
      getSettingValue() { return language; },
      setSettingValue(key, value) { settingStore.set(key,value).catch(error=>warnings.push(error)); },
      async setSettingValueAsync(key, value) { await settingStore.set(key,value); },
    } },
    canvas: unavailableCanvas ? null : {ds:{}, setDirty() {}},
    async loadGraphData(data, ...options) {
      data = structuredClone(data); // The actual native implementation clones its argument.
      loads.push({data:structuredClone(data), options});
      const outcome = (loads.length - 1) in outcomes ? outcomes[loads.length - 1] : true;
      const hooks = loadHookSequences[loads.length - 1] ||
        ['beforeLoadGraph','beforeConfigureGraph','afterConfigureGraph','afterLoadGraph'];
      for (const hook of hooks.filter(name=>name.startsWith('before'))) {
        if (hook === 'beforeConfigureGraph' && loads.length === pauseBeforeConfigureNumber) await pauseLoad();
        const hookData = structuredClone(data);
        if (staleConfigureData && hook === 'beforeConfigureGraph')
          hookData.extra.kvd.verification_load_id = 'previous-request';
        await extension[hook]?.(hookData);
      }
      if ((loads.length - 1) in rejections) throw rejections[loads.length - 1];
      current = structuredClone(data);
      if (loads.length === 1) changeInitialGraph?.(current);
      changeLoadedGraph?.(current, loads.length);
      if (loseCanvasOnReload && loads.length === 2) app.canvas = null;
      // The native configure catch returns false before either completion hook.
      if (!graphReady || outcome !== true) return graphReady ? outcome : false;
      for (const hook of hooks.filter(name=>name.startsWith('after'))) {
        if (hook === 'afterLoadGraph' && (deferLoads || loads.length === deferLoadNumber)) {
          await pauseLoad();
          if (rejectionAfterPause) throw rejectionAfterPause;
        }
        if (staleCompletionGraph) current.extra.kvd.verification_load_id = 'previous-request';
        await extension[hook]?.();
      }
      return (loads.length - 1) in returnedOutcomes ? returnedOutcomes[loads.length - 1] : true;
    },
  };
  if (dropLoadReturn) {
    const original = app.loadGraphData;
    // Same return-discarding semantics as the independently fetched live wrapper.
    app.loadGraphData = async function (...args) { await original.apply(this,args); };
  }
  Object.defineProperty(app,'isGraphReady',{get:()=>graphReady});
  Object.defineProperty(app, 'graph', {get() {
    assert.ok(graphReady, 'checker accessed the graph before initialization');
    const nodes = current.nodes.map(data => {
      const node = {...data, _kvdPanel:panelsLost || (losePanelsOnReload && loads.length >= 2) ? undefined : {}, widgets:[{name:'project_json', value:data.widgets_values?.[0]}]};
      Object.defineProperty(node,'title',{get:()=>data.title,set:value=>{data.title=value;}});
      return node;
    });
    return {_nodes:nodes, links:current.links, extra:current.extra, serialize:()=>{
      if (serializeError) throw serializeError;
      return structuredClone(current);
    },
      getNodeById:id=>nodes.find(node=>node.id === id)};
  }});
  const context = vm.createContext({
    URL, URLSearchParams, structuredClone, crypto:{randomUUID},
    location:{search:query},
    document:{
      createElement() { const element = {style:{}, setAttribute(){}, textContent:''}; elements.push(element); return element; },
      body:{append(){}},
    },
    sessionStorage:{getItem:key=>stored.get(key) ?? null, setItem:(key,value)=>stored.set(key,value)},
    setTimeout(callback, delay=0) {
      const id = ++timerId;
      timers.set(id,{callback,delay});
      if (delay === 0) scheduled.push(async()=>{
        if (!timers.has(id)) return;
        timers.delete(id);
        await callback();
      });
      return id;
    },
    clearTimeout:id=>timers.delete(id),
    console:{info:(...values)=>messages.push({level:'info',values}), error:(...values)=>messages.push({level:'error',values})},
  });
  if (diagnosticParseError) context.JSON = {stringify:JSON.stringify,parse(){throw diagnosticParseError;}};
  const appModule = new vm.SyntheticModule(['app'], function() { this.setExport('app',app); }, {context});
  const api = {async fetchApi(route, options) {
    assert.equal(route,'/settings/KVD.Language');
    assert.ok(!options?.method || options.method === 'GET');
    reads.push(persisted);
    if (reads.length === deferReadNumber) await new Promise(resolve=>{
      readResumers.push(resolve);
      for (const waiter of readWaiters.splice(0)) waiter();
    });
    if (losePanelsAfterFinalRead && reads.length === 4) panelsLost = true;
    const status = typeof readStatus === 'function' ? readStatus(reads.length) : readStatus;
    return {ok:status === 200,status,json:async()=>malformedRead ? {error:'Unconfirmed'} : persisted};
  }};
  const apiModule = new vm.SyntheticModule(['api'], function() { this.setExport('api',api); }, {context});
  const presentation = new vm.SourceTextModule(presentationSource,{context});
  const checker = new vm.SourceTextModule(checkerSource,{context,
    initializeImportMeta:meta=>{meta.url=pathToFileURL(process.cwd() + '/web/zz_verification.js').href;},
  });
  // Imports remain actual production modules; only the native host is synthetic.
  await checker.link(async specifier=>{
    if (specifier.endsWith('/app.js')) return appModule;
    if (specifier.endsWith('/api.js')) return apiModule;
    if (specifier.endsWith('/presentation.js')) return presentation;
    assert.equal(specifier,'./common/language-settings.js');
    return new vm.SourceTextModule(await readFile('web/common/language-settings.js','utf8'),{context});
  });
  context.fetch = async(url, options)=>{
    assert.ok(String(url).endsWith('/examples/foundation_project.json'));
    assert.ok(!options?.method || options.method === 'GET','checker must not submit a request');
    return {ok:true,json:async()=>structuredClone(fixtureForTest)};
  };
  await checker.evaluate();
  presentation.namespace.setLanguage(language);
  await extension.setup();
  return {extension, loads, scheduled, messages, elements, writes, reads, warnings,
    marker:()=>current?.extra?.kvd?.verification_load_id,
    serialized:()=>structuredClone(current),
    setMarker(value) { current.extra.kvd.verification_load_id = value; },
    fireDeadline() {
      const entry = [...timers].find(([,timer])=>timer.delay > 0);
      assert.ok(entry,'pending native loads/recovery require a bounded failure deadline');
      const [id,timer] = entry;
      assert.ok(timer.delay <= 30000,'a deadline must be bounded');
      timers.delete(id);
      timer.callback();
      return timer.delay;
    },
    outstandingTimers:()=>timers.size,
    setGraphReady() { graphReady = true; },
    async flush() { while (scheduled.length) await scheduled.shift()(); },
    receipt() { const entry = messages.findLast(message=>message.values[0] === '[KVD verification]'); return entry && JSON.parse(entry.values[1]); },
    language:()=>language,
    persistedLanguage:()=>persisted,
    saved:()=>stored.get('KVD.FoundationVerification.saved'),
    async whenWrite(count) {
      while (writes.length < count) await new Promise(resolve=>writeWaiters.push(resolve));
      return writes[count-1];
    },
    async whenLoadPaused() {
      while (!loadResumers.length) await new Promise(resolve=>loadWaiters.push(resolve));
      return loadResumers[0];
    },
    async whenReadPaused() {
      while (!readResumers.length) await new Promise(resolve=>readWaiters.push(resolve));
      return readResumers[0];
    },
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

test('a return-dropping wrapper requires the full per-call native lifecycle and exact graph', async()=>{
  const host = await harness({query:'?kvd-check=foundation&phase=roundtrip',dropLoadReturn:true});
  host.setGraphReady();
  await host.extension.afterLoadGraph();
  await host.flush();
  assert.equal(host.receipt().status,'PASS');
  assert.equal(host.receipt().native_loads.length,2);
  for (const load of host.receipt().native_loads) {
    assert.equal(load.return_type,'undefined');
    assert.equal(load.return_value,'undefined');
    assert.deepEqual(load.hooks,['beforeLoadGraph','beforeConfigureGraph','afterConfigureGraph','afterLoadGraph']);
    assert.equal(load.requested_graph_matched,true);
    assert.equal(load.completion,'native_lifecycle_and_graph');
  }
  assert.equal(host.receipt().native_serialization,'passed');
});

test('hidden native abort or incomplete lifecycle never accepts a void/true result', async()=>{
  for (const options of [
    {dropLoadReturn:true,outcomes:[false]},
    {dropLoadReturn:true,loadHookSequences:[['beforeLoadGraph','beforeConfigureGraph','afterConfigureGraph']]},
    {loadHookSequences:[['afterLoadGraph']]},
    {dropLoadReturn:true,loadHookSequences:[['beforeLoadGraph','beforeLoadGraph','beforeConfigureGraph','afterConfigureGraph','afterLoadGraph']]},
    {loadHookSequences:[['beforeLoadGraph','beforeConfigureGraph','afterLoadGraph','afterConfigureGraph']]},
    {returnedOutcomes:[null]}, {returnedOutcomes:[1]}, {returnedOutcomes:['true']},
  ]) {
    const host = await harness(options);
    host.setGraphReady();
    await host.extension.afterLoadGraph();
    await host.flush();
    assert.equal(host.receipt().status,'FAIL');
    assert.equal(host.saved(),undefined);
    assert.match(host.receipt().reason,/native.*load/i);
    assert.ok(Array.isArray(host.receipt().native_loads),'failed loads must retain their observed return and hook evidence');
    assert.equal(host.receipt().native_loads.length,1);
    assert.ok(host.receipt().native_loads[0].return_type);
  }
});

test('failed native loads retain typed return and readiness diagnostics without claiming success', async()=>{
  const host = await harness({outcomes:[false]});
  host.setGraphReady();
  await host.extension.afterLoadGraph();
  await host.flush();
  const receipt = host.receipt();
  assert.equal(receipt.status,'FAIL');
  assert.ok(Array.isArray(receipt.native_loads),'failed loads must retain diagnostics');
  assert.equal(receipt.native_loads[0].return_type,'boolean');
  assert.equal(receipt.native_loads[0].return_value,false);
  assert.deepEqual(receipt.native_loads[0].hooks,['beforeLoadGraph','beforeConfigureGraph']);
  assert.equal(receipt.native_loads[0].ready_before.graph,true);
  assert.equal(receipt.native_loads[0].ready_after.canvas,true);
  assert.match(receipt.error_stack,/Native.*load/i);
  assert.equal(receipt.native_loads[0].completion,undefined);
});

test('native promise rejection retains its actual error and stack, including a stackless rejection', async()=>{
  for (const rejection of [new Error('Native load rejection'),undefined]) {
    const host = await harness({rejections:[rejection]});
    host.setGraphReady();
    await host.extension.afterLoadGraph();
    await host.flush();
    const receipt = host.receipt();
    assert.equal(receipt.status,'FAIL');
    assert.equal(receipt.native_loads[0].rejected,true);
    assert.equal(receipt.native_loads[0].error,String(rejection?.message ?? rejection));
    assert.equal(receipt.native_loads[0].error_stack,rejection?.stack ?? null);
    assert.equal(receipt.error_stack,rejection?.stack ?? null);
    assert.equal(receipt.reason,String(rejection?.message ?? rejection));
    assert.equal(receipt.serialized_workflow,undefined);
    assert.equal(host.saved(),undefined);
  }
});

test('stale lifecycle data cannot complete this request even with identical nodes and links', async()=>{
  for (const options of [{staleConfigureData:true},{staleCompletionGraph:true}]) {
    const host = await harness({dropLoadReturn:true,...options});
    host.setGraphReady();
    await host.extension.afterLoadGraph();
    await host.flush();
    assert.equal(host.receipt().status,'FAIL');
    assert.match(host.receipt().reason,/native.*load/i);
    assert.equal(host.receipt().serialized_workflow,undefined);
    assert.equal(host.saved(),undefined);
  }
});

test('a stalled call and an unrelated completion event cannot create successful evidence', async()=>{
  const host = await harness({deferLoads:true,dropLoadReturn:true});
  host.setGraphReady();
  await host.extension.afterLoadGraph();
  const running = host.flush();
  const resume = await host.whenLoadPaused();
  await host.extension.afterLoadGraph(); // Stale event while the actual native call is still pending.
  await new Promise(resolve=>setImmediate(resolve));
  assert.equal(host.receipt(),undefined);
  assert.equal(host.saved(),undefined);
  resume(); // The real completion now produces a duplicate event, which must reject.
  await running;
  assert.equal(host.receipt().status,'FAIL');
  assert.match(host.receipt().reason,/native.*load/i);
  assert.equal(host.receipt().serialized_workflow,undefined);
});

test('F15: a pending second load fails within its deadline and verifies original-language recovery', async()=>{
  const host = await harness({query:'?kvd-check=foundation&phase=roundtrip',dropLoadReturn:true,deferLoadNumber:2});
  host.setGraphReady();
  await host.extension.afterLoadGraph();
  const running = host.flush();
  const resume = await host.whenLoadPaused();
  try {
    assert.equal(host.persistedLanguage(),'ru');
    assert.ok(host.marker());
    const deadline = host.fireDeadline();
    await running;
    const receipt = host.receipt();
    assert.equal(receipt.status,'FAIL');
    assert.match(receipt.reason,/native.*load.*(deadline|timed out|exceeded)/i);
    assert.equal(receipt.native_loads[1].timed_out,true);
    assert.equal(receipt.native_loads[1].deadline_ms,deadline);
    assert.equal(receipt.native_loads[1].return_state,'pending');
    assert.equal(receipt.native_loads[1].acceptance_invalidated,true);
    assert.equal(receipt.original_language_restored,true);
    assert.equal(receipt.restored_persisted_language,'en');
    assert.equal(host.persistedLanguage(),'en');
    assert.equal(host.marker(),undefined);
    assert.equal(host.saved(),undefined);
    assert.equal(receipt.serialized_workflow,undefined);
  } finally { resume(); await running; }
  await new Promise(resolve=>setImmediate(resolve));
  assert.equal(host.receipt().status,'FAIL','late settlement cannot revive the failed run');
  assert.equal(host.saved(),undefined);
  assert.equal(host.marker(),undefined);
  assert.equal(host.outstandingTimers(),0);
});

test('F15: late configuration cleans its expired ID without saving or repeating verification', async()=>{
  const host = await harness({pauseBeforeConfigureNumber:1,dropLoadReturn:true});
  host.setGraphReady();
  await host.extension.afterLoadGraph();
  const running = host.flush();
  const resume = await host.whenLoadPaused();
  try {
    host.fireDeadline();
    await running;
    assert.equal(host.receipt().status,'FAIL');
    assert.equal(host.saved(),undefined);
  } finally { resume(); await running; }
  await new Promise(resolve=>setImmediate(resolve));
  assert.equal(host.marker(),undefined);
  assert.equal(host.loads.length,1,'no automatic retry');
  assert.equal(host.receipt().status,'FAIL');
  assert.equal(host.messages.filter(m=>m.values[0] === '[KVD verification]').length,1);
  assert.equal(host.outstandingTimers(),0);
});

test('F15: late fulfillment or rejection preserves a newer request marker and remains failed', async()=>{
  for (const rejectionAfterPause of [undefined,new Error('Late native rejection')]) {
    const host = await harness({deferLoadNumber:1,dropLoadReturn:true,rejectionAfterPause});
    host.setGraphReady();
    await host.extension.afterLoadGraph();
    const running = host.flush();
    const resume = await host.whenLoadPaused();
    try {
      host.fireDeadline();
      await running;
      host.setMarker('newer-owned-or-foreign-request');
    } finally { resume(); await running; }
    await new Promise(resolve=>setImmediate(resolve));
    assert.equal(host.receipt().status,'FAIL');
    assert.equal(host.marker(),'newer-owned-or-foreign-request');
    assert.equal(host.saved(),undefined);
    assert.equal(host.loads.length,1);
    const late = host.messages.find(m=>m.values[0] === '[KVD verification late load]');
    assert.ok(late,'late settlements require honest diagnostics');
    assert.equal(JSON.parse(late.values[1]).accepted,false);
    assert.equal(host.outstandingTimers(),0);
  }
});

test('F15: pending recovery is bounded and cannot claim a restored preference', async()=>{
  const host = await harness({query:'?kvd-check=foundation&phase=roundtrip',deferLoadNumber:2,deferWrites:true});
  host.setGraphReady();
  await host.extension.afterLoadGraph();
  const running = host.flush();
  const saveRU = await host.whenWrite(1);
  saveRU.resolve();
  const resume = await host.whenLoadPaused();
  let restore;
  try {
    host.fireDeadline();
    restore = await host.whenWrite(2);
    host.fireDeadline();
    await running;
    assert.equal(host.receipt().status,'FAIL');
    assert.equal(host.receipt().original_language_restored,false);
    assert.equal(host.receipt().restored_persisted_language,undefined);
    assert.equal(host.persistedLanguage(),'ru');
    assert.equal(host.marker(),undefined);
    assert.equal(host.saved(),undefined);
  } finally { restore?.resolve(); resume(); await running; }
  await new Promise(resolve=>setImmediate(resolve));
  assert.equal(host.receipt().status,'FAIL');
  assert.equal(host.receipt().original_language_restored,false,'late recovery is not verified evidence');
  assert.equal(host.saved(),undefined);
  assert.equal(host.outstandingTimers(),0);
});

test('F15: stalled failure readback produces an unverified FAIL receipt within its own deadline', async()=>{
  const host = await harness({deferLoadNumber:1,deferReadNumber:2});
  host.setGraphReady();
  await host.extension.afterLoadGraph();
  const running = host.flush();
  const resumeLoad = await host.whenLoadPaused();
  let resumeRead;
  try {
    host.fireDeadline();
    resumeRead = await host.whenReadPaused();
    host.fireDeadline();
    await running;
    assert.equal(host.receipt().status,'FAIL');
    assert.equal(host.receipt().persisted_language,'unverified');
    assert.equal(host.receipt().original_language_restored,undefined,'no preference was changed');
    assert.equal(host.marker(),undefined);
    assert.equal(host.saved(),undefined);
  } finally { resumeRead?.(); resumeLoad(); await running; }
  await new Promise(resolve=>setImmediate(resolve));
  assert.equal(host.receipt().status,'FAIL');
  assert.equal(host.receipt().persisted_language,'unverified','late readback is not verified evidence');
  assert.equal(host.outstandingTimers(),0);
});

test('F16: every failed post-load assertion removes only its current marker', async()=>{
  for (const options of [{returnedOutcomes:[true,1]},{outcomes:[true,false]},
    {losePanelsOnReload:true},{changeLoadedGraph(graph,count){if (count === 2) graph.nodes[2].widgets_values[2]=true;}}]) {
    const host = await harness({query:'?kvd-check=foundation&phase=roundtrip',...options});
    host.setGraphReady();
    await host.extension.afterLoadGraph();
    await host.flush();
    assert.equal(host.receipt().status,'FAIL');
    assert.equal(host.persistedLanguage(),'en');
    assert.equal(host.marker(),undefined);
    assert.equal(host.saved(),undefined);
  }
});

test('F16: stale saved reserved IDs are stripped while other metadata and custom titles survive', async()=>{
  const saved = structuredClone(fixture);
  saved.nodes[1].title = 'Saved custom title / Сцена';
  saved.extra.kvd.verification_load_id = 'old-verification-request';
  saved.extra.kvd.other_metadata = {keep:'owned metadata'};
  saved.extra.unrelated_metadata = {keep:'other metadata'};
  const host = await harness({query:'?kvd-check=foundation&phase=persist',settingLanguage:'ru',savedWorkflow:saved,dropLoadReturn:true});
  host.setGraphReady();
  await host.extension.afterLoadGraph();
  await host.flush();
  assert.equal(host.receipt().status,'PASS');
  assert.equal(saved.extra.kvd.verification_load_id,'old-verification-request','input is not mutated');
  assert.notEqual(host.loads[0].data.extra.kvd.verification_load_id,'old-verification-request');
  const expected = structuredClone(saved);
  delete expected.extra.kvd.verification_load_id;
  assert.deepEqual(host.receipt().serialized_workflow,expected);
  assert.deepEqual(host.serialized(),expected);
  assert.deepEqual(JSON.parse(host.saved()),expected);
  assert.equal(host.outstandingTimers(),0);
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
  assert.equal(host.persistedLanguage(),'ru');
  assert.equal(host.receipt().persisted_language,'ru');
  const expected = structuredClone(fixture);
  expected.nodes[1].title = 'KVD check · custom / Сцена';
  const loaded = structuredClone(host.loads[1].data);
  assert.equal(loaded.extra.kvd.verification_load_id,host.receipt().native_loads[1].load_id);
  assert.notEqual(host.receipt().native_loads[0].load_id,host.receipt().native_loads[1].load_id);
  delete loaded.extra.kvd.verification_load_id;
  assert.deepEqual(loaded,expected);
  assert.deepEqual(host.receipt().serialized_workflow,expected);
  assert.deepEqual(JSON.parse(host.saved()),expected,'transient load IDs must not alter the saved fixture');
});

test('unset preference remains distinct from EN default before verified RU persistence', async()=>{
  const host = await harness({query:'?kvd-check=foundation&phase=roundtrip',storedLanguage:null});
  host.setGraphReady();
  await host.extension.afterLoadGraph();
  await host.flush();
  assert.equal(host.receipt().status,'PASS');
  assert.equal(host.receipt().initial_language,'en');
  assert.equal(host.receipt().initial_persisted_language,null);
  assert.equal(host.receipt().persisted_language,'ru');
  assert.deepEqual(host.writes.map(write=>write.value),['ru']);
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

test('a stale saved graph with different types or values is rejected before native loading', async()=>{
  for (const change of [graph=>{graph.nodes[0].type='UnexpectedNode';},
    graph=>{graph.nodes[2].widgets_values[2]=true;}]) {
    const saved = structuredClone(fixture);
    change(saved);
    const host = await harness({query:'?kvd-check=foundation&phase=persist',settingLanguage:'ru',savedWorkflow:saved});
    host.setGraphReady();
    await host.extension.afterLoadGraph();
    await host.flush();
    assert.equal(host.receipt().status,'FAIL');
    assert.equal(host.loads.length,0,'only the approved Project fixture may reach native loading');
    assert.match(host.receipt().reason,/saved.*fixture/i);
  }
});

test('F12: pending/rejected native save cannot produce PASS or a persisted fixture', async()=>{
  const host = await harness({query:'?kvd-check=foundation&phase=roundtrip',deferWrites:true});
  host.setGraphReady();
  await host.extension.afterLoadGraph();
  const running = host.flush();
  const save = await host.whenWrite(1);
  await new Promise(resolve=>setImmediate(resolve)); // Drain queued work while the write remains pending.
  assert.equal(host.receipt(),undefined,'must await the native setting write');
  assert.equal(host.saved(),undefined);
  assert.equal(host.language(),'ru');
  assert.equal(host.persistedLanguage(),'en');
  save.reject(new Error('Setting save rejected'));
  const restore = await host.whenWrite(2);
  assert.equal(host.receipt(),undefined,'restoration evidence must await completion');
  restore.resolve();
  await running;
  assert.equal(host.receipt().status,'FAIL');
  assert.equal(host.receipt().original_language_restored,true);
  assert.equal(host.receipt().restored_persisted_language,'en');
  assert.equal(host.saved(),undefined);
});

test('F12: failed restoration cannot claim restored persisted locale', async()=>{
  const host = await harness({query:'?kvd-check=foundation&phase=roundtrip',outcomes:[true,false],writeOutcomes:['saved','rejected']});
  host.setGraphReady();
  await host.extension.afterLoadGraph();
  await host.flush();
  assert.equal(host.receipt().status,'FAIL');
  assert.equal(host.receipt().original_language_restored,false);
  assert.equal(host.receipt().restored_persisted_language,undefined);
  assert.equal(host.persistedLanguage(),'ru');
  assert.equal(host.saved(),undefined);
});

test('F12: resolved HTTP-error save and unavailable readback cannot claim persistence', async()=>{
  for (const options of [{writeOutcomes:['http_error']},{readStatus:503},{malformedRead:true},
    {query:'?kvd-check=foundation&phase=persist',settingLanguage:'ru',storedLanguage:'en',savedWorkflow:fixture}]) {
    const host = await harness({query:'?kvd-check=foundation&phase=roundtrip',...options});
    host.setGraphReady();
    await host.extension.afterLoadGraph();
    await host.flush();
    assert.equal(host.receipt().status,'FAIL');
    assert.equal(host.receipt().language_roundtrip,undefined);
    assert.equal(host.receipt().page_reload_persistence,undefined);
    assert.equal(host.saved() !== undefined,!!options.savedWorkflow,'must not create a successful fixture');
  }
});

test('F13: each reload requires owned panels and a usable canvas', async()=>{
  for (const options of [{losePanelsOnReload:true},{loseCanvasOnReload:true},{losePanelsAfterFinalRead:true},
    {dropLoadReturn:true,losePanelsOnReload:true}]) {
    const host = await harness({query:'?kvd-check=foundation&phase=roundtrip',...options});
    host.setGraphReady();
    await host.extension.afterLoadGraph();
    await host.flush();
    assert.equal(host.loads.length,2);
    assert.equal(host.receipt().status,'FAIL');
    assert.match(host.receipt().reason,/presentation|canvas/i);
    assert.equal(host.saved(),undefined);
    assert.equal(host.persistedLanguage(),'en');
  }
});

test('semantic failure captures full stable projections and the first typed field difference', async()=>{
  const cases = [
    {change:g=>{g.nodes[2].widgets_values[2]=true;},path:'$["nodes"][2]["widgets_values"][2]',kind:'value',
      expected:{present:true,type:'boolean',value:false},actual:{present:true,type:'boolean',value:true}},
    {change:g=>{g.nodes[1].inputs[0].link=9;},path:'$["nodes"][1]["inputs"][0]["link"]',kind:'value',
      expected:{present:true,type:'number',value:1},actual:{present:true,type:'number',value:9}},
    {change:g=>{g.nodes[0].outputs[0].type='STRING';},path:'$["nodes"][0]["outputs"][0]["type"]',kind:'value',
      expected:{present:true,type:'string',value:'KVD_PROJECT'},actual:{present:true,type:'string',value:'STRING'}},
    {change:g=>{g.links[1][4]='0';},path:'$["links"][1][4]',kind:'type',
      expected:{present:true,type:'number',value:0},actual:{present:true,type:'string',value:'0'}},
    {change:g=>{g.nodes[1].id=22;},path:'$["nodes"][1]["id"]',kind:'value',
      expected:{present:true,type:'number',value:2},actual:{present:true,type:'number',value:22}},
    {change:g=>{delete g.nodes[1].type;},path:'$["nodes"][1]["type"]',kind:'missing_field',
      expected:{present:true,type:'string',value:'KVD_ValidateProject'},actual:{present:false,type:'missing'}},
    {change:g=>{g.nodes[2].widgets_values.push(null);},path:'$["nodes"][2]["widgets_values"][3]',kind:'missing_index',
      expected:{present:false,type:'missing'},actual:{present:true,type:'null',value:null}},
    {change:g=>{g.nodes[2].widgets_values.pop();},path:'$["nodes"][2]["widgets_values"][2]',kind:'missing_index',
      expected:{present:true,type:'boolean',value:false},actual:{present:false,type:'missing'}},
  ];
  for (const {change,path,kind,expected,actual} of cases) {
    const host = await harness({dropLoadReturn:true,changeInitialGraph:change});
    host.setGraphReady();
    await host.extension.afterLoadGraph();
    await host.flush();
    const receipt = host.receipt();
    assert.equal(receipt.status,'FAIL');
    assert.equal(receipt.reason,'Fixture data changed during native loading');
    const diagnostic = receipt.semantic_failure;
    assert.ok(diagnostic,'failed semantic comparison must retain its diagnostic');
    assert.equal(diagnostic.status,'captured');
    assert.equal(diagnostic.load_id,receipt.native_loads[0].load_id);
    assert.equal(diagnostic.stage,receipt.reason);
    assert.deepEqual(diagnostic.first_difference,{path,kind,expected,actual});
    assert.equal(diagnostic.expected_projection.nodes.length,4);
    assert.deepEqual(diagnostic.expected_projection.links,fixture.links);
    assert.equal(diagnostic.expected_projection.nodes[0].widgets_values[0],fixture.nodes[0].widgets_values[0]);
    assert.notDeepEqual(diagnostic.actual_projection,diagnostic.expected_projection);
    assert.equal(diagnostic.actual_projection.nodes[0].widgets_values[0],fixture.nodes[0].widgets_values[0]);
    assert.equal(diagnostic.actual_projection.nodes[0].title,undefined,'cosmetic data stays outside the stable projection');
    assert.equal(host.marker(),undefined);
    assert.equal(host.saved(),undefined);
    assert.equal(receipt.serialized_workflow,undefined);
    assert.equal(host.outstandingTimers(),0);
  }
});

test('first stable difference follows projection order and post-RU failure retains verified recovery', async()=>{
  const first = await harness({changeInitialGraph:g=>{
    g.nodes[3].id=44;
    g.links[0][2]=9;
    g.nodes[0].outputs[0].name='changed-port';
  }});
  first.setGraphReady(); await first.extension.afterLoadGraph(); await first.flush();
  assert.ok(first.receipt().semantic_failure,'failed semantic comparison must retain its diagnostic');
  assert.equal(first.receipt().semantic_failure.first_difference.path,'$["nodes"][0]["outputs"][0]["name"]');
  const ordered = await harness({query:'?kvd-check=foundation&phase=roundtrip',changeLoadedGraph(g,count){
    if (count === 2) g.nodes[0].widgets_values[0]='changed on second load';
  }});
  ordered.setGraphReady(); await ordered.extension.afterLoadGraph(); await ordered.flush();
  const receipt = ordered.receipt();
  assert.equal(receipt.status,'FAIL');
  assert.equal(receipt.semantic_failure.load_id,receipt.native_loads[1].load_id);
  assert.equal(receipt.semantic_failure.first_difference.path,'$["nodes"][0]["widgets_values"][0]');
  assert.equal(receipt.original_language_restored,true);
  assert.equal(receipt.restored_persisted_language,'en');
  assert.equal(ordered.saved(),undefined);
  assert.equal(ordered.marker(),undefined);
});

test('cosmetic changes leave existing stable acceptance and successful evidence unchanged', async()=>{
  const host = await harness({changeInitialGraph:g=>{
    g.nodes[0].title='Native cosmetic title'; g.nodes[0].pos=[999,888]; g.nodes[0].color='#123456';
    g.nodes[1].inputs[0].label='Localized input'; g.nodes[0].outputs[0].label='Localized output';
    g.extra.cosmetic={keep:'metadata'};
  }});
  host.setGraphReady(); await host.extension.afterLoadGraph(); await host.flush();
  assert.equal(host.receipt().status,'PASS');
  assert.equal(host.receipt().semantic_failure,undefined);
  assert.equal(host.receipt().serialized_workflow.nodes[0].title,'Native cosmetic title');
  assert.deepEqual(host.receipt().serialized_workflow.extra.cosmetic,{keep:'metadata'});
});

test('diagnostic budget and capture failure cannot mask rejection or prevent marker cleanup', async()=>{
  for (const options of [
    {changeInitialGraph:g=>{g.nodes[2].widgets_values[1]='x'.repeat(300000);}},
    {changeInitialGraph:g=>{g.nodes[2].widgets_values[2]=true;},diagnosticParseError:new Error('Diagnostic parser unavailable')},
  ]) {
    const host = await harness(options);
    host.setGraphReady(); await host.extension.afterLoadGraph(); await host.flush();
    const receipt = host.receipt();
    assert.equal(receipt.status,'FAIL');
    assert.equal(receipt.reason,'Fixture data changed during native loading');
    assert.ok(receipt.semantic_failure,'unavailable diagnostics must be reported explicitly');
    assert.equal(receipt.semantic_failure.status,'unavailable');
    assert.equal(receipt.semantic_failure.expected_projection,undefined);
    assert.equal(receipt.semantic_failure.actual_projection,undefined);
    assert.equal(receipt.semantic_failure.first_difference,undefined);
    assert.match(receipt.semantic_failure.capture_error,/limit|unavailable/i);
    assert.equal(host.marker(),undefined);
    assert.equal(host.saved(),undefined);
  }
  const original = new Error('Native serialization unavailable');
  const host = await harness({serializeError:original});
  host.setGraphReady(); await host.extension.afterLoadGraph(); await host.flush();
  assert.equal(host.receipt().reason,original.message);
  assert.equal(host.receipt().error_stack,original.stack);
  assert.equal(host.receipt().semantic_failure,undefined,'no comparison data was available');
  assert.equal(host.marker(),undefined);
});

test('PREP-DIAG1: overlong capture errors keep the entire unavailable envelope bounded', async()=>{
  for (const afterRU of [false,true]) {
    const host = await harness({query:'?kvd-check=foundation&phase='+(afterRU ? 'roundtrip' : 'display'),
      diagnosticParseError:new Error('x'.repeat(300000)),changeLoadedGraph(g,count){
        if (count === (afterRU ? 2 : 1)) g.nodes[2].widgets_values[2]=true;
      }});
    host.setGraphReady(); await host.extension.afterLoadGraph(); await host.flush();
    const receipt = host.receipt(), diagnostic = receipt.semantic_failure;
    assert.equal(receipt.status,'FAIL');
    assert.equal(receipt.reason,'Fixture data changed during native loading');
    assert.equal(diagnostic.status,'unavailable');
    assert.ok(JSON.stringify(diagnostic).length <= diagnostic.limit_characters,'whole unavailable envelope must respect the capture budget');
    assert.equal(diagnostic.capture_error_truncated,true);
    assert.equal(diagnostic.expected_projection,undefined);
    assert.equal(diagnostic.actual_projection,undefined);
    assert.equal(diagnostic.first_difference,undefined);
    assert.equal(diagnostic.load_id,receipt.native_loads[afterRU ? 1 : 0].load_id);
    assert.equal(host.marker(),undefined);
    assert.equal(host.saved(),undefined);
    assert.equal(receipt.serialized_workflow,undefined);
    assert.equal(host.persistedLanguage(),'en');
    if (afterRU) assert.equal(receipt.original_language_restored,true);
    assert.equal(host.outstandingTimers(),0);
  }
});

test('PREP-DIAG1: unprintable capture errors cannot replace mismatch or block verified recovery', async()=>{
  const failures = [
    {message:{toString(){throw new Error('diagnostic-format-error');}}},
    Object.defineProperty({},'message',{get(){throw new Error('diagnostic-message-error');}}),
  ];
  for (const diagnosticParseError of failures) for (const afterRU of [false,true]) {
    const host = await harness({query:'?kvd-check=foundation&phase='+(afterRU ? 'roundtrip' : 'display'),
      diagnosticParseError,changeLoadedGraph(g,count){
        if (count === (afterRU ? 2 : 1)) g.nodes[2].widgets_values[2]=true;
      }});
    host.setGraphReady(); await host.extension.afterLoadGraph(); await host.flush();
    const receipt = host.receipt(), diagnostic = receipt.semantic_failure;
    assert.equal(receipt.status,'FAIL');
    assert.equal(receipt.reason,'Fixture data changed during native loading');
    assert.equal(diagnostic.status,'unavailable');
    assert.match(diagnostic.capture_error,/formatting unavailable/i);
    assert.ok(JSON.stringify(diagnostic).length <= diagnostic.limit_characters);
    assert.equal(diagnostic.expected_projection,undefined);
    assert.equal(diagnostic.actual_projection,undefined);
    assert.equal(diagnostic.first_difference,undefined);
    assert.equal(host.marker(),undefined);
    assert.equal(host.saved(),undefined);
    assert.equal(host.persistedLanguage(),'en');
    if (afterRU) {
      assert.equal(receipt.original_language_restored,true);
      assert.equal(receipt.restored_persisted_language,'en');
    }
    assert.equal(host.outstandingTimers(),0);
  }
});

test('stable diagnostic preserves rejection of JSON object-key order with the original comparator', async()=>{
  // An offline opaque widget entry exercises the existing generic JSON field;
  // this is not a claim that a native Project widget accepts such a value.
  const testFixture = structuredClone(fixture);
  testFixture.nodes[2].widgets_values.push({first:1,second:2});
  const host = await harness({fixtureForTest:testFixture,changeInitialGraph(g){
    g.nodes[2].widgets_values[3]={second:2,first:1};
  }});
  host.setGraphReady(); await host.extension.afterLoadGraph(); await host.flush();
  const receipt = host.receipt(), difference = receipt.semantic_failure.first_difference;
  assert.equal(receipt.status,'FAIL');
  assert.equal(receipt.reason,'Fixture data changed during native loading');
  assert.equal(difference.path,'$["nodes"][2]["widgets_values"][3]');
  assert.equal(difference.kind,'object_key_order');
  assert.deepEqual(difference.expected.value,difference.actual.value);
  assert.notEqual(JSON.stringify(difference.expected.value),JSON.stringify(difference.actual.value));
  assert.deepEqual(Object.keys(difference.expected.value),['first','second']);
  assert.deepEqual(Object.keys(difference.actual.value),['second','first']);
  assert.equal(host.marker(),undefined);
  assert.equal(host.saved(),undefined);
});
