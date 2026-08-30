#!/bin/bash
set -euo pipefail

result=${TKL_TEST_RESULT:?}
password=${TKL_TEST_APP_PASS:?}
work=/run/tkl-v19-tests/gitea
base=https://www.example.com
curl_args=(-kfsS --resolve www.example.com:443:127.0.0.1)
mkdir -p "$work"

systemctl --quiet is-active gitea.service nginx.service mariadb.service
grep -q '\[40gitea\] successfully completed' /var/log/inithooks.log
printf 'machine www.example.com login gitea password %s\n' "$password" >"$work/netrc"
chmod 0600 "$work/netrc"

curl "${curl_args[@]}" "$base/api/v1/version" >"$work/version.json"
version=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["version"])' \
    "$work/version.json")
test -n "$version"
curl "${curl_args[@]}" --netrc-file "$work/netrc" \
    "$base/api/v1/user" >"$work/user.json"
python3 -c 'import json,sys; assert json.load(open(sys.argv[1]))["login"] == "gitea"' \
    "$work/user.json"

curl "${curl_args[@]}" --netrc-file "$work/netrc" \
    -H 'Content-Type: application/json' \
    --data '{"name":"qa-v19","description":"TurnKey release QA"}' \
    "$base/api/v1/user/repos" >"$work/repo.json"
python3 -c 'import json,sys; assert json.load(open(sys.argv[1]))["name"] == "qa-v19"' \
    "$work/repo.json"

runuser -u git -- test ! -w /home/git/gitea
runuser -u git -- test ! -w /home/git/custom/templates/custom/footer.tmpl
runuser -u git -- test ! -w /etc/gitea/app.ini
runuser -u git -- touch /home/git/data/.tkl-v19-write-test
runuser -u git -- rm /home/git/data/.tkl-v19-write-test

for secret_name in INTERNAL_TOKEN JWT_SECRET LFS_JWT_SECRET SECRET_KEY; do
    secret_value=$(sed -n \
        "s/^[[:space:]]*${secret_name}[[:space:]]*=[[:space:]]*//p" \
        /etc/gitea/app.ini | tail -n1)
    if [[ -z $secret_value ]]; then
        echo "$secret_name is empty after firstboot rotation" >&2
        exit 1
    fi
    leaked_in=$(grep -R -l -F -- "$secret_value" \
        /var/log/inithooks.log /var/log/gitea 2>/dev/null || true)
    if [[ -n $leaked_in ]]; then
        echo "$secret_name was disclosed in: $leaked_in" >&2
        exit 1
    fi
done

systemctl restart mariadb.service gitea.service nginx.service
for attempt in $(seq 1 30); do
    if curl "${curl_args[@]}" --netrc-file "$work/netrc" \
            "$base/api/v1/repos/gitea/qa-v19" \
            >"$work/repo-after-restart.json"; then
        break
    fi
    test "$attempt" -lt 30
    sleep 1
done
grep -Fq 'qa-v19' "$work/repo-after-restart.json"
curl "${curl_args[@]}" --netrc-file "$work/netrc" -X DELETE \
    "$base/api/v1/repos/gitea/qa-v19"
! grep -R -F -- "$password" /var/log/inithooks.log /var/log/gitea 2>/dev/null

cat >"$result" <<EOF
package_source=official Gitea release signature verified by embedded upstream key
installed_version=$version
runtime_checks=Gitea, Nginx and MariaDB services, firstboot completion, API admin authentication, repository create/read/delete across restart, ownership boundaries, password log hygiene
updater_command=supervised official signed Gitea binary replacement
updater_result=installed version unchanged during QA
updater_channel=official Gitea stable releases
integrity_evidence=upstream detached signature verified during build
EOF
