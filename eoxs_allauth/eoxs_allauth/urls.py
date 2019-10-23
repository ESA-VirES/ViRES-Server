#-------------------------------------------------------------------------------
#
# Project: EOxServer - django-allauth integration.
# Authors: Daniel Santillan <daniel.santillan@eox.at>
#          Martin Paces <martin.paces@eox.at>
#
#-------------------------------------------------------------------------------
# Copyright (C) 2016 EOX IT Services GmbH
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies of this Software or works derived from this Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#-------------------------------------------------------------------------------
# pylint: disable=missing-docstring, invalid-name

#from logging import INFO, WARNING
from django.conf.urls import url, include
from django.views.generic import TemplateView
from allauth.account.views import logout as account_logout
from .views import AccessTokenManagerView
#from .url_tools import decorate
#from .decorators import log_access

urlpatterns = [
    url(r'^', include('allauth.socialaccount.urls')),
    url(r'^', include('eoxs_allauth.vires_oauth.urls')),
    url(r"^logout/$", account_logout, name="account_logout"),
    url(r'^tokens/$', AccessTokenManagerView.as_view(), name='account_manage_access_tokens'),
]

document_urlpatterns = [
    url(r'^%s$' % name, TemplateView.as_view(template_name=("documents/%s.html" % name)), name=name)
    for name in [
        'changelog',
        'custom_data_format_description',
        'faq',
        'service_terms',
        'privacy_notice',
    ]
]
