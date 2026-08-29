#!/usr/bin/python3
"""Set Gitea admin password, email and domain to serve

Option:
    --pass=     unless provided, will ask interactively
    --pass-stdin
                read the password from standard input
    --email=    unless provided, will ask interactively
    --domain=   unless provided, will ask interactively
                DEFAULT=www.example.com
"""

import os
import sys
import getopt
import json
import secrets
import ssl
import urllib.request
from libinithooks import inithooks_cache
from mysqlconf import MySQL

from libinithooks.dialog_wrapper import Dialog
import subprocess

def usage(s=None):
    if s:
        print("Error:", s, file=sys.stderr)
    print("Syntax: %s [options]" % sys.argv[0], file=sys.stderr)
    print(__doc__, file=sys.stderr)
    sys.exit(1)

DEFAULT_DOMAIN="www.example.com"

def main():
    try:
        opts, args = getopt.gnu_getopt(
            sys.argv[1:], "h",
            ['help', 'pass=', 'pass-stdin', 'email=', 'domain='])
    except getopt.GetoptError as e:
        usage(e)

    email = ""
    domain = ""
    password = ""
    for opt, val in opts:
        if opt in ('-h', '--help'):
            usage()
        elif opt == '--pass':
            password = val
        elif opt == '--pass-stdin':
            password = sys.stdin.readline().rstrip('\r\n')
        elif opt == '--email':
            email = val
        elif opt == '--domain':
            domain = val

    if not password:
        d = Dialog('TurnKey Linux - First boot configuration')
        password = d.get_password(
            "Gitea Password",
            "Enter new password for the Gitea admin 'gitea' account.",
            pass_req = 8, min_complexity=4)

    if not email:
        if 'd' not in locals():
            d = Dialog('TurnKey Linux - First boot configuration')

        email = d.get_email(
            "Gitea Email",
            "Enter email address for the Gitea admin 'gitea' account.",
            "admin@example.com")

    inithooks_cache.write('APP_EMAIL', email)

    if not domain:
        if 'd' not in locals():
            d = Dialog('TurnKey Linux - First boot configuration')

        domain = d.get_input(
            "Gitea Domain",
            "Enter the domain to serve Gitea.",
            DEFAULT_DOMAIN)

    if domain == "DEFAULT":
        domain = DEFAULT_DOMAIN

    if any(char in domain for char in '\r\n|\\'):
        usage("domain contains unsupported characters")
    if any(char in email for char in '\r\n|\\'):
        usage("email contains unsupported characters")

    inithooks_cache.write('APP_DOMAIN', domain)

    config = "/etc/gitea/app.ini"
    gitea_env = {
        "USER": "git",
        "HOME": "/home/git",
        "GITEA_WORK_DIR": "/home/git",
    }
    token_name = f"turnkey-firstboot-{secrets.token_hex(8)}"
    token_result = subprocess.run([
            "./gitea", "admin", "user", "generate-access-token",
            "--username", "gitea", "--token-name", token_name,
            "--scopes", "write:admin", "--raw"
        ],
        user='git',
        group='git',
        cwd='/home/git',
        env=gitea_env,
        text=True,
        capture_output=True,
        check=True,
    )

    m = MySQL()
    try:
        payload = json.dumps({
            "source_id": 0,
            "login_name": "gitea",
            "email": email,
            "password": password,
            "must_change_password": False,
        }).encode()
        request = urllib.request.Request(
            "https://127.0.0.1/api/v1/admin/users/gitea",
            data=payload,
            method="PATCH",
            headers={
                "Authorization": f"token {token_result.stdout.strip()}",
                "Content-Type": "application/json",
            },
        )
        with urllib.request.urlopen(
                request, context=ssl._create_unverified_context()) as response:
            if response.status != 200:
                raise RuntimeError(f"Gitea user update returned {response.status}")
    finally:
        m.execute("DELETE FROM gitea.access_token WHERE name=%s;", (token_name,))

    subprocess.run(
        ['sed', '-i', "\\|DOMAIN|s|=.*|= %s|" % domain, config], check=True)
    subprocess.run(
        ['sed', '-i', "\\|ROOT_URL|s|=.*|= https+unix://%s:3000/|" % domain, config],
        check=True)
    subprocess.run(
        ['sed', '-i', "\\|FROM|s|=.*|= %s|" % email, config], check=True)
    subprocess.run(
        ['sed', '-i', "\\|NO_REPLY_ADDRESS|s|=.*|= noreply@%s|" % domain, config],
        check=True)

    subprocess.run(["systemctl", "restart", "gitea"], check=True)

if __name__ == "__main__":
    main()
