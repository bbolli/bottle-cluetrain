#!/usr/bin/env python
# encoding: utf-8
#
# Copyright 2015 Beat Bolli <me+python@drbeat.li>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from operator import itemgetter
from random import randint

from bottle import (
    redirect,
    request,
    route,
    run,
    template,
)

from theses import theses, languages


BASE_TEMPLATE = """\
<!DOCTYPE html>
<html>
<head>
<meta charset=utf-8>
<style>
body {
    background-color: white;
}
a {
    text-decoration: none;
    color: #336;
}
.n {
    position: absolute;
    top: 65px;
    left: 10%;
    color: #dcdcdc;
    font-size: 120pt;
    letter-spacing: -8px;
    z-index: -1;
}
.t {
    margin: 100px 16%;
    color: #666;
    font-size: 24pt;
}
.h {
    text-align: center;
    font-size: 175%;
}
.d {
    color: #d8d8d8;
}
</style>
"""

ABOUT_TEMPLATE = BASE_TEMPLATE + """<title>about</title>
</head>
<body>
<p class="h"><a href="/1" title="home">«</a></p>
<div class="n">about</div>
<div class="t">
    <p>original: <a href="http://cluetrain.com/">cluetrain.com</a></p>
    <p>source code: <a href="https://github.com/bbolli/bottle-cluetrain/">github.com/bbolli/bottle-cluetrain</a>
    <p>blog: <a href="https://drbeat.li/">beating the one-way web</a></p>
</div>
</body>
</html>
"""

THESIS_TEMPLATE = BASE_TEMPLATE + """
<title>clue #{{ n }}</title>
</head>
<body>
<p class="h">
    % if first:
    <a href="/{{ first }}" title="first">«</a>
    % else:
    <span class="d">«</span>
    % end
    % if prev:
    <a href="/{{ prev }}" title="previous">‹</a>
    % else:
    <span class="d">‹</span>
    % end
    &#x2003;<a href="/" title="random">*</a>&#x2003;<a href="/about" title="about">?</a>&#x2003;
    % if next:
    <a href="/{{ next }}" title="next">›</a>
    % else:
    <span class="d">›</span>
    % end
    % if last:
    <a href="/{{ last }}" title="last">»</a>
    % else:
    <span class="d">»</span>
    % end
</p>
<div class="n">{{ n }}</div>
<div class="t">{{ thesis }}</div>
</body>
</html>
"""


def http_accept_header(name):
    accepted = []
    header = request.get_header(name)
    if not header:
        return accepted
    for lq in [l.split(';') for l in header.split(',')]:
        attrs = dict(l.split('=', 1) for l in lq[1:])
        try:
            q = float(attrs.get('q', '1.0'))
        except ValueError:
            q = 0
        accepted.append((lq[0], q))
    accepted.sort(reverse=True, key=itemgetter(1))
    return [a[0] for a in accepted]


@route('/')
def random():
    n = randint(1, len(theses['en']))
    return redirect('/%d' % n)


@route('/<n:int>')
def thesis(n):
    for lang in http_accept_header('accept-language'):
        lang = lang[:2]
        if lang in languages:
            break
    else:
        lang = 'en'
    th = theses[lang]
    context = {'first': 0, 'prev': 0, 'next': 0, 'last': 0}
    if 1 <= n <= len(th):
        context.update({'n': n, 'thesis': th[n - 1]})
        if n > 1:
            context.update({'first': 1, 'prev': n - 1})
        if n < len(th):
            context.update({'next': n + 1, 'last': len(th)})
    else:
        context.update({'n': 404, 'thesis': 'not found', 'first': 1, 'last': len(th)})
    return template(THESIS_TEMPLATE, context)


@route('/about')
def about():
    return ABOUT_TEMPLATE


if __name__ == '__main__':
    run(host='0.0.0.0', port=8080, debug=True)
