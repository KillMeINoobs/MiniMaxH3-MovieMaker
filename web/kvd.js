import { app } from '../../scripts/app.js';
import { api } from '../../scripts/api.js';
import { registerPresentation, presentationFor, applyPresentation, getLanguage, setLanguage,
         onLanguageChange, statusText, errorText } from './common/presentation.js';

const SETTING_ID = 'KVD.Language';
const fields = {
  en: {project:'Project',project_json:'Project JSON',validation_report:'Validation report',
       project_root:'Project folder',project_file:'Relative filename',overwrite:'Overwrite existing file',saved_file:'Saved filename'},
  ru: {project:'Проект',project_json:'JSON проекта',validation_report:'Отчёт проверки',
       project_root:'Папка проекта',project_file:'Относительное имя',overwrite:'Перезаписать файл',saved_file:'Имя сохранённого файла'},
};
const tooltips = {
  en: {project_json:'A portable kmin.project 2.x record. Saved with this workflow.',
       project_root:'Your local project folder. Keep workflow paths private when sharing.',
       project_file:'A path relative to the selected folder; Unicode and spaces are supported.',
       overwrite:'Explicitly replace only this project at a current revision.',project:'A validated portable Project.'},
  ru: {project_json:'Переносимая запись kmin.project 2.x. Сохраняется с workflow.',
       project_root:'Ваша локальная папка проекта. Не публикуйте личные пути в workflow.',
       project_file:'Путь относительно выбранной папки; поддерживаются Unicode и пробелы.',
       overwrite:'Явно заменить только этот проект с актуальной ревизией.',project:'Проверенный переносимый проект.'},
};
const text = {
  KVD_ProjectJSON: {
    en: {title:'KVD Project · JSON',help:'Paste a portable project record. Check frames, settings and references without opening media.'},
    ru: {title:'KVD Проект · JSON',help:'Вставьте переносимую запись проекта. Проверка кадров, настроек и ссылок без открытия медиа.'}},
  KVD_LoadProject: {
    en: {title:'KVD Load Project',help:'Select a local folder and a relative project filename. Missing files are reported explicitly.'},
    ru: {title:'KVD Загрузить проект',help:'Укажите локальную папку и относительное имя проекта. Отсутствующие файлы дают явную ошибку.'}},
  KVD_SaveProject: {
    en: {title:'KVD Save Project',help:'Save locally and atomically. Existing files stay intact unless you select overwrite.'},
    ru: {title:'KVD Сохранить проект',help:'Атомарное локальное сохранение. Существующие файлы сохраняются, пока не выбрана перезапись.'}},
  KVD_ValidateProject: {
    en: {title:'KVD Validate Project',help:'Check exact timeline coverage and inherited scene settings. Media processing and generation are separate steps.'},
    ru: {title:'KVD Проверить проект',help:'Проверка покрытия таймлайна и наследования настроек сцен. Обработка медиа и генерация — отдельные шаги.'}},
};
for (const [classId, pair] of Object.entries(text)) {
  for (const locale of ['en','ru']) Object.assign(pair[locale], {fields:fields[locale],tooltips:tooltips[locale]});
  registerPresentation(classId, pair);
}

function refreshNode(node) {
  const presentation = applyPresentation(node);
  if (!presentation || !node._kvdPanel) return;
  const {root, heading, help, selector, status} = node._kvdPanel;
  root.lang = getLanguage();
  heading.textContent = getLanguage() === 'ru' ? 'Переносимый проект' : 'Portable project';
  help.textContent = presentation.help;
  selector.value = getLanguage();
  status.textContent = statusText(node._kvdStatus || 'STRUCTURE_ONLY');
}

async function changeLanguage(value) {
  try {
    await app.ui.settings.setSettingValue(SETTING_ID, value);
    setLanguage(value);
  } catch (error) {
    for (const node of app.graph?._nodes || []) if (node._kvdPanel) {
      node._kvdStatus = 'SETTINGS_ERROR';
      refreshNode(node);
    }
    console.error('[KVD] Interface preference could not be saved');
  }
}

function installPanel(node) {
  if (node._kvdPanel) return;
  const root = document.createElement('section');
  root.className = 'kvd-panel';
  const header = document.createElement('div'); header.className = 'kvd-panel__header';
  const heading = document.createElement('strong');
  const selector = document.createElement('select');
  selector.className = 'kvd-language';
  selector.setAttribute('aria-label', 'KVD · Interface language / Язык интерфейса');
  for (const [value, label] of [['en','EN · English'],['ru','RU · Русский']]) {
    const option = document.createElement('option'); option.value = value; option.textContent = label; selector.append(option);
  }
  selector.addEventListener('change', () => changeLanguage(selector.value));
  header.append(heading, selector);
  const badge = document.createElement('div'); badge.className = 'kvd-panel__badge'; badge.textContent = '24 FPS · 2.0';
  const help = document.createElement('p'); help.className = 'kvd-panel__help';
  const status = document.createElement('p'); status.className = 'kvd-panel__status';
  root.append(header, badge, help, status);
  const widget = node.addDOMWidget('kvd_presentation', 'KVD_PRESENTATION', root, {serialize:false,hideOnZoom:false});
  widget.serialize = false;
  widget.serializeValue = () => undefined;
  widget.computeSize = width => [width, 150];
  node._kvdPanel = {root, heading, help, selector, status};
  node.color = '#253947'; node.bgcolor = '#17262e';
  const executed = node.onExecuted;
  node.onExecuted = function(message) {
    const result = executed?.call(this, message);
    this._kvdStatus = message?.kvd_report?.[0]?.code || 'STRUCTURE_ONLY';
    refreshNode(this);
    return result;
  };
  refreshNode(node);
}

app.registerExtension({
  name: 'KVD.Foundation',
  settings: [{id:SETTING_ID,category:['KVD','Interface','Language'],name:'Interface language / Язык интерфейса',
    type:'combo',options:[{text:'English',value:'en'},{text:'Русский',value:'ru'}],defaultValue:'en',
    tooltip:'Language for KVD nodes only. Port keys and saved project data stay stable.',
    onChange(value) { setLanguage(value === 'ru' ? 'ru' : 'en'); }}],
  setup() {
    const link = document.createElement('link'); link.rel = 'stylesheet'; link.href = new URL('./theme.css', import.meta.url).href;
    document.head.append(link);
    setLanguage(app.ui.settings.getSettingValue(SETTING_ID, 'en') === 'ru' ? 'ru' : 'en');
    onLanguageChange(() => {
      for (const node of app.graph?._nodes || []) refreshNode(node);
    });
    api.addEventListener('execution_error', event => {
      const detail = event.detail;
      const node = app.graph?.getNodeById(detail?.node_id);
      if (!node?._kvdPanel) return;
      node._kvdStatus = String(detail.exception_message || '').match(/\b([A-Z][A-Z_]+):/)?.[1] || 'INVALID_RECORD';
      refreshNode(node);
    });
  },
  nodeCreated(node) {
    if (!presentationFor(node)) return;
    installPanel(node);
    node.size[0] = Math.max(node.size[0], node.comfyClass === 'KVD_ProjectJSON' ? 440 : 370);
  },
  loadedGraphNode(node) { refreshNode(node); },
  afterConfigureGraph() {
    for (const node of app.graph?._nodes || []) refreshNode(node);
  },
});
