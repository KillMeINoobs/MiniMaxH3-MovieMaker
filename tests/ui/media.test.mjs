import assert from 'node:assert/strict';
import {pathToFileURL} from 'node:url';
const ui = await import(pathToFileURL(process.cwd() + '/web/common/presentation.js'));
const media = await import(pathToFileURL(process.cwd() + '/web/media/presentation.js'));
assert.equal(ui.getLanguage(), 'en');
assert.equal(Object.keys(media.MEDIA_PRESENTATIONS).length, 8);
for (const [classId, pair] of Object.entries(media.MEDIA_PRESENTATIONS)) {
  assert.ok(pair.en.title && pair.ru.title && pair.en.help && pair.ru.help);
  const keys = Object.keys(pair.en.fields);
  assert.deepEqual(Object.keys(pair.ru.fields), keys);
  for (const key of keys) assert.ok(pair.en.tooltips[key] && pair.ru.tooltips[key]);
  const node = {comfyClass:classId, title:pair.en.title,
    inputs:[{name:'project',type:'KVD_PROJECT',link:73}],
    outputs:[{name:'prepared_media',type:'KVD_MEDIA',links:[74]}],
    widgets:keys.map(name=>({name,value:name==='source_file'?'Медиа с пробелами.nut':'preserve',options:{}}))};
  const semantics = n=>JSON.stringify({inputs:n.inputs.map(({name,type,link})=>({name,type,link})),
    outputs:n.outputs.map(({name,type,links})=>({name,type,links})),widgets:n.widgets.map(({name,value})=>({name,value}))});
  const before = semantics(node);
  ui.setLanguage('ru'); ui.applyPresentation(node);
  assert.equal(node.title, pair.ru.title);
  for (const widget of node.widgets) assert.equal(widget.label, pair.ru.fields[widget.name]);
  assert.equal(semantics(node), before);
  const loaded = JSON.parse(JSON.stringify(node));
  ui.setLanguage('en'); ui.applyPresentation(loaded);
  assert.equal(loaded.title, pair.en.title); assert.equal(semantics(loaded), before);
  loaded.title = 'My authored scene / Мой план';
  ui.setLanguage('ru'); ui.applyPresentation(loaded);
  assert.equal(loaded.title, 'My authored scene / Мой план');
}
const foreign = {type:'OtherPack',title:'Foreign',widgets:[{name:'project',value:1}]};
const before = JSON.stringify(foreign); ui.applyPresentation(foreign);
assert.equal(JSON.stringify(foreign),before);
assert.match(media.mediaStatus({native_frames:124}), /124/);
assert.match(media.mediaStatus({gpu:'not_performed'}), /CPU/);
console.log('PASS: eight owned EN/RU presentations; stable port/widget keys and values; custom titles and foreign nodes; synthetic host only.');
