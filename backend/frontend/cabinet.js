/* ---------- личный кабинет участника (frontend/cabinet.js, вставляется build_site.py) ---------- */
const LANG_NAMES = {ru:'Русский', kk:'Қазақша', en:'English'};
const CT = {
ru: {
  login:'Вход', account:'Кабинет', cabTitle:'Личный кабинет', cabLead:'Заявка на участие и подача статей.',
  loading:'Загрузка…', netErr:'Не удалось связаться с сервером. Проверьте интернет и попробуйте ещё раз.', err:'Что-то пошло не так. Попробуйте ещё раз.',
  fileMode:'Личный кабинет работает только на сайте симпозиума, а не в сохранённом файле страницы.',
  authLead:'Аккаунт нужен, чтобы подать статью и следить за заявкой. Для заявки на участие он не обязателен.',
  tabLogin:'Вход', tabRegister:'Регистрация', tabForgot:'Забыли пароль?', password2:'Повторите пароль', passHint:'Не короче 8 символов и не только цифры.',
  btnLogin:'Войти', btnRegister:'Создать аккаунт', btnReset:'Отправить ссылку',
  resetSent:'Если этот адрес зарегистрирован, мы отправили на него ссылку для смены пароля.', passMismatch:'Пароли не совпадают.',
  registeredOk:'Аккаунт создан. Мы отправили письмо со ссылкой для подтверждения почты.', fillIn:'Заполните: ',
  hello:'Вы вошли как', logout:'Выйти',
  notVerified:'Почта не подтверждена: без этого нельзя подать статью. Откройте ссылку из нашего письма.', resend:'Отправить письмо ещё раз',
  emailVerifiedOk:'Почта подтверждена.', emailVerifiedBad:'Ссылка недействительна или устарела. Войдите и отправьте письмо ещё раз.',
  tReg:'Заявка на участие', tPapers:'Статьи', tProfile:'Профиль',
  noReg:'У вас пока нет заявки на участие.', goReg:'Заполнить заявку',
  regLinkHint:'Заявки, поданные с этого email без входа в аккаунт, появятся здесь после подтверждения почты.',
  orgComment:'Комментарий оргкомитета', edit:'Изменить', save:'Сохранить', cancel:'Отмена', cancelReg:'Отменить заявку',
  confirmAgain:'Нажмите ещё раз, чтобы подтвердить', saved:'Сохранено.', regCancelled:'Заявка отменена.',
  newPaper:'Подать статью', needVerify:'Подтвердите почту, чтобы подать статью.', noPapers:'Статей пока нет.',
  authorsHint:'Через запятую, как в статье.', fileHint:'DOC, DOCX, PDF, RTF или ODT, до {mb} МБ.', fileKeep:'Оставьте пустым, чтобы не менять файл.',
  free:'бесплатно', submitPaper:'Отправить статью', paperSent:'Статья отправлена. О решении мы сообщим по почте.',
  download:'Скачать файл', withdraw:'Отозвать статью', paperWithdrawn:'Статья отозвана.', editorComment:'Комментарий редакции',
  fee:'Взнос', feeNote:'Как оплатить взнос, оргкомитет сообщит по почте после рассмотрения статьи.',
  revisionNote:'Загрузите исправленную версию — статья снова уйдёт на рассмотрение.', submittedAt:'Подана', dirNone:'— не выбрано —',
  profileSaved:'Профиль сохранён.', changePass:'Смена пароля', passChanged:'Пароль изменён.',
  emailFixed:'Email изменить нельзя. Если нужен другой адрес, напишите оргкомитету.',
  resetTitle:'Новый пароль', resetLead:'Придумайте новый пароль для входа в личный кабинет.', resetBtn:'Сохранить пароль',
  resetBad:'Ссылка неполная. Запросите новую на странице входа.', toLogin:'Ко входу',
  regAsUser:'Вы вошли как {name}. Заявка появится в личном кабинете.',
  regHave:'У вас уже есть заявка на участие. Посмотреть, изменить или отменить её можно в личном кабинете.',
  toCabinet:'Перейти в личный кабинет', regAccountHint:'Хотите следить за статусом заявки?', regAccountLink:'Войдите или создайте аккаунт с тем же email.',
  regSentCab:'Статус заявки — в личном кабинете.', pubCtaHint:'Статьи подаются через личный кабинет участника.',
  stReg:{new:'Новая — на рассмотрении', confirmed:'Подтверждена', waitlist:'Лист ожидания', rejected:'Отклонена', cancelled:'Отменена'},
  stPaper:{submitted:'Подана', under_review:'На рассмотрении', revision:'Нужна доработка', recommended:'Рекомендована в журнал', accepted:'Принята к публикации', rejected:'Отклонена', published:'Опубликована', withdrawn:'Отозвана'},
  f:{email:'Электронная почта', password:'Пароль', full_name:'ФИО', organization:'Организация', country:'Страна', phone:'Телефон', lang:'Язык писем',
     title:'Название статьи', authors:'Авторы', abstract:'Аннотация', keywords:'Ключевые слова', direction:'Научное направление', language:'Язык статьи',
     target:'Издание', file:'Файл рукописи', comment:'Комментарий', old_password:'Текущий пароль', new_password:'Новый пароль',
     paper:'Статья', name:'ФИО', org:'Организация', day:'День участия', role:'Формат участия', topic:'Тема доклада', note:'Комментарий'}
},
kk: {
  login:'Кіру', account:'Кабинет', cabTitle:'Жеке кабинет', cabLead:'Қатысуға өтінім және мақала жіберу.',
  loading:'Жүктелуде…', netErr:'Сервермен байланыс орнамады. Интернетті тексеріп, қайталап көріңіз.', err:'Бірдеңе дұрыс болмады. Қайталап көріңіз.',
  fileMode:'Жеке кабинет сақталған бет файлында емес, тек симпозиум сайтында жұмыс істейді.',
  authLead:'Мақала жіберу және өтінімді бақылау үшін аккаунт қажет. Қатысуға өтінім беру үшін ол міндетті емес.',
  tabLogin:'Кіру', tabRegister:'Тіркелу', tabForgot:'Құпиясөзді ұмыттыңыз ба?', password2:'Құпиясөзді қайталаңыз', passHint:'Кемінде 8 таңба, тек сандардан тұрмауы керек.',
  btnLogin:'Кіру', btnRegister:'Аккаунт ашу', btnReset:'Сілтеме жіберу',
  resetSent:'Егер бұл мекенжай тіркелген болса, оған құпиясөзді өзгерту сілтемесін жібердік.', passMismatch:'Құпиясөздер сәйкес келмейді.',
  registeredOk:'Аккаунт ашылды. Поштаны растау сілтемесі бар хат жібердік.', fillIn:'Толтырыңыз: ',
  hello:'Сіз кірдіңіз:', logout:'Шығу',
  notVerified:'Пошта расталмаған: онсыз мақала жіберуге болмайды. Біздің хаттағы сілтемені ашыңыз.', resend:'Хатты қайта жіберу',
  emailVerifiedOk:'Пошта расталды.', emailVerifiedBad:'Сілтеме жарамсыз немесе ескірген. Кіріп, хатты қайта жіберіңіз.',
  tReg:'Қатысуға өтінім', tPapers:'Мақалалар', tProfile:'Профиль',
  noReg:'Сізде әзірге қатысуға өтінім жоқ.', goReg:'Өтінім толтыру',
  regLinkHint:'Осы email арқылы аккаунтсыз берілген өтінімдер пошта расталғаннан кейін осында шығады.',
  orgComment:'Ұйымдастыру комитетінің пікірі', edit:'Өзгерту', save:'Сақтау', cancel:'Болдырмау', cancelReg:'Өтінімнен бас тарту',
  confirmAgain:'Растау үшін тағы басыңыз', saved:'Сақталды.', regCancelled:'Өтінімнен бас тартылды.',
  newPaper:'Мақала жіберу', needVerify:'Мақала жіберу үшін поштаны растаңыз.', noPapers:'Әзірге мақала жоқ.',
  authorsHint:'Мақаладағыдай, үтір арқылы.', fileHint:'DOC, DOCX, PDF, RTF немесе ODT, {mb} МБ-қа дейін.', fileKeep:'Файлды өзгертпеу үшін бос қалдырыңыз.',
  free:'тегін', submitPaper:'Мақаланы жіберу', paperSent:'Мақала жіберілді. Шешім туралы поштамен хабарлаймыз.',
  download:'Файлды жүктеу', withdraw:'Мақаланы кері алу', paperWithdrawn:'Мақала кері алынды.', editorComment:'Редакция пікірі',
  fee:'Жарна', feeNote:'Жарнаны қалай төлеу керектігін ұйымдастыру комитеті мақала қаралғаннан кейін поштамен хабарлайды.',
  revisionNote:'Түзетілген нұсқаны жүктеңіз — мақала қайта қаралады.', submittedAt:'Жіберілген күні', dirNone:'— таңдалмаған —',
  profileSaved:'Профиль сақталды.', changePass:'Құпиясөзді өзгерту', passChanged:'Құпиясөз өзгертілді.',
  emailFixed:'Email-ді өзгертуге болмайды. Басқа мекенжай керек болса, ұйымдастыру комитетіне жазыңыз.',
  resetTitle:'Жаңа құпиясөз', resetLead:'Жеке кабинетке кіру үшін жаңа құпиясөз ойлап табыңыз.', resetBtn:'Құпиясөзді сақтау',
  resetBad:'Сілтеме толық емес. Кіру бетінде жаңасын сұраңыз.', toLogin:'Кіруге',
  regAsUser:'Сіз {name} ретінде кірдіңіз. Өтінім жеке кабинетте көрінеді.',
  regHave:'Сізде қатысуға өтінім бар. Оны жеке кабинетте көруге, өзгертуге немесе одан бас тартуға болады.',
  toCabinet:'Жеке кабинетке өту', regAccountHint:'Өтінім мәртебесін бақылағыңыз келе ме?', regAccountLink:'Сол email арқылы кіріңіз немесе аккаунт ашыңыз.',
  regSentCab:'Өтінім мәртебесі — жеке кабинетте.', pubCtaHint:'Мақалалар қатысушының жеке кабинеті арқылы жіберіледі.',
  stReg:{new:'Жаңа — қаралуда', confirmed:'Расталды', waitlist:'Күту тізімі', rejected:'Қабылданбады', cancelled:'Бас тартылды'},
  stPaper:{submitted:'Жіберілді', under_review:'Қаралуда', revision:'Пысықтау қажет', recommended:'Журналға ұсынылды', accepted:'Жариялауға қабылданды', rejected:'Қабылданбады', published:'Жарияланды', withdrawn:'Кері алынды'},
  f:{email:'Электрондық пошта', password:'Құпиясөз', full_name:'Аты-жөні', organization:'Ұйым', country:'Ел', phone:'Телефон', lang:'Хаттар тілі',
     title:'Мақала атауы', authors:'Авторлар', abstract:'Аңдатпа', keywords:'Түйін сөздер', direction:'Ғылыми бағыт', language:'Мақала тілі',
     target:'Басылым', file:'Қолжазба файлы', comment:'Пікір', old_password:'Ағымдағы құпиясөз', new_password:'Жаңа құпиясөз',
     paper:'Мақала', name:'Аты-жөні', org:'Ұйым', day:'Қатысу күні', role:'Қатысу форматы', topic:'Баяндама тақырыбы', note:'Пікір'}
},
en: {
  login:'Sign in', account:'Account', cabTitle:'My account', cabLead:'Your application and paper submissions.',
  loading:'Loading…', netErr:'Could not reach the server. Check your connection and try again.', err:'Something went wrong. Please try again.',
  fileMode:'Your account works only on the symposium website, not in a saved copy of the page.',
  authLead:'An account lets you submit a paper and follow your application. You do not need one just to register for the symposium.',
  tabLogin:'Sign in', tabRegister:'Create account', tabForgot:'Forgot password?', password2:'Repeat password', passHint:'At least 8 characters, not only digits.',
  btnLogin:'Sign in', btnRegister:'Create account', btnReset:'Send link',
  resetSent:'If this address is registered, we have sent it a link to reset your password.', passMismatch:'The passwords do not match.',
  registeredOk:'Your account has been created. We have emailed you a link to confirm your address.', fillIn:'Please fill in: ',
  hello:'Signed in as', logout:'Sign out',
  notVerified:'Your email is not confirmed yet. You need to confirm it before submitting a paper — open the link in our email.', resend:'Send the email again',
  emailVerifiedOk:'Your email is confirmed.', emailVerifiedBad:'The link is invalid or has expired. Sign in and request a new one.',
  tReg:'Application', tPapers:'Papers', tProfile:'Profile',
  noReg:'You have not applied to take part yet.', goReg:'Fill in the application',
  regLinkHint:'Applications sent from this email without signing in will appear here once you confirm your email.',
  orgComment:'Note from the organisers', edit:'Edit', save:'Save', cancel:'Cancel', cancelReg:'Withdraw application',
  confirmAgain:'Click again to confirm', saved:'Saved.', regCancelled:'Your application has been withdrawn.',
  newPaper:'Submit a paper', needVerify:'Confirm your email to submit a paper.', noPapers:'No papers yet.',
  authorsHint:'Comma-separated, as in the paper.', fileHint:'DOC, DOCX, PDF, RTF or ODT, up to {mb} MB.', fileKeep:'Leave empty to keep the current file.',
  free:'free', submitPaper:'Submit paper', paperSent:'Your paper has been submitted. We will email you about the decision.',
  download:'Download file', withdraw:'Withdraw paper', paperWithdrawn:'The paper has been withdrawn.', editorComment:'Note from the editors',
  fee:'Fee', feeNote:'The organisers will email you how to pay the fee once your paper has been reviewed.',
  revisionNote:'Upload the revised version — the paper will go back for review.', submittedAt:'Submitted', dirNone:'— not selected —',
  profileSaved:'Profile saved.', changePass:'Change password', passChanged:'Password changed.',
  emailFixed:'Your email cannot be changed. If you need a different address, contact the organisers.',
  resetTitle:'Set a new password', resetLead:'Choose a new password for your account.', resetBtn:'Save password',
  resetBad:'This link is incomplete. Request a new one on the sign-in page.', toLogin:'To sign in',
  regAsUser:'You are signed in as {name}. Your application will appear in your account.',
  regHave:'You have already applied. You can view, change or withdraw your application in your account.',
  toCabinet:'Go to my account', regAccountHint:'Want to follow your application?', regAccountLink:'Sign in or create an account with the same email.',
  regSentCab:'You can follow its status in your account.', pubCtaHint:'Papers are submitted through your participant account.',
  stReg:{new:'New — under review', confirmed:'Confirmed', waitlist:'Waiting list', rejected:'Declined', cancelled:'Withdrawn'},
  stPaper:{submitted:'Submitted', under_review:'Under review', revision:'Revision required', recommended:'Recommended to a journal', accepted:'Accepted for publication', rejected:'Declined', published:'Published', withdrawn:'Withdrawn'},
  f:{email:'Email', password:'Password', full_name:'Full name', organization:'Organisation', country:'Country', phone:'Phone', lang:'Language for emails',
     title:'Title', authors:'Authors', abstract:'Abstract', keywords:'Keywords', direction:'Research area', language:'Language of the paper',
     target:'Publication', file:'Manuscript file', comment:'Comment', old_password:'Current password', new_password:'New password',
     paper:'Paper', name:'Full name', org:'Organisation', day:'Day of attendance', role:'Participation', topic:'Presentation topic', note:'Comment'}
}
};
Object.values(CT).forEach(c => { c.f.password2 = c.password2; c.f.new_password2 = c.password2; });
const ct = () => CT[lang] || CT.en;
const EXTRA_ROUTES = ['cabinet', 'reset-password'];
const CAB = {me: undefined, flash: [], tab: null, authMode: 'login', data: null};
const META = {};
const ST_CLASS = {confirmed:'ok', accepted:'ok', published:'ok', recommended:'ok', paid:'ok',
                  new:'warn', waitlist:'warn', submitted:'warn', under_review:'warn', revision:'warn', pending:'warn', review:'warn',
                  rejected:'bad', cancelled:'bad', withdrawn:'bad', failed:'bad', refunded:'bad'};
