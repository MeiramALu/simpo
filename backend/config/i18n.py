"""
Сообщения API на языке посетителя сайта (ru / kk / en).

Язык выбирает ApiLanguageMiddleware по заголовку Accept-Language, который
сайт отправляет с каждым запросом. Админка всегда на русском.
"""
from django.utils import translation

LANGS = ('ru', 'kk', 'en')

MESSAGES = {
    'email_taken': {
        'ru': 'Пользователь с таким email уже зарегистрирован. Войдите или восстановите пароль.',
        'kk': 'Бұл email бойынша пайдаланушы тіркелген. Кіріңіз немесе құпиясөзді қалпына келтіріңіз.',
        'en': 'An account with this email already exists. Sign in or reset your password.',
    },
    'bad_credentials': {
        'ru': 'Неверный email или пароль.',
        'kk': 'Email немесе құпиясөз қате.',
        'en': 'Incorrect email or password.',
    },
    'inactive': {
        'ru': 'Учётная запись отключена. Напишите на al-farabi@kaznu.kz.',
        'kk': 'Есептік жазба өшірілген. al-farabi@kaznu.kz мекенжайына жазыңыз.',
        'en': 'This account is disabled. Please write to al-farabi@kaznu.kz.',
    },
    'bad_old_password': {
        'ru': 'Текущий пароль указан неверно.',
        'kk': 'Ағымдағы құпиясөз қате.',
        'en': 'The current password is incorrect.',
    },
    'reset_sent': {
        'ru': 'Если такой email зарегистрирован, на него отправлено письмо.',
        'kk': 'Егер бұл email тіркелген болса, оған хат жіберілді.',
        'en': 'If this email is registered, we have sent a message to it.',
    },
    'bad_link': {
        'ru': 'Ссылка недействительна или устарела.',
        'kk': 'Сілтеме жарамсыз немесе ескірген.',
        'en': 'The link is invalid or has expired.',
    },
    'email_verified': {'ru': 'Email подтверждён.', 'kk': 'Email расталды.', 'en': 'Email confirmed.'},
    'already_verified': {'ru': 'Email уже подтверждён.', 'kk': 'Email бұрын расталған.', 'en': 'Email is already confirmed.'},
    'email_sent': {'ru': 'Письмо отправлено.', 'kk': 'Хат жіберілді.', 'en': 'Email sent.'},
    'reg_duplicate': {
        'ru': 'С этого email уже подана заявка. Войдите в личный кабинет с этим email, чтобы посмотреть или изменить её.',
        'kk': 'Бұл email арқылы өтінім бұрын жіберілген. Оны көру немесе өзгерту үшін осы email-мен жеке кабинетке кіріңіз.',
        'en': 'An application has already been sent from this email. Sign in to your account with this email to view or change it.',
    },
    'reg_locked': {
        'ru': 'Эту заявку уже нельзя изменить.',
        'kk': 'Бұл өтінімді енді өзгертуге болмайды.',
        'en': 'This application can no longer be changed.',
    },
    'reg_inactive': {'ru': 'Заявка уже не активна.', 'kk': 'Өтінім енді белсенді емес.', 'en': 'This application is no longer active.'},
    'need_verified_email': {
        'ru': 'Подтвердите email, чтобы подавать статьи и оплачивать взнос.',
        'kk': 'Мақала жіберу және жарна төлеу үшін email-ді растаңыз.',
        'en': 'Confirm your email to submit papers and pay the fee.',
    },
    'target_closed': {
        'ru': 'Приём статей в это издание закрыт.',
        'kk': 'Бұл басылымға мақала қабылдау жабық.',
        'en': 'This publication no longer accepts papers.',
    },
    'paper_locked': {
        'ru': 'Статью в этом статусе изменить нельзя.',
        'kk': 'Бұл мәртебедегі мақаланы өзгертуге болмайды.',
        'en': 'A paper with this status cannot be changed.',
    },
    'paper_no_withdraw': {
        'ru': 'Эту статью отозвать нельзя. Напишите на al-farabi@kaznu.kz.',
        'kk': 'Бұл мақаланы кері алуға болмайды. al-farabi@kaznu.kz мекенжайына жазыңыз.',
        'en': 'This paper cannot be withdrawn. Please write to al-farabi@kaznu.kz.',
    },
    'file_too_big': {
        'ru': 'Файл больше {mb} МБ.',
        'kk': 'Файл {mb} МБ-тан үлкен.',
        'en': 'The file is larger than {mb} MB.',
    },
    'already_paid': {
        'ru': 'Взнос за эту статью уже оплачен.',
        'kk': 'Бұл мақала үшін жарна төленген.',
        'en': 'The fee for this paper has already been paid.',
    },
    'not_payable': {
        'ru': 'Оплата станет доступна после принятия статьи к публикации.',
        'kk': 'Мақала жариялауға қабылданғаннан кейін төлеуге болады.',
        'en': 'Payment becomes available once the paper is accepted for publication.',
    },
    'receipt_types': {
        'ru': 'Допустимы файлы PDF, JPG, PNG.',
        'kk': 'PDF, JPG, PNG файлдары ғана.',
        'en': 'Only PDF, JPG and PNG files are accepted.',
    },
    'provider_unavailable': {
        'ru': 'Этот способ оплаты недоступен.',
        'kk': 'Бұл төлем тәсілі қолжетімсіз.',
        'en': 'This payment method is not available.',
    },
    'no_receipt_needed': {
        'ru': 'Для этого платежа квитанция не нужна.',
        'kk': 'Бұл төлемге түбіртек қажет емес.',
        'en': 'No receipt is needed for this payment.',
    },
    'pay_no_cancel': {
        'ru': 'Этот платёж нельзя отменить.',
        'kk': 'Бұл төлемді болдырмауға болмайды.',
        'en': 'This payment cannot be cancelled.',
    },
}

