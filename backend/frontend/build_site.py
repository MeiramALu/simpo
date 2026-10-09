"""
Собирает frontend/site/index.html из исходного HTML фронта и подключает
форму регистрации к API (/api/registrations/). Заодно чинит форму:
выбранные «День участия» / «Формат участия» видны в тёмной теме, а при
ошибке подсвечиваются конкретные незаполненные поля. Страница «Докладчики»
берёт данные из админки (/api/speakers/). Язык по умолчанию — английский.
Личный кабинет (вход, заявка, статьи) — frontend/cabinet.js и cabinet.css. Значок вкладки
(favicon) делается из логотипа КазНУ в шапке — нужен Pillow.

Исходный файл не меняется. После каждой правки фронта запускайте заново:

    python frontend/build_site.py "../al-farabi-symposium-2026 V2.html"

Если страницу открыть без сервера (file://), форма ведёт себя как раньше —
предлагает скопировать текст заявки и отправить на почту.
"""
import base64
import io
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_SRC = HERE.parent.parent / 'al-farabi-symposium-2026 V2.html'

FORM_CSS = """/* --- правки формы регистрации (build_site.py) --- */
.choice input:checked+span{background:var(--gold);border-color:var(--gold);color:#1E2640;font-weight:700}
.field.err .choice span,.field.err textarea{border-color:#B3261E}
.field.err>label,.field.err>legend{color:#E0564C}
</style>"""

# исходная строка проверки — заменяется целиком
REQ_CHECK_LINE = r"""  if (!data.name || !data.org || !/.+@.+\..+/.test(data.email) || !data.day || !data.role){ msg.innerHTML = `<div class="notice err">${esc(F.req)}</div>`; return; }"""

FORM_VALIDATION = """  const miss = [['name', !data.name], ['org', !data.org], ['email', !/.+@.+\\..+/.test(data.email)], ['day', !data.day], ['role', !data.role]]
    .filter(x => x[1]).map(x => x[0]);
  f.querySelectorAll('.field.err').forEach(x => x.classList.remove('err'));
  if (miss.length){
    const lab = {name:F.name, org:F.org, email:F.email, day:F.days, role:F.role};
    const pre = {ru:'Заполните: ', kk:'Толтырыңыз: ', en:'Please fill in: '}[lang] || '';
    miss.forEach(n => { const el = E[n]; const node = el.tagName ? el : el[0]; node && node.closest('.field')?.classList.add('err'); });
    msg.innerHTML = `<div class="notice err">${esc(pre + miss.map(n => lab[n]).join(', '))}</div>`;
    const first = E[miss[0]]; (first.tagName ? first : first[0])?.focus();
    return;
  }"""

FORM_BIND = """form.onsubmit = submitReg;
    form.addEventListener('change', e => e.target.closest('.field')?.classList.remove('err'));
    form.addEventListener('input', e => e.target.closest('.field')?.classList.remove('err'));
    regFormState(form);"""

API_HELPERS = """/* ---------- backend API ---------- */
const API = (window.AFGS_API || '').replace(/\\/$/, '');
function apiHeaders(json){
  const h = {};
  if (json) h['Content-Type'] = 'application/json';
  h['Accept-Language'] = lang;
  try { const tk = localStorage.getItem('afgs-token'); if (tk) h['Authorization'] = 'Token ' + tk; } catch(e) {}
  const m = document.cookie.match(/(?:^|; )csrftoken=([^;]+)/);
  if (m) h['X-CSRFToken'] = decodeURIComponent(m[1]);
  return h;
}

/* ---------- speakers from admin ---------- */
const SPK = {};  // lang -> группы из /api/speakers/; null — API недоступен, показываем встроенные из программы
async function loadSpeakers(){
  const l = lang; SPK[l] = null;
  if (location.protocol === 'file:') return;
  try { const r = await fetch(API + '/api/speakers/?lang=' + l); if (r.ok) SPK[l] = await r.json(); } catch(e) {}
  if (SPK[l] && route() === 'speakers' && l === lang) render(true);
}

/* ---------- registration ---------- */"""

# Страница «Докладчики»: данные из админки (/api/speakers/), встроенные — запасной вариант
SPEAKERS_PAGE_OLD = r"""  speakers: () => {
    const L = t(); const G = speakerGroups(); const f = window.__spf ?? 0;
    return head(L.spTitle, L.spLead) + `<section class="section" style="padding-top:10px"><div class="wrap">
      <div class="filters" role="group">${L.spFilters.map((x,i)=>`<button class="tab" aria-selected="${i===f}" data-spf="${i}">${esc(x)}</button>`).join('')}</div>
      ${G.map((g,i)=> (f===0||f===i+1) ? `<div class="sgroup"><h2>${esc(L.spFilters[i+1])}</h2><div class="sub">${esc(L.spSub[i])}</div><div class="sgrid">${g.map(spCard).join('')}</div></div>` : '').join('')}
    </div></section>`;
  },"""

