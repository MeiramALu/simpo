"""
Сквозные тесты API. Запуск: python manage.py test
"""
import re
import shutil
import tempfile
from decimal import Decimal

from django.core import mail
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from django.contrib.auth.models import Group

from accounts.models import User
from papers.models import Paper, PublicationFee
from registrations.models import Registration
from siteconfig.models import SiteSettings

TMP_MEDIA = tempfile.mkdtemp()

# ровно то, что отправляет submitReg() во фронте
FRONT_PAYLOAD = {
    'name': 'Иванов Иван', 'org': 'КазНУ', 'country': 'Казахстан', 'email': 'Ivan@Example.com',
    'phone': '+7 700 000 0000', 'day': 'both', 'role': 'speaker', 'direction': 'Секция 1',
    'topic': 'Добродетель у аль-Фараби', 'note': '', 'lang': 'ru', 'submittedAt': '2026-09-30T10:00:00Z',
}


def doc(name='paper.docx', size=100):
    return SimpleUploadedFile(name, b'x' * size, content_type='application/octet-stream')


@override_settings(MEDIA_ROOT=TMP_MEDIA, ORGANIZERS_EMAILS=['org@example.com'],
                   FRONTEND_URL='http://front')
class BaseAPITest(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TMP_MEDIA, ignore_errors=True)

    def setUp(self):
        cache.clear()
        self.c = APIClient()

    def make_user(self, email='user@example.com', verified=True, **kw):
        return User.objects.create_user(email=email, password='Strong-pass-123', full_name='Тест Тестов',
                                        email_verified=verified, **kw)

    def login(self, user):
        self.c.force_authenticate(user)


class AuthTests(BaseAPITest):
    def test_register_login_me_logout(self):
        r = self.c.post('/api/auth/register/', {'email': 'New@Example.com', 'password': 'Strong-pass-123',
                                                 'full_name': 'Новый Участник', 'lang': 'en'}, format='json')
        self.assertEqual(r.status_code, 201, r.data)
        self.assertEqual(r.data['user']['email'], 'new@example.com')
        self.assertFalse(r.data['user']['email_verified'])
        self.assertEqual(len(mail.outbox), 1)  # письмо подтверждения

        r = self.c.post('/api/auth/login/', {'email': 'new@example.com', 'password': 'Strong-pass-123'}, format='json')
        self.assertEqual(r.status_code, 200)
        token = r.data['token']

        self.c.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        r = self.c.patch('/api/auth/me/', {'organization': 'KazNU', 'email': 'hack@x.com'}, format='json')
        self.assertEqual(r.data['organization'], 'KazNU')
        self.assertEqual(r.data['email'], 'new@example.com')  # email менять нельзя

        self.assertEqual(self.c.post('/api/auth/logout/').status_code, 204)
        self.assertEqual(self.c.get('/api/auth/me/').status_code, 401)

    def test_register_duplicate_and_weak_password(self):
        self.make_user()
        r = self.c.post('/api/auth/register/', {'email': 'USER@example.com', 'password': 'Strong-pass-123', 'full_name': 'X'}, format='json')
        self.assertEqual(r.status_code, 400)
        r = self.c.post('/api/auth/register/', {'email': 'a@b.kz', 'password': '123', 'full_name': 'X'}, format='json')
        self.assertEqual(r.status_code, 400)

    def test_wrong_password(self):
        self.make_user()
        r = self.c.post('/api/auth/login/', {'email': 'user@example.com', 'password': 'nope'}, format='json')
        self.assertEqual(r.status_code, 400)

    def test_email_verification_links_registrations(self):
        Registration.objects.create(full_name='A', organization='B', email='user@example.com', day='6', role='listener')
        self.c.post('/api/auth/register/', {'email': 'user@example.com', 'password': 'Strong-pass-123', 'full_name': 'A'}, format='json')
        link = re.search(r'http://\S+email/verify/link/\S+', mail.outbox[-1].body).group(0)
        r = self.c.get(link)
        self.assertEqual(r.status_code, 302)
        self.assertIn('email_verified=1', r['Location'])
        u = User.objects.get(email='user@example.com')
        self.assertTrue(u.email_verified)
        self.assertEqual(u.registrations.count(), 1)

    def test_password_reset(self):
        self.make_user()
        r = self.c.post('/api/auth/password/reset/', {'email': 'user@example.com'}, format='json')
        self.assertEqual(r.status_code, 200)
        uid, token = re.search(r'uid=([^&\s]+)&token=(\S+)', mail.outbox[-1].body).groups()
        r = self.c.post('/api/auth/password/reset/confirm/', {'uid': uid, 'token': token, 'new_password': 'Another-pass-456'}, format='json')
        self.assertEqual(r.status_code, 200, r.data)
        r = self.c.post('/api/auth/password/reset/confirm/', {'uid': uid, 'token': token, 'new_password': 'Third-pass-789'}, format='json')
        self.assertEqual(r.status_code, 400)  # токен одноразовый
        self.assertTrue(User.objects.get().check_password('Another-pass-456'))

    def test_password_reset_unknown_email_is_silent(self):
        r = self.c.post('/api/auth/password/reset/', {'email': 'nobody@example.com'}, format='json')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)


