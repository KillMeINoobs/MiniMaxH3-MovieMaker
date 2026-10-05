import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import vm from 'node:vm';
import {pathToFileURL} from 'node:url';
import test from 'node:test';

test('owned media extension preserves callbacks/data and follows shared language without persistence/queue calls', async()=>{
  let extension; const nodes = [];
  const app = {registerExtension:value=>{extension=value;},graph:{_nodes:nodes}};
  const context = vm.createContext({URL, document:{
    head:{append(){}},createElement:()=>({setAttribute(){}})},
    fetch(){throw new Error('No network/queue operation is authorized by presentation');}});
  const host = new vm.SyntheticModule(['app'],function(){this.setExport('app',app);},{context});
  const files = ['web/media/media.js','web/media/presentation.js','web/common/presentation.js'];
  const modules = new Map();
  for(const file of files) modules.set(file,new vm.SourceTextModule(await readFile(file,'utf8'),{context,
    initializeImportMeta:meta=>{meta.url=pathToFileURL(process.cwd()+'/'+file).href;}}));
  const presentation = modules.get(files[2]);
  const owner = modules.get(files[0]);
  await owner.link(specifier=>{
    if(specifier.endsWith('/app.js')) return host;
    if(specifier.includes('common/presentation.js')) return presentation;
    assert.equal(specifier,'./presentation.js'); return modules.get(files[1]);
  });
  await owner.evaluate(); extension.setup();
  let executed=0; const widgets=[{name:'codec',value:'ffv1-nut'}];
  const node={comfyClass:'KVD_AssembleExport',size:[200,100],widgets,
    onExecuted(){executed++; return 'existing-callback';},
    addDOMWidget(name,type,element){const widget={name,type,value:element};widgets.push(widget);return widget;}};
  nodes.push(node); extension.nodeCreated(node);
  assert.equal(widgets[1].serialize,false); assert.equal(widgets[1].serializeValue(),undefined);
  assert.equal(node.onExecuted({kvd_report:[{video:{decoded_frames:24,fps:{num:24,den:1}},export_dimensions:[38,20]}]}),'existing-callback');
  assert.equal(executed,1); assert.match(node._kvdMediaSummary.textContent,/24.*frames.*24\/1 FPS.*38 × 20/);
  presentation.namespace.setLanguage('ru');
  assert.match(node._kvdMediaSummary.textContent,/кадров/); assert.equal(widgets[0].value,'ffv1-nut');
  extension.nodeCreated(node); assert.equal(widgets.length,2,'owned panel is installed once');
  const foreign={comfyClass:'Foreign',size:[100,100]};
  extension.nodeCreated(foreign); assert.deepEqual(foreign,{comfyClass:'Foreign',size:[100,100]});
  node.onExecuted({kvd_report:[{decoded_frames:6}]});
  assert.doesNotMatch(node._kvdMediaSummary.textContent,/24\/1/,'source-probe counts must not imply CFR24');
});
