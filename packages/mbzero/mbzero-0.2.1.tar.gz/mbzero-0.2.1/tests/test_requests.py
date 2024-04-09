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

from mbzero import mbzrequest as mbr


MUSICBRAINZ_API = mbr.MUSICBRAINZ_API
OTHER_API = "https://example.com"


@patch('requests.get')
class RequestTest(unittest.TestCase):
    def setUp(self):
        self.user_agent = "test_user_agent"
        self.headers = {"User-Agent": self.user_agent}
        self.payload = {"fmt": "json"}

    def testSend(self, mock_get):
        mbr.MbzRequest(self.user_agent
                       ).get("/request",
                             payload=self.payload, headers=self.headers)
        mock_get.assert_called_once_with(
            MUSICBRAINZ_API + "/request", self.payload, headers=self.headers)

    def testSendOpts(self, mock_get):
        mbr.MbzRequest(self.user_agent
                       ).get("/request",
                             payload=self.payload, headers=self.headers,
                             opts={"limit": 10})
        self.payload["limit"] = 10
        mock_get.assert_called_once_with(
            MUSICBRAINZ_API + "/request",
            self.payload, headers=self.headers)

    def testSendOptsExtraHeaders(self, mock_get):
        extraHeaders = {"my": "header"}
        expectedHeaders = dict(self.headers, **extraHeaders)
        mbr.MbzRequest(self.user_agent
                       ).get("/request",
                             payload=self.payload, headers=self.headers,
                             opts={"extra_headers": extraHeaders})
        mock_get.assert_called_once_with(
            MUSICBRAINZ_API + "/request", self.payload, headers=expectedHeaders)

    def testSendOptsExtraPayloads(self, mock_get):
        extraPayload = {"my": "payload"}
        expectedPayload = dict(self.payload, **extraPayload)
        mbr.MbzRequest(self.user_agent
                       ).get("/request",
                             payload=self.payload, headers=self.headers,
                             opts={"extra_payload": extraPayload})
        mock_get.assert_called_once_with(
            MUSICBRAINZ_API + "/request", expectedPayload, headers=self.headers)

    def testSendOptsAPIOther(self, mock_get):
        mbr.MbzRequest(self.user_agent
                       ).get("/request",
                             payload=self.payload, headers=self.headers,
                             opts={"url": OTHER_API})
        mock_get.assert_called_once_with(
            OTHER_API + "/request", self.payload, headers=self.headers)

    def testSendOptsAPINone(self, mock_get):
        mbr.MbzRequest(self.user_agent
                       ).get("/request",
                             payload=self.payload, headers=self.headers,
                             opts={"url": ""})
        mock_get.assert_called_once_with(
            "/request", self.payload, headers=self.headers)

    def testSendSetAPINone(self, mock_get):
        req = mbr.MbzRequest(self.user_agent
                             )
        req.set_url("")
        req.get("/request",
                payload=self.payload, headers=self.headers)
        mock_get.assert_called_once_with(
            "/request", self.payload, headers=self.headers)


