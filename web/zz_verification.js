// Opt-in frontend conformance tool. Inert on normal pages. Never queues or executes nodes.
import { app } from '../../scripts/app.js';
import { api } from '../../scripts/api.js';
import { getLanguage, setLanguage } from './common/presentation.js';
import { SETTING_ID, effectiveLanguage, readPersistedLanguage, persistLanguage } from './common/language-settings.js';

function semanticWorkflow(graph) {
  return JSON.stringify({nodes: graph.nodes.map(n => ({id:n.id,type:n.type,mode:n.mode ?? 0,
    widgets_values:n.widgets_values || [],
    inputs:(n.inputs || []).map(({name,type,link}) => ({name,type,link:link ?? null})),
    outputs:(n.outputs || []).map(({name,type,links}) => ({name,type,links:links || []}))})), links:graph.links});
}
function check(value, message) { if (!value) throw new Error(message); }
const DIAGNOSTIC_CHARACTER_LIMIT = 262144;
function firstStableDifference(expected, actual) {
  const type = value => value === null ? 'null' : Array.isArray(value) ? 'array' : typeof value;
  const side = (value,present) => present ? {present:true,type:type(value),value} : {present:false,type:'missing'};
  const pending = [{expected,actual,path:'$',expectedPresent:true,actualPresent:true}];
  while (pending.length) {
    const item = pending.pop();
    const {expected:a,actual:b,path,expectedPresent,actualPresent} = item;
    const difference = kind => ({path,kind,expected:side(a,expectedPresent),actual:side(b,actualPresent)});
    if (!expectedPresent || !actualPresent) return difference(item.missingKind);
    const kind = type(a);
    if (kind !== type(b)) return difference('type');
    if (kind !== 'array' && kind !== 'object') {
      if (a !== b) return difference('value');
      continue;
    }
    const keysA = Object.keys(a), keysB = Object.keys(b);
    if (kind === 'object' && keysA.length === keysB.length && keysA.every(k=>Object.hasOwn(b,k)) &&
      keysA.some((k,i)=>k !== keysB[i])) return difference('object_key_order');
    const keys = kind === 'array' ? Array.from({length:Math.max(a.length,b.length)},(_,i)=>i) :
      [...keysA,...keysB.filter(k=>!Object.hasOwn(a,k))];
    for (let i=keys.length-1;i>=0;i--) {
      const key = keys[i];
      pending.push({expected:a[key],actual:b[key],path:path+'['+JSON.stringify(key)+']',
        expectedPresent:Object.hasOwn(a,key),actualPresent:Object.hasOwn(b,key),
        missingKind:kind === 'array' ? 'missing_index' : 'missing_field'});
    }
  }
  return null;
}
function checkStableWorkflow(actual, expected, message, receipt, loadId=null) {
  // Equality uses the original full JSON strings, never the diagnostic budget or diff.
  if (actual !== expected) {
    const details = {stage:message,load_id:loadId,comparison:'exact_stable_json',
      expected_characters:expected.length,actual_characters:actual.length,
      limit_characters:DIAGNOSTIC_CHARACTER_LIMIT};
    try {
      if (expected.length + actual.length > DIAGNOSTIC_CHARACTER_LIMIT)
        throw new Error('Stable projections exceed the diagnostic character limit');
      const expectedProjection = JSON.parse(expected), actualProjection = JSON.parse(actual);
      const firstDifference = firstStableDifference(expectedProjection,actualProjection);
      if (!firstDifference) throw new Error('First stable field difference unavailable');
      const diagnostic = {...details,status:'captured',expected_projection:expectedProjection,
        actual_projection:actualProjection,first_difference:firstDifference};
      if (JSON.stringify(diagnostic).length > DIAGNOSTIC_CHARACTER_LIMIT)
        throw new Error('Stable projections and first difference exceed the diagnostic character limit');
      receipt.semantic_failure = diagnostic;
    } catch (error) {
      let captureError = 'Diagnostic error formatting unavailable';
      try { captureError = String(error?.message ?? error); } catch {}
      const unavailable = {...details,status:'unavailable',capture_error:captureError.slice(0,1024),
        capture_error_truncated:captureError.length > 1024};
      try {
        if (JSON.stringify(unavailable).length > DIAGNOSTIC_CHARACTER_LIMIT)
          throw new Error('Unavailable diagnostic envelope exceeds its character limit');
        receipt.semantic_failure = unavailable;
      } catch {
        receipt.semantic_failure = {status:'unavailable',limit_characters:DIAGNOSTIC_CHARACTER_LIMIT,
          capture_error:'Diagnostic envelope formatting unavailable',metadata_unavailable:true};
      }
    }
  }
  check(actual === expected,message); // Capture failure must preserve this original rejection.
}
const FAILURE_DEADLINE_MS = 15000;
async function beforeFailureDeadline(promise, message, onExpire) {
  let timer;
  try {
    return await Promise.race([promise,new Promise((_,reject)=>{
      timer = setTimeout(()=>{
        onExpire?.();
        reject(new Error(message));
      },FAILURE_DEADLINE_MS);
    })]);
  } finally { clearTimeout(timer); }
}
function withoutVerificationMarker(graph) {
  const copy = structuredClone(graph);
  if (copy.extra?.kvd) delete copy.extra.kvd.verification_load_id;
  return copy;
}
let pendingCheck;
let activeLoad;
const loadHooks = ['beforeLoadGraph','beforeConfigureGraph','afterConfigureGraph','afterLoadGraph'];
function readiness() {
  const observed = {graph:false,canvas:false};
  try {
    observed.graph = app.isGraphReady === true;
    // Do not access the native canvas getter before graph initialization.
    observed.canvas = observed.graph && !!app.canvas?.ds;
  } catch {} // Unavailable readiness is recorded as unavailable, never successful.
  return observed;
}
function observeLoadHook(name, data) {
  if (!activeLoad || activeLoad.expired) return;
  activeLoad.trace.hooks.push(name);
  if (name === 'beforeConfigureGraph') {
    try {
      activeLoad.trace.requested_graph_matched =
        data.extra?.kvd?.verification_load_id === activeLoad.trace.load_id &&
        semanticWorkflow(data) === activeLoad.expected;
    }
    catch { activeLoad.trace.requested_graph_matched = false; }
  } else if (name === 'afterConfigureGraph' || name === 'afterLoadGraph') {
    const key = name === 'afterConfigureGraph' ? 'configured_graph_matched' : 'completed_graph_matched';
    try { activeLoad.trace[key] = app.isGraphReady === true &&
      app.graph.extra?.kvd?.verification_load_id === activeLoad.trace.load_id; }
    catch { activeLoad.trace[key] = false; }
  }
}
app.registerExtension({
  name:'KVD.FoundationVerification',
  setup() {
    const query = new URLSearchParams(location.search);
    if (query.get('kvd-check') !== 'foundation') return;
    const banner = document.createElement('div');
    banner.id = 'kvd-verification'; banner.setAttribute('role','status');
    Object.assign(banner.style,{position:'fixed',top:'58px',left:'70px',zIndex:'1000',
      background:'#17262e',color:'#e4edf1',padding:'10px 14px',border:'1px solid #72c7c5',borderRadius:'8px',maxWidth:'800px'});
    document.body.append(banner);
    banner.textContent = 'KVD foundation: waiting for the native workflow to finish loading';
    // Capture the query before native workflow navigation repairs the URL.
    pendingCheck = {banner, phase:query.get('phase') || 'roundtrip',
      startup:[{event:'setup',...readiness()}]};
  },
  beforeLoadGraph() { observeLoadHook('beforeLoadGraph'); },
  beforeConfigureGraph(data) { observeLoadHook('beforeConfigureGraph',data); },
  afterConfigureGraph() { observeLoadHook('afterConfigureGraph'); },
  afterLoadGraph() {
    observeLoadHook('afterLoadGraph');
    if (!pendingCheck) return;
    const requested = pendingCheck;
    requested.startup.push({event:'initial_afterLoadGraph',...readiness()});
    pendingCheck = undefined;
    // This native lifecycle hook provides readiness. Dispatch after it returns
    // to avoid recursively awaiting loadGraphData inside its own load hook.
    setTimeout(() => verify(requested), 0);
  },
});

