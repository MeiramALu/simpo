"""
Правки сайта по документу «симпозиум сайт жаңа нұсқа» (15.10.2026) и новой программе (13.10.2026).

Вызывается из build_site.py после остальных шагов: apply(html) -> html.
Каждая правка проверяет, что нашла ровно ожидаемое место, иначе сборка останавливается.
"""
import base64
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BACKEND = HERE.parent
L3 = ('ru', 'kk', 'en')


def _fail(what):
    sys.exit(f'update_2026_10: не найдено место для правки «{what}» — структура фронта изменилась, поправьте update_2026_10.py')


def sub(html, old, new, count=1):
    if html.count(old) != count:
        _fail(old[:80])
    return html.replace(old, new)


def resub(html, pattern, repl, count, flags=0):
    new, n = re.subn(pattern, repl, html, flags=flags)
    if n != count:
        _fail(f'{pattern[:80]} (найдено {n}, ожидалось {count})')
    return new


def js(value):
    return json.dumps(value, ensure_ascii=False)


# ---------- организаторы: только название университета, без Чжэнчжоу, с логотипами ----------
ORGS = {
    'ru': [['Организатор', 'Комитет науки Министерства науки и высшего образования Республики Казахстан', 'science-committee'],
           ['Организатор', 'Казахский национальный университет имени аль-Фараби', 'kaznu'],
           ['Организатор', 'Институт философии, политологии и религиоведения Комитета науки МНВО РК', 'iph'],
           ['Партнёр', 'ICESCO – Исламская организация по вопросам образования, науки и культуры', 'icesco']],
    'kk': [['Ұйымдастырушы', 'Қазақстан Республикасы Ғылым және жоғары білім министрлігінің Ғылым комитеті', 'science-committee'],
           ['Ұйымдастырушы', 'Әл-Фараби атындағы Қазақ ұлттық университеті', 'kaznu'],
           ['Ұйымдастырушы', 'ҚР ҒЖБМ Ғылым комитетінің Философия, саясаттану және дінтану институты', 'iph'],
           ['Серіктес', 'ICESCO – Ислам әлемінің білім, ғылым және мәдениет ұйымы', 'icesco']],
    'en': [['Organiser', 'Science Committee of the Ministry of Science and Higher Education of the Republic of Kazakhstan', 'science-committee'],
           ['Organiser', 'Al-Farabi Kazakh National University', 'kaznu'],
           ['Organiser', 'Institute of Philosophy, Political Science and Religious Studies, Science Committee', 'iph'],
           ['Partner', 'ICESCO – Islamic World Educational, Scientific and Cultural Organization', 'icesco']],
}