const ACTIVE_REG = ['new', 'confirmed', 'waitlist'];
const hashQuery = () => new URLSearchParams(location.hash.split('?')[1] || '');
const tmpl = (s, o) => String(s).replace(/\{(\w+)\}/g, (_, k) => o[k] ?? '');

function getToken(){ try { return localStorage.getItem('afgs-token'); } catch(e){ return null; } }
function setToken(v){ try { v ? localStorage.setItem('afgs-token', v) : localStorage.removeItem('afgs-token'); } catch(e){} }

/* запрос к API: JSON или FormData; устаревший токен сбрасывается и запрос повторяется без него */
async function cabApi(method, path, body, retried){
  const isForm = body instanceof FormData;
  const h = apiHeaders(body !== undefined && !isForm);
  let r;
  try { r = await fetch(API + path, {method, headers:h, body: body === undefined ? undefined : (isForm ? body : JSON.stringify(body))}); }
  catch(e){ return {ok:false, status:0, data:{detail: ct().netErr}}; }
  let data = null;
  try { data = await r.json(); } catch(e){}
  if (r.status === 401 && getToken() && !retried){
    setToken(null); CAB.me = null; cabStatic();
    if (!path.startsWith('/api/auth/me')) return cabApi(method, path, body, true);
  }
  return {ok:r.ok, status:r.status, data};
}