SPEAKERS_PAGE_NEW = r"""  speakers: () => {
    const L = t();
    if (!(lang in SPK)) loadSpeakers();
    const G = SPK[lang] || speakerGroups().map((g,i) => ({title:L.spFilters[i+1], subtitle:L.spSub[i], speakers:g}));
    const f = Math.min(window.__spf ?? 0, G.length);
    const tabs = [L.spFilters[0], ...G.map(g => g.title)];
    return head(L.spTitle, L.spLead) + `<section class="section" style="padding-top:10px"><div class="wrap">
      <div class="filters" role="group">${tabs.map((x,i)=>`<button class="tab" aria-selected="${i===f}" data-spf="${i}">${esc(x)}</button>`).join('')}</div>
      ${G.map((g,i)=> (f===0||f===i+1) && g.speakers.length ? `<div class="sgroup"><h2>${esc(g.title)}</h2>${g.subtitle?`<div class="sub">${esc(g.subtitle)}</div>`:''}<div class="sgrid">${g.speakers.map(spCard).join('')}</div></div>` : '').join('')}
    </div></section>`;
  },"""

SPEAKER_AVATAR_OLD = '<div class="ini" aria-hidden="true">${esc(initials(s.name))}</div>'
SPEAKER_AVATAR_NEW = ('${s.photo ? `<img class="ini" src="${esc(s.photo)}" alt="" loading="lazy" style="object-fit:cover">`'
                      ' : `<div class="ini" aria-hidden="true">${esc(initials(s.name))}</div>`}')

API_SUBMIT = """  if (location.protocol !== 'file:'){
    try {
      const r = await fetch(API + '/api/registrations/', {method:'POST', headers:apiHeaders(true), body:JSON.stringify(data)});
      if (r.status === 401 && getToken()){ setToken(null); CAB.me = null; cabStatic(); return submitReg(e); }
      if (r.ok){
        msg.innerHTML = `<div class="notice">${esc(F.ok)}${getToken() ? ` <a href="#/cabinet">${esc(ct().regSentCab)}</a>` : ''}</div>`;
        f.reset(); $('#topicfield').classList.add('hidden'); regFormState(f); return;
      }
      if (r.status === 400 || r.status === 403){
        const j = await r.json().catch(() => null);
        msg.innerHTML = `<div class="notice err">${esc(j ? cabErr(j) : F.req)}</div>`; return;
      }
    } catch(err) {}
  }
  let db = null;"""


# Личный кабинет: вход/регистрация, заявка, статьи, профиль (код — frontend/cabinet.js)
CABINET_STEPS = [
    # маршруты #/cabinet и #/reset-password
    ("return ROUTES.includes(h) ? h : '';", "return (ROUTES.includes(h) || EXTRA_ROUTES.includes(h)) ? h : '';"),
    # ссылка «Вход / Кабинет» в шапке
    ('<div class="langs" role="group" aria-label="Language">',
     '<a class="acct" id="acct-link" href="#/cabinet"></a><div class="langs" role="group" aria-label="Language">'),
    ("  $('#fnav2').innerHTML", "  cabStatic();\n  $('#fnav2').innerHTML"),
    ('<nav class="main" id="nav" aria-label="Main"><ul id="navlist"></ul></nav>',
     '<nav class="main" id="nav" aria-label="Main"><ul id="navlist"></ul><a class="acct acct-nav" id="acct-link-nav" href="#/cabinet"></a></nav>'),
    # подпись партнёра: на английском короткая (полное название — во всплывающей подсказке)
    ("p1:'Science Committee, Ministry of Science and Higher Education of Kazakhstan'", "p1:'Science Committee, MSHE RK'"),
    # в английской версии мелкая строка над названием дублировала его — показываем даты и город
    ("brandSmall:'Al-Farabi Global Symposium', brandName:'Al-Farabi Global Symposium – 2026'",
     "brandSmall:'6–7 November 2026 · Almaty', brandName:'Al-Farabi Global Symposium – 2026'"),
    # над формой заявки: срок, «приём закрыт», «вы вошли как …»
    ('<p class="muted" style="max-width:44em">${esc(L.regIntro)}</p>',
     '<p class="muted" style="max-width:44em">${esc(L.regIntro)}</p><div id="regstate" aria-live="polite"></div>'),
    # страница «Программа» — из админки (/api/program/)
    ("  const d = P()[di];", "  const d = progDays()[di];"),
    ("    const cur = window.__day ?? 1;\n    return head(L.progTitle",
     "    if (!(lang in PRG)) loadProgram();\n    const tabsP = PRG[lang] ? PRG[lang].map(d => d.tab) : L.dayTabs;\n"
     "    const cur = Math.min(window.__day ?? 1, tabsP.length - 1);\n    return head(L.progTitle"),
    ('${L.dayTabs.map((d,i)=>`<button class="tab" role="tab"', '${tabsP.map((d,i)=>`<button class="tab" role="tab"'),
    # кнопки «Скачать программу / письмо»: файл из админки, если загружен
    ("  const blob = b64ToBlob(FILES[key], 'application/pdf');",
     "  let blob = null;\n"
     "  if (location.protocol !== 'file:'){ try { const r = await fetch(API + `/api/documents/${kind}/?lang=${lang}`); "
     "if (r.ok) blob = await r.blob(); } catch(e) {} }\n"
     "  if (!blob) blob = b64ToBlob(FILES[key], 'application/pdf');"),
    # страница «Публикации»: суммы из админки и кнопка «Подать статью»
    ('${esc(L.fee1)}', "${esc(feeText('tuva', L.fee1))}"),
    ('${esc(L.fee2)}', "${esc(feeText('vestnik_philosophy', L.fee2))}"),
    ('${esc(L.pubWarn)}</div></div>',
     '${esc(L.pubWarn)}</div></div><div class="pub pub-cta"><a class="btn btn-maroon" href="#/cabinet?tab=papers">'
     '${esc(ct().newPaper)} ${ARROW}</a><span class="muted">${esc(ct().pubCtaHint)}</span></div>'),
    # «Открыть на карте»: вместо одной ссылки на Google — меню: место, отели, где поесть, остановки
    # в Google Maps, 2ГИС и Яндекс Картах (mapMenu в cabinet.js)
    ('<a class="btn btn-outline" href="https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(v[3])}" '
     'target="_blank" rel="noopener">${esc(L.map)}</a>', '${mapMenu(vi, v, L.map)}'),
]


