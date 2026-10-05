// Pure presentation state. Class IDs, socket/widget names and values stay stable.
const presentations = new Map();
const subscribers = new Set();
let language = 'en';

export function getLanguage() { return language; }
export function setLanguage(value) {
  if (!['en', 'ru'].includes(value)) throw new Error('Unsupported KVD language');
  language = value;
  for (const listener of subscribers) listener(value);
}
export function onLanguageChange(listener) {
  subscribers.add(listener);
  return () => subscribers.delete(listener);
}
export function registerPresentation(classId, translations) {
  if (!classId.startsWith('KVD_') || !translations.en || !translations.ru)
    throw new Error('KVD presentation requires stable class ID and EN/RU text');
  presentations.set(classId, translations);
}
export function presentationFor(node) {
  return presentations.get(node.comfyClass || node.type)?.[language];
}
export function applyPresentation(node) {
  const translations = presentations.get(node.comfyClass || node.type);
  if (!translations) return;
  const current = translations[language];
  const defaultTitles = [translations.en.title, translations.ru.title];
  if (!node.title || defaultTitles.includes(node.title)) node.title = current.title;
  for (const slot of [...(node.inputs || []), ...(node.outputs || []), ...(node.widgets || [])]) {
    if (current.fields?.[slot.name]) {
      slot.label = current.fields[slot.name];
      slot.localized_name = current.fields[slot.name];
    }
    if (current.tooltips?.[slot.name]) {
      slot.tooltip = current.tooltips[slot.name];
      if (slot.options) slot.options.tooltip = current.tooltips[slot.name];
    }
    if (slot.name === 'overwrite' && slot.options) {
      slot.options.on = language === 'ru' ? 'Да' : 'Yes';
      slot.options.off = language === 'ru' ? 'Нет' : 'No';
    }
  }
  node.setDirtyCanvas?.(true, true);
  return current;
}