/* текст ошибки API с подписями полей на языке сайта */
function cabErr(d){
  if (!d) return ct().err;
  if (typeof d === 'string') return d;
  if (Array.isArray(d)) return d.map(cabErr).join(' ');
  return Object.entries(d).map(([k, v]) => {
    const m = typeof v === 'object' ? cabErr(v) : String(v);
    const lab = ct().f[k];
    return lab ? `${lab}: ${m}` : m;
  }).join(' ');
}

async function loadMe(force){
  if (CAB.me !== undefined && !force) return CAB.me;
  if (!getToken()){ CAB.me = null; return null; }
  const r = await cabApi('GET', '/api/auth/me/');
  CAB.me = r.ok ? r.data : (r.status === 0 ? CAB.me ?? null : null);
  cabStatic();
  return CAB.me;
}

async function loadMeta(force){
  const c = META[lang];
  if (c && !force && Date.now() - c.at < 60000) return c.data;
  if (location.protocol === 'file:') return null;
  const r = await cabApi('GET', '/api/meta/');
  if (r.ok){ META[lang] = {data:r.data, at:Date.now()}; return r.data; }
  return c ? c.data : null;
}

/* ссылки «Вход / Кабинет» в шапке (в строке меню на компьютере, рядом с языками на телефоне) */
const PARTNER_FULL = {ru:'Комитет науки Министерства науки и высшего образования Республики Казахстан',
                      kk:'ҚР Ғылым және жоғары білім министрлігінің Ғылым комитеті',
                      en:'Science Committee, Ministry of Science and Higher Education of the Republic of Kazakhstan'};
function cabStatic(){
  const label = (CAB.me || (CAB.me === undefined && getToken())) ? ct().account : ct().login;
  ['acct-link', 'acct-link-nav'].forEach(id => {
    const a = document.getElementById(id);
    if (!a) return;
    a.textContent = label;
    if (route() === 'cabinet') a.setAttribute('aria-current', 'page'); else a.removeAttribute('aria-current');
  });
  const partner = document.querySelector('.partner');
  if (partner) partner.title = PARTNER_FULL[lang] || '';
}

