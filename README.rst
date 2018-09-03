Gitea - Git with a cup of tea!
==============================

`Gitea`_ is a painless self-hosted Git service. It is similar to GitHub,
Bitbucket and Gitlab. Gitea is a fork of Gogs, a lightweight code
hosting solution written in Go and published under the MIT license.

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
   - Pre-configured to use MySQL (recommended for production).
   - Includes Nginx pre-configured to proxy to Gitea daemon, with SSL
     support out of the box (performance, security).

- Includes postfix MTA (bound to localhost) for sending of email (e.g.
  password recovery). Also includes webmin postfix module for
  convenience.

Credentials *(passwords set at first boot)*
-------------------------------------------

-  Webmin, SSH, MySQL, Adminer: username **root**
-  Gitea: username is **gitea**, password is set at first boot

.. _Gitea: https://gitea.io
.. _Gitea documentation: https://docs.gitea.io/en-us/install-from-binary/
.. _TurnKey Core: https://www.turnkeylinux.org/core
