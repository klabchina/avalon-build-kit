# -*- coding: utf-8 -*-
import urllib.request as urllib2
import urllib.parse as urlparse

__author__ = 'Kevin Sun <sun-w@klab.com>'


def get(url, params):
    full_url = url
    if params is not None:
        data = urlparse.urlencode(params)
        full_url = full_url + "?" + data
    with urllib2.urlopen(full_url) as f:
        content = f.read()
    return content


def post(url, params):
    if params is not None:
        data = urlparse.urlencode(params)
    else:
        data = ""
    data = data.encode('utf-8')
    request = urllib2.Request(url)
    request.add_header("Content-Type", "application/x-www-form-urlencoded;charset=utf-8")
    with urllib2.urlopen(request, data) as f:
        content = f.read()
    return content