/* «аль-Фараби», «Әл-Фараби», «Al-Farabi»: слово с дефисом не переносится по дефису */
const NB_SELECTOR = '.bt, h1, h2, h3, h4, .ev, .theme, .badge, .tab, .motto, nav.main a, .unav a, footer b, .fee';
function noBreakHyphens(){
  document.querySelectorAll(NB_SELECTOR).forEach(el => {
    const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
    const nodes = [];
    while (walker.nextNode()) nodes.push(walker.currentNode);
    nodes.forEach(n => {
      if (n.parentElement.classList.contains('nw') || !/[\p{L}\d]-[\p{L}\d]/u.test(n.data)) return;
      const frag = document.createDocumentFragment();
      let last = 0;
      for (const m of n.data.matchAll(/[\p{L}\d]+(?:-[\p{L}\d]+)+/gu)){
        frag.append(n.data.slice(last, m.index));
        const span = document.createElement('span'); span.className = 'nw'; span.textContent = m[0];
        frag.append(span); last = m.index + m[0].length;
      }
      frag.append(n.data.slice(last));
      n.replaceWith(frag);
    });
  });
}
let nbQueued = false;
new MutationObserver(() => {
  if (nbQueued) return;
  nbQueued = true;
  requestAnimationFrame(() => { nbQueued = false; noBreakHyphens(); });
}).observe(document.body, {childList:true, subtree:true, characterData:true});

/* ---- мелкие помощники разметки ---- */
const cabNote = (txt, err) => `<div class="notice${err ? ' err' : ''}">${esc(txt)}</div>`;
const cabSt = (map, code) => `<span class="st st-${ST_CLASS[code] || 'warn'}"><i></i>${esc(map[code] || code)}</span>`;
const cabDl = (k, v) => v ? `<div><dt>${esc(k)}</dt><dd>${esc(v)}</dd></div>` : '';
function cabMoney(a, c){
  const n = Number(a);
  const s = new Intl.NumberFormat('ru-RU', {maximumFractionDigits:2}).format(n).replace(/\s/g, ' ');
  return `${s} ${c === 'KZT' ? (lang === 'en' ? 'KZT' : '₸') : c}`;
}
function cabDate(iso){
  if (!iso) return '';
  try { return new Date(iso).toLocaleDateString({ru:'ru-RU', kk:'kk-KZ', en:'en-GB'}[lang], {day:'numeric', month:'long', year:'numeric'}); }
  catch(e){ return iso.slice(0, 10); }
}
function cabFld(o){
  const id = 'c-' + (o.form || '') + '-' + o.name, type = o.type || 'text';
  const req = o.req ? ' required' : '';
  let input;
  if (type === 'textarea') input = `<textarea id="${id}" name="${o.name}" rows="${o.rows || 5}"${req}>${esc(o.value || '')}</textarea>`;
  else if (type === 'select') input = `<select id="${id}" name="${o.name}">${o.options.map(([v, l]) => `<option value="${esc(v)}"${String(v) === String(o.value ?? '') ? ' selected' : ''}>${esc(l)}</option>`).join('')}</select>`;
  else input = `<input id="${id}" name="${o.name}" type="${type}"${o.ac ? ` autocomplete="${o.ac}"` : ''}${o.accept ? ` accept="${o.accept}"` : ''}${o.readonly ? ' readonly' : ''}${req}${type === 'file' ? '' : ` value="${esc(o.value || '')}"`}>`;
  return `<div class="field${o.half ? '' : ' full'}"><label for="${id}">${esc(o.label)}${o.req ? ' *' : ''}</label>${input}${o.hint ? `<span class="hint">${esc(o.hint)}</span>` : ''}</div>`;
}
const cabSubmitRow = (label, cancelAct) => `<div class="field full"><div class="cab-actions" style="margin-top:0"><button class="btn btn-maroon btn-sm" type="submit">${esc(label)}</button>${cancelAct ? `<button type="button" class="linkbtn" data-act="${cancelAct}">${esc(ct().cancel)}</button>` : ''}</div></div><div class="field full formmsg" aria-live="polite"></div>`;
function busy(form, on){ form.querySelectorAll('button').forEach(b => { b.disabled = on; }); form.setAttribute('aria-busy', on); }
function formErr(form, txt){ const m = form.querySelector('.formmsg'); if (m) m.innerHTML = txt ? cabNote(txt, true) : ''; }
function missing(form, names){
  const E = form.elements, miss = names.filter(n => { const el = E[n]; return el && (el.type === 'file' ? !el.files.length : !String(el.value).trim()); });
  form.querySelectorAll('.field.err').forEach(x => x.classList.remove('err'));
  miss.forEach(n => E[n].closest('.field')?.classList.add('err'));
  return miss.length ? ct().fillIn + miss.map(n => ct().f[n] || n).join(', ') : '';
}
function flashHTML(){ return CAB.flash.splice(0).map(([m, e]) => cabNote(m, e)).join(''); }
function cabFlash(msg, err){ CAB.flash.push([msg, err]); }
function dirOpts(current){
  const D = P();
  const list = [D[1].rows[10], D[1].rows[13], D[1].rows[15], D[2].rows[8], D[2].rows[9], D[2].rows[10]].filter(Boolean).map(r => r.title);
  if (current && !list.includes(current)) list.push(current);
  return [['', ct().dirNone], ...list.map(x => [x, x])];
}
const metaNow = () => (CAB.data && CAB.data.meta) || {};
function targetLabel(code, fallback){ const x = (metaNow().publication_targets || []).find(t => t.value === code); return x ? x.label : (fallback || code); }

/* ---- страницы ---- */
PAGES.cabinet = () => { setTimeout(initCabinet); return head(ct().cabTitle, ct().cabLead) + `<section class="section cab" style="padding-top:28px"><div class="wrap"><div id="cab"><p class="muted">${esc(ct().loading)}</p></div></div></section>`; };
PAGES['reset-password'] = () => { setTimeout(initReset); return head(ct().resetTitle, ct().resetLead) + `<section class="section cab" style="padding-top:28px"><div class="wrap"><div id="cab"></div></div></section>`; };

async function initCabinet(){
  const box = $('#cab'); if (!box) return;
  const T = ct();
  if (location.protocol === 'file:'){ box.innerHTML = cabNote(T.fileMode, true); return; }
  const q = hashQuery();
  if (q.has('email_verified')){ const ok = q.get('email_verified') === '1'; cabFlash(ok ? T.emailVerifiedOk : T.emailVerifiedBad, !ok); }
  if (q.has('tab')) CAB.tab = q.get('tab');
  if ([...q.keys()].length) history.replaceState(null, '', '#/cabinet');
  const me = await loadMe(true);
  if (!$('#cab')) return;
  if (!me) return renderAuth();
  renderCabinet();
}

