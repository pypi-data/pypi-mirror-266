#!/bin/sh
set -ex

if [ -x /usr/libexec/platform-python ]; then
    PYTHON=/usr/libexec/platform-python
elif [ -x /usr/bin/python3 ]; then
    PYTHON=/usr/bin/python3
fi

SITELIB=$($PYTHON -c 'from sys import version_info as v; print("/usr/lib/python{}.{}/site-packages".format(v.major, v.minor))')

## phase 1, install files

make install_server install_mockapi install_python PYTHON=$PYTHON PYTHON_SITELIB=$SITELIB

## phase 2, user, change permissions

# user and group
getent group ipaapi >/dev/null || groupadd -f -r ipaapi
getent passwd ipahcc >/dev/null || useradd -r -g ipaapi -s /sbin/nologin -d /usr/share/ipa-hcc -c "IPA Hybrid Cloud Console enrollment service" ipahcc

chown ipahcc:root -R /etc/ipa/hcc
chmod 750 /etc/ipa/hcc
chown ipahcc:ipaapi -R /var/cache/ipa-hcc
semanage fcontext -a -f a -s system_u -t httpd_cache_t -r 's0' '/var/cache/ipa-hcc(/.*)?' || :
restorecon -R /var/cache/ipa-hcc || :

$PYTHON -m compileall ${SITELIB}/ipaserver/install/plugins ${SITELIB}/ipaserver/plugins ${SITELIB}/ipahcc

# ensure correct SELinux labels
restorecon -R $SITELIB/ipahcc* $SITELIB/ipaserver/

# run updater
ipa-ldap-updater \
    -S /usr/share/ipa/schema.d/85-hcc.ldif \
    /usr/share/ipa/updates/85-hcc.update \
    /usr/share/ipa/updates/86-hcc-registration-service.update

systemctl daemon-reload
systemctl restart ipa-hcc-update.timer
killall -9 httpd
systemctl restart httpd.service

# force schema cache update
rm -rf ~/.cache/ipa

echo "NOTE: $0 is a hack for internal development."
echo "Some changes require a proper ipa-server-upgrade or ipactl restart."
