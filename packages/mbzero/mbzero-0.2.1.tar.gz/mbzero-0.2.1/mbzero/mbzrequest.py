# -*- coding: utf-8 -*-
#
# This file is part of the mbzero library
#
# Copyright (C) 2023 Louis Rannou
#
# This file is distributed under a BSD-2-Clause type license.
# See the LICENSE file for more information.

from mbzero.mbzerror import MbzWebServiceError

import requests

MUSICBRAINZ_API = "https://musicbrainz.org/ws/2"


class MbzRequestError(MbzWebServiceError):
    """Request failed"""
    pass


class MbzSubmissionError(MbzWebServiceError):
    """Submission failed"""
    pass


class MbzRequest():
    """Base class for requests"""

    def __init__(self, user_agent, client=None):
        """Initialize a request

        :param user_agent: User agent to be sent on request"""
        self.url = MUSICBRAINZ_API
        self.user_agent = user_agent
        self.client = client or self.user_agent
        self.payload = {"fmt": "json"}

    def set_url(self, url):
        """Change the API endpoint

        :param url: new API endpoint"""
        self.url = url

    def get(self, request, credentials=None,
            headers=None, payload=None, opts=None):
        """Send a request

        :param: request: the request to send to the server
        :param url:  Optional API endpoint (defaults is musicbrainz.org API)
        :param credentials: Optional credentials class for authentication
        :param headers: Optional request headers
        :param payload: Optional request parameters"""

        url = self.url or ""

        if payload is None:
            _payload = self.payload.copy() or {}
        else:
            _payload = payload.copy()

        if headers is None:
            _headers = {}
        else:
            _headers = headers.copy()
        if "User-Agent" not in _headers:
            _headers["User-Agent"] = self.user_agent

        if opts is not None:
            if "url" in opts:
                url = opts.get("url") or ""
            if "extra_headers" in opts:
                _headers.update(opts.get("extra_headers"))
            if "extra_payload" in opts:
                _payload.update(opts.get("extra_payload"))
            for opt in "fmt", "limit", "offset":
                if opt in opts and opts.get(opt):
                    _payload[opt] = opts.get(opt)

        try:
            if credentials and credentials.has_oauth2():
                r = credentials._oauth2_get(request,
                                            payload=_payload, headers=_headers,
                                            url=url)
            elif credentials:
                cred = credentials.auth()
                r = requests.get(
                    url + request, _payload, headers=_headers,
                    auth=requests.auth.HTTPDigestAuth(cred[0], cred[1]))
            else:
                r = requests.get(url + request, _payload, headers=_headers)
            r.raise_for_status()
            return r.content
        except requests.exceptions.RequestException as e:
            raise MbzRequestError(e)

    def post(self, request, data, data_type, credentials,
             headers=None, payload=None, opts=None):
        """Send a request

        :param: request: the request to send to the server
        :param: data: the content to submit
        :param: data_type: the content type (only "xml" is supported)
        :param url:  Optional API endpoint (defaults is musicbrainz.org API)
        :param credentials: Optional credentials class for authentication
        :param headers: Optional request headers
        :param payload: Optional request parameters"""

        url = self.url or ""

        if payload is None:
            _payload = self.payload.copy() or {}
        else:
            _payload = payload.copy()
        if "client" not in _payload:
            _payload["client"] = self.client

        if headers is None:
            _headers = {}
        else:
            _headers = headers.copy()
        if "User-Agent" not in _headers:
            _headers["User-Agent"] = self.user_agent

        if data_type == "xml":
            _headers["Content-Type"] = "application/xml; charset=utf-8"
        else:
            raise Exception("Musicbrainz does not support %s content"
                            % data_type)

        if opts is not None:
            if "url" in opts:
                url = opts.get("url", "")
            if "extra_headers" in opts:
                _headers.update(opts.get("extra_headers"))
            if "extra_payload" in opts:
                _payload.update(opts.get("extra_payload"))
            for opt in "fmt", "limit", "offset":
                if opt in opts and opts.get(opt):
                    _payload[opt] = opts.get(opt)

        try:
            if credentials.has_oauth2():
                r = credentials._oauth2_post(request, data=data,
                                             payload=_payload,
                                             headers=_headers,
                                             url=url)
            else:
                cred = credentials.auth()
                r = requests.post(
                    url + request, data=data, params=_payload, headers=_headers,
                    auth=requests.auth.HTTPDigestAuth(cred[0], cred[1]))
            r.raise_for_status()
            return r.content
        except requests.exceptions.RequestException as e:
            raise MbzSubmissionError(e)


