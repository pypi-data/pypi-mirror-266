# -*- coding: utf-8 -*-
#
# This file is part of the mbzero library
#
# Copyright (C) 2023 Louis Rannou
#
# This file is distributed under a BSD-2-Clause type license.
# See the LICENSE file for more information.


class MbzError(Exception):
    """Base class for all exceptions related to MusicBrainz."""
    pass


class MbzWebServiceError(MbzError):
    """Error related to MusicBrainz API requests."""
    def __init__(self, message=None, cause=None):
        """Pass ``cause`` if this exception was caused by another exception.
        """
        self.message = message
        self.cause = cause

    def __str__(self):
        if self.message:
            msg = "%s, " % self.message
        else:
            msg = ""
            msg += "caused by: %s" % str(self.cause)
        return msg


class MbzOauth2Error(MbzWebServiceError):
    """OAuth2 failure"""
    pass
