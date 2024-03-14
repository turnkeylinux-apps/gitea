Gitea - Git with a cup of tea!
==============================

`Gitea`_ is a painless self-hosted Git service. It is somewhat similar
to GitHub, Bitbucket and Gitlab. As well as support for Git revision
control, it also provides issue tracking and development wiki pages.
Gitea is a fork of Gogs, a lightweight code hosting solution written
in Go and published under the MIT license.

This appliance includes all the standard features in `TurnKey Core`_,
and on top of that:

- Gitea configurations:
   
   - Gitea binary installed from latest upstream to /home/git/gitea.

     **Security note**: Updates to Gitea may require supervision so
     they **ARE NOT** configured to install automatically. See the
     "Updating to a new version" section in the `Gitea documentation`_
     for upgrade instructions.

   - Set Gitea admin password and email on firstboot (convenience,
     security).
   - Set Gitea domain to serve on first boot (convenience).
   - Pre-configured to use MySQL (MariaDB) (recommended for production).
   - Includes Nginx pre-configured to reverse proxy to Gitea daemon, with
     SSL support out of the box (performance, security).

- Includes postfix MTA (bound to localhost) for sending of email (e.g.
  password recovery). Also includes webmin postfix module for
  convenience.

Gitea Actions - CI/CD "Act" runners
-----------------------------------

As of TurnKey Gitea v18.0, `Gitea Actions`_ are supported and enabled
by default. Pre-built `Act runner`_ binaries can be downloaded from Gitea.
Builds on the Gitea host is supported but discouraged, unless using
Docker (which requires additional install).

For further info, please read the `Gitea Actions`_ docs. Please see the
`act_runner Readme`_ for links to examples.

Credentials *(passwords set at first boot)*
-------------------------------------------

-  Webmin, SSH, MySQL: username **root**
-  Gitea: username **gitea** (or email entered at firstboot)

.. _Gitea: https://gitea.io
.. _Gitea documentation: https://docs.gitea.io/en-us/install-from-binary/
.. _TurnKey Core: https://www.turnkeylinux.org/core
.. _Gitea Actions: https://docs.gitea.com/usage/actions/overview
.. _Act runner: https://dl.gitea.com/act_runner/
.. _act_runner Readme: https://gitea.com/gitea/act_runner/src/branch/main/examples#readme