function renderAuth(mode){
  const box = $('#cab'); if (!box) return;
  const T = ct(), F = T.f;
  CAB.authMode = mode || CAB.authMode || 'login';
  const m = CAB.authMode;
  const tabs = [['login', T.tabLogin], ['register', T.tabRegister], ['forgot', T.tabForgot]]
    .map(([k, l]) => `<button type="button" class="tab" aria-selected="${k === m}" data-auth="${k}">${esc(l)}</button>`).join('');
  let form = '';
  if (m === 'login') form = cabFld({form:'a', name:'email', label:F.email, type:'email', ac:'email', req:true, half:true})
    + cabFld({form:'a', name:'password', label:F.password, type:'password', ac:'current-password', req:true, half:true}) + cabSubmitRow(T.btnLogin);
  else if (m === 'register') form = cabFld({form:'a', name:'full_name', label:F.full_name, ac:'name', req:true})
    + cabFld({form:'a', name:'organization', label:F.organization, ac:'organization', half:true}) + cabFld({form:'a', name:'country', label:F.country, ac:'country-name', half:true})
    + cabFld({form:'a', name:'email', label:F.email, type:'email', ac:'email', req:true, half:true}) + cabFld({form:'a', name:'phone', label:F.phone, type:'tel', ac:'tel', half:true})
    + cabFld({form:'a', name:'password', label:F.password, type:'password', ac:'new-password', req:true, half:true, hint:T.passHint})
    + cabFld({form:'a', name:'password2', label:T.password2, type:'password', ac:'new-password', req:true, half:true}) + cabSubmitRow(T.btnRegister);
  else form = cabFld({form:'a', name:'email', label:F.email, type:'email', ac:'email', req:true, half:true}) + cabSubmitRow(T.btnReset);
  box.innerHTML = flashHTML() + `<p class="muted" style="max-width:44em">${esc(T.authLead)}</p><div class="tabs" role="tablist">${tabs}</div><form class="form" id="authform" novalidate>${form}</form>`;
  box.querySelectorAll('[data-auth]').forEach(b => b.onclick = () => renderAuth(b.dataset.auth));
  $('#authform').onsubmit = submitAuth;
}

async function submitAuth(e){
  e.preventDefault();
  const f = e.target, T = ct(), m = CAB.authMode, v = Object.fromEntries(new FormData(f));
  const need = m === 'register' ? ['full_name', 'email', 'password', 'password2'] : m === 'login' ? ['email', 'password'] : ['email'];
  const miss = missing(f, need);
  if (miss) return formErr(f, miss);
  if (m === 'register' && v.password !== v.password2) return formErr(f, T.passMismatch);
  busy(f, true);
  let r;
  if (m === 'login') r = await cabApi('POST', '/api/auth/login/', {email:v.email.trim(), password:v.password});
  else if (m === 'register') r = await cabApi('POST', '/api/auth/register/', {email:v.email.trim(), password:v.password, full_name:v.full_name.trim(),
    organization:v.organization.trim(), country:v.country.trim(), phone:v.phone.trim(), lang});
  else {
    r = await cabApi('POST', '/api/auth/password/reset/', {email:v.email.trim()});
    busy(f, false);
    if (r.ok){ f.reset(); f.querySelector('.formmsg').innerHTML = cabNote(T.resetSent); } else formErr(f, cabErr(r.data));
    return;
  }
  busy(f, false);
  if (!r.ok) return formErr(f, cabErr(r.data));
  setToken(r.data.token); CAB.me = r.data.user; cabStatic();
  if (m === 'register') cabFlash(T.registeredOk);
  renderCabinet();
}

async function renderCabinet(){
  const box = $('#cab'); if (!box) return;
  if (!CAB.data) box.innerHTML = `<p class="muted">${esc(ct().loading)}</p>`;
  const [regs, papers, meta] = await Promise.all([cabApi('GET', '/api/registrations/'), cabApi('GET', '/api/papers/'), loadMeta(true)]);
  if (!$('#cab')) return;
  if (!CAB.me) return renderAuth('login');
  CAB.data = {regs: regs.ok ? regs.data : [], papers: papers.ok ? papers.data : [], meta: meta || {}};
  if (!regs.ok && regs.status === 0) cabFlash(ct().netErr, true);
  drawCabinet();
}

function drawCabinet(){
  const box = $('#cab'); if (!box || !CAB.me || !CAB.data) return;
  const T = ct(), me = CAB.me, d = CAB.data;
  const tabs = [['reg', T.tReg, d.regs.length], ['papers', T.tPapers, d.papers.length], ['profile', T.tProfile, 0]];
  if (!tabs.some(x => x[0] === CAB.tab)) CAB.tab = 'reg';
  const panes = {reg:paneReg, papers:panePapers, profile:paneProfile};
  box.innerHTML = `<div id="cabmsg" aria-live="polite">${flashHTML()}</div>`
    + `<div class="cab-top"><div><span class="muted">${esc(T.hello)}</span> <b>${esc(me.full_name)}</b> <span class="muted">· ${esc(me.email)}</span></div>`
    + `<button type="button" class="btn btn-outline btn-sm" data-act="logout">${esc(T.logout)}</button></div>`
    + (me.email_verified ? '' : `<div class="notice err">${esc(T.notVerified)} <button type="button" class="linkbtn" data-act="resend">${esc(T.resend)}</button></div>`)
    + `<div class="tabs" role="tablist">${tabs.map(([k, l, n]) => `<button type="button" class="tab" role="tab" aria-selected="${k === CAB.tab}" data-cabtab="${k}">${esc(l)}${n ? ` <span class="cnt">${n}</span>` : ''}</button>`).join('')}</div>`
    + `<div id="cabpane" role="tabpanel">${panes[CAB.tab]()}</div>`;
  box.onclick = cabClick;
  box.onsubmit = cabSubmit;
}
function cabMsg(txt, err){
  const m = $('#cabmsg'); if (!m) return;
  m.innerHTML = cabNote(txt, err);
  m.scrollIntoView({behavior:'smooth', block:'nearest'});
}