def build(src: Path, dst: Path):
    html = src.read_text(encoding='utf-8')
    cab_css = (HERE / 'cabinet.css').read_text(encoding='utf-8')
    cab_js = (HERE / 'cabinet.js').read_text(encoding='utf-8')
    steps = [
        ('</style>', FORM_CSS.replace('</style>', cab_css + '</style>')),
        (REQ_CHECK_LINE, FORM_VALIDATION),
        ('form.onsubmit = submitReg;', FORM_BIND),
        ('/* ---------- registration ---------- */',
         API_HELPERS.replace('/* ---------- registration ---------- */', cab_js + '\n/* ---------- registration ---------- */')),
        ('  let db = null;', API_SUBMIT),
        (SPEAKERS_PAGE_OLD, SPEAKERS_PAGE_NEW),
        (SPEAKER_AVATAR_OLD, SPEAKER_AVATAR_NEW),
        # Сайт открывается на английском. Если посетитель сам выбрал язык кнопкой,
        # выбор запоминается (localStorage 'afgs-lang') и в следующий раз открывается он.
        ("let lang = 'ru';", "let lang = 'en';"),
        ('<html lang="ru">', '<html lang="en">'),
        ('<title>Глобальный симпозиум аль-Фараби – 2026</title>', '<title>Al-Farabi Global Symposium – 2026</title>'),
        *CABINET_STEPS,
    ]
    if build_favicons(html, dst.parent):
        steps.append(('</head>', FAVICON_LINKS + '</head>'))
    for old, new in steps:
        if html.count(old) != 1:
            sys.exit(f'Не найдено место для вставки: {old!r} — структура фронта изменилась, поправьте build_site.py')
        html = html.replace(old, new)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(html, encoding='utf-8')
    print(f'Готово: {dst} ({dst.stat().st_size // 1024} КБ)')


FAVICON_LINKS = ('<link rel="icon" type="image/png" sizes="96x96" href="/favicon.png">'
                 '<link rel="apple-touch-icon" href="/apple-touch-icon.png">')


def build_favicons(html, out_dir: Path):
    """
    Значок вкладки = логотип КазНУ из шапки сайта (<a class="brand"><img src="data:...">).
    Логотип дополняется прозрачными полями до квадрата, чтобы браузер не сплющил его.
    """
    m = re.search(r'<a class="brand" href="#/"><img src="data:image/[a-z+]+;base64,([A-Za-z0-9+/=]+)"', html)
    if not m:
        print('Логотип в шапке не найден — значок вкладки не создан')
        return False
    try:
        from PIL import Image
    except ImportError:
        print('Pillow не установлен (pip install Pillow) — значок вкладки не создан')
        return False
    logo = Image.open(io.BytesIO(base64.b64decode(m.group(1)))).convert('RGBA')
    out_dir.mkdir(parents=True, exist_ok=True)

    def square(size, background, margin):
        canvas = Image.new('RGBA', (size, size), background)
        inner = size - 2 * margin
        img = logo.copy()
        img.thumbnail((inner, inner), Image.LANCZOS)
        canvas.alpha_composite(img, ((size - img.width) // 2, (size - img.height) // 2))
        return canvas

    square(96, (0, 0, 0, 0), 0).save(out_dir / 'favicon.png', optimize=True)
    square(256, (0, 0, 0, 0), 0).save(out_dir / 'favicon.ico', sizes=[(16, 16), (32, 32), (48, 48), (64, 64)])
    # iOS не поддерживает прозрачность — белый фон и поля
    square(180, (255, 255, 255, 255), 12).convert('RGB').save(out_dir / 'apple-touch-icon.png', optimize=True)
    return True


if __name__ == '__main__':
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_SRC
    build(src, HERE / 'site' / 'index.html')
