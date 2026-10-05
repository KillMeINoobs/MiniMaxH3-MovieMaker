import {registerPresentation, getLanguage} from '../common/presentation.js';

// Text only. Serialized enums, sockets and widget .name values stay unchanged.
const entries = {
  project_root: ['Project folder','Папка проекта','Existing local folder explicitly selected by you.','Существующая локальная папка, которую вы явно выбрали.'],
  ffmpeg_path: ['FFmpeg executable','Исполняемый файл FFmpeg','Absolute path to an existing FFmpeg. No installation or download.','Абсолютный путь к существующему FFmpeg. Без установки и загрузки.'],
  ffprobe_path: ['ffprobe executable','Исполняемый файл ffprobe','Absolute path to an existing ffprobe from the same reviewed build.','Абсолютный путь к существующему ffprobe из той же проверенной сборки.'],
  disk_quota_mb: ['Disk budget · MiB','Лимит диска · МиБ','Per-operation output and temporary disk limit.','Лимит диска для результата и временных файлов операции.'],
  working_set_mb: ['RGB buffer budget · MiB','Лимит RGB-буферов · МиБ','Active Python frame buffers; external backend memory is reported separately.','Активные буферы кадров Python; память внешнего backend указана отдельно.'],
  source_file: ['Source filename','Имя исходника','Project-relative file path; Unicode and spaces work.','Путь к файлу относительно папки проекта; Unicode и пробелы поддерживаются.'],
  video_stream: ['Video stream index','Индекс видеопотока','Absolute stream index, not its video-only ordinal.','Абсолютный индекс потока, а не номер только среди видеопотоков.'],
  audio_stream: ['Audio stream index · −1 off','Индекс аудиопотока · −1 выкл.','−1 excludes audio; otherwise choose its absolute stream index.','−1 исключает звук; иначе выберите абсолютный индекс аудиопотока.'],
  endpoint_duration: ['Ambiguous EOF duration','Длительность при неясном EOF','Blank uses decoded last-frame duration. Missing duration requires explicit seconds, e.g. 1/24.','Пустое поле использует декодированную длительность последнего кадра. Если её нет, укажите секунды, например 1/24.'],
  source_media: ['Source media','Исходное медиа','Fingerprinted selected source with actual decoded timing.','Выбранный исходник с отпечатком и фактическими временными метками.'],
  probe: ['Decoded source probe','Проверка исходника','Actual selected-stream timing and source fingerprint.','Фактические времена выбранных потоков и отпечаток исходника.'],
  normalized: ['Normalized source','Нормализованный исходник','Whole-source canonical CFR24 disk media and its provenance.','Канонический CFR24 всего исходника на диске и его происхождение.'],
  canonical_media: ['Canonical CFR24 media','Каноническое медиа CFR24','Normalized once for the whole source; windows never resample independently.','Одна нормализация всего исходника; окна не пересчитывают FPS отдельно.'],
  audio_mode: ['Source audio mode','Режим исходного звука','preserve retains global PCM; mute produces no soundtrack.','preserve сохраняет глобальный PCM; mute отключает звуковую дорожку.'],
  sample_rate: ['PCM sample rate · Hz','Частота PCM · Гц','Global sample mapping uses absolute frame boundaries.','Сэмплы глобального PCM соответствуют абсолютным границам кадров.'],
  audio_timeline: ['Audio timeline','Таймлайн звука','Source origin, global sample rate, modes and explicit scene decisions.','Начало исходника, глобальная частота сэмплов, режимы и явные решения по сценам.'],
  project: ['Project','Проект','Validated portable project with stable scene identities.','Проверенный переносимый проект с постоянными идентификаторами сцен.'],
  render_profile: ['Native render profile','Нативный профиль генерации','Checked limits and frame lattice. Source policy alone is not GPU evidence.','Проверенные лимиты и сетка кадров. Исходная политика сама по себе не подтверждает GPU.'],
  prompt: ['Editable scene prompt','Редактируемый промпт сцены','Visible authored prompt, kept in scene settings.','Видимый авторский промпт, сохранённый в настройках сцены.'],
  seed: ['Seed · decimal string','Seed · десятичная строка','0 through 18446744073709551615; kept as a string.','От 0 до 18446744073709551615; сохраняется строкой.'],
  window_plan: ['Window plan','План окон','Exact selected useful coverage with legal native padding.','Точное полезное покрытие выбранных сцен с допустимым нативным дополнением.'],
  window_index: ['Window index · from zero','Индекс окна · с нуля','Choose a planned window in timeline order.','Выберите окно плана по порядку таймлайна.'],
  window: ['Generation window','Окно генерации','Technical window; editorial scene identities and ranges are preserved.','Техническое окно; идентификаторы и диапазоны монтажных сцен сохраняются.'],
  spatial: ['Spatial transform','Пространственное преобразование','Displayed rotation/SAR, service canvas pad and exact inverse crop.','Отображаемые поворот/SAR, дополнение холста и точное обратное обрезание.'],
  prepared: ['Prepared disk artifact','Подготовленный файл на диске','Bounded native-window manifest; no whole-film IMAGE tensor.','Ограниченный манифест нативного окна; без IMAGE-тензора всего фильма.'],
  prepared_media: ['Native window media','Медиа нативного окна','Actual padded native frames at exactly 24/1 FPS.','Фактические дополненные нативные кадры с точной частотой 24/1 FPS.'],
  results_json: ['Selected result records','Записи выбранных результатов','JSON array of successful current RenderResult records; replaces active selection.','Массив JSON успешных актуальных RenderResult; заменяет активный выбор.'],
  selection: ['Export range selection','Выбор диапазонов экспорта','full needs all scenes; selected concatenates selected scenes only.','full требует все сцены; selected соединяет только выбранные сцены.'],
  codec: ['Final export codec','Кодек итогового экспорта','ffv1-nut is lossless; h264-aac encodes video/audio once at the end.','ffv1-nut — без потерь; h264-aac кодирует видео/звук один раз в конце.'],
  odd_dimensions: ['Odd dimensions policy','Правило нечётных размеров','reject or explicit pad_even for H.264; actual export dimensions are reported.','reject или явное pad_even для H.264; отчёт содержит фактический размер экспорта.'],
  export_result: ['Export result','Результат экспорта','Verified CPU assembly record. This does not establish H3 generation.','Проверенная запись CPU-сборки. Она не подтверждает генерацию H3.'],
  export_media: ['Export media','Медиа экспорта','Verified final disk media with actual fingerprint.','Проверенный итоговый файл с фактическим отпечатком.'],
  media_report: ['Media report','Отчёт медиа','Timing, useful/native counts, selection, audio and actual dimensions.','Времена, полезные/нативные кадры, выбор, звук и фактические размеры.'],
};
const nodes = {
  KVD_ProbeMedia: ['KVD Probe Media','KVD Проверить медиа','Measure decoded PTS, displayed origin and EOF before normalization.','Измерьте декодированные PTS, начало отображения и EOF перед нормализацией.'],
  KVD_NormalizeMedia: ['KVD Normalize · CFR24','KVD Нормализация · CFR24','One whole-source normalization. Frame selection and global PCM remain auditable on disk.','Одна нормализация всего исходника. Выбор кадров и глобальный PCM сохраняются на диске.'],
  KVD_MediaProject: ['KVD Media Project','KVD Медиапроект','Create one editable scene. The default profile has checked source limits; human H3 validation remains separate.','Создайте одну редактируемую сцену. Лимиты профиля проверены по исходникам; проверка H3 человеком остаётся отдельной.'],
  KVD_PlanWindows: ['KVD Plan Windows','KVD План окон','Balanced technical windows cover selected scenes exactly. Every native pad counts toward the profile limit.','Сбалансированные технические окна точно покрывают выбранные сцены. Все дополнения входят в лимит профиля.'],
  KVD_SelectWindow: ['KVD Select Window','KVD Выбрать окно','Select one planned window, canonical media and spatial transform without decoding.','Выберите окно плана, каноническое медиа и преобразование без декодирования.'],
  KVD_PrepareWindow: ['KVD Prepare Window','KVD Подготовить окно','Prepare one bounded disk window with explicit service padding and no independent FPS resampling.','Подготовьте одно ограниченное окно на диске с явным дополнением и без отдельного пересчёта FPS.'],
  KVD_SelectResults: ['KVD Select Results','KVD Выбрать результаты','Choose successful current results explicitly. Missing windows stay incomplete.','Явно выберите успешные актуальные результаты. Отсутствующие окна остаются незавершёнными.'],
  KVD_AssembleExport: ['KVD Assemble & Export','KVD Сборка и экспорт','Check selected useful outputs, preserve absolute audio boundaries and encode one final export.','Проверьте выбранные полезные результаты, сохраните абсолютные границы звука и закодируйте итоговый экспорт.'],
};
export const MEDIA_PRESENTATIONS = {};
for (const [id, text] of Object.entries(nodes)) {
  const pair = {};
  for (const [locale, offset] of [['en',0],['ru',1]]) {
    pair[locale] = {title:text[offset],help:text[offset+2],fields:{},tooltips:{}};
    for (const [key, values] of Object.entries(entries)) {
      pair[locale].fields[key] = values[offset]; pair[locale].tooltips[key] = values[offset+2];
    }
  }
  MEDIA_PRESENTATIONS[id] = pair; registerPresentation(id,pair);
}
export function mediaStatus(report = {}) {
  const ru = getLanguage() === 'ru';
  const pieces = [ru ? 'CPU · медиа' : 'CPU · media'];
  const frames = report.frame_count ?? report.video?.decoded_frames ?? report.decoded_frames;
  if (frames !== undefined) pieces.push(`${frames} ${ru?'кадров':'frames'}`);
  const fps = report.video?.fps ?? report.fps ?? report.recipe?.fps;
  if (fps) pieces.push(`${fps.num}/${fps.den} FPS`);
  if (report.native_frames !== undefined) pieces.push(`${report.native_frames} ${ru?'нативных кадров':'native frames'}`);
  if (report.export_dimensions) pieces.push(report.export_dimensions.join(' × '));
  if (report.audio?.global_pcm_samples) pieces.push(`${report.audio.global_pcm_samples} PCM`);
  return pieces.join(' · ');
}
