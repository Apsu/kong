# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2011 OpenStack, LLC
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""Functional test case against the OpenStack Nova API server"""

import json
import os
import tempfile
import unittest
import httplib2
import urllib
import hashlib
import time
import os
import tests
import subprocess
from pprint import pprint
from utils import SERVICES
from resttest.jsontools import nested_search

r = SERVICES['keystone']
admin = SERVICES['keystone-admin']

class TestKeystoneAPI2(tests.FunctionalTest):
    tags = ['nova', 'nova-api', 'keystone']

    def test_keystone_d5_failed_auth(self):
        r.POST('/tokens',
               body={ "passwordCredentials":
                      { "username": "bad",
                        "password": "bad" }},
               code = 400)

    def test_keystone_v2_failed_auth(self):
        r.POST('/tokens',
                    body={ "auth": { "passwordCredentials":
                                     { "username": "bad",
                                       "password": "bad" }}},
                    code = 401)

    def test_keystone_d5_successful_auth(self):
        r.POST_with_keys_eq('/tokens',
                            { "auth/token/id": self.nova['X-Auth-Token'] },
                            body={ "passwordCredentials":
                                   { "username": self.keystone['user'],
                                     "password": self.keystone['pass'] }},
                            code = 200)

    def test_keystone_v2_successful_auth(self):
        r.POST_with_keys_eq('/tokens',
                            { "access/token/id": self.nova['X-Auth-Token'] },
               body={ "auth": { "passwordCredentials":
                                { "username": self.keystone['user'],
                                  "password": self.keystone['pass'] },
                                  "tenantId": self.keystone['tenantid']}},
               code = 200)

    def test_keystone_d5_bad_key(self):
        r.POST('/tokens',
               body={ "passwordCredentials":
                      { "username": self.keystone['user'],
                        "password": "badpass" }},
               code = 401)

    def test_keystone_v2_bad_key(self):
        r.POST('/tokens',
               body={ "auth": { "passwordCredentials":
                                { "username": self.keystone['user'],
                                  "password": "badpass" }}},
               code = 401)

    def test_keystone_d5_no_key(self):
        r.POST('/tokens',
               body={ "passwordCredentials":
                      { "username": self.keystone['user']}},
               code = 400)

    def test_keystone_v2_no_key(self):
        r.POST('/tokens',
               body={ "auth": { "passwordCredentials":
                                { "username": self.keystone['user']}}},
               code = 400)

    def test_keystone_v2_no_key_essex(self):
        r.POST('/tokens',
               body={ "auth": { "passwordCredentials":
                                { "username": self.keystone['user']}}},
               code = 401)

    def test_keystone_v2_get_tenant_list_essex(self):
        response, d = r.GET("/tenants")
        self.assertEqual(len(nested_search("/tenants/*/id=%s" %
                                       (self.keystone['tenantid']),
                                       d)), 1)
                                       
    def test_keystone_v2_check_token(self):
        admin.HEAD("/tokens/%s" % r.token, code=204)