class RegistrationTests(BaseAPITest):
    def test_anonymous_frontend_payload(self):
        r = self.c.post('/api/registrations/', FRONT_PAYLOAD, format='json')
        self.assertEqual(r.status_code, 201, r.data)
        reg = Registration.objects.get()
        self.assertEqual(reg.email, 'ivan@example.com')
        self.assertEqual(reg.full_name, 'Иванов Иван')
        self.assertIsNone(reg.user)
        recipients = sorted(m.to[0] for m in mail.outbox)
        self.assertEqual(recipients, ['ivan@example.com', 'org@example.com'])

    def test_duplicate_email_rejected(self):
        self.c.post('/api/registrations/', FRONT_PAYLOAD, format='json')
        r = self.c.post('/api/registrations/', {**FRONT_PAYLOAD, 'email': 'ivan@EXAMPLE.com'}, format='json')
        self.assertEqual(r.status_code, 400)
        self.assertIn('email', r.data)

    def test_required_fields_and_choices(self):
        r = self.c.post('/api/registrations/', {**FRONT_PAYLOAD, 'day': '8', 'name': ''}, format='json')
        self.assertEqual(r.status_code, 400)
        self.assertIn('day', r.data)
        self.assertIn('name', r.data)

    def test_listener_topic_dropped(self):
        self.c.post('/api/registrations/', {**FRONT_PAYLOAD, 'role': 'listener'}, format='json')
        self.assertEqual(Registration.objects.get().topic, '')

    def test_owner_list_edit_cancel(self):
        u = self.make_user(email='ivan@example.com')
        self.c.post('/api/registrations/', FRONT_PAYLOAD, format='json')  # подана без входа
        other = self.make_user(email='other@example.com')
        self.login(other)
        self.assertEqual(self.c.get('/api/registrations/').data, [])

        self.login(u)
        items = self.c.get('/api/registrations/').data
        self.assertEqual(len(items), 1)
        rid = items[0]['id']
        r = self.c.patch(f'/api/registrations/{rid}/', {'day': '7', 'email': 'x@x.com'}, format='json')
        self.assertEqual(r.status_code, 200, r.data)
        self.assertEqual(r.data['day'], '7')
        self.assertEqual(r.data['email'], 'ivan@example.com')

        r = self.c.post(f'/api/registrations/{rid}/cancel/')
        self.assertEqual(r.data['status'], 'cancelled')
        self.assertEqual(self.c.patch(f'/api/registrations/{rid}/', {'day': '6'}, format='json').status_code, 400)
        # после отмены можно подать заново
        self.assertEqual(self.c.post('/api/registrations/', FRONT_PAYLOAD, format='json').status_code, 201)

    def test_throttle(self):
        for i in range(30):
            self.c.post('/api/registrations/', {**FRONT_PAYLOAD, 'email': f'u{i}@example.com'}, format='json')
        r = self.c.post('/api/registrations/', {**FRONT_PAYLOAD, 'email': 'u99@example.com'}, format='json')
        self.assertEqual(r.status_code, 429)