/* ---- вкладка «Заявка» ---- */
function paneReg(){
  const T = ct(), F = t().f, d = CAB.data;
  if (!d.regs.length) return `<div class="cab-card"><p style="margin-top:0">${esc(T.noReg)}</p><a class="btn btn-maroon btn-sm" href="#/participants">${esc(T.goReg)} ${ARROW}</a>`
    + (CAB.me.email_verified ? '' : `<p class="hint" style="margin-bottom:0">${esc(T.regLinkHint)}</p>`) + `</div>`;
  return d.regs.map(r => {
    if (CAB.editReg === r.id) return regEditForm(r);
    const active = ACTIVE_REG.includes(r.status);
    const dayTxt = F.dayOpts[['6', '7', 'both'].indexOf(r.day)] || r.day, roleTxt = F.roleOpts[['listener', 'speaker'].indexOf(r.role)] || r.role;
    return `<article class="cab-card"><div class="cab-head"><h3>${esc(r.name)}</h3>${cabSt(T.stReg, r.status)}</div>`
      + `<dl class="cab-dl">${cabDl(T.f.day, dayTxt)}${cabDl(T.f.role, roleTxt)}${cabDl(T.f.org, r.org)}${cabDl(T.f.country, r.country)}`
      + `${cabDl(T.f.direction, r.direction)}${r.role === 'speaker' ? cabDl(T.f.topic, r.topic) : ''}${cabDl(T.f.note, r.note)}${cabDl(T.submittedAt, cabDate(r.created_at))}</dl>`
      + (r.admin_comment ? cabNote(`${T.orgComment}: ${r.admin_comment}`) : '')
      + (active ? `<div class="cab-actions"><button type="button" class="btn btn-outline btn-sm" data-act="reg-edit" data-id="${r.id}">${esc(T.edit)}</button>`
        + `<button type="button" class="linkbtn danger" data-act="reg-cancel" data-id="${r.id}" data-confirm="1">${esc(T.cancelReg)}</button></div>` : '')
      + `</article>`;
  }).join('');
}
function regEditForm(r){
  const T = ct(), F = t().f;
  const radios = (name, vals, labels, cur) => `<div class="choices">${vals.map((v, i) => `<label class="choice"><input type="radio" name="${name}" value="${v}"${v === cur ? ' checked' : ''}><span>${esc(labels[i])}</span></label>`).join('')}</div>`;
  return `<article class="cab-card"><form class="form" data-form="reg-edit" data-id="${r.id}" novalidate>`
    + `<fieldset class="field full"><legend>${esc(F.days)}</legend>${radios('day', ['6', '7', 'both'], F.dayOpts, r.day)}</fieldset>`
    + `<fieldset class="field full"><legend>${esc(F.role)}</legend>${radios('role', ['listener', 'speaker'], F.roleOpts, r.role)}</fieldset>`
    + cabFld({form:'r' + r.id, name:'direction', label:T.f.direction, type:'select', options:dirOpts(r.direction), value:r.direction})
    + cabFld({form:'r' + r.id, name:'topic', label:T.f.topic, value:r.topic, hint:F.topicHint})
    + cabFld({form:'r' + r.id, name:'note', label:T.f.note, type:'textarea', rows:3, value:r.note})
    + cabSubmitRow(T.save, 'reg-edit-cancel') + `</form></article>`;
}

/* ---- вкладка «Статьи» ---- */
function panePapers(){
  const T = ct(), d = CAB.data, m = d.meta, pm = m.papers || {open:true};
  let top;
  if (CAB.newPaper && pm.open) top = `<div class="cab-card">${paperForm(null)}</div>`;
  else if (!pm.open) top = cabNote(pm.closed_message || '', true);
  else if (pm.require_verified_email !== false && !CAB.me.email_verified) top = cabNote(T.needVerify, true);
  else top = `<div class="cab-actions" style="margin-top:0"><button type="button" class="btn btn-maroon" data-act="paper-new">${esc(T.newPaper)} ${ARROW}</button>`
    + (pm.deadline_text ? `<span class="hint">${esc(pm.deadline_text)}</span>` : '') + `</div>`;
  const list = d.papers.length ? d.papers.map(paperCard).join('') : `<p class="muted" style="margin-top:24px">${esc(T.noPapers)}</p>`;
  return top + list;
}
function paperForm(p){
  const T = ct(), F = T.f, m = metaNow(), key = p ? 'p' + p.id : 'pn';
  const targets = (m.publication_targets || []).filter(x => x.is_active || (p && x.value === p.target))
    .map(x => [x.value, `${x.label} — ${Number(x.fee_amount) > 0 ? cabMoney(x.fee_amount, x.fee_currency) : T.free}`]);
  const mb = (m.papers && m.papers.max_upload_mb) || 20;
  return `<form class="form" data-form="${p ? 'paper-edit' : 'paper-new'}"${p ? ` data-id="${p.id}"` : ''} novalidate>`
    + (p && p.status === 'revision' ? `<div class="field full">${cabNote(T.revisionNote)}</div>` : '')
    + cabFld({form:key, name:'title', label:F.title, req:true, value:p && p.title})
    + cabFld({form:key, name:'authors', label:F.authors, req:true, value:p && p.authors, hint:T.authorsHint})
    + cabFld({form:key, name:'abstract', label:F.abstract, type:'textarea', rows:6, req:true, value:p && p.abstract})
    + cabFld({form:key, name:'keywords', label:F.keywords, value:p && p.keywords})
    + cabFld({form:key, name:'direction', label:F.direction, type:'select', options:dirOpts(p && p.direction), value:p ? p.direction : ''})
    + cabFld({form:key, name:'target', label:F.target, type:'select', options:targets, value:p ? p.target : 'proceedings', half:true})
    + cabFld({form:key, name:'language', label:F.language, type:'select', options:Object.entries(LANG_NAMES), value:p ? p.language : lang, half:true})
    + cabFld({form:key, name:'file', label:F.file, type:'file', accept:'.doc,.docx,.pdf,.rtf,.odt', req:!p, hint:(p ? T.fileKeep + ' ' : '') + tmpl(T.fileHint, {mb})})
    + cabSubmitRow(p ? T.save : T.submitPaper, p ? 'paper-edit-cancel' : 'paper-new-cancel') + `</form>`;
}
function paperCard(p){
  const T = ct();
  if (CAB.editPaper === p.id) return `<article class="cab-card">${paperForm(p)}</article>`;
  const editable = ['submitted', 'revision'].includes(p.status);
  // взнос — только для сведения: оплата проходит вне сайта, по письму оргкомитета
  const paid = Number(p.fee_amount) > 0;
  const feeShown = paid ? cabMoney(p.fee_amount, p.fee_currency) : T.free;
  return `<article class="cab-card"><div class="cab-head"><h3>${esc(p.title)}</h3>${cabSt(T.stPaper, p.status)}</div>`
    + `<dl class="cab-dl">${cabDl(T.f.target, targetLabel(p.target, p.target_display))}${cabDl(T.fee, feeShown)}`
    + `${cabDl(T.f.authors, p.authors)}${cabDl(T.f.direction, p.direction)}${cabDl(T.f.language, LANG_NAMES[p.language])}${cabDl(T.submittedAt, cabDate(p.created_at))}</dl>`
    + (p.reviewer_comment ? cabNote(`${T.editorComment}: ${p.reviewer_comment}`) : '')
    + (p.status === 'revision' ? `<p class="hint">${esc(T.revisionNote)}</p>` : '')
    + (paid && !['rejected', 'withdrawn'].includes(p.status) ? `<p class="hint">${esc(T.feeNote)}</p>` : '')
    + `<div class="cab-actions"><button type="button" class="btn btn-outline btn-sm" data-act="paper-file" data-id="${p.id}" data-name="${esc(p.original_filename || 'paper')}">${esc(T.download)}</button>`
    + (editable ? `<button type="button" class="btn btn-outline btn-sm" data-act="paper-edit" data-id="${p.id}">${esc(T.edit)}</button>` : '')
    + (!['published', 'withdrawn', 'rejected'].includes(p.status) ? `<button type="button" class="linkbtn danger" data-act="paper-withdraw" data-id="${p.id}" data-confirm="1">${esc(T.withdraw)}</button>` : '')
    + `</div></article>`;
}
/* ---- вкладка «Профиль» ---- */
function paneProfile(){
  const T = ct(), F = T.f, me = CAB.me;
  return `<form class="form" data-form="profile" novalidate>`
    + cabFld({form:'pf', name:'email', label:F.email, value:me.email, readonly:true, hint:T.emailFixed, half:true})
    + cabFld({form:'pf', name:'full_name', label:F.full_name, value:me.full_name, req:true, half:true})
    + cabFld({form:'pf', name:'organization', label:F.organization, value:me.organization, half:true})
    + cabFld({form:'pf', name:'country', label:F.country, value:me.country, half:true})
    + cabFld({form:'pf', name:'phone', label:F.phone, type:'tel', value:me.phone, half:true})
    + cabFld({form:'pf', name:'lang', label:F.lang, type:'select', options:Object.entries(LANG_NAMES), value:me.lang, half:true})
    + cabSubmitRow(T.save) + `</form><h3 class="subh">${esc(T.changePass)}</h3><form class="form" data-form="password" novalidate>`
    + cabFld({form:'pw', name:'old_password', label:F.old_password, type:'password', ac:'current-password', req:true})
    + cabFld({form:'pw', name:'new_password', label:F.new_password, type:'password', ac:'new-password', req:true, half:true, hint:T.passHint})
    + cabFld({form:'pw', name:'new_password2', label:T.password2, type:'password', ac:'new-password', req:true, half:true})
    + cabSubmitRow(T.changePass) + `</form>`;
}