class MbzRequestLookup(MbzRequest):
    """Class for lookup requests"""

    def __init__(self, user_agent, entity_type, mbid, includes=[]):
        """Initialize a lookup request

        :param user_agent: string User agent to be sent on request
        :param entity_type: string Musicbrainz entity
        :param mbid: string Musicbrainz ID
        :param includes: list of strings of Musicbrainz includes"""
        super().__init__(user_agent)
        self.entity_type = entity_type
        self.mbid = mbid
        self.includes = includes

    def send(self, credentials=None, opts=None):
        """Format the request and send

        :param credentials: Optional MbzCredentials for authentication
        :param opts: Optional dictionary of parameters.
                     Valid options are url, fmt, limit, offset"""
        payload = self.payload

        if self.includes:
            payload["inc"] = "+".join(self.includes)
        request = "/%s/%s" % (self.entity_type, self.mbid)

        return super().get(request, credentials=credentials,
                           payload=payload, opts=opts)


class MbzRequestBrowse(MbzRequest):
    """Class for browse requests"""

    def __init__(self, user_agent, entity_type,
                 bw_entity_type, mbid, includes=[]):
        """Initialize a lookup request

        :param user_agent: string User agent to be sent on request
        :param entity_type: string Musicbrainz entity
        :param bw_entity_type: string Musicbrainz browse entity
        :param mbid: string Musicbrainz ID
        :param includes: list of strings of Musicbrainz includes"""
        super().__init__(user_agent)
        self.entity_type = entity_type
        self.bw_entity_type = bw_entity_type
        self.mbid = mbid
        self.includes = includes

    def send(self, credentials=None, opts=None):
        """Format the request and send

        :param credentials: Optional MbzCredentials for authentication
        :param opts: Optional dictionary of parameters.
                     Valid options are url, fmt, limit, offset"""
        payload = self.payload

        if self.includes:
            payload["inc"] = "+".join(self.includes)
        request = "/%s?%s=%s" % (self.entity_type, self.bw_entity_type,
                                 self.mbid)

        return super().get(request, credentials=credentials,
                           payload=payload, opts=opts)


class MbzRequestSearch(MbzRequest):
    """Class for search requests"""
    def __init__(self, user_agent, entity_type, query):
        """Initialize a lookup request

        :param user_agent: string User agent to be sent on request
        :param entity_type: string Musicbrainz entity
        :param query: string Musicbrainz query"""
        super().__init__(user_agent)
        self.entity_type = entity_type
        self.query = query

    def send(self, credentials=None, opts=None):
        """Format the request and send

        :param credentials: Optional MbzCredentials for authentication
        :param opts: Optional dictionary of parameters.
                     Valid options are url, fmt, limit, offset"""
        payload = self.payload

        request = "/%s?query=%s" % (self.entity_type, self.query)

        return super().get(request, credentials=credentials,
                           payload=payload, opts=opts)


class MbzSubmission(MbzRequest):
    """Class for submissions"""
    def __init__(self, user_agent, entity_type, data, data_type, client=None):
        """Initialize the submission request

        :param user_agent: string User agent to be sent on request
        :param entity_type: string Musicbrainz entity to submit
        :param data: string content to submit
        :param data_type: string data content type (only xml is supported)
        :param client: optional client (defaults to user agent)"""
        super().__init__(user_agent, client)
        self.entity_type = entity_type
        self.data = data
        if data_type != "xml":
            raise Exception("Data content %s is not supported" % data_type)
        self.data_type = data_type

    def send(self, credentials=None, opts=None):
        """Format the submission and send

        :param credentials: Optional MbzCredentials for authentication
        :param opts: Optional dictionary of parameters.
                     Valid options are url, fmt, limit, offset"""
        payload = self.payload

        request = "/%s" % (self.entity_type)

        return super().post(request, self.data, self.data_type,
                            credentials=credentials,
                            payload=payload, opts=opts)