class PaperTests(BaseAPITest):
    def submit(self, target='tuva', **kw):
        data = {'title': 'О добродетели', 'authors': 'Тестов Т.', 'abstract': 'Аннотация', 'target': target,
                'file': doc(), **kw}
        return self.c.post('/api/papers/', data, format='multipart')

    def test_submit_requires_verified_email(self):
        self.login(self.make_user(verified=False))
        self.assertEqual(self.submit().status_code, 403)

    def test_submit_and_fee(self):
        self.login(self.make_user())
        r = self.submit()
        self.assertEqual(r.status_code, 201, r.data)
        self.assertEqual((r.data['fee_amount'], r.data['fee_currency']), ('300.00', 'USD'))
        self.assertFalse(r.data['can_pay'])
        self.assertEqual(r.data['original_filename'], 'paper.docx')
        r = self.submit(target='vestnik_religion')
        self.assertEqual((r.data['fee_amount'], r.data['fee_currency']), ('60000.00', 'KZT'))

    def test_bad_file_extension(self):
        self.login(self.make_user())
        r = self.submit(file=doc('virus.exe'))
        self.assertEqual(r.status_code, 400)

    def test_edit_only_when_editable_and_revision_resets_status(self):
        u = self.make_user()
        self.login(u)
        pid = self.submit().data['id']
        Paper.objects.filter(pk=pid).update(status='under_review')
        self.assertEqual(self.c.patch(f'/api/papers/{pid}/', {'title': 'X'}, format='multipart').status_code, 400)
        Paper.objects.filter(pk=pid).update(status='revision')
        r = self.c.patch(f'/api/papers/{pid}/', {'file': doc('v2.pdf')}, format='multipart')
        self.assertEqual(r.status_code, 200, r.data)
        self.assertEqual(r.data['status'], 'submitted')
        self.assertEqual(r.data['original_filename'], 'v2.pdf')

    def test_file_access(self):
        u = self.make_user()
        self.login(u)
        pid = self.submit().data['id']
        r = self.c.get(f'/api/papers/{pid}/file/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(b''.join(r.streaming_content), b'x' * 100)
        self.login(self.make_user(email='other@example.com'))
        self.assertEqual(self.c.get(f'/api/papers/{pid}/file/').status_code, 404)
        staff = self.make_user(email='staff@example.com', is_staff=True)
        self.login(staff)
        self.assertEqual(self.c.get(f'/api/papers/{pid}/file/').status_code, 404)  # сотрудник без роли
        staff.groups.add(Group.objects.get(name='Редакция'))
        self.login(User.objects.get(pk=staff.pk))  # сбросить кэш прав
        self.assertEqual(self.c.get(f'/api/papers/{pid}/file/').status_code, 200)


class PaymentRemovedTests(BaseAPITest):
    """Оплаты на сайте нет: взнос только для сведения, путь участника заканчивается подачей статьи."""

    def test_no_payment_api_admin_or_cabinet_tab(self):
        user = self.make_user()
        self.login(user)
        paper = Paper.objects.create(user=user, title='T', authors='A', abstract='B', target='tuva', file=doc(), status='accepted')
        self.assertEqual(self.c.post('/api/payments/', {'paper': paper.pk, 'provider': 'manual'}, format='json').status_code, 404)
        self.assertEqual(self.c.get('/api/payments/').status_code, 404)
        self.assertNotIn('payment_providers', self.c.get('/api/meta/').data)
        # сумма взноса по-прежнему видна автору
        self.assertEqual(self.c.get(f'/api/papers/{paper.pk}/').data['fee_amount'], '300.00')
        admin = User.objects.create_superuser(email='admin@example.com', password='Strong-pass-123', full_name='Админ')
        self.client.force_login(admin)
        self.assertEqual(self.client.get('/admin/payments/payment/').status_code, 404)
        self.assertNotIn('bank_iik', self.client.get('/admin/siteconfig/sitesettings/1/change/').content.decode())
        html = self.c.get('/').content.decode()
        self.assertNotIn('/api/payments/', html)
        self.assertIn('feeNote', html)


class SiteTests(BaseAPITest):
    def test_index_and_meta(self):
        r = self.c.get('/')
        self.assertEqual(r.status_code, 200)
        self.assertIn(b"/api/registrations/", r.content)
        self.assertIn('csrftoken', r.cookies)
        m = self.c.get('/api/meta/').data
        self.assertEqual(len(m['publication_targets']), 6)


class AdminSmokeTests(BaseAPITest):
    def test_admin_pages_open(self):
        admin = User.objects.create_superuser(email='admin@example.com', password='Strong-pass-123', full_name='Админ')
        user = self.make_user()
        paper = Paper.objects.create(user=user, title='T', authors='A', abstract='B', file=doc())
        reg = Registration.objects.create(full_name='A', organization='B', email='a@b.kz', day='6', role='listener')
        self.client.force_login(admin)
        for url in ['/admin/', '/admin/accounts/user/', '/admin/accounts/user/add/', f'/admin/accounts/user/{user.pk}/change/',
                    '/admin/registrations/registration/', f'/admin/registrations/registration/{reg.pk}/change/',
                    '/admin/papers/paper/', f'/admin/papers/paper/{paper.pk}/change/']:
            self.assertEqual(self.client.get(url).status_code, 200, url)
        # создание пользователя через админку
        r = self.client.post('/admin/accounts/user/add/', {'email': 'added@example.com', 'full_name': 'Добавленный',
                                                          'usable_password': 'true', 'password1': 'Strong-pass-123',
                                                          'password2': 'Strong-pass-123'})
        self.assertEqual(r.status_code, 302)
        self.assertTrue(User.objects.filter(email='added@example.com').exists())
        # CSV-выгрузка и смена статуса с письмом
        r = self.client.post('/admin/registrations/registration/', {'action': 'export_csv_registrations', '_selected_action': [reg.pk]})
        self.assertEqual(r['Content-Type'], 'text/csv; charset=utf-8')
        mail.outbox.clear()
        self.client.post('/admin/registrations/registration/', {'action': 'set_confirmed', '_selected_action': [reg.pk]})
        reg.refresh_from_db()
        self.assertEqual(reg.status, 'confirmed')
        self.assertEqual(mail.outbox[0].to, ['a@b.kz'])

    def test_session_user_can_still_register_via_site(self):
        """Сотрудник залогинен в админке и заполняет форму на сайте — CSRF-токен из cookie должен сработать."""
        admin = User.objects.create_superuser(email='admin@example.com', password='Strong-pass-123', full_name='Админ')
        c = self.client_class(enforce_csrf_checks=True)
        c.force_login(admin)
        token = c.get('/').cookies['csrftoken'].value
        r = c.post('/api/registrations/', FRONT_PAYLOAD, content_type='application/json', HTTP_X_CSRFTOKEN=token)
        self.assertEqual(r.status_code, 201)


class SiteSettingsTests(BaseAPITest):
    def conf(self, **kw):
        c = SiteSettings.load()
        for k, v in kw.items():
            setattr(c, k, v)
        c.save()

    def test_registration_closed(self):
        self.conf(registration_open=False)
        r = self.c.post('/api/registrations/', {**FRONT_PAYLOAD, 'lang': 'en'}, format='json')
        self.assertEqual(r.status_code, 403)
        self.assertEqual(r.data['detail'], 'Registration is closed.')
        self.conf(registration_closed_ru='Приём завершён 1 ноября.')
        r = self.c.post('/api/registrations/', FRONT_PAYLOAD, format='json')
        self.assertEqual(r.data['detail'], 'Приём завершён 1 ноября.')
        self.assertFalse(self.c.get('/api/meta/').data['registration_open'])

    def test_duplicate_message_localized(self):
        self.c.post('/api/registrations/', FRONT_PAYLOAD, format='json')
        r = self.c.post('/api/registrations/', {**FRONT_PAYLOAD, 'lang': 'kk'}, format='json')
        self.assertIn('өтінім', r.data['email'][0])

    def test_organizer_emails_and_participant_emails_toggle(self):
        self.conf(organizers_emails='a@kaznu.kz, b@kaznu.kz', send_participant_emails=False)
        self.c.post('/api/registrations/', FRONT_PAYLOAD, format='json')
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['a@kaznu.kz', 'b@kaznu.kz'])

    def test_papers_closed_and_target_closed(self):
        self.login(self.make_user())
        data = lambda t: {'title': 'T', 'authors': 'A', 'abstract': 'B', 'target': t, 'file': doc()}
        PublicationFee.objects.filter(target='tuva').update(is_active=False)
        self.assertEqual(self.c.post('/api/papers/', data('tuva'), format='multipart').status_code, 400)
        self.assertEqual(self.c.post('/api/papers/', data('proceedings'), format='multipart').status_code, 201)
        self.conf(papers_open=False)
        self.assertEqual(self.c.post('/api/papers/', data('proceedings'), format='multipart').status_code, 403)

    def test_fee_amount_from_admin(self):
        user = self.make_user()
        paper = Paper.objects.create(user=user, title='T', authors='A', abstract='B', target='tuva', file=doc())
        PublicationFee.objects.filter(target='tuva').update(amount=250)
        self.assertEqual(paper.fee[0], 250)

    def test_admin_settings_page(self):
        admin = User.objects.create_superuser(email='admin@example.com', password='Strong-pass-123', full_name='Админ')
        self.client.force_login(admin)
        r = self.client.get('/admin/siteconfig/sitesettings/')
        self.assertEqual(r.status_code, 302)
        r = self.client.get(r['Location'])
        self.assertEqual(r.status_code, 200)
        self.assertEqual(self.client.get('/admin/papers/publicationfee/').status_code, 200)


