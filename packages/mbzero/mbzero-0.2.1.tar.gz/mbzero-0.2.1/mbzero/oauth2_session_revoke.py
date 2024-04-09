# -*- coding: utf-8 -*-
#
# This file is part of the mbzero library
# Copyright (C) 2023 Louis Rannou
# This file is distributed under a BSD-2-Clause type license.
# See the LICENSE file for more information.

from oauthlib.oauth2 import InsecureTransportError, is_secure_transport
from oauthlib.oauth2 import TemporarilyUnavailableError, ServerError
from oauthlib.oauth2 import UnsupportedTokenTypeError


def revoke_token(
        oauth2_session,
        revoke_url,
        token,
        body="",
        auth=None,
        timeout=None,
        headers=None,
        verify=None,
        proxies=None,
        **kwargs):
    """Request to revoke token. This is handmade since it does not exist in
    requests_oauthlib

    :param revoke_url: The revocation endpoint, must be HTTPS.
    :param token: The access token to revoke
    :param body: Optional application/x-www-form-urlencoded body to add the
                 include in the token request. Prefer kwargs over body.
    :param auth: An auth tuple or method as accepted by `requests`.
    :param timeout: Timeout of the request in seconds.
    :param headers: A dict of headers to be used by `requests`.
    :param verify: Verify SSL certificate.
    :param proxies: The `proxies` argument will be passed to `requests`.
    :param kwargs: Extra parameters to include in the token request.
    """
    if not revoke_url:
        raise ValueError("No token endpoint set for auto_refresh.")

    if not is_secure_transport(revoke_url):
        raise InsecureTransportError()

    _headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    if headers:
        _headers.update(headers)

    data = {'token': token}
    if 'client_id' in kwargs:
        data['client_id'] = kwargs['client_id']
    if 'client_secret' in kwargs:
        data['client_secret'] = kwargs['client_secret']

    print(revoke_url)
    print(data)
    print(headers)

    r = oauth2_session.post(revoke_url,
                            data=data,
                            auth=auth,
                            timeout=timeout,
                            headers=_headers,
                            verify=verify,
                            withhold_token=True,
                            proxies=proxies
                            )
    if not r.ok and r.status_code == 400:
        if 'unsupported_token_type' in r.text:
            raise UnsupportedTokenTypeError(
                "Revocation not supported by server")
        raise ServerError('Server error')
    elif r.status_code == 503:
        raise TemporarilyUnavailableError("Service unavailable")
