(() => {
  'use strict';
  const get = id => document.getElementById(id);
  let token = '', live = false, snapshot = null, selected = 'mixed', requestGeneration = 0;
  const scenarios = {
    mixed: {values:[25,88],seconds:[8040,2880],note:'Bir göz çalışmaya hazır. Diğeri biraz yoruldu.'},
    sleep: {values:[100,100],seconds:[2520,4320],note:'Biraz mola. İki göz de yenilenmeyi bekliyor.'},
    renewed: {values:[0,0],seconds:[18000,18000],note:'Yeniden hazır. Küçük bir kutlama zamanı.'},
    offline: {values:[null,null],seconds:[null,null],note:'Bağlantı yok. Bilmediği kapasiteyi tahmin etmiyor.'}
  };
  const duration = seconds => {
    if (seconds === null || seconds === undefined) return '—';
    if (seconds <= 0) return 'Doğrulanıyor';
    const minutes = Math.ceil(seconds / 60), days = Math.floor(minutes / 1440);
    const hours = Math.floor(minutes % 1440 / 60), remainder = minutes % 60;
    if (days) return `${days}g ${hours}s`;
    if (hours) return `${hours}s ${String(remainder).padStart(2,'0')}dk`;
    return `${minutes}dk`;
  };
  function chooseWindow(provider) {
    const windows = provider?.windows || [];
    return get('window-choice').value === 'week'
      ? windows.find(w => w.id === 'seven_day' || w.window_minutes >= 1440)
      : windows.find(w => w.id === 'five_hour' || w.id === 'primary' && (w.window_minutes === null || w.window_minutes < 1440));
  }
  function drawProvider(key, provider, demo) {
    const item = chooseWindow(provider);
    const remaining = typeof item?.used_percent === 'number' ? Math.round(100-item.used_percent) : null;
    const now = Math.floor(Date.now()/1000);
    const seconds = typeof item?.resets_at === 'number' ? Math.max(0,item.resets_at-now) : null;
    const age = typeof provider?.observed_at === 'number' ? Math.max(0,now-provider.observed_at) : null;
    const stale = !demo && (provider?.status !== 'ok' || age === null || age > (snapshot.stale_after ?? 180));
    let mood = remaining === null || stale ? 'unknown' : remaining <= 0 ? 'sleep' : remaining <= 20 ? 'low' : 'ready';
    if (demo && selected === 'renewed') mood = 'renewed';
    get(`eye-${key}`).dataset.mood = mood;
    get(`eye-${key}`).setAttribute('aria-label',`${key === 'openai' ? 'Codex' : 'Claude'}: ${remaining === null ? 'kapasite bilinmiyor' : '%'+remaining+' kaldı'}. ${duration(seconds)}`);
    get(`eye-${key}-percent`).textContent = stale && remaining !== null ? `Son: %${remaining}` : remaining === null ? 'Veri yok' : `%${remaining} kaldı`;
    const label = duration(seconds);
    get(`eye-${key}-time`).textContent = label === 'Doğrulanıyor' ? 'Bekle' : label;
    get(`${key}-percent`).textContent = remaining === null ? '—' : remaining;
    get(`${key}-countdown`).textContent = label;
    get(`${key}-status`).textContent = demo ? 'Örnek' : !item ? 'Veri yok' : stale ? 'Son bilinen' : seconds === 0 ? 'Doğrulama bekliyor' : 'Güncel';
    const meter = get(`${key}-meter`);
    meter.firstElementChild.style.width = `${remaining ?? 0}%`;
    if (remaining === null) meter.removeAttribute('aria-valuenow');
    else meter.setAttribute('aria-valuenow',remaining);
    meter.setAttribute('aria-valuetext',remaining === null ? 'Bilinmiyor' : `${remaining}% kaldı`);
    get(`${key}-age`).textContent = demo ? 'Örnek veri · gerçek hesabına bağlı değil' : age === null ? 'Henüz veri alınmadı' : `Son gözlem ${duration(age).replace('Doğrulanıyor','0dk')} önce${stale ? ' · güncel olmayabilir' : ''}`;
  }
  function draw() {
    if (!snapshot) return;
    drawProvider('openai', snapshot.providers.openai, !live);
    drawProvider('claude', snapshot.providers.claude, !live);
    get('mode-label').textContent = live ? 'Yardımcı servise bağlı' : 'Örnek veriler';
    document.body.dataset.live = String(live);
    const device = snapshot.device;
    get('connection-path').textContent = live && device?.online ? device.transport === 'usb' ? 'BİLGİSAYAR → USB → LYMYT' : 'BİLGİSAYAR → WI-FI → LYMYT' : 'BİLGİSAYAR → LYMYT';
    get('character-note').textContent = live ? device?.online ? `Fiziksel Lymyt bağlı${device.motion === true ? ' · hareket algılandı' : ''}${device.acceleration ? ' · ADXL345 aktif' : ''}.` : 'Gerçek limit verileri · fiziksel cihaz çevrimdışı.' : scenarios[selected].note;
    document.querySelectorAll('[data-scenario]').forEach(button => {
      button.disabled = live;
      button.setAttribute('aria-pressed',String(!live && button.dataset.scenario === selected));
    });
  }
  function demo(key) {
    selected = key; live = false; token = ''; requestGeneration++;
    get('device-token').value = '';
    const now = Math.floor(Date.now()/1000), scene = scenarios[key];
    snapshot = {providers:{}};
    ['openai','claude'].forEach((provider,index) => {
      const reset = scene.seconds[index] === null ? null : now+scene.seconds[index];
      snapshot.providers[provider] = {status:key === 'offline' ? 'unknown':'ok',observed_at:now,windows:[
        {id:provider === 'openai' ? 'primary':'five_hour',used_percent:scene.values[index],resets_at:reset,window_minutes:300},
        {id:provider === 'openai' ? 'secondary':'seven_day',used_percent:scene.values[index],resets_at:reset === null ? null:now+259200,window_minutes:10080}
      ]};
    });
    get('connection-message').textContent = 'Örnek veriler gösteriliyor. Fiziksel cihaz henüz bağlanmadı.';
    draw();
  }
  async function refresh(generation) {
    if (!token) return;
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(),8000);
    try {
      const response = await fetch('/v1/status',{headers:{Authorization:'Bearer '+token},cache:'no-store',signal:controller.signal});
      if (!response.ok) throw new Error(response.status === 401 ? 'Cihaz anahtarı geçersiz.' : 'Yardımcı servis yanıt vermiyor.');
      const data = await response.json();
      if (data.schema_version !== 1 || !data.providers?.openai || !data.providers?.claude) throw new Error('Veri biçimi uyumsuz.');
      if (generation !== requestGeneration) return;
      snapshot = data; live = true;
      get('connection-message').textContent = 'Limit servisine bağlı. Anahtar yalnızca bu sayfanın belleğinde tutulur. Cihaz durumu gerçek telemetriyle doğrulanır.';
      draw();
    } catch (error) {
      if (generation !== requestGeneration) return;
      get('connection-message').textContent = error.name === 'AbortError' ? 'Bağlantı zaman aşımına uğradı.' : error.message;
      if (live && snapshot) {
        Object.values(snapshot.providers).forEach(provider => provider.status = 'stale');
        draw();
        get('mode-label').textContent = 'Bağlantı kesildi';
        document.body.dataset.live = 'false';
      }
    } finally { clearTimeout(timeout); }
  }
  document.querySelectorAll('[data-scenario]').forEach(button => button.addEventListener('click',() => demo(button.dataset.scenario)));
  get('demo-button').addEventListener('click',() => demo('mixed'));
  get('window-choice').addEventListener('change',draw);
  get('connect-form').addEventListener('submit',event => {
    event.preventDefault(); token = get('device-token').value.trim(); requestGeneration++;
    refresh(requestGeneration);
  });
  setInterval(() => { if (token) refresh(requestGeneration); },30000);
  setInterval(draw,1000);
  demo('mixed');
})();