class RoleTests(BaseAPITest):
    def staff(self, role, email):
        u = self.make_user(email=email, is_staff=True)
        u.groups.add(Group.objects.get(name=role))
        self.client.force_login(u)
        return u

    def setUp(self):
        super().setUp()
        self.user = self.make_user()
        self.paper = Paper.objects.create(user=self.user, title='T', authors='A', abstract='B', file=doc(), status='accepted', target='tuva')
        self.reg = Registration.objects.create(full_name='A', organization='B', email='a@b.kz', day='6', role='listener')

    def test_roles_created(self):
        self.assertEqual(set(Group.objects.values_list('name', flat=True)),
                         {'Оргкомитет', 'Редакция', 'Администратор симпозиума'})

    def test_orgcommittee(self):
        self.staff('Оргкомитет', 'org@kaznu.kz')
        self.assertEqual(self.client.get('/admin/registrations/registration/').status_code, 200)
        self.assertEqual(self.client.get('/admin/siteconfig/sitesettings/1/change/').status_code, 403)
        r = self.client.post('/admin/registrations/registration/', {'action': 'export_csv_registrations', '_selected_action': [self.reg.pk]})
        self.assertEqual(r['Content-Type'], 'text/csv; charset=utf-8')

    def test_editor_cannot_export_registrations(self):
        self.staff('Редакция', 'ed@kaznu.kz')
        self.assertEqual(self.client.get('/admin/registrations/registration/').status_code, 403)
        self.assertEqual(self.client.get(f'/admin/papers/paper/{self.paper.pk}/change/').status_code, 200)
        self.assertEqual(self.client.get(f'/api/papers/{self.paper.pk}/file/').status_code, 200)

    def test_symposium_admin_limits(self):
        boss = self.staff('Администратор симпозиума', 'boss@kaznu.kz')
        root = User.objects.create_superuser(email='root@example.com', password='Strong-pass-123', full_name='Root')
        self.assertEqual(self.client.get('/admin/siteconfig/sitesettings/1/change/').status_code, 200)
        # суперпользователя видит только на чтение и изменить не может
        self.assertNotIn('name="email"', self.client.get(f'/admin/accounts/user/{root.pk}/change/').content.decode())
        r = self.client.post(f'/admin/accounts/user/{root.pk}/change/', {'email': 'x@x.kz', 'full_name': 'X'})
        self.assertEqual(r.status_code, 403)
        root.refresh_from_db()
        self.assertEqual(root.email, 'root@example.com')
        page = self.client.get(f'/admin/accounts/user/{self.user.pk}/change/').content.decode()
        self.assertNotIn('name="is_superuser"', page)
        self.assertIn('name="groups"', page)
        # назначает роль сотруднику
        emp = self.make_user(email='emp@kaznu.kz')
        r = self.client.post(f'/admin/accounts/user/{emp.pk}/change/', {
            'email': emp.email, 'full_name': emp.full_name, 'lang': 'ru', 'is_active': 'on', 'is_staff': 'on',
            'groups': [Group.objects.get(name='Редакция').pk], 'is_superuser': 'on',
            'date_joined_0': '2026-09-30', 'date_joined_1': '10:00:00',
        })
        self.assertEqual(r.status_code, 302, r.content[:2000])
        emp.refresh_from_db()
        self.assertTrue(emp.is_staff)
        self.assertFalse(emp.is_superuser)  # повысить до суперпользователя нельзя
        self.assertEqual([g.name for g in emp.groups.all()], ['Редакция'])


class SiteFormTests(BaseAPITest):
    def test_form_fixes_in_built_site(self):
        html = self.c.get('/').content.decode()
        self.assertIn('.choice input:checked+span{background:var(--gold)', html)
        self.assertIn("miss.forEach", html)
        self.assertNotIn('if (!data.name || !data.org', html)