# ---------- научные направления: четыре панели (время, зал, модератор — из документа) ----------
ROOM = {
    409: {'ru': 'конференц-зал №409 Научной библиотеки «Аль-Фараби»', 'kk': '«Әл-Фараби» ғылыми кітапханасының №409 конференц-залы',
          'en': 'conference hall No. 409, Al-Farabi Scientific Library'},
    408: {'ru': 'конференц-зал №408 Научной библиотеки «Аль-Фараби»', 'kk': '«Әл-Фараби» ғылыми кітапханасының №408 конференц-залы',
          'en': 'conference hall No. 408, Al-Farabi Scientific Library'},
}
DIRS = [
    {'time': '14:30 – 16:00', 'room': ROOM[409],
     't': {'ru': 'Наследие аль-Фараби и глобальные вызовы', 'kk': 'Әл-Фараби мұрасы және жаһандық сын-қатерлер',
           'en': 'Al-Farabi’s Legacy and Global Challenges'},
     's': {'ru': 'Добродетельное общество, нравственность, управление, государственность и межкультурный диалог.',
           'kk': 'Қайырымды қоғам, адамгершілік, басқару, мемлекеттілік және мәдениетаралық диалог мәселелері.',
           'en': 'The virtuous society, morality, governance, statehood and intercultural dialogue.'},
     'l': {'ru': ['Нравственность, лидерство и государственность: идеи аль-Фараби для управления в ХХІ веке',
                  'Философия добродетельного общества аль-Фараби в условиях кризиса мирового порядка',
                  'Наследие аль-Фараби в контексте глобальной повестки дня ООН',
                  'Язык и межкультурный диалог в наследии аль-Фараби'],
           'kk': ['Адамгершілік, көшбасшылық және мемлекеттілік: XXI ғасырдағы басқару үшін Әл-Фараби тағылымдары',
                  'Әлемдік тәртіп дағдарысы жағдайындағы Әл-Фарабидің қайырымды қоғам философиясы',
                  'Әл-Фараби мұрасы және БҰҰ-ның жаһандық күн тәртібі',
                  'Әл-Фараби мұрасындағы тіл және мәдениетаралық диалог'],
           'en': ['Morality, Leadership, and Statehood: Insights from Al-Farabi for Governance in the XXI Century',
                  'Al-Farabi’s Philosophy of the Virtuous Society amid the Crisis of the World Order',
                  'Al-Farabi’s Legacy and the United Nations Global Agenda',
                  'Language and Intercultural Dialogue in Al-Farabi’s Legacy']},
     'mod': {'ru': 'Алтаев Жакипбек Алтаевич, доктор философских наук, профессор Казахского национального университета имени аль-Фараби',
             'kk': 'Алтаев Жакипбек Алтаевич, философия ғылымдарының докторы, Әл-Фараби атындағы Қазақ ұлттық университетінің профессоры',
             'en': 'Altayev Zhakypbek Altayevich, Doctor of Philosophy, Professor, Al-Farabi Kazakh National University'}},
    {'time': '14:30 – 16:00', 'room': ROOM[408],
     't': {'ru': 'Аль-Фараби и философия будущего', 'kk': 'Әл-Фараби және болашақ философиясы',
           'en': 'Al-Farabi and the Philosophy of the Future'},
     's': {'ru': 'Искусственный интеллект, этика технологий, образование и общество будущего.',
           'kk': 'Жасанды интеллект, технология этикасы, білім беру және болашақ қоғам туралы философиялық талқылаулар.',
           'en': 'Artificial intelligence, ethics of technology, education and the society of the future.'},
     'l': {'ru': ['Философия аль-Фараби и искусственный интеллект: этический баланс во взаимодействии человека и технологий',
                  'Будущее глобального порядка и этические принципы',
                  'Будущие модели образования, идентичности и государственности в контексте идей аль-Фараби'],
           'kk': ['Әл-Фараби философиясы және жасанды интеллект: адам мен технология арасындағы моральдық тепе-теңдік',
                  'Жаһандық тәртіптің болашағы және этикалық ұстанымдар',
                  'Әл-Фараби идеялары аясындағы білім беру, бірегейлік және мемлекеттіліктің болашақ модельдері'],
           'en': ['Al-Farabi’s Philosophy and Artificial Intelligence: Ethical Balance in Human–Technology Interaction',
                  'The Future of the Global Order and Ethical Principles',
                  'Future Models of Education, Identity, and Statehood in the Context of Al-Farabi’s Ideas']},
     'mod': {'ru': 'Тулеубаева Самал Абаевна, доктор филологических наук, и.о. профессора Евразийского национального университета имени Л.Н. Гумилева',
             'kk': 'Тулеубаева Самал Абаевна, филология ғылымдарының докторы, Л.Н. Гумилев атындағы Еуразия ұлттық университетінің профессоры м.а.',
             'en': 'Tuleubayeva Samal Abayevna, Doctor of Philology, Acting Professor, L.N. Gumilyov Eurasian National University'}},
    {'time': '16:20 – 18:00', 'room': ROOM[409],
     't': {'ru': 'Аль-Фараби и воспитание ответственного гражданина', 'kk': 'Әл-Фараби және жауапты азамат тәрбиесі',
           'en': 'Al-Farabi and the Development of Responsible Citizens'},
     's': {'ru': 'Добродетель, гражданская ответственность, этика служения и образование.',
           'kk': 'Ізгілік, азаматтық жауапкершілік, қызмет ету этикасы және білім беру мәселелері.',
           'en': 'Virtue, civic responsibility, the ethics of service and education.'},
     'l': {'ru': ['Добродетель как основа гражданственности в казахстанском обществе',
                  'Этика служения, честность и добропорядочность в культуре управления',
                  'Наследие аль-Фараби и трансформация образования'],
           'kk': ['Ізгілік – қазақстандық қоғамдағы азаматтықтың негізі',
                  'Басқару мәдениетіндегі қызмет ету этикасы, адалдық және парасаттылық',
                  'Әл-Фараби мұрасы және білім беру трансформациясы'],
           'en': ['Virtue as the Foundation of Citizenship in Kazakhstani Society',
                  'Ethics of Service, Integrity, and Prudence in the Culture of Governance',
                  'Al-Farabi’s Legacy and the Transformation of Education']},
     'mod': {'ru': 'Сағиқызы Аяжан Сагиевна, главный научный сотрудник Института философии, политологии и религиоведения КН МНВО РК, '
                   'доктор философских наук, профессор',
             'kk': 'Сағиқызы Аяжан Сагиевна, ҚР ҒЖБМ Ғылым комитетінің Философия, саясаттану және дінтану институтының бас ғылыми '
                   'қызметкері, философия ғылымдарының докторы, профессор',
             'en': 'Sagykyzy Ayazhan Sagiyevna, Chief Researcher, Institute of Philosophy, Political Science and Religious Studies, '
                   'CS MSHE RK, Doctor of Philosophy, Professor'}},
    {'time': '16:20 – 18:00', 'room': ROOM[408],
     't': {'ru': 'Казахстанский опыт постижения аль-Фараби', 'kk': 'Фарабитанудың қазақстандық тәжірибесі',
           'en': 'Kazakhstan’s Experience in Farabi Studies'},
     's': {'ru': 'Казахстанская школа фарабиеведения, переводы и интерпретации наследия, вклад отечественных учёных.',
           'kk': 'Қазақстандық фарабитану мектебі, мұраның аудармалары мен түсіндірмелері, отандық ғалымдардың үлесі.',
           'en': 'The Kazakhstani school of Farabi studies, translations and interpretations, and the contribution of national scholars.'},
     'l': {'ru': ['Становление и развитие казахстанской школы фарабиеведения: преемственность интеллектуального наследия аль-Фараби',
                  'Переводы и интерпретации наследия аль-Фараби в казахстанской науке',
                  'Вклад отечественных ученых в мировое фарабиеведение'],
           'kk': ['Қазақстандық фарабитану мектебінің қалыптасуы мен дамуы: әл-Фарабидің зияткерлік мұрасының сабақтастығы',
                  'Қазақстан ғылымындағы әл-Фараби мұрасының аудармалары мен интерпретациялары',
                  'Отандық ғалымдардың әлемдік әл-Фарабитануға қосқан үлесі'],
           'en': ['The Formation and Development of the Kazakhstani School of Farabi Studies: Continuity of Al-Farabi’s Intellectual Legacy',
                  'Translations and Interpretations of Al-Farabi’s Legacy in Kazakhstani Scholarship',
                  'The Contribution of Kazakhstani Scholars to Global Al-Farabi Studies']},
     'mod': {'ru': 'Коянбаева Гульнара Ромсеитовна, ведущий научный сотрудник Института философии, политологии и религиоведения КН МНВО РК, '
                   'кандидат философских наук, ассоциированный профессор',
             'kk': 'Коянбаева Гульнара Ромсеитовна, ҚР ҒЖБМ Ғылым комитетінің Философия, саясаттану және дінтану институтының жетекші ғылыми '
                   'қызметкері, философия ғылымдарының кандидаты, қауымдастырылған профессор',
             'en': 'Koyanbayeva Gulnara Romseitovna, Leading Researcher, Institute of Philosophy, Political Science and Religious Studies, '
                   'CS MSHE RK, Candidate of Philosophical Sciences, Associate Professor'}},
]


