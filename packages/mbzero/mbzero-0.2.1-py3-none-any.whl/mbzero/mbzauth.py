# -*- coding: utf-8 -*-
#
# This file is part of the mbzero library
# Copyright (C) 2023 Louis Rannou
# This file is distributed under a BSD-2-Clause type license.
# See the LICENSE file for more information.

from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import OAuth2Error

from mbzero.mbzerror import MbzWebServiceError, MbzOauth2Error

from mbzero.oauth2_session_revoke import revoke_token

MUSICBRAINZ_OAUTH2_URI = "urn:ietf:wg:oauth:2.0:oob"
MUSICBRAINZ_HN = "https://musicbrainz.org"
MUSICBRAINZ_OAUTH2 = MUSICBRAINZ_HN + "/oauth2"
OAUTH2_PATH_AUTH = "/authorize"
OAUTH2_PATH_TOKEN = "/token"
OAUTH2_PATH_REVOKE = "/revoke"


class MbzCredentials():
    """Class for Musicbrainz authentication."""

    def __init__(self, oauth2_url=None):
        """Initialize credentials

        :param oauth2_url: optional OAuth2 endpoint"""
        self.name = None
        self.password = None
        self.oauth2_url = oauth2_url or MUSICBRAINZ_OAUTH2
        self.oauth2_client_id = None
        self.oauth2_client_secret = None
        self.oauth2_session = None
        self.oauth2_token = None
        self.oauth2_refresh_token = None

    def has_auth(self):
        """Returns true if name/passwd credentials have been set"""
        return (self.name is not None) and (self.password is not None)

    def has_oauth2(self):
        """Returns true if OAuth2 has been set"""
        return self.oauth2_token is not None

    def auth_set(self, name, passwd):
        """Username/password authentication"""
        self.name = name
        self.password = passwd

    def auth(self):
        """Get username/password"""
        return (self.name, self.password)

    def oauth2(self):
        """Get the OAuth2 session"""
        return self.oauth2_session

    def oauth2_set_url(self, url):
        """Change the default OAuth2 endpoint"""
        self.oauth2_url = url

    def oauth2_new(self, token, refresh_token=None,
                   client_id=None, client_secret=None,
                   redirect_uri=MUSICBRAINZ_OAUTH2_URI, scope=[]):
        """Create a session with existing tokens

        :param token: access token to use for authentication
        :param refresh_token: refresh token to use for refreshing
        :param client_id: optional client application ID
        :param client_secret: optional client application secret
        :param redirect_uri: optional redirect URI (defaults to the redirect
                             URI defined in the Musicbrainz documentation)
        :param scope: optional Musicbrainz scope"""
        try:
            self.oauth2_session = OAuth2Session(client_id,
                                                redirect_uri=redirect_uri,
                                                scope=scope)
            self.oauth2_client_id = client_id
            self.oauth2_client_secret = client_secret
            self.oauth2_token = token
            self.oauth2_refresh_token = refresh_token
        except Exception as e:
            raise MbzOauth2Error(e)

    def oauth2_init(self, client_id, url=None,
                    redirect_uri=MUSICBRAINZ_OAUTH2_URI, scope=[]):
        """Initialize the creation of tokens

        :param client_id: client application ID
        :param url: optional authentification endpoint(defaults to musicbrainz)
        :param redirect_uri: optional redirect URI (defaults to the redirect
                             URI defined in the Musicbrainz documentation)
        :param scope: optional Musicbrainz scope
        :return: an authorization URL to visit"""
        if url is None:
            url = self.oauth2_url + OAUTH2_PATH_AUTH

        try:
            self.oauth2_session = OAuth2Session(client_id,
                                                redirect_uri=redirect_uri,
                                                scope=scope)
            auth_url, _ = self.oauth2_session.authorization_url(url)
            self.oauth2_client_id = client_id
            return auth_url
        except Exception as e:
            raise MbzOauth2Error(e)

    def oauth2_confirm(self, response_code, client_secret,
                       url=None):
        """Confirm the authorization with the response code.

        :param response_code: the response code given by the authentication URL
        :param client_secret: client application secret
        :param url: optional token endpoint (defaults to musicbrainz)
        :return: the access token"""
        if url is None:
            url = self.oauth2_url + OAUTH2_PATH_TOKEN

        try:
            token = self.oauth2_session.fetch_token(
                url, code=response_code,
                client_secret=client_secret)
            self.oauth2_client_secret = client_secret
            self.oauth2_token = token["access_token"]
            self.oauth2_refresh_token = token["refresh_token"]
            return token
        except Exception as e:
            raise MbzOauth2Error(e)

    def oauth2_refresh(self, refresh_token=None,
                       url=None):
        """Refresh an access token.

        :param refresh_token: optional refresh token used to refresh the
                              access token
        :param url: optional token endpoint (defaults to musicbrainz)
        :return: the new access token"""
        if not self.oauth2_refresh_token and not refresh_token:
            raise MbzOauth2Error("No refresh token known")
        elif not refresh_token:
            refresh_token = self.oauth2_refresh_token

        if url is None:
            url = self.oauth2_url + OAUTH2_PATH_TOKEN

        try:
            token = self.oauth2_session.refresh_token(
                url, refresh_token=refresh_token,
                client_id=self.oauth2_client_id,
                client_secret=self.oauth2_client_secret)
            self.oauth2_token = token["access_token"]
            return token
        except Exception as e:
            raise MbzOauth2Error(e)

    def oauth2_revoke(self, token=None, url=None):
        """Revoke a token pair

        :param token: optional token used to refresh the access token
        :param url: optional revocation endpoint (defaults to musicbrainz)
        """
        if not self.oauth2_token and not token:
            raise MbzOauth2Error("No refresh token known")
        elif not token:
            token = self.oauth2_token

        if url is None:
            url = self.oauth2_url + OAUTH2_PATH_REVOKE

        try:
            revoke_token(self.oauth2_session,
                         url, token,
                         client_id=self.oauth2_client_id,
                         client_secret=self.oauth2_client_secret)
        except OAuth2Error as e:
            raise MbzOauth2Error(e)

    def _oauth2_get(self, request, payload={}, headers={},
                    url=None):
        """OAuth2 GET request

        :param: request: the request to send to the server
        :param payload: Optional request parameters
        :param headers: Optional request headers
        :param url: Optional API endpoint (defaults is to
                    musicbrainz.org OAuth2 endpoint)
        :return: the result of the request"""
        if url is None:
            url = self.oauth2_url

        headers["Authorization"] = "Bearer %s" % self.oauth2_token

        return self.oauth2_session.get(
            url + request, params=payload,
            headers=headers)

    def _oauth2_post(self, request, payload={}, headers={},
                     data=None, url=None):
        if url is None:
            url = self.oauth2_url

        headers["Authorization"] = "Bearer %s" % self.oauth2_token

        return self.oauth2_session.post(
            url + request, data=data, params=payload,
            headers=headers)