@patch('requests.get')
class LookupTest(unittest.TestCase):
    def setUp(self):
        self.user_agent = "test_user_agent"
        self.headers = {"User-Agent": self.user_agent}
        self.payload = {"fmt": "json"}

    def testLookup(self, mock_get):
        mbr.MbzRequestLookup(self.user_agent, "artist",
                             "0383dadf-2a4e-4d10-a46a-e9e041da8eb3").send()
        mock_get.assert_called_once_with(
            MUSICBRAINZ_API + "/artist/0383dadf-2a4e-4d10-a46a-e9e041da8eb3",
            self.payload, headers=self.headers)

    def testLookupAPIOther(self, mock_get):
        mbr.MbzRequestLookup(self.user_agent, "artist",
                             "0383dadf-2a4e-4d10-a46a-e9e041da8eb3"
                             ).send(opts={"url": OTHER_API})
        mock_get.assert_called_once_with(
            OTHER_API + "/artist/0383dadf-2a4e-4d10-a46a-e9e041da8eb3",
            self.payload, headers=self.headers)

    def testLookupAPINone(self, mock_get):
        mbr.MbzRequestLookup(self.user_agent, "artist",
                             "0383dadf-2a4e-4d10-a46a-e9e041da8eb3"
                             ).send(opts={"url": ""})
        mock_get.assert_called_once_with(
            "/artist/0383dadf-2a4e-4d10-a46a-e9e041da8eb3",
            self.payload, headers=self.headers)

    def testLookupSetAPI(self, mock_get):
        req = mbr.MbzRequestLookup(self.user_agent, "artist",
                                   "0383dadf-2a4e-4d10-a46a-e9e041da8eb3")
        req.set_url(OTHER_API)
        req.send()
        mock_get.assert_called_once_with(
            OTHER_API + "/artist/0383dadf-2a4e-4d10-a46a-e9e041da8eb3",
            self.payload, headers=self.headers)

    def testLookupSetAPINone(self, mock_get):
        req = mbr.MbzRequestLookup(self.user_agent,
                                   "artist",
                                   "0383dadf-2a4e-4d10-a46a-e9e041da8eb3")
        req.set_url("")
        req.send()
        mock_get.assert_called_once_with(
            "/artist/0383dadf-2a4e-4d10-a46a-e9e041da8eb3",
            self.payload, headers=self.headers)

    def testLookupOpts(self, mock_get):
        expectedPayload = self.payload.copy()
        expectedPayload["limit"] = 10
        mbr.MbzRequestLookup(self.user_agent,
                             "artist", "0383dadf-2a4e-4d10-a46a-e9e041da8eb3"
                             ).send(opts={"limit": 10})
        mock_get.assert_called_once_with(
            MUSICBRAINZ_API + "/artist/0383dadf-2a4e-4d10-a46a-e9e041da8eb3",
            expectedPayload, headers=self.headers)

    def testLookupOptsNone(self, mock_get):
        mbr.MbzRequestLookup(self.user_agent,
                             "artist", "0383dadf-2a4e-4d10-a46a-e9e041da8eb3"
                             ).send(opts={"limit": None})
        mock_get.assert_called_once_with(
            MUSICBRAINZ_API + "/artist/0383dadf-2a4e-4d10-a46a-e9e041da8eb3",
            self.payload, headers=self.headers)

    def testLookupXml(self, mock_get):
        self.payload["fmt"] = "xml"
        mbr.MbzRequestLookup(self.user_agent,
                             "artist", "0383dadf-2a4e-4d10-a46a-e9e041da8eb3"
                             ).send(opts={"fmt": "xml"})
        mock_get.assert_called_once_with(
            MUSICBRAINZ_API + "/artist/0383dadf-2a4e-4d10-a46a-e9e041da8eb3",
            self.payload, headers=self.headers)

    def testLookupFmtNone(self, mock_get):
        mbr.MbzRequestLookup(self.user_agent,
                             "artist", "0383dadf-2a4e-4d10-a46a-e9e041da8eb3"
                             ).send(opts={"fmt": None})
        mock_get.assert_called_once_with(
            MUSICBRAINZ_API + "/artist/0383dadf-2a4e-4d10-a46a-e9e041da8eb3",
            self.payload, headers=self.headers)

    def testLookupInc(self, mock_get):
        self.payload["inc"] = "recordings+releases+release-groups"
        mbr.MbzRequestLookup(self.user_agent,
                             "artist", "0383dadf-2a4e-4d10-a46a-e9e041da8eb3",
                             ["recordings", "releases", "release-groups"]
                             ).send()
        mock_get.assert_called_once_with(
            MUSICBRAINZ_API + "/artist/0383dadf-2a4e-4d10-a46a-e9e041da8eb3",
            self.payload, headers=self.headers)