def dirs_js(lang):
    return js([{'t': d['t'][lang], 's': d['s'][lang], 'l': d['l'][lang], 'time': d['time'], 'room': d['room'][lang],
                'mod': d['mod'][lang]} for d in DIRS])


# ---------- встроенная программа (запасная, если сервер недоступен; по ней же «Ключевые события») ----------
def front_program():
    days = json.loads((BACKEND / 'program' / 'seed_program_2026_10.json').read_text(encoding='utf-8'))
    seed = json.loads((BACKEND / 'speakers' / 'seed_2026_10.json').read_text(encoding='utf-8'))
    cards = {c['key']: c for c in seed['cards']}
    out = {}
    for l in L3:
        res = []
        for d in days:
            rows = []
            for r in d['rows']:
                row = {'time': r['time'][l], 'title': r['title'][l], 'room': r['room'][l]}
                blocks = []
                for b in r['blocks']:
                    items = []
                    for it in b['items']:
                        if 'card' in it:
                            c = cards[it['card']]
                            topic = c[f'topic_{l}']
                            items.append({'name': c[f'name_{l}'], 'country': c[f'country_{l}'], 'role': c[f'role_{l}'], 'topic': topic,
                                          'tbc': not topic and c['group'] != 'welcome'})
                        else:
                            items.append({'text': it['text'][l]})
                    blocks.append({'label': b['label'][l] or None, 'items': items})
                if blocks:
                    row['blocks'] = blocks
                rows.append(row)
            event = [x for x in d['event'][l].splitlines() if x.strip()]
            res.append({'tab': d['tab'][l], 'date': d['date'][l], 'note': d['note'][l], 'event': event or None, 'rows': rows})
        out[l] = res
    return out


