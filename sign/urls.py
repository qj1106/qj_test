# -*- coding: utf-8 -*-
from django.conf.urls import url
from sign import views_if

urlpatterns = [
    # guest system interface:
    # ex : /api/add_event/
    url (r'^add_event/', views_if.add_event, name='add_event'),
    # ex:  /api/get_event/
    url (r'^get_event/', views_if.get_event, name='get_event'),
    # ex:  /api/add_guest/
    url (r'^add_guest/', views_if.add_guest, name='add_guest'),
    # ex:  /api/get_guest/
    url (r'^get_guest/', views_if.get_guest, name='get_guest'),
    # ex:  /api/user_sign/
    url (r'^user_sign/', views_if.user_sign, name='user_sign'),
]
