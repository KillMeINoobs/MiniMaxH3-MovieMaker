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
let pendingCheck;
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
    pendingCheck = {banner, phase:query.get('phase') || 'roundtrip'};
  },
  afterLoadGraph() {
    if (!pendingCheck) return;
    const requested = pendingCheck;
    pendingCheck = undefined;
    // This native lifecycle hook provides readiness. Dispatch after it returns
    // to avoid recursively awaiting loadGraphData inside its own load hook.
    setTimeout(() => verify(requested), 0);
  },
});

async function verify({banner, phase}) {
    const receipt = {scope:'actual ComfyUI frontend; registration/serialization only',gpu:'not_performed',
      queued:false,phase};
    let initialLanguage;
    let languageTouched = false;
    try {
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
      const selected = phase === 'persist' && saved ? JSON.parse(saved) : fixture;
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
        const completed = await app.loadGraphData(data,true,true,null,{skipAssetScans:true});
        check(completed === true,'Native workflow load did not complete');
        checkLoadedGraph();
      };
      await load(selected);
      checkTitles();
      const before = semanticWorkflow(app.graph.serialize());
      check(before === semanticWorkflow(selected),'Fixture data changed during native loading');
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
        check(semanticWorkflow(serialized) === before,'Language changed keys, values or connections');
        await load(serialized);
        check(semanticWorkflow(app.graph.serialize()) === before,'Native save/configure roundtrip changed data');
        checkTitles();
      } else if (phase === 'persist') {
        check(saved && initialLanguage === 'ru' && getLanguage() === 'ru','Russian did not persist over page reload');
        check(semanticWorkflow(app.graph.serialize()) === semanticWorkflow(JSON.parse(saved)),'Page reload changed saved workflow');
      }
      receipt.persisted_language = await readPersistedLanguage(api);
      receipt.current_language = getLanguage();
      receipt.displayed_language = getLanguage();
      check(effectiveLanguage(receipt.persisted_language) === receipt.displayed_language,
        'Final displayed and persisted KVD languages do not agree');
      checkLoadedGraph();
      checkTitles();
      const actual = app.graph.serialize();
      check(semanticWorkflow(actual) === before,'Final graph keys, values or connections changed');
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
      if (phase === 'roundtrip')
        sessionStorage.setItem('KVD.FoundationVerification.saved',JSON.stringify(actual));
      receipt.status = 'PASS';
      banner.textContent = 'KVD foundation: PASS · ' + receipt.phase + ' · ' + receipt.current_language.toUpperCase() + ' · 4 nodes / 2 links · no queue';
      console.info('[KVD verification]',JSON.stringify(receipt));
    } catch (error) {
      receipt.status = 'FAIL'; receipt.reason = String(error.message);
      if (languageTouched) {
        try {
          const restored = await persistLanguage(app.ui.settings,api,initialLanguage);
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
      try { receipt.persisted_language = await readPersistedLanguage(api); }
      catch { receipt.persisted_language = 'unverified'; }
      banner.textContent = 'KVD foundation: FAIL · ' + error.message;
      console.error('[KVD verification]',JSON.stringify(receipt));
    }
}