async function verify({banner, phase, startup}) {
    const receipt = {scope:'actual ComfyUI frontend; registration/serialization only',gpu:'not_performed',
      queued:false,phase,startup,native_loads:[]};
    let initialLanguage;
    let languageTouched = false;
    try {
      startup.push({event:'verification_dispatch',...readiness()});
      check(['roundtrip','persist','display'].includes(phase),'Unknown verification phase');
      check(app.isGraphReady === true,'Native graph initialization has not completed');
      check(app.canvas?.ds,'Native canvas is unavailable');
      initialLanguage = app.ui.settings.getSettingValue(SETTING_ID) ?? 'en';
      receipt.initial_language = initialLanguage;
      receipt.initial_persisted_language = await readPersistedLanguage(api);
      check(initialLanguage === effectiveLanguage(receipt.initial_persisted_language) && getLanguage() === initialLanguage,
        'Initial displayed and persisted KVD languages do not agree');
      const response = await fetch(new URL('./examples/foundation_project.json', import.meta.url));
      check(response.ok,'Fixture unavailable');
      const fixture = await response.json();
      const saved = sessionStorage.getItem('KVD.FoundationVerification.saved');
      const selected = withoutVerificationMarker(phase === 'persist' && saved ? JSON.parse(saved) : fixture);
      checkStableWorkflow(semanticWorkflow(selected),semanticWorkflow(fixture),
        'Saved verification fixture has different Project types, ports, values or links',receipt);
      const expectedTitles = new Map(selected.nodes.filter(n=>n.title).map(n=>[n.id,n.title]));
      const checkTitles = () => {
        for (const [id,title] of expectedTitles)
          check(app.graph.getNodeById(id)?.title === title,'Custom title changed during native loading or language change');
      };
      const checkLoadedGraph = () => {
        check(app.isGraphReady === true,'Native graph initialization has not completed');
        check(app.canvas?.ds,'Native canvas is unavailable');
        check(app.graph._nodes.length === 4,'Expected four actual Project nodes');
        check(app.graph._nodes.every(n=>n._kvdPanel),'KVD presentation did not initialize after loading');
        check(Object.keys(app.graph.links).length === 2,'Expected two native graph links');
      };
      const load = async data => {
        check(!activeLoad,'Another native workflow load is being observed');
        const expected = semanticWorkflow(data);
        const trace = {load_id:crypto.randomUUID(),hooks:[],ready_before:readiness(),deadline_ms:FAILURE_DEADLINE_MS};
        // Native loading clones its argument, so an object identity cannot bind
        // its callbacks. Mark only this synthetic fixture's owned metadata with
        // a fresh request ID; remove it before saving verified graph evidence.
        const requested = withoutVerificationMarker(data);
        requested.extra = {...requested.extra,kvd:{...requested.extra?.kvd,verification_load_id:trace.load_id}};
        receipt.native_loads.push(trace);
        const observation = {trace,expected,expired:false};
        activeLoad = observation;
        const cleanupOwnMarker = () => {
          if (requested.extra.kvd.verification_load_id === trace.load_id)
            delete requested.extra.kvd.verification_load_id;
          try {
            if (app.isGraphReady !== true) return 'unavailable';
            const kvd = app.graph.extra?.kvd;
            if (!kvd || !Object.hasOwn(kvd,'verification_load_id')) return 'absent';
            if (kvd.verification_load_id !== trace.load_id) return 'different_request_preserved';
            delete kvd.verification_load_id;
            return Object.hasOwn(kvd,'verification_load_id') ? 'unavailable' : 'removed';
          } catch { return 'unavailable'; }
        };
        const describeReturn = value => ({return_type:typeof value,return_value:value === undefined ? 'undefined' :
          typeof value === 'number' && !Number.isFinite(value) ? String(value) :
          value === null || ['boolean','number','string'].includes(typeof value) ? value : '[nonprimitive]'});
        const recordLateSettlement = settlement => {
          const late = {load_id:trace.load_id,accepted:false,...settlement,
            marker_cleanup:cleanupOwnMarker(),ready_after:readiness()};
          trace.late_settlement = late;
          console.info('[KVD verification late load]',JSON.stringify(late));
        };
        try {
          let completed;
          try {
            const native = Promise.resolve(app.loadGraphData(requested,true,true,null,{skipAssetScans:true}));
            const observed = native.then(value=>{
              if (observation.expired) recordLateSettlement({state:'fulfilled',...describeReturn(value)});
              return value;
            },error=>{
              if (!observation.expired) throw error;
              recordLateSettlement({state:'rejected',error:String(error?.message ?? error),
                error_stack:typeof error?.stack === 'string' ? error.stack : null});
              // The failed run already settled; handle a late rejection without reviving it.
            });
            completed = await beforeFailureDeadline(observed,'Native workflow load exceeded its failure deadline',()=>{
              observation.expired = true;
              trace.timed_out = true;
              trace.return_state = 'pending';
            });
            trace.return_state = 'fulfilled';
            Object.assign(trace,describeReturn(completed));
          } catch (error) {
            if (!trace.timed_out) { trace.rejected = true; trace.return_state = 'rejected'; }
            trace.error = String(error?.message ?? error);
            trace.error_stack = typeof error?.stack === 'string' ? error.stack : null;
            throw error;
          }
          // A fulfilled void result alone is insufficient: this particular call
          // must complete the source-supported lifecycle and full graph assertions.
          check(completed === true || completed === undefined,'Native workflow load did not complete');
          check(JSON.stringify(trace.hooks) === JSON.stringify(loadHooks),
            'Native workflow load completion hooks are missing, duplicated or out of order');
          check(trace.requested_graph_matched === true,'Native workflow load configured different fixture data');
          check(trace.configured_graph_matched === true && trace.completed_graph_matched === true &&
            app.graph.extra?.kvd?.verification_load_id === trace.load_id,
            'Native workflow load completion belongs to a different request');
          checkLoadedGraph();
          checkStableWorkflow(semanticWorkflow(app.graph.serialize()),expected,
            'Fixture data changed during native loading',receipt,trace.load_id);
          trace.completion = completed === true ? 'native_return_and_lifecycle' : 'native_lifecycle_and_graph';
        } catch (error) {
          observation.expired = true;
          trace.acceptance_invalidated = true;
          throw error;
        } finally {
          trace.ready_after = readiness();
          if (activeLoad === observation) activeLoad = undefined;
          trace.marker_cleanup = cleanupOwnMarker();
          if (trace.completion && !['removed','absent'].includes(trace.marker_cleanup)) {
            observation.expired = true;
            trace.acceptance_invalidated = true;
            throw new Error('Native workflow load marker cleanup could not be verified');
          }
        }
      };
      await load(selected);
      checkTitles();
      const before = semanticWorkflow(app.graph.serialize());
      checkStableWorkflow(before,semanticWorkflow(selected),'Fixture data changed during native loading',
        receipt,receipt.native_loads.at(-1)?.load_id);
      if (phase === 'roundtrip') {
        // Exercise a custom title without changing the committed fixture or semantic keys.
        const title = 'KVD check · custom / Сцена';
        app.graph.getNodeById(2).title = title;
        expectedTitles.set(2,title);
        languageTouched = true;
        await persistLanguage(app.ui.settings,api,'en'); setLanguage('en');
        check(getLanguage() === 'en','English setting did not apply');
        checkTitles();
        await persistLanguage(app.ui.settings,api,'ru'); setLanguage('ru');
        check(getLanguage() === 'ru','Russian setting did not apply');
        checkTitles();
        const serialized = app.graph.serialize();
        checkStableWorkflow(semanticWorkflow(serialized),before,'Language changed keys, values or connections',
          receipt,receipt.native_loads.at(-1)?.load_id);
        await load(serialized);
        checkStableWorkflow(semanticWorkflow(app.graph.serialize()),before,'Native save/configure roundtrip changed data',
          receipt,receipt.native_loads.at(-1)?.load_id);
        checkTitles();
      } else if (phase === 'persist') {
        check(saved && initialLanguage === 'ru' && getLanguage() === 'ru','Russian did not persist over page reload');
        checkStableWorkflow(semanticWorkflow(app.graph.serialize()),semanticWorkflow(JSON.parse(saved)),
          'Page reload changed saved workflow',receipt,receipt.native_loads.at(-1)?.load_id);
      }
      receipt.persisted_language = await readPersistedLanguage(api);
      receipt.current_language = getLanguage();
      receipt.displayed_language = getLanguage();
      check(effectiveLanguage(receipt.persisted_language) === receipt.displayed_language,
        'Final displayed and persisted KVD languages do not agree');
      checkLoadedGraph();
      checkTitles();
      const actual = withoutVerificationMarker(app.graph.serialize());
      checkStableWorkflow(semanticWorkflow(actual),before,'Final graph keys, values or connections changed',
        receipt,receipt.native_loads.at(-1)?.load_id);
      const input = app.graph.getNodeById(1).widgets.find(w=>w.name === 'project_json').value;
      check(input.includes('Сцена') && input.includes('18446744073709551615'),'Unicode or seed value lost');
      receipt.nodes = actual.nodes.map(n=>n.type); receipt.links = actual.links.length;
      if (phase === 'roundtrip') {
        check(receipt.persisted_language === 'ru','Russian persistence could not be verified');
        receipt.language_roundtrip = 'passed'; receipt.native_serialization = 'passed';
      } else if (phase === 'persist') {
        check(receipt.persisted_language === 'ru','Russian persistence could not be verified');
        receipt.page_reload_persistence = 'passed';
      }
      receipt.custom_titles = expectedTitles.size ? 'passed' : 'not_checked';
      // Center only this explicitly loaded synthetic fixture, not a human graph.
      app.canvas.ds.scale = 0.75;
      app.canvas.ds.offset = [30,60];
      app.canvas.setDirty(true,true);
      if (phase === 'roundtrip' || phase === 'persist')
        sessionStorage.setItem('KVD.FoundationVerification.saved',JSON.stringify(actual));
      // Only this opted-in, successfully checked synthetic fixture is exposed.
      // AO console capture can retain its actual native serialization privately.
      receipt.serialized_workflow = actual;
      receipt.status = 'PASS';
      banner.textContent = 'KVD foundation: PASS · ' + receipt.phase + ' · ' + receipt.current_language.toUpperCase() + ' · 4 nodes / 2 links · no queue';
      console.info('[KVD verification]',JSON.stringify(receipt));
    } catch (error) {
      receipt.status = 'FAIL'; receipt.reason = String(error?.message ?? error);
      receipt.error_stack = typeof error?.stack === 'string' ? error.stack : null;
      if (languageTouched) {
        try {
          const restored = await beforeFailureDeadline(persistLanguage(app.ui.settings,api,initialLanguage),
            'Original KVD preference restoration exceeded its failure deadline');
          setLanguage(initialLanguage);
          receipt.original_language_restored = true;
          receipt.restored_displayed_language = getLanguage();
          receipt.restored_persisted_language = restored;
        } catch {
          receipt.original_language_restored = false;
          receipt.reason += '; original KVD preference restoration failed or could not be verified';
        }
      }
      receipt.displayed_language = getLanguage();
      try { receipt.persisted_language = await beforeFailureDeadline(readPersistedLanguage(api),
        'Final KVD preference readback exceeded its failure deadline'); }
      catch { receipt.persisted_language = 'unverified'; }
      banner.textContent = 'KVD foundation: FAIL · ' + receipt.reason;
      console.error('[KVD verification]',JSON.stringify(receipt));
    }
}