# Названия изданий — как на странице Publications
TARGET_LABELS = {
    'proceedings': {'ru': 'Электронный сборник материалов', 'kk': 'Электрондық материалдар жинағы',
                    'en': 'Electronic proceedings'},
    'tuva': {'ru': '«Новые исследования Тувы» (Scopus Q1)', 'kk': '«Тываны жаңа зерттеу» (Scopus Q1)',
             'en': '“New Research of Tuva” (Scopus Q1)'},
    'vestnik_philosophy': {'ru': '«Вестник КазНУ. Серия философии, культурологии и политологии»',
                           'kk': '«ҚазҰУ Хабаршысы. Философия, мәдениеттану және саясаттану сериясы»',
                           'en': '“KazNU Bulletin. Philosophy, Cultural Studies and Political Science Series”'},
    'vestnik_religion': {'ru': '«Вестник КазНУ. Серия религиоведения»', 'kk': '«ҚазҰУ Хабаршысы. Дінтану сериясы»',
                         'en': '“KazNU Bulletin. Religious Studies Series”'},
    'vestnik_pedagogy': {'ru': '«Вестник КазНУ. Серия педагогические науки»',
                         'kk': '«ҚазҰУ Хабаршысы. Педагогикалық ғылымдар сериясы»',
                         'en': '“KazNU Bulletin. Pedagogical Sciences Series”'},
    'vestnik_psychology': {'ru': '«Вестник КазНУ. Серия психологии и социологии»',
                           'kk': '«ҚазҰУ Хабаршысы. Психология және социология сериясы»',
                           'en': '“KazNU Bulletin. Psychology and Sociology Series”'},
}

MONTHS = {
    'ru': ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля', 'августа', 'сентября', 'октября',
           'ноября', 'декабря'],
    'kk': ['қаңтар', 'ақпан', 'наурыз', 'сәуір', 'мамыр', 'маусым', 'шілде', 'тамыз', 'қыркүйек', 'қазан',
           'қараша', 'желтоқсан'],
    'en': ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
           'November', 'December'],
}


def current_lang():
    lang = (translation.get_language() or 'ru')[:2]
    return lang if lang in LANGS else 'ru'


def tr(key, lang=None, **kw):
    m = MESSAGES[key]
    return m.get(lang or current_lang(), m['ru']).format(**kw)


def date_text(d, lang=None):
    """15 октября 2026 / 2026 жылғы 15 қазан / 15 October 2026"""
    lang = lang or current_lang()
    month = MONTHS[lang][d.month - 1]
    if lang == 'kk':
        return f'{d.year} жылғы {d.day} {month}'
    return f'{d.day} {month} {d.year}'


def target_label(code, lang=None):
    labels = TARGET_LABELS.get(code)
    return labels.get(lang or current_lang(), labels['ru']) if labels else code
