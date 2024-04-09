# -*- coding: utf-8 -*-
#
# This file is part of the mbzero library
#
# Copyright (C) 2023 Louis Rannou
#
# This file is distributed under a BSD-2-Clause type license. See the LICENSE
# file for more information.

import unittest
from unittest.mock import patch

from mbzero import mbzauth as mba


class AuthTest(unittest.TestCase):
    def testAuth(self):
        cred = mba.MbzCredentials()
        self.assertFalse(cred.has_auth())
        cred.auth_set("name", "pass")
        self.assertTrue(cred.has_auth())
        self.assertEqual(cred.auth(), ("name", "pass"))
        cred.auth_set(None, None)
        self.assertFalse(cred.has_auth())

    def testOauth2(self):
        cred = mba.MbzCredentials()
        self.assertFalse(cred.has_oauth2())
        cred.oauth2_new("token")
        self.assertTrue(cred.has_oauth2())
        cred.oauth2_new(None)
        self.assertFalse(cred.has_oauth2())


class Oauth2TestInit(unittest.TestCase):
    def setUp(self):
        self.client_id = "clientID"
        self.client_secret = "clientSecret"
        self.token = "token"
        self.refresh = "refresh"
        self.cred = mba.MbzCredentials()

    @patch('requests_oauthlib.OAuth2Session.authorization_url')
    def testInit(self, mock_auth):
        mock_auth.return_value = ["auth_url", 1]
        self.cred.oauth2_init(self.client_id)
        mock_auth.assert_called_once_with(
            mba.MUSICBRAINZ_OAUTH2 + mba.OAUTH2_PATH_AUTH
        )

    @patch('requests_oauthlib.OAuth2Session.authorization_url')
    def testInitURLOther(self, mock_auth):
        self.cred = mba.MbzCredentials(oauth2_url="somewhere")
        mock_auth.return_value = ["auth_url", 1]
        self.cred.oauth2_init(self.client_id)
        mock_auth.assert_called_once_with(
            "somewhere" + mba.OAUTH2_PATH_AUTH
        )

    @patch('requests_oauthlib.OAuth2Session.authorization_url')
    def testInitURLChange(self, mock_auth):
        self.cred.oauth2_set_url("somewhere")
        mock_auth.return_value = ["auth_url", 1]
        self.cred.oauth2_init(self.client_id)
        mock_auth.assert_called_once_with(
            "somewhere" + mba.OAUTH2_PATH_AUTH
        )

    @patch('requests_oauthlib.OAuth2Session.authorization_url')
    def testInitURLSetOther(self, mock_auth):
        mock_auth.return_value = ["auth_url", 1]
        self.cred.oauth2_init(self.client_id, url="somewhere")
        mock_auth.assert_called_once_with(
            "somewhere"
        )


class Oauth2Process(unittest.TestCase):
    def setUp(self):
        self.client_id = "clientID"
        self.client_secret = "clientSecret"
        self.token = "token"
        self.refresh = "refresh"
        self.cred = mba.MbzCredentials()
        self.cred.oauth2_new(self.token, self.refresh,
                             client_id=self.client_id,
                             client_secret=self.client_secret)
        self.headers = {"Authorization": "Bearer %s" % self.token}

    @patch('requests_oauthlib.OAuth2Session.fetch_token')
    def testConfirm(self, mock_fetch):
        mock_fetch.return_value = {"access_token": self.token,
                                   "refresh_token": self.refresh}
        self.cred.oauth2_confirm("code", self.client_secret)
        mock_fetch.assert_called_once_with(
            mba.MUSICBRAINZ_OAUTH2 + mba.OAUTH2_PATH_TOKEN,
            code="code", client_secret=self.client_secret)

    @patch('requests_oauthlib.OAuth2Session.fetch_token')
    def testConfirmAPIOther(self, mock_fetch):
        mock_fetch.return_value = {"access_token": self.token,
                                   "refresh_token": self.refresh}
        self.cred.oauth2_confirm("code", self.client_secret,
                                 url="somewhere")
        mock_fetch.assert_called_once_with(
            "somewhere", code="code", client_secret=self.client_secret)

    @patch('requests_oauthlib.OAuth2Session.refresh_token')
    def testRefresh(self, mock_refresh):
        mock_refresh.return_value = {"access_token": self.token,
                                     "refresh_token": self.refresh}
        self.cred.oauth2_refresh(self.refresh)
        mock_refresh.assert_called_once_with(
            mba.MUSICBRAINZ_OAUTH2 + mba.OAUTH2_PATH_TOKEN,
            refresh_token=self.refresh,
            client_id=self.client_id, client_secret=self.client_secret)

    @patch('requests_oauthlib.OAuth2Session.refresh_token')
    def testRefreshAPIOther(self, mock_refresh):
        mock_refresh.return_value = {"access_token": self.token,
                                     "refresh_token": self.refresh}
        self.cred.oauth2_refresh(self.refresh,
                                 url="somewhere")
        mock_refresh.assert_called_once_with(
            "somewhere",
            refresh_token=self.refresh,
            client_id=self.client_id, client_secret=self.client_secret)

    @patch('requests_oauthlib.OAuth2Session.get')
    def testGet(self, mock_get):
        self.cred._oauth2_get("/request")
        mock_get.assert_called_once_with(
            mba.MUSICBRAINZ_OAUTH2 + "/request",
            params={}, headers=self.headers)

    @patch('requests_oauthlib.OAuth2Session.get')
    def testGetAPIOther(self, mock_get):
        self.cred._oauth2_get("/request", url="somewhere")
        mock_get.assert_called_once_with(
            "somewhere/request",
            params={}, headers=self.headers)

    @patch('requests_oauthlib.OAuth2Session.get')
    def testGetAPIEmpty(self, mock_get):
        self.cred._oauth2_get("/request", url="")
        mock_get.assert_called_once_with(
            "/request",
            params={}, headers=self.headers)

    @patch('requests_oauthlib.OAuth2Session.get')
    def testGetWithPayload(self, mock_get):
        self.cred._oauth2_get("/request", payload={"pl": "test"})
        mock_get.assert_called_once_with(
            mba.MUSICBRAINZ_OAUTH2 + "/request",
            params={"pl": "test"}, headers=self.headers)

    @patch('requests_oauthlib.OAuth2Session.get')
    def testGetWithHeaders(self, mock_get):
        headers = {"hd": "test"}
        self.cred._oauth2_get("/request", headers=headers)
        headers.update(self.headers)
        mock_get.assert_called_once_with(
            mba.MUSICBRAINZ_OAUTH2 + "/request",
            params={}, headers=headers)