class FaviconTests(BaseAPITest):
    def test_favicons(self):
        html = self.c.get('/').content.decode()
        self.assertIn('<link rel="icon" type="image/png" sizes="96x96" href="/favicon.png">', html)
        for url, ctype in [('/favicon.png', 'image/png'), ('/favicon.ico', 'image/x-icon'), ('/apple-touch-icon.png', 'image/png')]:
            r = self.c.get(url)
            self.assertEqual((r.status_code, r['Content-Type']), (200, ctype), url)

    def test_admin_has_favicon(self):
        admin = User.objects.create_superuser(email='admin@example.com', password='Strong-pass-123', full_name='Админ')
        self.client.force_login(admin)
        self.assertIn('href="/favicon.png"', self.client.get('/admin/').content.decode())


class SpeakerTests(BaseAPITest):
    def test_seeded_from_program(self):
        from speakers.models import Speaker, SpeakerGroup
        self.assertEqual(SpeakerGroup.objects.count(), 4)
        self.assertEqual(Speaker.objects.count(), 39)
        data = self.c.get('/api/speakers/?lang=ru').data
        self.assertEqual([g['title'] for g in data],
                         ['Пленарное заседание 6 ноября', 'Панели', 'Пленарное заседание 7 ноября', 'Модераторы'])
        self.assertEqual([len(g['speakers']) for g in data], [6, 14, 8, 11])
        first = data[0]['speakers'][0]
        self.assertEqual((first['name'], first['country'], first['day'], first['where'], first['tbc']),
                         ('Эллиотт Марк С.', 'США', '6 ноября', 'Пленарное заседание', True))
        en = self.c.get('/api/speakers/?lang=en').data[0]['speakers'][0]
        self.assertEqual((en['name'], en['day']), ('Mark C. Elliott', '6 November'))

    def test_admin_changes_reach_api(self):
        from speakers.models import Speaker, SpeakerGroup
        g = SpeakerGroup.objects.get(key='plenary6')
        Speaker.objects.create(group=g, order=1, day='6', name_ru='Новый Докладчик', topic_ru='О добродетели')
        Speaker.objects.filter(name_ru='Аяди Салем').update(is_published=False)
        names = [s['name'] for s in self.c.get('/api/speakers/?lang=kk').data[0]['speakers']]
        self.assertEqual(names[0], 'Новый Докладчик')  # нет перевода — показывается русский
        self.assertNotIn('Аяди Салем', names)
        self.assertEqual(len(names), 6)
        SpeakerGroup.objects.filter(key='moderators').update(is_published=False)
        self.assertEqual(len(self.c.get('/api/speakers/').data), 3)

    def test_photo(self):
        import io
        from PIL import Image
        from speakers.models import Speaker
        buf = io.BytesIO()
        Image.new('RGB', (10, 10), 'red').save(buf, 'PNG')
        s = Speaker.objects.get(name_ru='Аяди Салем')
        s.photo = SimpleUploadedFile('a.png', buf.getvalue(), content_type='image/png')
        s.save()
        card = next(x for x in self.c.get('/api/speakers/').data[0]['speakers'] if x['id'] == s.pk)
        self.assertIn(f'/api/speakers/{s.pk}/photo/', card['photo'])
        self.assertEqual(self.c.get(card['photo']).status_code, 200)

    def test_admin_and_roles(self):
        from speakers.models import Speaker
        u = self.make_user(email='org@kaznu.kz', is_staff=True)
        u.groups.add(Group.objects.get(name='Оргкомитет'))
        self.client.force_login(u)
        self.assertEqual(self.client.get('/admin/speakers/speaker/').status_code, 200)
        self.assertEqual(self.client.get('/admin/speakers/speaker/add/').status_code, 200)
        s = Speaker.objects.first()
        self.assertEqual(self.client.get(f'/admin/speakers/speaker/{s.pk}/change/').status_code, 200)
        self.assertEqual(self.client.get('/admin/speakers/speakergroup/').status_code, 200)

    def test_removed_role_perm_is_not_restored(self):
        from django.contrib.auth.models import Permission
        from siteconfig.roles import sync_roles
        g = Group.objects.get(name='Оргкомитет')
        p = Permission.objects.get(codename='delete_speaker')
        g.permissions.remove(p)
        sync_roles()
        self.assertFalse(g.permissions.filter(pk=p.pk).exists())
        sync_roles(reset=True)
        self.assertTrue(g.permissions.filter(pk=p.pk).exists())

    def test_site_uses_api(self):
        html = self.c.get('/').content.decode()
        self.assertIn("fetch(API + '/api/speakers/?lang=' + l)", html)
        self.assertIn('<img class="ini"', html)


class DefaultLanguageTests(BaseAPITest):
    def test_site_opens_in_english(self):
        html = self.c.get('/').content.decode()
        self.assertIn('<html lang="en">', html)
        self.assertIn("let lang = 'en';", html)
        self.assertIn('<title>Al-Farabi Global Symposium – 2026</title>', html)
        # выбор посетителя по-прежнему запоминается
        self.assertIn("localStorage.getItem('afgs-lang')", html)