const errors = {
  INVALID_RECORD: ['Check the required fields, types and permitted values.', 'Проверьте обязательные поля, типы и допустимые значения.'],
  INVALID_JSON: ['Use valid UTF-8 JSON without duplicate keys or nonfinite numbers.', 'Нужен корректный JSON UTF-8 без повторных ключей и бесконечных чисел.'],
  INVALID_LOCATOR: ['Select a project folder and use a relative path without traversal.', 'Выберите папку проекта и относительный путь без переходов за её границы.'],
  INVALID_INTERVAL: ['Frame ranges use integer [start, end) with start smaller than end.', 'Диапазоны кадров: целые [начало, конец), начало меньше конца.'],
  INVALID_RATIONAL: ['Use a reduced fraction with a positive denominator.', 'Используйте сокращённую дробь с положительным знаменателем.'],
  INVALID_SEED: ['Seed must be a decimal string from 0 to 18446744073709551615.', 'Seed — десятичная строка от 0 до 18446744073709551615.'],
  INVALID_EVIDENCE: ['A verified result needs matching real validation receipts.', 'Подтверждённому результату нужны соответствующие реальные свидетельства проверки.'],
  UNSUPPORTED_SCHEMA_MAJOR: ['Keep the original file; this schema major needs explicit migration.', 'Сохраните исходный файл: этой версии схемы нужна явная миграция.'],
  UNSUPPORTED_REQUIRED_FEATURE: ['This project requires a feature the installed package does not support.', 'Проект требует функцию, которую установленный пакет не поддерживает.'],
  UNSUPPORTED_CAPABILITY: ['This runtime operation is not implemented or enabled by its profile.', 'Эта операция ещё не реализована или не разрешена её профилем.'],
  DUPLICATE_ID: ['Stable record or node IDs must be unique within their kind.', 'Постоянные идентификаторы записей и узлов должны быть уникальны в своём типе.'],
  DANGLING_REFERENCE: ['A referenced record is missing or has the wrong role.', 'Указанная запись отсутствует или имеет неподходящую роль.'],
  COVERAGE_MISMATCH: ['Useful frame ranges must cover the intended interval exactly once.', 'Полезные диапазоны должны покрывать нужный интервал ровно один раз.'],
  STALE_DEPENDENCY: ['An edited dependency is stale. Update its revision and revalidate.', 'Изменённая зависимость устарела. Обновите ревизию и повторите проверку.'],
  SOURCE_MISSING: ['The selected project file or a listed asset is missing.', 'Выбранный файл проекта или указанный ресурс отсутствует.'],
  SOURCE_CHANGED: ['The file content differs from the recorded fingerprint.', 'Содержимое файла отличается от записанного отпечатка.'],
  AMBIGUOUS_MEDIA_TIMING: ['The source presentation span needs an explicit timing policy.', 'Для временного диапазона исходника требуется явное правило обработки.'],
  TARGET_EXISTS: ['Choose a new filename or explicitly enable overwrite.', 'Выберите новое имя файла или явно разрешите перезапись.'],
  PROJECT_IO_ERROR: ['Check folder access and support for atomic local file writes.', 'Проверьте доступ к папке и поддержку атомарной записи локальных файлов.'],
  PROJECT_BUSY: ['Another save is publishing this project. Retry after it completes.', 'Другой процесс сохраняет этот проект. Повторите после завершения.'],
  EXTENSION_IMPORT_ERROR: ['An owned extension could not load. Check its installation and optional imports.', 'Не удалось загрузить расширение проекта. Проверьте установку и необязательные импорты.'],
  MIGRATION_UNSUPPORTED: ['This input needs a separate migration profile; the original stays intact.', 'Этому файлу нужен отдельный профиль миграции; исходник сохранён.'],
  RESOURCE_LIMIT: ['The requested data exceeds the declared resource limit.', 'Объём запрошенных данных превышает объявленное ограничение.'],
  FRAME_COUNT_MISMATCH: ['Useful, padding and context frame counts do not agree.', 'Числа полезных, дополняющих и контекстных кадров не согласованы.'],
  AUDIO_SYNC_MISMATCH: ['Audio samples must match absolute frame boundaries.', 'Число аудиосэмплов должно соответствовать абсолютным границам кадров.'],
  UNSUPPORTED_EXPORT_DIMENSIONS: ['Check the shared canvas grid and declared output dimensions.', 'Проверьте сетку общего холста и объявленные размеры результата.'],
  MODEL_INCOMPATIBLE: ['The selected component profile is incompatible.', 'Выбранный профиль компонентов несовместим.'],
  PARTIAL_RESULT: ['An unfinished or unvalidated result cannot count as completed output.', 'Незавершённый или непроверенный результат не считается готовым.'],
  CANCELLED: ['The owned operation was cancelled; completed receipts remain available.', 'Операция отменена; свидетельства завершённых результатов сохранены.'],
  ANALYSIS_UNAVAILABLE: ['Scene analysis is unavailable; authored prompts remain editable.', 'Анализ сцены недоступен; авторские промпты доступны для редактирования.'],
  PROMPT_INVALID: ['Check prompt blocks, accepted text and their content hashes.', 'Проверьте блоки промпта, принятый текст и его хеши.'],
  REFERENCE_UNBOUND: ['Approve and bind appearance references explicitly for this scene.', 'Явно подтвердите и привяжите референсы внешности к этой сцене.'],
  REFERENCE_CONFLICT: ['Reference identity, content, labels and sockets must agree.', 'Идентичность, содержимое, метки и порты референсов должны согласовываться.'],
  CONTINUATION_INCOMPATIBLE: ['Continuation must use a verified compatible state inside one shot.', 'Продолжению нужно проверенное совместимое состояние внутри одного плана.'],
  CONTINUATION_TAIL_UNMAPPED: ['Map the last useful tail explicitly before using continuation.', 'Явно сопоставьте последний полезный хвост перед продолжением.'],
  SETTINGS_ERROR: ['The interface preference could not be saved. Try again.', 'Не удалось сохранить настройку языка интерфейса. Повторите попытку.'],
};
export const ERROR_CODES = Object.freeze(Object.keys(errors));
export function errorText(code) {
  const text = errors[code] || ['Check the validation report for details.', 'Подробности указаны в отчёте проверки.'];
  return text[language === 'ru' ? 1 : 0];
}
export function statusText(code) {
  const table = {
    SETTINGS_SAVING: ['Saving interface preference…', 'Сохранение настройки языка…'],
    STRUCTURE_ONLY: ['Structure checks · media is not opened', 'Проверка структуры · медиа не открывается'],
    STRUCTURE_VALID: ['Project structure validated · assets not checked', 'Структура проекта проверена · ресурсы не проверены'],
    PROJECT_SAVED: ['Project saved locally', 'Проект сохранён локально'],
  };
  return table[code]?.[language === 'ru' ? 1 : 0] || errorText(code);
}

export function languageStateText({displayed = language,persisted,restored}) {
  const names = {en:'English',ru:'Русский'};
  const saved = persisted === null ? (language === 'ru' ? 'По умолчанию · English' : 'Default · English')
    : names[persisted] || (language === 'ru' ? 'Не подтверждено' : 'Unverified');
  let text = language === 'ru' ? `Сейчас: ${names[displayed]}. Сохранено: ${saved}.`
    : `Current: ${names[displayed]}. Saved: ${saved}.`;
  if (restored === true) text += language === 'ru' ? ' Прежняя настройка подтверждена.' : 'Previous preference confirmed.';
  if (restored === false) text += language === 'ru' ? ' Восстановление не подтверждено.' : 'Restoration unverified.';
  return text;
}
