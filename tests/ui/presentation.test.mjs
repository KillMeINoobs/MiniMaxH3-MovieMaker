import assert from 'node:assert/strict';
import { pathToFileURL } from 'node:url';
const ui = await import(pathToFileURL(process.cwd() + '/web/common/presentation.js'));
assert.equal(ui.getLanguage(), 'en');
ui.registerPresentation('KVD_Test', {
  en: { title: 'Project', help: 'Load a project', fields: { project_json: 'Project JSON', project: 'Project' } },
  ru: { title: 'Проект', help: 'Загрузить проект', fields: { project_json: 'JSON проекта', project: 'Проект' } },
});
const node = { type: 'KVD_Test', title: 'Project',
  inputs: [{ name: 'project', type: 'KVD_PROJECT', link: 42 }],
  outputs: [{ name: 'project', type: 'KVD_PROJECT', links: [43] }],
  widgets: [{ name: 'project_json', value: 'Папка с пробелами', options: {} }],
};
const semantics = n => JSON.stringify({inputs:n.inputs.map(({name,type,link})=>({name,type,link})),
  outputs:n.outputs.map(({name,type,links})=>({name,type,links})),widgets:n.widgets.map(({name,value})=>({name,value}))});
const before = semantics(node);
ui.applyPresentation(node);
assert.equal(node.widgets[0].label, 'Project JSON');
ui.setLanguage('ru');
ui.applyPresentation(node);
assert.equal(node.title, 'Проект');
assert.equal(node.widgets[0].label, 'JSON проекта');
assert.equal(semantics(node), before);
const reloaded = JSON.parse(JSON.stringify(node));
ui.setLanguage('en');
ui.applyPresentation(reloaded);
assert.equal(reloaded.title, 'Project');
assert.equal(semantics(reloaded), before);
node.title = 'My personal title';
ui.applyPresentation(node);
assert.equal(node.title, 'My personal title');
const foreign = {type:'OtherPack',title:'Unchanged',widgets:[{name:'x',value:9}]};
const foreignBefore = JSON.stringify(foreign);
ui.applyPresentation(foreign);
assert.equal(JSON.stringify(foreign), foreignBefore);
ui.setLanguage('ru');
for(const code of ui.ERROR_CODES) assert.ok(ui.errorText(code).length > 10);
assert.match(ui.errorText('SOURCE_MISSING'), /файл/i);
assert.throws(()=>ui.setLanguage('fr'));
console.log('PASS: EN default; EN/RU preserve keys, links, values, custom titles; foreign packs untouched; all error codes translated.');
