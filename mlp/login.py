"""
Taken from EVE-MLP
https://github.com/shish/eve-mlp


Copyright (C) 2013 Shish <webmaster@shishnet.org>

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

import os
import sys
import requests
from urllib.parse import urljoin
import re
import logging


log = logging.getLogger(__name__)

cert_file = requests.certs.where()

if getattr(sys, 'frozen', False):
    # The application is frozen
    datadir = os.path.dirname(sys.executable)
    cert_file = os.path.join(datadir, 'cacert.pem')


LAUNCHER_INFO = 'http://client.eveonline.com/patches/win_launcherinfoTQ_inc.txt'


class LoginFailed(Exception):
    pass


def do_login(username, password):
    log.debug("<submit_login(%s)> Using cached SSO login URL", username)

    #login_action_url = "https://sisilogin.testeveonline.com/oauth/authorize/?" + \
    #                   "client_id=eveLauncherTQ&lang=en&response_type=token&" + \
    #                   "redirect_uri=https://sisilogin.testeveonline.com/launcher?client_id=eveLauncherTQ&scope=eveClientToken"
    #login_action_url = get_login_action_url(LAUNCHER_INFO)
    
    login_action_url = "https://login.eveonline.com/Account/LogOn?" + \
        "ReturnUrl=%2Foauth%2Fauthorize%2F%3Fclient_id%3DeveLauncherTQ%26lang%3Den%26response_type%3Dtoken%26" + \
        "redirect_uri%3Dhttps%3A%2F%2Flogin.eveonline.com%2Flauncher%3Fclient_id%3DeveLauncherTQ%26scope%3DeveClientToken"

    access_token = submit_login(login_action_url, username, password)
    launch_token = get_launch_token(access_token, username)

    return launch_token


def get_login_action_url(launcher_url):
    from bs4 import BeautifulSoup
    import yaml

    # get general info
    launcher_info = yaml.load(requests.get(launcher_url, verify=cert_file))
    landing_url = launcher_info["UISettings"]["LandingPage"]
    landing_url = urljoin(launcher_url, landing_url)

    # load main launcher page
    landing_page = BeautifulSoup(requests.get(landing_url, verify=cert_file))
    login_url = landing_page.find(id="sso-frame").get("src")
    login_url = urljoin(landing_url, login_url)

    # load login frame
    login_page = BeautifulSoup(requests.get(login_url, verify=cert_file))
    action_url = login_page.find(name="form").get("action")
    action_url = urljoin(login_url, action_url)

    return action_url


def submit_login(action_url, username, password):
    log.info("<submit_login(%s)> Submitting username / password", username)

    auth_result = requests.post(
        action_url,
        data={"UserName": username, "Password": password},
        verify=cert_file
    )

    if "<title>License Agreement Update</title>" in auth_result.text:
        raise LoginFailed("Need to accept EULA")

    matches = re.search("#access_token=([^&]+)", auth_result.url)
    if not matches:
        raise LoginFailed("Invalid username / password?")
    return matches.group(1)


def get_launch_token(access_token, username):
    log.info("<submit_login(%s)> Fetching launch token", username)

    response = requests.get(
        "https://login.eveonline.com/launcher/token?accesstoken=" + access_token,
        verify=cert_file
    )
    matches = re.search("#access_token=([^&]+)", response.url)
    if not matches:
        raise LoginFailed("No launch token?")
    return matches.group(1)