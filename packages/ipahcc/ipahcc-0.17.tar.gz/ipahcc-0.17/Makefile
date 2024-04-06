VERSION = 0.17
RPM_WITH = client mockapi stageconsole
RPM_WITHOHT =

srcdir = .
abs_srcdir = $(shell pwd)
DEST = /

# /etc
SYSCONFDIR := $(shell rpm --eval '%{_sysconfdir}')
# /usr
PREFIX = $(shell rpm --eval '%{_prefix}')
# /usr/share
DATADIR := $(shell rpm --eval '%{_datadir}')
# /usr/bin/python3 or /usr/libexec/platform-python
PYTHON := $(shell rpm --eval '%{python3}')
# /usr/lib/pythonX.Y/site-packages
PYTHON_SITELIB := $(shell $(PYTHON) -c 'from sys import version_info as v; print("/usr/lib/python{}.{}/site-packages".format(v.major, v.minor))')
# /usr/lib/systemd/system
UNITDIR:= $(shell rpm --eval '%{_unitdir}')
# /usr/share/man
MANDIR:= $(shell rpm --eval '%{_mandir}')
# /var/lib
SHAREDSTATEDIR := $(shell rpm --eval '%{_sharedstatedir}')
# /var
LOCALSTATEDIR := $(shell rpm --eval '%{_localstatedir}')
# default SELinux type
SELINUXTYPE ?= targeted

INSTALL = install
INSTALL_DATAFILE = $(INSTALL) -d -m644
INSTALL_EXE = $(INSTALL) -D -m755
MKDIR_P = mkdir -p -m755
CP_PD = cp -p -d
CP_CONFIG = $(CP_PD) -n

# rpkg --outdir must be an absolute path
RPKGDIR = $(abs_srcdir)/build/rpkg
SPECDIR = build/spec
FEDORABUILDDIR = $(srcdir)/build/fedora

FEDORA_RPMDIRS = $(FEDORABUILDDIR)/BUILD $(FEDORABUILDDIR)/BUILDROOT $(FEDORABUILDDIR)/RPMS $(FEDORABUILDDIR)/SOURCES $(FEDORABUILDDIR)/SRPMS

CERT = tests/clients/3cc18ba1-1bdf-4873-b95d-7375789eefbd.pem
OPENAPI_YAML = api/public.openapi.yaml

VENV = .venv

.PHONY: all
all: test rehash lint version $(VENV) selinuxpolicy

.PHONY: clean-idm-ci
clean-idm-ci:
	rm -rf config credentials
	rm -f mrack.* runner.log
	rm -f host-info.txt

