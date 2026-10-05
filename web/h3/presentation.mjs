import {registerPresentation,getLanguage,errorText} from '../common/presentation.js';

const entries={
  KVD_ControlSettings:['KVD Structural Settings','KVD Настройки структуры',
    'Choose native Canny or explicit structural off before planning. Preparation needs no H3 weights; generation has a separate strict resource preflight.',
    'Выберите нативный Canny или явное отключение структуры off до планирования. Подготовка не требует весов H3; для генерации ресурсы проверяются отдельно.'],
  KVD_H3Profile:['KVD H3 Profile','KVD Профиль H3',
    'Select the exact template checkpoints and native schema handoff. Missing files or incompatible metadata stop the render. GPU fit remains unverified.',
    'Выберите точные веса шаблона и файл схем нативных узлов. Отсутствующие файлы или несовместимые метаданные останавливают рендер. Вместимость GPU не проверена.'],
  KVD_BuildControl:['KVD Canny Control','KVD Контроль Canny',
    'Compute native Canny for one prepared window. Canny controls structure; structural off removes this branch. Source RGB is not an appearance reference.',
    'Вычислите нативный Canny для одного подготовленного окна. Canny задаёт структуру; off отключает эту ветвь. Исходный RGB не служит референсом внешности.'],
  KVD_CompileWindowPrompt:['KVD Window Prompt','KVD Промпт окна',
    'Author the exact visible text for this window. Whitespace and text are preserved. The first path uses no appearance references or hidden enhancer.',
    'Отредактируйте точный видимый текст для этого окна. Пробелы и текст сохраняются. Первый путь работает без референсов внешности и скрытого улучшения промпта.'],
  KVD_BindWindow:['KVD Bind Window','KVD Связать окно',
    'Bind the current authored prompt, control map, model profile and sampling settings. An edited dependency invalidates the previous active result.',
    'Свяжите текущий авторский промпт, карту контроля, профиль модели и параметры семплирования. Изменение зависимости снимает прежний активный результат.'],
  KVD_ExpandNativeRender:['KVD Native H3 Render','KVD Нативный рендер H3',
    'Use the native queue, conditioning, sampler and decoders for one bounded 24 FPS window. References, audio guide and inpainting are disconnected.',
    'Нативная очередь, кондиционирование, семплер и декодеры для одного ограниченного окна 24 FPS. Референсы, аудиогайд и инпейтинг отключены.'],
  KVD_FinalizeWindow:['KVD Finalize Window','KVD Завершить окно',
    'Validate decoded geometry/count, remove padding, and persist useful video/PCM. Feed the current results JSON array to Select Results; original audio retains its global timeline.',
    'Проверьте размеры и число декодированных кадров, уберите дополнение и сохраните полезное видео/PCM. Передайте JSON-массив текущих результатов в Select Results; исходное аудио сохраняет общий таймлайн.'],
  KVD_ControlPreview:['KVD Control Preview','KVD Просмотр контроля',
    'Inspect one actual computed Canny frame before rendering. A preview requires Canny; structural off has no map.',
    'Просмотрите один реально вычисленный кадр Canny до рендера. Для просмотра нужен Canny; у режима off карты нет.'],
  KVD_WindowGate:['KVD Window Gate','KVD Порядок окон',
    'Require exact predecessor finalization before the next window. The order token carries no image or audio tensor.',
    'Дождитесь точного завершения предыдущего окна. Маркер порядка не содержит тензоры изображения или аудио.'],
  KVD_OrderedModel:['KVD Ordered Model','KVD Модель по порядку',
    'Native graph helper: expose the linked model after the serial window gate.',
    'Помощник нативного графа: передайте подключённую модель после проверки порядка окон.'],
  KVD_OrderedClip:['KVD Ordered CLIP','KVD CLIP по порядку',
    'Native graph helper: encode authored text only after the serial window gate.',
    'Помощник нативного графа: кодируйте авторский текст после проверки порядка окон.'],
  KVD_ControlImage:['KVD Control IMAGE','KVD Изображение контроля',
    'Native graph helper: materialize one verified bounded RGB structural map; no full-film tensor.',
    'Помощник нативного графа: загрузите одну проверенную ограниченную RGB-карту структуры; без тензора всего фильма.'],
  KVD_NativeReceipt:['KVD Decode Receipt','KVD Свидетельство декодирования',
    'Native graph helper: record exact decoded output identity. Useful finalization and human GPU acceptance remain separate.',
    'Помощник нативного графа: зафиксируйте точную идентичность декодированного выхода. Завершение полезного окна и ручная приёмка GPU выполняются отдельно.'],
};
export const OWN_IDS=Object.freeze(Object.keys(entries));
const fields={
  en:{project:'Project',window:'Window',prepared:'Prepared window',control:'Structural control',compiled_prompt:'Compiled prompt',
    control_mode:'Structural mode',low_threshold:'Low Canny threshold',high_threshold:'High Canny threshold',strength:'Control strength',
    start_percent:'Control start fraction',end_percent:'Control end fraction',
    prompt:'Authored window prompt',prompt_text:'Exact prompt text',render_profile:'H3 profile',spatial:'Spatial transform',
    project_root:'Project folder',native_schema_file:'Native schema handoff',ffmpeg_path:'FFmpeg executable',ffprobe_path:'ffprobe executable',
    working_set_bytes:'Working memory budget (bytes)',disk_quota_bytes:'Disk budget (bytes)',timeout_seconds:'CPU operation deadline (seconds)',
    structural_control:'Structural mode',model_file:'Base checkpoint',clip_file:'Text encoder checkpoint',video_vae_file:'Video VAE',
    audio_vae_file:'Audio VAE',patch_file:'Control checkpoint',model:'Native model',clip:'Native CLIP',video_vae:'Native video VAE',
    audio_vae:'Native audio VAE',patch:'Native control patch',images:'Decoded frames',audio:'Decoded audio',order_token:'Serial order',
    attempt:'Attempt',request_id:'Request ID',result_json:'Current results JSON array',render_result:'Useful result',preview_frame:'Preview frame',preview:'Canny preview',
    profile_report:'Profile report',control_report:'Control report',graph_report:'Native graph report',gate:'Window gate',manifest:'Map/receipt JSON',
    asset_root:'Project folder',project_id:'Project ID',plan_revision:'Plan revision',ordinal:'Window ordinal',useful_start:'Useful start frame'},
  ru:{project:'Проект',window:'Окно',prepared:'Подготовленное окно',control:'Контроль структуры',compiled_prompt:'Собранный промпт',
    control_mode:'Режим структуры',low_threshold:'Нижний порог Canny',high_threshold:'Верхний порог Canny',strength:'Сила контроля',
    start_percent:'Начало контроля (доля)',end_percent:'Конец контроля (доля)',
    prompt:'Авторский промпт окна',prompt_text:'Точный текст промпта',render_profile:'Профиль H3',spatial:'Пространственное преобразование',
    project_root:'Папка проекта',native_schema_file:'Файл схем нативных узлов',ffmpeg_path:'Исполняемый файл FFmpeg',ffprobe_path:'Исполняемый файл ffprobe',
    working_set_bytes:'Лимит рабочей памяти (байты)',disk_quota_bytes:'Лимит диска (байты)',timeout_seconds:'Лимит времени CPU (секунды)',
    structural_control:'Режим структуры',model_file:'Основные веса',clip_file:'Веса кодировщика текста',video_vae_file:'VAE видео',
    audio_vae_file:'VAE аудио',patch_file:'Веса контроля',model:'Нативная модель',clip:'Нативный CLIP',video_vae:'Нативный VAE видео',
    audio_vae:'Нативный VAE аудио',patch:'Нативный патч контроля',images:'Декодированные кадры',audio:'Декодированное аудио',order_token:'Порядок окон',
    attempt:'Попытка',request_id:'ID запроса',result_json:'JSON-массив текущих результатов',render_result:'Полезный результат',preview_frame:'Кадр просмотра',preview:'Просмотр Canny',
    profile_report:'Отчёт профиля',control_report:'Отчёт контроля',graph_report:'Отчёт нативного графа',gate:'Проверка порядка',manifest:'JSON карты/свидетельства',
    asset_root:'Папка проекта',project_id:'ID проекта',plan_revision:'Ревизия плана',ordinal:'Порядковый номер окна',useful_start:'Первый полезный кадр'},
};
for(const [id,[en,ru,enHelp,ruHelp]] of Object.entries(entries)) {
  registerPresentation(id,{en:{title:en,help:enHelp,fields:fields.en,tooltips:{prompt:enHelp}},
                           ru:{title:ru,help:ruHelp,fields:fields.ru,tooltips:{prompt:ruHelp}}});
}

