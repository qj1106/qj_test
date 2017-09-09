from base64 import encode
from datetime import datetime
from django.contrib.auth.models import User
from django.test import TestCase, Client
from sign.models import Event, Guest
# Create your tests here.

class tests (TestCase):
    ''' 数据库测试 '''

    def setUp(self):
        Event.objects.create (id=4, name="oneplus 3 event", status=True, limit=10, address='深圳', start_time='2017-08-31 12:18:22')
        Guest.objects.create (id=13, realname='Alen', phone='13711001101', email='alen@mail.com', sign=False, event_id=4)

    def test_event(self):
        result = Event.objects.get (name='oneplus 3 event')
        self.assertEqual (result.address, '深圳')
        self.assertTrue (result.status)

    def test_guest(self):
        result = Guest.objects.filter (event_id=4).count ()
        self.assertEqual (result, 1)
        result1 = Guest.objects.get (realname='Alen')
        self.assertEqual (result1.phone, '13711001101')
        self.assertFalse (result1.sign)

    def tearDown(self):
        pass


class testindex (TestCase):
    ''' 登陆页面测试 '''

    def test_index(self):
        response = self.client.get ('/')
        self.assertEqual (response.status_code, 200)
        self.assertTemplateUsed (response, 'index.html')


class testlogin (TestCase):
    ''' 登陆测试 '''

    def setUp(self):
        User.objects.create_user ('admin', 'admin@mail.com', 'admin123')
        self.client = Client ()

    def test_login_success(self):
        test_data = {'username': 'admin', 'password': 'admin123'}
        response = self.client.get ('/login_action/', data=test_data)
        self.assertEqual (response.status_code, 302)

    def test_login_null(self):
        test_data = {'username': '', 'password': ''}
        response = self.client.get ('/login_action/', data=test_data)
        self.assertEqual (response.status_code, 200)
        self.assertIn (b'username or password error!', response.content)

    def test_login_error(self):
        test_data = {'username': 'admin', 'password': '123'}
        response = self.client.get ('/login_action/', data=test_data)
        self.assertEqual (response.status_code, 200)
        self.assertIn (b'username or password', response.content)

    def tearDown(self):
        pass


class testevent (TestCase):
    def setUp(self):
        Event.objects.create (id=4, name="oneplus 3 event", status=True, limit=10, address='深圳', start_time=datetime (2017, 8, 10, 14, 0, 0))
        self.client = Client ()

    def test_event_success(self):
        response = self.client.get ('/event_manage/')
        # print(response.content)
        self.assertEqual (response.status_code, 200)
        self.assertIn (b'oneplus 3 event', response.content)
        # encode编码，decode解码
        self.assertIn ('深圳'.encode (), response.content)

    def test_event_search(self):
        response = self.client.get ('/search_name/', {'name': 'oneplus 3 event'})
        self.assertEqual (response.stauts_code, 200)
        self.assertEqual (b'oneplus 3 event', response.content)

    def tearDown(self):
        pass


class testmanage (TestCase):
    def setUp(self):
        Event.objects.create (id=5, name="xiaomi 3 event", status=True, limit=10, address='北京', start_time=datetime (2017, 8, 12, 14, 0, 0))
        Guest.objects.create (id=13, realname='Alen', phone='13711001101', email='alen@mail.com', sign=False, event_id=5)
        self.client = Client ()

    def test_manage(self):
        response = self.client.get ('/guest_manage/')
        self.assertEqual (response.status_code, 200)
        self.assertIn (b'Alen', response.content)
        self.assertIn (b'xiaomi 3 event', response.content)

    def test_manage_search(self):
        response = self.client.get ('/guest_search/', {'phone': '13711001101'})
        self.assertEqual (response.status_code, 200)
        self.assertIn (b'xiaomi 3 event', response.content)
        self.assertIn (b'13711001101', response.content)

    def tearDown(self):
        pass


class testsign (TestCase):
    def setUp(self):
        Event.objects.create (id=5, name="xiaomi 3 event", status=True, limit=10, address='北京', start_time=datetime (2017, 8, 12, 14, 0, 0))
        Event.objects.create (id=6, name="xiaomi 2 event", status=True, limit=100, address='深圳', start_time=datetime (2017, 9, 12, 14, 0, 0))
        Guest.objects.create (id=13, realname='Alen', phone='13711001101', email='alen@mail.com', sign=False, event_id=5)
        Guest.objects.create (id=14, realname='George', phone='18876594118', email='george@mail.com', sign=True, event_id=6)
        self.client = Client ()

    def test_sign_error(self):
        response = self.client.post ('/sign_index_action/5/', {'phone': '13711001234'})
        self.assertEqual (response.status_code, 200)
        self.assertIn ('手机号有误！请重新输入'.encode (), response.content)

    def test_sign_has(self):
        response = self.client.post ('/sign_index_action/6/', {'phone': '18876594118'})
        self.assertEqual (response.status_code, 200)
        self.assertIn ('用户已签到！'.encode(), response.content)

    def test_sign_null(self):
        response = self.client.post ('/sign_index_action/5/', {'phone': '18876594118'})
        self.assertEqual (response.status_code, 200)
        self.assertIn ('该用户未产于此次发布会！请核实'.encode (), response.content)

    def test_sign_success(self):
        response = self.client.post ('/sign_index_action/5/', {'phone': '13711001101'})
        self.assertEqual (response.status_code, 200)
        self.assertIn ('签到成功!'.encode (), response.content)

    def tearDown(self):
        pass