/* ---- клики и формы кабинета ---- */
async function cabClick(e){
  const b = e.target.closest('[data-act],[data-cabtab]');
  if (!b) return;
  const T = ct(), id = b.dataset.id;
  if (b.dataset.cabtab){ CAB.tab = b.dataset.cabtab; return drawCabinet(); }
  if (b.dataset.confirm && !b.dataset.armed){
    b.dataset.armed = '1'; b.dataset.label = b.textContent; b.textContent = T.confirmAgain;
    setTimeout(() => { if (b.isConnected){ delete b.dataset.armed; b.textContent = b.dataset.label; } }, 4000);
    return;
  }
  const act = b.dataset.act;
  const refresh = (msg, err) => { if (msg) cabFlash(msg, err); return renderCabinet(); };
  if (act === 'logout'){ await cabApi('POST', '/api/auth/logout/'); setToken(null); CAB.me = null; CAB.data = null; cabStatic(); return renderAuth('login'); }
  if (act === 'resend'){ const r = await cabApi('POST', '/api/auth/email/resend/'); return cabMsg(r.ok ? r.data.detail : cabErr(r.data), !r.ok); }
  if (act === 'reg-edit'){ CAB.editReg = +id; return drawCabinet(); }
  if (act === 'reg-edit-cancel'){ CAB.editReg = null; return drawCabinet(); }
  if (act === 'reg-cancel'){ const r = await cabApi('POST', `/api/registrations/${id}/cancel/`); return r.ok ? refresh(T.regCancelled) : cabMsg(cabErr(r.data), true); }
  if (act === 'paper-new'){ CAB.newPaper = true; return drawCabinet(); }
  if (act === 'paper-new-cancel'){ CAB.newPaper = false; return drawCabinet(); }
  if (act === 'paper-edit'){ CAB.editPaper = +id; return drawCabinet(); }
  if (act === 'paper-edit-cancel'){ CAB.editPaper = null; return drawCabinet(); }
  if (act === 'paper-withdraw'){ const r = await cabApi('POST', `/api/papers/${id}/withdraw/`); return r.ok ? refresh(T.paperWithdrawn) : cabMsg(cabErr(r.data), true); }
  if (act === 'paper-file') return cabDownload(`/api/papers/${id}/file/`, b.dataset.name);
}

async function cabSubmit(e){
  const f = e.target.closest('form[data-form]');
  if (!f) return;
  e.preventDefault();
  const T = ct(), kind = f.dataset.form, id = f.dataset.id, fd = new FormData(f);
  const done = (msg) => { cabFlash(msg); return renderCabinet(); };
  let need = [], r;
  if (kind === 'paper-new') need = ['title', 'authors', 'abstract', 'file'];
  if (kind === 'paper-edit') need = ['title', 'authors', 'abstract'];
  if (kind === 'profile') need = ['full_name'];
  if (kind === 'password') need = ['old_password', 'new_password', 'new_password2'];
  const miss = missing(f, need);
  if (miss) return formErr(f, miss);
  if (kind === 'password' && fd.get('new_password') !== fd.get('new_password2')) return formErr(f, T.passMismatch);
  formErr(f, ''); busy(f, true);
  if (kind === 'reg-edit') r = await cabApi('PATCH', `/api/registrations/${id}/`, {day:fd.get('day'), role:fd.get('role'), direction:fd.get('direction'),
    topic:(fd.get('topic') || '').trim(), note:(fd.get('note') || '').trim(), lang});
  else if (kind === 'paper-new' || kind === 'paper-edit'){
    const file = fd.get('file');
    if (file && !file.name) fd.delete('file');
    r = await cabApi(kind === 'paper-new' ? 'POST' : 'PATCH', kind === 'paper-new' ? '/api/papers/' : `/api/papers/${id}/`, fd);
  }
  else if (kind === 'profile') r = await cabApi('PATCH', '/api/auth/me/', {full_name:fd.get('full_name').trim(), organization:fd.get('organization').trim(),
    country:fd.get('country').trim(), phone:fd.get('phone').trim(), lang:fd.get('lang')});
  else if (kind === 'password') r = await cabApi('POST', '/api/auth/password/change/', {old_password:fd.get('old_password'), new_password:fd.get('new_password')});
  busy(f, false);
  if (!r || !r.ok) return formErr(f, cabErr(r && r.data));
  if (kind === 'reg-edit'){ CAB.editReg = null; return done(T.saved); }
  if (kind === 'paper-new'){ CAB.newPaper = false; return done(T.paperSent); }
  if (kind === 'paper-edit'){ CAB.editPaper = null; return done(T.saved); }
  if (kind === 'profile'){ CAB.me = r.data; return done(T.profileSaved); }
  if (kind === 'password'){ setToken(r.data.token); CAB.me = r.data.user; return done(T.passChanged); }
}

