from django.test import TestCase, Client
from lesson import models, views

# Create your tests here.

from unittest import mock
import ddt

@ddt.ddt
class MaterialTestcase(TestCase):

    def setUp(self):
        super(MaterialTestcase, self).setUp()
        self.client = Client()
        self.user = models.User(first_name='testuser')
        self.user.save()

    def test_material_created_return_200(self):

        response = self.client.post(
            '/create/',
            {'title': 'testtitle',
             'body': 'testbody',
             'material_type': 'practice'},
        )

        self.assertEqual(response.status_code, 200)


    def test_material_one_material(self):

        self.client.post(
            '/create/',
            {'title': 'testtitle',
             'body': 'testbody',
             'material_type': 'practice'},
        )

        material = models.Material.objects.get()
        self.assertEqual(material.title, 'testtitle')

    @ddt.data('sl1', 'sl2')
    def test_material_slug_created(self, title):
        self.client.post(
            '/create/',
            {'title': title,
             'body': 'testbody',
             'material_type': 'practice'},
        )

        material = models.Material.objects.get()
        self.assertEqual(material.slug, title)

    @ddt.data(
        ('sl 1', 'sl-1'),
        ('s l2', 's-l2'),
        ('s l 3', 's-l-3'),
    )
    @ddt.unpack
    def test_material_slug_created_correctly(self, title, expected_slug):
        self.client.post(
            '/create/',
            {'title': title,
             'body': 'testbody',
             'material_type': 'practice'},
        )

        material = models.Material.objects.get()
        self.assertEqual(material.slug, expected_slug)

    def test_send_mail(self):
        material = models.Material(slug='slug',
                                   author=self.user,
                                   body='mybody')
        material.save()

        with mock.patch('lesson.views.send_mail') as mail_mock:
            response = self.client.post(
                '/'+str(material.id)+'/share/',
                {'name': 'test_name',
                 'to_email': 'test@mail.com',
                 'comment': 'comment'},
            )

            mail_mock.assert_called_once()

    @mock.patch('lesson.views.send_mail')
    def test_send_mail_args(self, mail_mock):
        material = models.Material(slug='slug',
                                   author=self.user,
                                   body='mybody')
        material.save()

        response = self.client.post(
            '/'+str(material.id)+'/share/',
            {'name': 'test_name',
                'to_email': 'test@mail.com',
                'comment': 'comment'},
        )

        # response = self.client.post(
        #     '/'+str(material.id)+'/share/',
        #     {'name': 'test_name',
        #         'to_email': 'test@mail.com',
        #         'comment': 'comment'},
        # )
        expected_body = views.TEMPLATE.format(
            title='',
            uri='http://testserver/2021/1/5/slug/',
            name='test_name',
            comment='comment',
        )
        mail_mock.assert_called_with('test_name asks you to review: ',
                                     expected_body,
                                     'supersiteadmin@mysote.com',
                                     ['test@mail.com'])

        # self.assertEqual(mail_mock.call_args_list[0][0][1], expected_body)
        mail_mock.assert_called_once()