@patch('requests.get')
class BrowseTest(unittest.TestCase):
    def setUp(self):
        self.user_agent = "test_user_agent"
        self.headers = {"User-Agent": self.user_agent}
        self.payload = {"fmt": "json"}

    def testBrowse(self, mock_get):
        mbr.MbzRequestBrowse(self.user_agent, "release", "artist",
                             "0383dadf-2a4e-4d10-a46a-e9e041da8eb3").send()
        mock_get.assert_called_once_with(
            MUSICBRAINZ_API +
            "/release?artist=0383dadf-2a4e-4d10-a46a-e9e041da8eb3",
            self.payload, headers=self.headers)

    def testBrowseAPIOther(self, mock_get):
        mbr.MbzRequestBrowse(self.user_agent, "release", "artist",
                             "0383dadf-2a4e-4d10-a46a-e9e041da8eb3"
                             ).send(opts={"url": OTHER_API})
        mock_get.assert_called_once_with(
            OTHER_API +
            "/release?artist=0383dadf-2a4e-4d10-a46a-e9e041da8eb3",
            self.payload, headers=self.headers)

    def testBrowseAPINone(self, mock_get):
        mbr.MbzRequestBrowse(self.user_agent, "release",
                             "artist", "0383dadf-2a4e-4d10-a46a-e9e041da8eb3"
                             ).send(opts={"url": ""})
        mock_get.assert_called_once_with(
            "/release?artist=0383dadf-2a4e-4d10-a46a-e9e041da8eb3",
            self.payload, headers=self.headers)

    def testBrowseSetAPI(self, mock_get):
        req = mbr.MbzRequestBrowse(self.user_agent, "release", "artist",
                                   "0383dadf-2a4e-4d10-a46a-e9e041da8eb3")
        req.set_url(OTHER_API)
        req.send()
        mock_get.assert_called_once_with(
            OTHER_API
            + "/release?artist=0383dadf-2a4e-4d10-a46a-e9e041da8eb3",
            self.payload, headers=self.headers)

    def testBrowseSetAPINone(self, mock_get):
        req = mbr.MbzRequestBrowse(self.user_agent, "release", "artist",
                                   "0383dadf-2a4e-4d10-a46a-e9e041da8eb3")
        req.set_url("")
        req.send()
        mock_get.assert_called_once_with(
            "/release?artist=0383dadf-2a4e-4d10-a46a-e9e041da8eb3",
            self.payload, headers=self.headers)

    def testBrowseOpts(self, mock_get):
        self.payload["limit"] = 10
        mbr.MbzRequestBrowse(self.user_agent, "release", "artist",
                             "0383dadf-2a4e-4d10-a46a-e9e041da8eb3"
                             ).send(opts={"limit": 10})
        mock_get.assert_called_once_with(
            MUSICBRAINZ_API +
            "/release?artist=0383dadf-2a4e-4d10-a46a-e9e041da8eb3",
            self.payload, headers=self.headers)

    def testBrowseOptsNone(self, mock_get):
        mbr.MbzRequestBrowse(self.user_agent, "release", "artist",
                             "0383dadf-2a4e-4d10-a46a-e9e041da8eb3"
                             ).send(opts={"limit": None})
        mock_get.assert_called_once_with(
            MUSICBRAINZ_API +
            "/release?artist=0383dadf-2a4e-4d10-a46a-e9e041da8eb3",
            self.payload, headers=self.headers)

    def testBrowseXml(self, mock_get):
        self.payload["fmt"] = "xml"
        mbr.MbzRequestBrowse(self.user_agent, "release", "artist",
                             "0383dadf-2a4e-4d10-a46a-e9e041da8eb3"
                             ).send(opts={"fmt": "xml"})
        mock_get.assert_called_once_with(
            MUSICBRAINZ_API +
            "/release?artist=0383dadf-2a4e-4d10-a46a-e9e041da8eb3",
            self.payload, headers=self.headers)

    def testBrowseFmtNone(self, mock_get):
        mbr.MbzRequestBrowse(self.user_agent, "release", "artist",
                             "0383dadf-2a4e-4d10-a46a-e9e041da8eb3"
                             ).send(opts={"fmt": None})
        mock_get.assert_called_once_with(
            MUSICBRAINZ_API +
            "/release?artist=0383dadf-2a4e-4d10-a46a-e9e041da8eb3",
            self.payload, headers=self.headers)

    def testBrowseInc(self, mock_get):
        self.payload["inc"] = "recordings+releases+release-groups"
        mbr.MbzRequestBrowse(self.user_agent, "release", "artist",
                             "0383dadf-2a4e-4d10-a46a-e9e041da8eb3",
                             ["recordings", "releases", "release-groups"]
                             ).send()
        mock_get.assert_called_once_with(
            MUSICBRAINZ_API +
            "/release?artist=0383dadf-2a4e-4d10-a46a-e9e041da8eb3",
            self.payload, headers=self.headers)