async function cabDownload(path, name){
  let r;
  try { r = await fetch(API + path, {headers:apiHeaders(false)}); } catch(e){ return cabMsg(ct().netErr, true); }
  if (!r.ok) return cabMsg(ct().err, true);
  const url = URL.createObjectURL(await r.blob());
  const a = document.createElement('a'); a.href = url; a.download = name || 'file';
  document.body.appendChild(a); a.click(); a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 4000);
}

/* ---- страница нового пароля (ссылка из письма) ---- */
function initReset(){
  const box = $('#cab'); if (!box) return;
  const T = ct(), q = hashQuery(), uid = q.get('uid'), token = q.get('token');
  if (!uid || !token){ box.innerHTML = cabNote(T.resetBad, true) + `<p><a href="#/cabinet">${esc(T.toLogin)}</a></p>`; return; }
  box.innerHTML = `<form class="form" id="resetform" novalidate>`
    + cabFld({form:'rs', name:'new_password', label:T.f.new_password, type:'password', ac:'new-password', req:true, half:true, hint:T.passHint})
    + cabFld({form:'rs', name:'new_password2', label:T.password2, type:'password', ac:'new-password', req:true, half:true})
    + cabSubmitRow(T.resetBtn) + `</form>`;
  $('#resetform').onsubmit = async e => {
    e.preventDefault();
    const f = e.target, v = Object.fromEntries(new FormData(f));
    const miss = missing(f, ['new_password', 'new_password2']);
    if (miss) return formErr(f, miss);
    if (v.new_password !== v.new_password2) return formErr(f, T.passMismatch);
    busy(f, true);
    const r = await cabApi('POST', '/api/auth/password/reset/confirm/', {uid, token, new_password:v.new_password});
    busy(f, false);
    if (!r.ok) return formErr(f, cabErr(r.data));
    setToken(r.data.token); CAB.me = r.data.user; cabFlash(T.passChanged);
    location.hash = '#/cabinet';
  };
}

/* ---- форма заявки на странице «Участникам»: срок, закрытый приём, данные из аккаунта ---- */
async function regFormState(form){
  const box = document.getElementById('regstate');
  if (!box || !form || location.protocol === 'file:') return;
  const T = ct();
  const [meta, me] = await Promise.all([loadMeta(), loadMe()]);
  if (!form.isConnected) return;
  const parts = [];
  const rm = meta && meta.registration;
  if (rm && !rm.open){ form.classList.add('hidden'); box.innerHTML = cabNote(rm.closed_message, true); return; }
  if (rm && rm.deadline_text) parts.push(cabNote(rm.deadline_text));
  if (me){
    const regs = await cabApi('GET', '/api/registrations/');
    if (!form.isConnected) return;
    if (regs.ok && regs.data.some(r => ACTIVE_REG.includes(r.status))){
      form.classList.add('hidden');
      box.innerHTML = parts.join('') + `<div class="notice">${esc(T.regHave)} <a href="#/cabinet">${esc(T.toCabinet)}</a></div>`;
      return;
    }
    const E = form.elements, put = (n, v) => { if (E[n] && !E[n].value && v) E[n].value = v; };
    put('name', me.full_name); put('org', me.organization); put('country', me.country); put('email', me.email); put('phone', me.phone);
    parts.push(cabNote(tmpl(T.regAsUser, {name:me.full_name})));
  } else parts.push(`<p class="hint">${esc(T.regAccountHint)} <a href="#/cabinet">${esc(T.regAccountLink)}</a></p>`);
  form.classList.remove('hidden');
  box.innerHTML = parts.join('');
}

/* ---- суммы взносов на странице «Публикации» — из админки ---- */
function feeText(target, fallback){
  const c = META[lang];
  if (!c){
    if (location.protocol !== 'file:') loadMeta().then(d => { if (d && route() === 'publications') render(true); });
    return fallback;
  }
  const x = (c.data.publication_targets || []).find(t => t.value === target);
  return x ? (Number(x.fee_amount) > 0 ? cabMoney(x.fee_amount, x.fee_currency) : ct().free) : fallback;
}

/* ---- программа из админки (/api/program/); встроенная во фронт — запасной вариант ---- */
const PRG = {};
async function loadProgram(){
  const l = lang; PRG[l] = null;
  if (location.protocol === 'file:') return;
  try {
    const r = await fetch(API + '/api/program/?lang=' + l);
    if (r.ok){ const d = await r.json(); if (Array.isArray(d) && d.length) PRG[l] = d; }
  } catch(e) {}
  if (PRG[l] && route() === 'program' && l === lang) render(true);
}
const progDays = () => PRG[lang] || P();

/* ---- «Открыть на карте»: отдельная страница /map/ — площадка, отели, где поесть, остановки ---- */
// две кнопки: своя карта (/map/) и Google Карты (/map/google/ — карта из «Google Мои карты», если задана в админке)
const GMAP_LABEL = {ru:'Google Карты', kk:'Google Maps', en:'Google Maps'};
function mapMenu(vi, v, label){
  const google = `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(v[3])}`;
  if (location.protocol === 'file:') return `<a class="btn btn-outline" href="${google}" target="_blank" rel="noopener">${esc(label)}</a>`;
  return `<div class="map-btns"><a class="btn btn-outline" href="${API}/map/?v=${vi}&lang=${lang}" target="_blank" rel="noopener">${esc(label)}</a>`
    + `<a class="btn btn-outline" href="${API}/map/google/?v=${vi}" target="_blank" rel="noopener">${esc(GMAP_LABEL[lang] || GMAP_LABEL.en)}</a></div>`;
}
