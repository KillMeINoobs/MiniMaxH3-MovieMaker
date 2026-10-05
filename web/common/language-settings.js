// Only this pack's preference is read or written. No cached value proves a save.
export const SETTING_ID = 'KVD.Language';
export const effectiveLanguage = stored => stored === null ? 'en' : stored;

export async function readPersistedLanguage(api) {
  const response = await api.fetchApi('/settings/' + encodeURIComponent(SETTING_ID));
  if (!response.ok) throw new Error('KVD preference readback failed (HTTP ' + response.status + ')');
  const stored = await response.json();
  if (stored !== null && !['en','ru'].includes(stored))
    throw new Error('Persisted KVD language could not be verified');
  return stored; // null is the native unset preference, whose declared default is English.
}

export async function persistLanguage(settings, api, language) {
  if (!['en','ru'].includes(language)) throw new Error('Unsupported KVD language');
  if (typeof settings.setSettingValueAsync !== 'function')
    throw new Error('Awaitable KVD setting API is unavailable');
  const write = settings.setSettingValueAsync(SETTING_ID,language);
  if (!write || typeof write.then !== 'function')
    throw new Error('KVD setting write completion is unavailable');
  await write;
  // Native store writes can resolve an HTTP error or skip an unchanged value.
  const persisted = await readPersistedLanguage(api);
  if (effectiveLanguage(persisted) !== language)
    throw new Error('KVD language persistence could not be verified');
  if ((settings.getSettingValue(SETTING_ID) ?? 'en') !== language)
    throw new Error('Cached KVD language differs from the verified preference');
  return persisted;
}