@patch('requests.get')
class SearchTest(unittest.TestCase):
    def setUp(self):
        self.user_agent = "test_user_agent"
        self.headers = {"User-Agent": self.user_agent}
        self.payload = {"fmt": "json"}

    def testSearch(self, mock_get):
        mbr.MbzRequestSearch(self.user_agent, "release", "QUERY").send()
        mock_get.assert_called_once_with(
            MUSICBRAINZ_API + "/release?query=QUERY",
            self.payload, headers=self.headers)

    def testSearchAPIOther(self, mock_get):
        mbr.MbzRequestSearch(self.user_agent, "release", "QUERY"
                             ).send(opts={"url": OTHER_API})
        mock_get.assert_called_once_with(
            OTHER_API + "/release?query=QUERY",
            self.payload, headers=self.headers)

    def testSearchAPINone(self, mock_get):
        mbr.MbzRequestSearch(self.user_agent, "release", "QUERY"
                             ).send(opts={"url": ""})
        mock_get.assert_called_once_with(
            "/release?query=QUERY",
            self.payload, headers=self.headers)

    def testSearchSetAPI(self, mock_get):
        req = mbr.MbzRequestSearch(self.user_agent, "release", "QUERY")
        req.set_url(OTHER_API)
        req.send()
        mock_get.assert_called_once_with(
            OTHER_API + "/release?query=QUERY",
            self.payload, headers=self.headers)

    def testSearchSetAPINone(self, mock_get):
        req = mbr.MbzRequestSearch(self.user_agent, "release", "QUERY")
        req.set_url("")
        req.send()
        mock_get.assert_called_once_with(
            "/release?query=QUERY",
            self.payload, headers=self.headers)

    def testSearchOpts(self, mock_get):
        self.payload["limit"] = 10
        mbr.MbzRequestSearch(self.user_agent, "release", "QUERY"
                             ).send(opts={"limit": 10})
        mock_get.assert_called_once_with(
            MUSICBRAINZ_API + "/release?query=QUERY",
            self.payload, headers=self.headers)

    def testSearchOptsNone(self, mock_get):
        mbr.MbzRequestSearch(self.user_agent, "release", "QUERY"
                             ).send(opts={"limit": None})
        mock_get.assert_called_once_with(
            MUSICBRAINZ_API + "/release?query=QUERY",
            self.payload, headers=self.headers)

    def testSearchXml(self, mock_get):
        self.payload["fmt"] = "xml"
        mbr.MbzRequestSearch(self.user_agent, "release", "QUERY"
                             ).send(opts={"fmt": "xml"})
        mock_get.assert_called_once_with(
            MUSICBRAINZ_API + "/release?query=QUERY",
            self.payload, headers=self.headers)

    def testSearchFmtNone(self, mock_get):
        mbr.MbzRequestSearch(self.user_agent, "release", "QUERY"
                             ).send(opts={"fmt": None})
        mock_get.assert_called_once_with(
            MUSICBRAINZ_API + "/release?query=QUERY",
            self.payload, headers=self.headers)