class SpeakerFromRegistrationTests(BaseAPITest):
    def setUp(self):
        super().setUp()
        self.org = self.make_user(email='org@kaznu.kz', is_staff=True)
        self.org.groups.add(Group.objects.get(name='Оргкомитет'))
        self.client.force_login(self.org)
        self.reg = Registration.objects.create(full_name='Иванов Иван', organization='КазНУ', country='Казахстан',
                                               email='ivan@example.com', day='both', role='speaker',
                                               topic='О добродетели', direction='Панель 2')

    def site_names(self):
        return [s['name'] for g in self.c.get('/api/speakers/').data for s in g['speakers']]

    def test_confirm_creates_hidden_draft(self):
        from speakers.models import Speaker
        r = self.client.post('/admin/registrations/registration/', {'action': 'set_confirmed', '_selected_action': [self.reg.pk]}, follow=True)
        self.assertContains(r, 'Черновики из заявок')
        card = Speaker.objects.get(registration=self.reg)
        self.assertEqual((card.name_ru, card.role_ru, card.topic_ru, card.session_ru, card.day, card.is_published),
                         ('Иванов Иван', 'КазНУ', 'О добродетели', 'Панель 2', '6', False))
        self.assertEqual(card.group.key, 'drafts')
        self.assertNotIn('Иванов Иван', self.site_names())  # черновик не на сайте
        # повторное подтверждение / действие не создаёт дубль
        self.client.post('/admin/registrations/registration/', {'action': 'make_speaker_cards', '_selected_action': [self.reg.pk]})
        self.assertEqual(Speaker.objects.filter(registration=self.reg).count(), 1)
        # оргкомитет публикует: переносит в группу и включает показ
        from speakers.models import SpeakerGroup
        card.group = SpeakerGroup.objects.get(key='panels'); card.is_published = True; card.save()
        self.assertIn('Иванов Иван', self.site_names())
        page = self.client.get('/admin/registrations/registration/').content.decode()
        self.assertIn('на сайте', page)
        # отклонение заявки убирает карточку с сайта
        self.client.post('/admin/registrations/registration/', {'action': 'set_rejected', '_selected_action': [self.reg.pk]})
        self.assertNotIn('Иванов Иван', self.site_names())

    def test_action_for_already_confirmed(self):
        from speakers.models import Speaker
        Registration.objects.filter(pk=self.reg.pk).update(status='confirmed')  # подтверждена раньше, без карточки
        listener = Registration.objects.create(full_name='Слушатель', organization='X', email='l@x.kz', day='6',
                                               role='listener', status='confirmed')
        r = self.client.post('/admin/registrations/registration/', {'action': 'make_speaker_cards',
                             '_selected_action': [self.reg.pk, listener.pk]}, follow=True)
        self.assertContains(r, 'Пропущено 1')
        self.assertEqual(Speaker.objects.filter(registration__isnull=False).count(), 1)

    def test_status_change_in_form_and_participant_cancel(self):
        from speakers.models import Speaker
        self.client.post('/admin/registrations/registration/', {'action': 'set_confirmed', '_selected_action': [self.reg.pk]})
        Speaker.objects.filter(registration=self.reg).update(is_published=True)
        user = self.make_user(email='ivan@example.com')
        self.login(user)
        self.c.post(f'/api/registrations/{self.reg.pk}/cancel/')
        self.assertFalse(Speaker.objects.get(registration=self.reg).is_published)

    def test_editor_without_speaker_perm_gets_no_card(self):
        from speakers.models import Speaker
        ed = self.make_user(email='ed@kaznu.kz', is_superuser=False, is_staff=True)
        ed.groups.add(Group.objects.get(name='Редакция'))
        # у Редакции нет доступа к заявкам вообще
        self.client.force_login(ed)
        self.assertEqual(self.client.get('/admin/registrations/registration/').status_code, 403)
        self.assertFalse(Speaker.objects.filter(registration=self.reg).exists())

    def test_draft_photo_visible_in_admin_only(self):
        import io
        from PIL import Image
        from speakers.services import create_draft_card
        card, _ = create_draft_card(self.reg)
        buf = io.BytesIO(); Image.new('RGB', (4, 4)).save(buf, 'PNG')
        card.photo = SimpleUploadedFile('p.png', buf.getvalue(), content_type='image/png'); card.save()
        self.assertEqual(self.client.get(f'/api/speakers/{card.pk}/photo/').status_code, 200)
        self.assertEqual(self.c.get(f'/api/speakers/{card.pk}/photo/').status_code, 404)
        self.assertEqual(self.client.get(f'/admin/speakers/speaker/{card.pk}/change/').status_code, 200)
        self.assertEqual(self.client.get(f'/admin/registrations/registration/{self.reg.pk}/change/').status_code, 200)