.PHONY: clean-selinux
clean-selinux:
	rm -f selinux/*.pp rm -f selinux/*.pp.bz2
	rm -rf selinux/tmp

.PHONY: clean
clean: clean-selinux
	find -name __pycache__ | xargs rm -rf
	rm -f .coverage*
	rm -rf htmlcov
	rm -rf .mypy_cache
	rm -rf $(RPKGDIR)
	rm -rf dist build
	rm -rf src/*.egg-info src/*.dist-info
	rm -rf $(VENV)

.PHONY: cleanall
cleanall: clean clean-idm-ci
	rm -rf .tox .ruff_cache .mypy_cache
	rm -rf ipahcc ipaserver

$(OPENAPI_YAML):
	git submodule update --init

src/ipahcc/server/schema/%.json: contrib/convert_schema.py $(OPENAPI_YAML)
	contrib/convert_schema.py

.PHONY: generate-api
generate-api:
	rm -f src/ipahcc/server/schema/*.json
	$(MAKE) src/ipahcc/server/schema/defs.json

.PHONY: update-api
update-api:
	git submodule update --remote
	$(MAKE) generate-api

.PHONY: tox
tox:
	tox -p auto

.PHONY: lint
lint: ruff
	tox -e format,yamllint

.PHONY: ruff
ruff:
	tox -e ruff

.PHONY: version
version:
	sed -i 's/^__version__\ =\ ".*\"/__version__ = "$(VERSION)"/g' \
		$(srcdir)/src/ipahcc/_version.py

# SELinux
SELINUX_POLICYDIR = $(DATADIR)/selinux/packages/$(SELINUXTYPE)
SELINUX_MAKEFILE = $(DATADIR)/selinux/devel/Makefile
SELINUX_MODULENAME = ipa-hcc

selinux/$(SELINUX_MODULENAME).pp.bz2:

selinux/%.pp.bz2: selinux/%.pp
	bzip2 -f -9 $^

selinux/%.pp: selinux/%.te selinux/%.fc selinux/%.if
	@# SELinux Makefile assumes that policy files are in CURDIR
	make -C selinux -f $(SELINUX_MAKEFILE) $(nodir $@)

.PHONY: selinuxpolicy
selinuxpolicy: selinux/$(SELINUX_MODULENAME).pp.bz2

.PHONY: rpkg
rpkg: $(OPENAPI_YAML)
	@if ! test -d .git; then echo "rpkg requires a git repository" >&2; exit 2; fi
	@rm -rf $(RPKGDIR)
	@mkdir -p $(RPKGDIR)
	rpkg local --outdir $(RPKGDIR) $(foreach cond,$(RPM_WITH),--with $(cond)) $(foreach cond,$(RPM_WITHOUT),--without $(cond))
	@# ignore python3-ipahcc+server meta pacakge
	rpmlint --ignore-unused-rpmlintrc --strict -r ipa-hcc.rpmlintrc $(RPKGDIR)/noarch/ipa-hcc*.rpm $(RPKGDIR)/noarch/python3-ipahcc-*.rpm
	@find $(RPKGDIR) -name '*.rpm' -printf "%f\n"

$(SPECDIR)/ipa-hcc.spec: $(srcdir)/ipa-hcc.spec.rpkg .git/index $(MAKEFILE_LIST)
	@rm -f $@
	@mkdir -p $(dir $@)
	rpkg spec --outdir $(abspath $(dir $@))

$(FEDORABUILDDIR)/ipa-hcc.spec: $(SPECDIR)/ipa-hcc.spec
	@mkdir -p $(dir $@)
	sed \
		-e s'|^VCS:.*||' \
		-e s'|^Version:.*|Version:        $(VERSION)|' \
		-e 's|^Source:.*|Source:         https://github.com/podengo-project/ipa-hcc/archive/refs/tags/ipa-hcc-%{version}-1.tar.gz|' \
		-e 's|^%setup.*|%autosetup -n ipa-hcc-ipa-hcc-%{version}-1|' \
		$< > $@

.PHONY: spec
spec: $(FEDORABUILDDIR)/ipa-hcc.spec

.PHONY: fedorabuild
fedorabuild: $(FEDORABUILDDIR)/ipa-hcc.spec
	rm -rf $(FEDORA_RPMDIRS)
	mkdir -p $(FEDORA_RPMDIRS)
	spectool --get-files --sourcedir --define "_topdir $(abspath $(FEDORABUILDDIR))" $<

	rpmbuild \
		--define "_topdir $(abspath $(FEDORABUILDDIR))" \
		$(foreach cond,$(RPM_WITH),--with $(cond)) \
		$(foreach cond,$(RPM_WITHOUT),--without $(cond)) \
		-ba $<
	rpmlint --ignore-unused-rpmlintrc --strict -r ipa-hcc.rpmlintrc $(FEDORA_RPMDIRS)
	find $(FEDORABUILDDIR) -name '*.rpm' -printf '%f\n'
	rpm -qR ./build/fedora/RPMS/noarch/*.rpm | sort -u
	rpmdeplint check-sat --repos-from-system $(FEDORABUILDDIR)/RPMS/noarch/ipa-hcc-server-*.rpm

.PHONY: test
test:
	openssl verify -purpose sslclient -CApath $(srcdir)/install/server/cacerts/ $(CERT)

.PHONY: run-idm-ci
run-idm-ci:
	@# idm-ci needs OpenStack cloud config
	@if [[ ! -f ~/.config/openstack/clouds.yaml ]]; then \
		echo '~/.config/openstack/clouds.yaml is missing'; \
		exit 2; \
	fi

	@if [[ $$(klist 2>&1 | grep -q REDHAT.COM) ]]; then \
		echo 'No Kerberos ticket found'; \
		exit 2; \
	fi

	@# tmpfs at /root/.ansible is needed to work around an SELinux violation
	@# when copying files from fusefs to mount point.
	MRACK_VM_OWNER=$(shell python3 -c 'from gssapi import Credentials; c = Credentials(usage="initiate"); print(str(c.name).split("@")[0])'); \
	podman run -ti --rm \
		-v ~/.config/openstack/clouds.yaml:/root/.config/openstack/clouds.yaml:z,ro \
		-e OS_CLOUD=$${OS_CLOUD:-openstack} \
		-e MRACK_VM_OWNER=$$MRACK_VM_OWNER \
		-v $(PWD):/ipa-hcc:z \
		-w /ipa-hcc \
		--tmpfs /root/.ansible:rw,mode=750 \
		quay.io/idmops/idm-ci:latest /bin/bash

.PHONY: rehash
rehash:
	openssl rehash install/server/cacerts

$(VENV):
	$(PYTHON) -m venv --system-site-packages $(VENV)
	$(VENV)/bin/python -m pip install --editable .

.PHONY: stubgen
stubgen:
	stubgen src/ipaserver/plugins/ -o stubs/ipaserver/plugins/
	stubgen src/ipaserver/install/plugins/ -o stubs/ipaserver/install/plugins/

.PHONY: install_python
install_python:
	$(PYTHON) setup.py install -O1 --root $(DEST) --prefix $(PREFIX)

.PHONY: install_client
install_client:
	$(MKDIR_P) $(DEST)$(UNITDIR)
	$(CP_PD) $(srcdir)/install/client/systemd/ipa-hcc-auto-enrollment.service $(DEST)$(UNITDIR)/
	$(MKDIR_P) $(DEST)$(SYSCONFDIR)/sysconfig
	$(CP_CONFIG) $(srcdir)/install/client/sysconfig/ipa-hcc-auto-enrollment $(DEST)$(SYSCONFDIR)/sysconfig/

.PHONY: install_client_prepare
install_client_prepare:
	$(MKDIR_P) $(DEST)$(UNITDIR)
	$(CP_PD) $(srcdir)/install/client/systemd/ipa-hcc-client-prepare.service $(DEST)$(UNITDIR)/
	$(MKDIR_P) $(DEST)$(SYSCONFDIR)/sysconfig
	$(CP_CONFIG) $(srcdir)/install/client/sysconfig/ipa-hcc-client-prepare $(DEST)$(SYSCONFDIR)/sysconfig/

.PHONY: install_server_plugin
install_server_plugin:
	$(MKDIR_P) $(DEST)$(DATADIR)/ipa-hcc
	$(CP_CONFIG) $(srcdir)/install/server/ipa/hcc.conf $(DEST)$(DATADIR)/ipa-hcc/hcc.conf.example
	$(MKDIR_P) $(DEST)$(DATADIR)/ipa-hcc/cacerts
	$(CP_PD) $(srcdir)/install/server/cacerts/* $(DEST)$(DATADIR)/ipa-hcc/cacerts/
	$(MKDIR_P) $(DEST)$(UNITDIR)
	$(CP_PD) $(srcdir)/install/server/systemd/ipa-hcc-update.* $(DEST)$(UNITDIR)/
	$(MKDIR_P) $(DEST)$(MANDIR)/man1
	$(CP_PD) $(srcdir)/install/server/man/*.1 $(DEST)$(MANDIR)/man1/
	$(MKDIR_P) $(DEST)$(DATADIR)/ipa/updates/
	$(CP_PD) $(srcdir)/install/server/updates/85-hcc.update $(DEST)$(DATADIR)/ipa/updates/
	$(MKDIR_P) $(DEST)$(DATADIR)/ipa/schema.d
	$(CP_PD) $(srcdir)/install/server/schema.d/85-hcc.ldif $(DEST)$(DATADIR)/ipa/schema.d/
	$(MKDIR_P) $(DEST)$(DATADIR)/ipa/ui/js/plugins/hccconfig
	$(CP_PD) $(srcdir)/install/server/ui/js/plugins/hccconfig/hccconfig.js $(DEST)$(DATADIR)/ipa/ui/js/plugins/hccconfig/
	$(MKDIR_P) $(DEST)$(DATADIR)/ipa/ui/js/plugins/hcchost/
	$(CP_PD) $(srcdir)/install/server/ui/js/plugins/hcchost/hcchost.js $(DEST)$(DATADIR)/ipa/ui/js/plugins/hcchost/
	$(MKDIR_P) $(DEST)$(DATADIR)/ipa/ui/js/plugins/hccidp/
	$(CP_PD) $(srcdir)/install/server/ui/js/plugins/hccidp/hccidp.js $(DEST)$(DATADIR)/ipa/ui/js/plugins/hccidp/

.PHONY: install_registration_service
install_registration_service:
	$(MKDIR_P) $(DEST)$(DATADIR)/ipa-hcc
	$(CP_PD) $(srcdir)/install/registration/wsgi/hcc_registration_service.py $(DEST)$(DATADIR)/ipa-hcc/
	$(MKDIR_P) $(DEST)$(LOCALSTATEDIR)/cache/ipa-hcc
	$(MKDIR_P) $(DEST)$(SHAREDSTATEDIR)/ipa/gssproxy
	$(MKDIR_P) $(DEST)$(DATADIR)/ipa/updates
	$(CP_PD) $(srcdir)/install/registration/updates/86-hcc-registration-service.update $(DEST)$(DATADIR)/ipa/updates/
	$(MKDIR_P) $(DEST)$(SYSCONFDIR)/httpd/conf.d
	$(CP_CONFIG) $(srcdir)/install/registration/httpd/ipa-hcc.conf $(DEST)$(SYSCONFDIR)/httpd/conf.d/
	$(MKDIR_P) $(DEST)$(SYSCONFDIR)/gssproxy
	$(CP_CONFIG) $(srcdir)/install/registration/gssproxy/85-ipa-hcc.conf $(DEST)$(SYSCONFDIR)/gssproxy/

.PHONY: install_mockapi
install_mockapi:
	$(MKDIR_P) $(DEST)$(DATADIR)/ipa-hcc
	$(CP_PD) $(srcdir)/install/mockapi/wsgi/hcc_mockapi.py $(DEST)$(DATADIR)/ipa-hcc/
	$(MKDIR_P) $(DEST)$(SYSCONFDIR)/httpd/conf.d
	$(CP_CONFIG) $(srcdir)/install/mockapi/httpd/ipa-hcc-mockapi.conf $(DEST)$(SYSCONFDIR)/httpd/conf.d/

	$(MKDIR_P) $(DEST)$(DATADIR)/ipa/updates
	$(CP_PD) $(srcdir)/install/mockapi/updates/87-hcc-mockapi.update $(DEST)$(DATADIR)/ipa/updates/

.PHONY: install_selinux
install_selinux: selinux/$(SELINUX_MODULENAME).pp.bz2
	$(MKDIR_P) $(DEST)$(SELINUX_POLICYDIR)
	$(CP_PD) $< $(DEST)$(SELINUX_POLICYDIR)

.PHONY: install_server
install_server: install_server_plugin install_registration_service install_selinux

.PHONY: install
install: install_python install_client install_server
