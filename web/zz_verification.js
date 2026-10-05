// Opt-in frontend conformance tool. Inert on normal pages. Never queues or executes nodes.
import { app } from '../../scripts/app.js';
import { getLanguage, setLanguage } from './common/presentation.js';

function semanticWorkflow(graph) {
  return JSON.stringify({nodes: graph.nodes.map(n => ({id:n.id,type:n.type,mode:n.mode,
    widgets_values:n.widgets_values || [],
    inputs:(n.inputs || []).map(({name,type,link}) => ({name,type,link})),
    outputs:(n.outputs || []).map(({name,type,links}) => ({name,type,links}))})), links:graph.links});
}
function check(value, message) { if (!value) throw new Error(message); }
app.registerExtension({
  name:'KVD.FoundationVerification',
  async setup() {
    const query = new URLSearchParams(location.search);
    if (query.get('kvd-check') !== 'foundation') return;
    const banner = document.createElement('div');
    banner.id = 'kvd-verification'; banner.setAttribute('role','status');
    Object.assign(banner.style,{position:'fixed',top:'58px',left:'70px',zIndex:'1000',
      background:'#17262e',color:'#e4edf1',padding:'10px 14px',border:'1px solid #72c7c5',borderRadius:'8px',maxWidth:'800px'});
    document.body.append(banner);
    const receipt = {scope:'actual ComfyUI frontend; registration/serialization only',gpu:'not_performed',
      queued:false,phase:query.get('phase') || 'roundtrip'};
    try {
      const response = await fetch(new URL('./examples/foundation_project.json', import.meta.url));
      check(response.ok,'Fixture unavailable');
      const fixture = await response.json();
      const phase = receipt.phase;
      const saved = sessionStorage.getItem('KVD.FoundationVerification.saved');
      const initialLanguage = app.ui.settings.getSettingValue('KVD.Language','en');
      receipt.initial_language = initialLanguage;
      await app.loadGraphData(phase === 'persist' && saved ? JSON.parse(saved) : fixture);
      const before = semanticWorkflow(app.graph.serialize());
      check(app.graph._nodes.length === 4,'Expected four actual Project nodes');
      check(app.graph._nodes.every(n=>n._kvdPanel),'KVD presentation did not initialize');
      check(Object.keys(app.graph.links).length === 2,'Expected two native graph links');
      if (phase === 'roundtrip') {
        await app.ui.settings.setSettingValue('KVD.Language','en'); setLanguage('en');
        check(getLanguage() === 'en','English setting did not apply');
        await app.ui.settings.setSettingValue('KVD.Language','ru'); setLanguage('ru');
        check(getLanguage() === 'ru','Russian setting did not apply');
        const serialized = app.graph.serialize();
        check(semanticWorkflow(serialized) === before,'Language changed keys, values or connections');
        sessionStorage.setItem('KVD.FoundationVerification.saved',JSON.stringify(serialized));
        await app.loadGraphData(serialized);
        check(semanticWorkflow(app.graph.serialize()) === before,'Native save/configure roundtrip changed data');
        receipt.language_roundtrip = 'passed'; receipt.native_serialization = 'passed';
      } else if (phase === 'persist') {
        check(saved && initialLanguage === 'ru' && getLanguage() === 'ru','Russian did not persist over page reload');
        check(semanticWorkflow(app.graph.serialize()) === semanticWorkflow(JSON.parse(saved)),'Page reload changed saved workflow');
        receipt.page_reload_persistence = 'passed';
      }
      const actual = app.graph.serialize();
      const input = app.graph.getNodeById(1).widgets.find(w=>w.name === 'project_json').value;
      check(input.includes('Сцена') && input.includes('18446744073709551615'),'Unicode or seed value lost');
      receipt.nodes = actual.nodes.map(n=>n.type); receipt.links = actual.links.length;
      receipt.current_language = getLanguage(); receipt.status = 'PASS';
      // Center only this explicitly loaded synthetic fixture, not a human graph.
      app.canvas.ds.scale = 0.75;
      app.canvas.ds.offset = [30,60];
      app.canvas.setDirty(true,true);
      banner.textContent = 'KVD foundation: PASS · ' + receipt.phase + ' · EN/RU · 4 nodes / 2 links · no queue';
      console.info('[KVD verification]',JSON.stringify(receipt));
    } catch (error) {
      receipt.status = 'FAIL'; receipt.reason = String(error.message);
      banner.textContent = 'KVD foundation: FAIL · ' + error.message;
      console.error('[KVD verification]',JSON.stringify(receipt));
    }
  },
});