class DeadlineAndLanguageTests(BaseAPITest):
    def conf(self, **kw):
        c = SiteSettings.load()
        for k, v in kw.items():
            setattr(c, k, v)
        c.save()

    def test_registration_deadline_auto_close(self):
        import datetime
        from django.utils import timezone
        today = timezone.localdate()
        self.conf(registration_deadline=today)
        m = self.c.get('/api/meta/', HTTP_ACCEPT_LANGUAGE='en').data['registration']
        self.assertTrue(m['open'])
        self.assertIn('Applications are accepted until', m['deadline_text'])
        self.assertEqual(self.c.post('/api/registrations/', FRONT_PAYLOAD, format='json').status_code, 201)
        self.conf(registration_deadline=today - datetime.timedelta(days=1))
        m = self.c.get('/api/meta/', HTTP_ACCEPT_LANGUAGE='kk').data['registration']
        self.assertFalse(m['open'])
        self.assertIn('аяқталды', m['closed_message'])
        r = self.c.post('/api/registrations/', {**FRONT_PAYLOAD, 'email': 'x@y.kz', 'lang': 'ru'}, format='json')
        self.assertEqual(r.status_code, 403)
        self.assertIn('завершён', r.data['detail'])
        self.conf(registration_closed_en='Closed — see you in 2027!')
        m = self.c.get('/api/meta/', HTTP_ACCEPT_LANGUAGE='en-US,en;q=0.9').data['registration']
        self.assertEqual(m['closed_message'], 'Closed — see you in 2027!')

    def test_papers_deadline(self):
        import datetime
        from django.utils import timezone
        self.login(self.make_user())
        self.conf(papers_deadline=timezone.localdate() - datetime.timedelta(days=1))
        r = self.c.post('/api/papers/', {'title': 'T', 'authors': 'A', 'abstract': 'B', 'file': doc()}, format='multipart',
                        HTTP_ACCEPT_LANGUAGE='en')
        self.assertEqual(r.status_code, 403)
        self.assertIn('closed on', r.data['detail'])

    def test_api_messages_follow_language_admin_stays_russian(self):
        self.make_user()
        bad = {'email': 'user@example.com', 'password': 'nope'}
        self.assertEqual(self.c.post('/api/auth/login/', bad, format='json', HTTP_ACCEPT_LANGUAGE='en').data['non_field_errors'][0],
                         'Incorrect email or password.')
        self.assertEqual(self.c.post('/api/auth/login/', bad, format='json', HTTP_ACCEPT_LANGUAGE='kk').data['non_field_errors'][0],
                         'Email немесе құпиясөз қате.')
        self.assertEqual(self.c.post('/api/auth/login/', bad, format='json', HTTP_ACCEPT_LANGUAGE='ru').data['non_field_errors'][0],
                         'Неверный email или пароль.')
        admin = User.objects.create_superuser(email='admin@example.com', password='Strong-pass-123', full_name='Админ')
        self.client.force_login(admin)
        page = self.client.get('/admin/', HTTP_ACCEPT_LANGUAGE='en').content.decode()
        self.assertIn('Настройки симпозиума', page)
        self.assertIn('Выйти', page)  # интерфейс Django на русском

    def test_meta_localized_targets(self):
        m = self.c.get('/api/meta/', HTTP_ACCEPT_LANGUAGE='en').data
        tuva = next(t for t in m['publication_targets'] if t['value'] == 'tuva')
        self.assertEqual(tuva['label'], '“New Research of Tuva” (Scopus Q1)')
        self.assertTrue(tuva['is_active'])

    def test_verify_link_goes_to_cabinet(self):
        u2 = User.objects.create_user(email='v@example.com', password='Strong-pass-123', full_name='V')
        from accounts.tokens import email_verification_token, encode_uid
        r = self.c.get(f'/api/auth/email/verify/link/?uid={encode_uid(u2)}&token={email_verification_token.make_token(u2)}')
        self.assertIn('/#/cabinet?email_verified=1', r['Location'])

    def test_admin_settings_page_with_new_fields(self):
        admin = User.objects.create_superuser(email='admin@example.com', password='Strong-pass-123', full_name='Админ')
        self.client.force_login(admin)
        page = self.client.get('/admin/siteconfig/sitesettings/1/change/').content.decode()
        for name in ('registration_deadline', 'registration_closed_kk', 'papers_deadline', 'papers_closed_en'):
            self.assertIn(f'name="{name}"', page)

    def test_site_has_cabinet(self):
        html = self.c.get('/').content.decode()
        for marker in ('id="acct-link"', "PAGES.cabinet", "EXTRA_ROUTES.includes(h)", 'id="regstate"', "feeText('tuva'"):
            self.assertIn(marker, html)