export function reportText(report={}) {
  const ru=getLanguage()==='ru';
  const table={
    PROFILE_SOURCE_CHECKED:ru?'Схемы и метаданные проверены · GPU не проверен':'Source/schema metadata checked · GPU unverified',
    CONTROL_READY:ru?'Карта нативного Canny готова':'Native Canny map ready',
    CONTROL_CONFIGURED:ru?'Настройки структуры заданы · перепланируйте окна':'Structural settings set · plan windows next',
    CONTROL_OFF:ru?'Контроль структуры: off':'Structural control: off',
    PROMPT_AUTHORED:ru?'Точный авторский текст · без переписывания':'Exact authored text · no rewriting',
    WINDOW_BOUND:ru?'Текущие зависимости окна связаны':'Current window dependencies bound',
    GRAPH_COMPILED:ru?'Нативный граф собран · приёмка GPU не выполнена':'Native graph compiled · GPU acceptance not performed',
    USEFUL_FINALIZED:ru?'Полезное окно сохранено · приёмка GPU не выполнена':'Useful window persisted · GPU acceptance not performed',
    DEPENDENCY_MISSING:ru?'Нужен существующий нативный бэкенд и его зависимости':'The existing native backend and its dependencies are required',
  };
  let text=table[report.code] || (report.code?errorText(report.code):(ru?'Проверка человеком ещё не выполнена':'Human validation not performed'));
  if(Number.isInteger(report.useful_frames)) text+=` · ${report.useful_frames} ${ru?'кадров':'frames'} · ${report.width} × ${report.height}`;
  else if(Number.isInteger(report.frames)) text+=` · ${report.frames} ${ru?'кадров':'frames'}`;
  return text;
}
