#!/usr/bin/python3
"""Set Gitea admin password, email and domain to serve

Option:
    --pass=     unless provided, will ask interactively
    --email=    unless provided, will ask interactively
    --domain=   unless provided, will ask interactively
                DEFAULT=www.example.com
"""

import os
import sys
import getopt
import inithooks_cache
from mysqlconf import MySQL

from dialog_wrapper import Dialog
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
        opts, args = getopt.gnu_getopt(sys.argv[1:], "h",
                                       ['help', 'pass=', 'email=', 'domain='])
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
        elif opt == '--email':
            email = val
        elif opt == '--domain':
            domain = val

    if not password:
        d = Dialog('TurnKey Linux - First boot configuration')
        password = d.get_password(
            "Gitea Password",
            "Enter new password for the Gitea 'admin' account.",
            pass_req = 8, min_complexity=4)

    if not email:
        if 'd' not in locals():
            d = Dialog('TurnKey Linux - First boot configuration')

        email = d.get_email(
            "Gitea Email",
            "Enter email address for the Gitea 'admin' account.",
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

    inithooks_cache.write('APP_DOMAIN', domain)

    config = "/etc/gitea/app.ini"
    subprocess.run(["su", "git", "-c", "cd /home/git && ./gitea admin change-password -u gitea -p %s" % password])
    subprocess.run(['sed', '-i', "\|DOMAIN|s|=.*|= %s|" % domain, config])
    subprocess.run(['sed', '-i', "\|ROOT_URL|s|=.*|= https://%s/|" % domain, config])
    subprocess.run(['sed', '-i', "\|FROM|s|=.*|= %s|" % email, config])

    m = MySQL()
    m.execute("UPDATE gitea.user SET email='%s' WHERE id=1;" % (email,))

    subprocess.run(["systemctl", "restart", "gitea"])

if __name__ == "__main__":
    main()