class ProgramTests(BaseAPITest):
    def source_program(self, lang):
        import json
        from pathlib import Path
        html = (Path(__file__).resolve().parent.parent / 'al-farabi-symposium-2026 V2.html').read_text(encoding='utf-8')
        line = next(l for l in html.split('\n') if l.startswith('const PROGRAM = '))
        return json.loads(line[len('const PROGRAM = '):].rstrip().rstrip(';'))[lang]

    def test_seed_matches_frontend_program_ru(self):
        from program.models import ProgramDay, ProgramEntry, ProgramSlot
        self.assertEqual((ProgramDay.objects.count(), ProgramSlot.objects.count(), ProgramEntry.objects.count()), (4, 36, 62))
        self.assertGreaterEqual(ProgramEntry.objects.filter(speaker__isnull=False).count(), 38)
        api = self.c.get('/api/program/?lang=ru').data
        src = self.source_program('ru')
        self.assertEqual(len(api), len(src))
        for d_api, d_src in zip(api, src):
            self.assertEqual(d_api['date'], d_src['date'])
            self.assertEqual(d_api['event'], d_src.get('event'))
            self.assertEqual(len(d_api['rows']), len(d_src['rows']))
            for r_api, r_src in zip(d_api['rows'], d_src['rows']):
                self.assertEqual((r_api['time'], r_api['title'], r_api['room']), (r_src['time'], r_src['title'], r_src.get('room') or ''))
                self.assertEqual(len(r_api.get('blocks', [])), len(r_src.get('blocks', [])), r_src['title'])
                for b_api, b_src in zip(r_api.get('blocks', []), r_src.get('blocks', [])):
                    self.assertEqual(b_api['label'], b_src.get('label'))
                    for i_api, i_src in zip(b_api['items'], b_src['items']):
                        if 'text' in i_src:
                            self.assertEqual(i_api, {'text': i_src['text']})
                        else:
                            for f in ('name', 'country', 'role', 'topic'):
                                self.assertEqual(i_api[f], i_src.get(f, ''), (r_src['title'], f))
                            self.assertEqual(i_api['tbc'], bool(i_src.get('tbc')) and not i_src.get('topic'))

    def test_languages_and_hidden_speaker(self):
        from speakers.models import Speaker
        en = self.c.get('/api/program/?lang=en').data
        self.assertEqual(en[1]['tab'], '6 November')
        self.assertIn('AL-FARABI', en[1]['event'][0].upper())
        kk = self.c.get('/api/program/?lang=kk').data
        mono = kk[1]['rows'][6]['blocks'][0]['items'][0]
        self.assertIn('text', mono)  # в казахской версии — строкой текста

        def names(data):
            return [i.get('name') for d in data for r in d['rows'] for b in r.get('blocks', []) for i in b['items']]
        self.assertIn('Эллиотт Марк С.', names(self.c.get('/api/program/?lang=ru').data))
        Speaker.objects.filter(name_ru='Эллиотт Марк С.').update(is_published=False)
        self.assertNotIn('Эллиотт Марк С.', names(self.c.get('/api/program/?lang=ru').data))
        Speaker.objects.filter(name_ru='Эллиотт Марк С.').update(name_ru='Эллиотт М.', is_published=True)
        self.assertIn('Эллиотт М.', names(self.c.get('/api/program/?lang=ru').data))  # правка карточки видна в программе

    def test_documents(self):
        from program.models import Document
        self.assertEqual(self.c.get('/api/documents/program/?lang=en').status_code, 404)
        Document.objects.create(kind='program', lang='ru', file=SimpleUploadedFile('p.pdf', b'%PDF-1.4 ru'))
        r = self.c.get('/api/documents/program/?lang=en')  # нет английского — отдаётся русский
        self.assertEqual(r.status_code, 200)
        self.assertEqual(b''.join(r.streaming_content), b'%PDF-1.4 ru')
        self.assertIn('programme_RU.pdf', r['Content-Disposition'])

    def test_admin_pages(self):
        from program.models import ProgramBlock, ProgramDay, ProgramEntry, ProgramSlot
        from speakers.models import Speaker
        u = self.make_user(email='org@kaznu.kz', is_staff=True)
        u.groups.add(Group.objects.get(name='Оргкомитет'))
        self.client.force_login(u)
        urls = ['/admin/program/programday/', f'/admin/program/programday/{ProgramDay.objects.first().pk}/change/',
                '/admin/program/programslot/', f'/admin/program/programslot/{ProgramSlot.objects.first().pk}/change/',
                f'/admin/program/programblock/{ProgramBlock.objects.first().pk}/change/',
                f'/admin/program/programentry/{ProgramEntry.objects.first().pk}/change/', '/admin/program/document/add/',
                f'/admin/speakers/speaker/{Speaker.objects.first().pk}/change/']
        for url in urls:
            self.assertEqual(self.client.get(url).status_code, 200, url)
        self.assertIn('Выступления в программе', self.client.get(urls[-1]).content.decode())


class SpeakerPublishTests(BaseAPITest):
    """Оплаты нет: карточку из заявки показывает на сайте админ, неоплаченный взнос этому не мешает."""

    def test_publish_card_with_paid_target_paper(self):
        from django.forms import modelform_factory
        from speakers.models import Speaker, SpeakerGroup
        from speakers.services import create_draft_card
        user = self.make_user(email='spk@example.com')
        reg = Registration.objects.create(full_name='Докладчик', organization='X', email='spk@example.com',
                                          day='6', role='speaker', status='confirmed', user=user)
        card, _ = create_draft_card(reg)
        self.assertFalse(card.is_published)  # сам по себе на сайт не попадает
        Paper.objects.create(user=user, title='Платная', authors='A', abstract='B', target='tuva', file=doc(), status='accepted')
        Form = modelform_factory(Speaker, fields=('group', 'day', 'name_ru', 'is_published'))
        f = Form({'group': SpeakerGroup.objects.get(key='panels').pk, 'day': '6', 'name_ru': card.name_ru, 'is_published': 'on'},
                 instance=card)
        self.assertTrue(f.is_valid(), f.errors)
        admin = User.objects.create_superuser(email='admin@example.com', password='Strong-pass-123', full_name='Админ')
        self.client.force_login(admin)
        page = self.client.get('/admin/speakers/speaker/').content.decode()
        self.assertNotIn('не оплачен', page)


class HeaderPolishTests(BaseAPITest):
    def test_header_and_hyphen_fixes_in_site(self):
        html = self.c.get('/').content.decode()
        self.assertIn('id="acct-link-nav"', html)
        self.assertIn("p1:'Science Committee, MSHE RK'", html)
        self.assertIn('function noBreakHyphens', html)
        self.assertIn('progDays()[di]', html)
        self.assertIn('/api/documents/', html)

    def test_venue_map_menu(self):
        html = self.c.get('/').content.decode()
        self.assertIn('${mapMenu(vi, v, L.map)}', html)
        for marker in ('2gis.kz/almaty/search/', 'yandex.kz/maps/', 'const NEARBY = [', 'Ғылым', "hotels:'Отели'",
                       'ajax/libs/leaflet/1.9.4/', 'tile.openstreetmap.org'):
            self.assertIn(marker, html)