def logos_js():
    data = {}
    for p in sorted((HERE / 'logos').glob('*.png')):
        data[p.stem] = 'data:image/png;base64,' + base64.b64encode(p.read_bytes()).decode()
    return js(data)


def apply(html):
    # Глобальный → Международный (только название симпозиума; «глобальные вызовы» не трогаем)
    html = resub(html, r'Глобальн(ый|ого|ом|ому|ым)(\s+симпозиум)', r'Международн\1\2', 9)
    html = re.sub(r'ГЛОБАЛЬН(ЫЙ|ОГО)(\s+СИМПОЗИУМ)', r'МЕЖДУНАРОДН\1\2', html)
    html = re.sub(r'(?<![А-Яа-яӘәҒғҚқҢңӨөҰұҮүІіҺһ])Жаһандық(\s+симпозиум)', r'Халықаралық\1', html)
    html = re.sub(r'(?<![А-Яа-яӘәҒғҚқҢңӨөҰұҮүІіҺһ])жаһандық(\s+симпозиум)', r'халықаралық\1', html)
    html = re.sub(r'ЖАҺАНДЫҚ(\s+СИМПОЗИУМ)', r'ХАЛЫҚАРАЛЫҚ\1', html)
    html = re.sub(r'\bGlobal(\s+Symposium|\s+Al-Farabi\s+Symposium)', r'International\1', html)
    html = re.sub(r'\bGLOBAL(\s+SYMPOSIUM)', r'INTERNATIONAL\1', html)
    if re.search(r'[Гг]лобальн\w*\s+симпозиум|[Жж]аһандық\s+симпозиум|Global\s+Symposium', html):
        _fail('переименование Global → International')

    # три панели → четыре
    html = html.replace('три научные панели', 'четыре научные панели').replace('Три научные панели', 'Четыре научные панели')
    html = html.replace('үш ғылыми панел', 'төрт ғылыми панел').replace('three research panels', 'four research panels')

    # «Смотреть программу» → «Программа»
    for old, new in (("viewProgram:'Смотреть программу'", "viewProgram:'Программа'"),
                     ("viewProgram:'Бағдарламаны қарау'", "viewProgram:'Бағдарлама'"),
                     ("viewProgram:'View programme'", "viewProgram:'Programme'")):
        html = sub(html, old, new)

    # подзаголовок «Докладчики»: модераторов на странице больше нет, темы почти у всех известны
    for old, new in (("spLead:'Пленарные докладчики, участники панелей и модераторы сессий. Темы докладов уточняются.'",
                      "spLead:'Приветственные слова, пленарные доклады и участники четырёх панелей симпозиума 6 ноября.'"),
                     ("spLead:'Пленарлық баяндамашылар, панель қатысушылары және сессия модераторлары. Баяндама тақырыптары нақтыланады.'",
                      "spLead:'6 қарашадағы симпозиумның құттықтау сөздері, пленарлық баяндамалары және төрт панелінің қатысушылары.'"),
                     ("spLead:'Plenary speakers, panel participants and session moderators. Presentation topics are being confirmed.'",
                      "spLead:'Welcome remarks, plenary reports and the participants of the four panels of the symposium on 6 November.'")):
        html = sub(html, old, new)

    # языки: KZ, RU, EN
    html = sub(html, '<button data-lang="ru">RU</button><button data-lang="kk">KK</button><button data-lang="en">EN</button>',
               '<button data-lang="kk">KZ</button><button data-lang="ru">RU</button><button data-lang="en">EN</button>')

    # убрать герб министерства у переключателя языков
    html = resub(html, r'<div class="partners"><div class="partner"><img src="data:image/[^"]+" alt=""><span data-t="p1"></span></div></div>',
                 '', 1)

    # организаторы: данные, логотипы; данные «Концепции» больше не перезаписывают организаторов и направления
    html = sub(html, '  t.orgs[4][1] = c.partner5;\n', '')
    html = sub(html, "  c.dirs.forEach((d, i) => { if (t.dirs[i]) { t.dirs[i].t = d.t; t.dirs[i].l = d.l; } "
                     "else t.dirs.push({t:d.t, s:d.s || '', l:d.l}); });\n",
               '  // направления — из T.dirs (четыре панели, 13.10.2026)\n')
    for l, first in (('ru', 'Организатор'), ('kk', 'Ұйымдастырушы'), ('en', 'Organiser')):
        html = resub(html, r"orgs:\[\['" + first + r"'.*?\]\],", lambda m, l=l: f'orgs:{js(ORGS[l])},', 1, re.S)
    html = sub(html, 'function orgsBlock(){ const L=t(); return `<ul class="orgs">${L.orgs.map(o=>`<li><div class="r">${esc(o[0])}</div>'
                     '<div class="o">${esc(o[1])}</div></li>`).join(\'\')}</ul>`; }',
               f'const ORG_LOGOS = {logos_js()};\n'
               'function orgsBlock(){ const L=t(); return `<ul class="orgs">${L.orgs.map(o=>`<li><div class="r">${esc(o[0])}</div>'
               '<div class="o">${o[2] && ORG_LOGOS[o[2]] ? `<img class="org-logo" src="${ORG_LOGOS[o[2]]}" alt="">` : \'\'}'
               '<span>${esc(o[1])}</span></div></li>`).join(\'\')}</ul>`; }')

    # контакты — внутри страницы «Организаторы» (под списком); пункт меню «Контакты» убран, ссылка #/contacts ведёт туда же
    html = sub(html, "organizers: () => { const L=t(), c=CC[lang]; return head(L.orgTitle, L.orgLead) + sectionWrap('', orgsBlock()) + ",
               "organizers: () => { const L=t(), c=CC[lang]; return head(L.orgTitle, L.orgLead) + sectionWrap('', orgsBlock()) "
               "+ sectionWrap(L.ctTitle, `<p class=\"muted\" style=\"margin-top:-8px\">${esc(L.ctLead)}</p>` + contactsBlock(), true, 'contacts') + ")
    html = sub(html, "contacts: () => { const L=t(); return head(L.ctTitle, L.ctLead) + sectionWrap('', contactsBlock()); }",
               "contacts: () => { setTimeout(() => { const c = document.getElementById('contacts'); if (c) c.scrollIntoView(); }); "
               "return PAGES.organizers(); }")
    html = resub(html, r"(nav:\[[^\]]*?),\s*'(Контакты|Байланыс|Contacts)'\]", r'\1]', 3)
    html = sub(html, "[L.nav[8],'#/contacts']", "[L.ctTitle,'#/contacts']")

    # направления: четыре панели; время/зал/модератор — из данных, а не из строк старой программы
    for l, first in (('ru', 'Наследие'), ('kk', 'Әл-Фараби мұрасы'), ('en', 'Al-Farabi’s Legacy')):
        html = resub(html, r"dirs:\[\s*\{t:'" + first + r".*?\]\}\]", lambda m, l=l: f'dirs:{dirs_js(l)}', 1, re.S)
    html = sub(html, '  const L = t(); const rows = P()[1].rows; const refs = [10,13,15];', '  const L = t();')
    html = sub(html, '    const r = refs[i] !== undefined ? rows[refs[i]] : null; const mod = r && (r.blocks||[]).find(b=>b.label && MODLAB.test(b.label));',
               '    const r = d.time ? d : null;  // время, зал и модератор панели — в данных направления')
    html = sub(html, '${full&&mod&&mod.items[0]?`<div>${esc(L.moderator)}: ${esc(mod.items[0].name)}</div>`:\'\'}',
               '${full&&d.mod?`<div>${esc(L.moderator)}: ${esc(d.mod)}</div>`:\'\'}')
    # список направлений в форме заявки
    html = sub(html, 'dirOpts = [D[1].rows[10],D[1].rows[13],D[1].rows[15],D[2].rows[8],D[2].rows[9],D[2].rows[10]].map(r=>r.title);',
               'dirOpts = t().dirs.map(d=>d.t);')

    # встроенная программа = новая; «Ключевые события» на главной — строки новой программы
    html = resub(html, r'const PROGRAM = \{.*?\};\n', lambda m: f'const PROGRAM = {js(front_program())};\n', 1, re.S)
    html = sub(html, '  const pick = [[1,3],[1,5],[1,6],[1,7],[1,10],[1,13],[1,15],[1,16],[2,3],[2,6],[2,12]];',
               '  const pick = [[1,4],[1,6],[1,8],[1,9],[1,11],[1,12],[1,13],[1,15],[1,16],[1,17],[2,0]];')
    return html
