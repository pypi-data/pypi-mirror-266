import json
import os
import unittest
from email.message import Message
from unittest import mock
from urllib.error import HTTPError
from urllib.request import OpenerDirector

from dns.rdtypes.IN.SRV import SRV
from ipaplatform.paths import paths
from ipapython import ipautil

import conftest
from ipahcc import hccplatform
from ipahcc.client import auto_enrollment
from ipahcc.server import schema

HOST_CONF_REQUEST = {
    "domain_type": hccplatform.HCC_DOMAIN_TYPE,
}

HOST_CONF_RESPONSE = {
    "domain_name": conftest.DOMAIN,
    "domain_type": hccplatform.HCC_DOMAIN_TYPE,
    "domain_id": conftest.DOMAIN_ID,
    "auto_enrollment_enabled": True,
    "token": conftest.DUMMY_TOKEN,
    hccplatform.HCC_DOMAIN_TYPE: {
        "realm_name": conftest.REALM,
        "cabundle": conftest.IPA_CA_DATA,
        "enrollment_servers": [
            {"fqdn": conftest.SERVER_FQDN},
        ],
        "ipa_client_install_args": [
            "--enable-dns-updates",
        ],
        "automount_location": "default",
    },
}

REGISTER_REQUEST = {
    "domain_type": hccplatform.HCC_DOMAIN_TYPE,
    "domain_name": conftest.DOMAIN,
    "domain_id": conftest.DOMAIN_ID,
    "token": conftest.DUMMY_TOKEN,
}

REGISTER_RESPONSE = {"status": "ok", "kdc_cabundle": conftest.KDC_CA_DATA}

IDMSVC_API_URL = f"https://{conftest.SERVER_FQDN}/api/idmsvc/v1"


class TestAutoEnrollmentNoMock(unittest.TestCase):
    def test_schema(self):
        schema.validate_schema(HOST_CONF_REQUEST, "HostConfRequest")
        schema.validate_schema(HOST_CONF_RESPONSE, "HostConfResponse")
        schema.validate_schema(REGISTER_REQUEST, "HostRegisterRequest")
        schema.validate_schema(REGISTER_RESPONSE, "HostRegisterResponse")


class TestAutoEnrollment(conftest.IPABaseTests):
    def setUp(self):
        super().setUp()
        self.mock_hccplatform()

        p = mock.patch.object(ipautil, "run")
        self.m_run = p.start()
        self.addCleanup(p.stop)

        p = mock.patch.object(OpenerDirector, "open")
        self.m_urlopen = p.start()
        # hcc_host_conf, hcc_register
        self.m_urlopen.side_effect = [
            conftest.jsonio(HOST_CONF_RESPONSE),
            conftest.jsonio(REGISTER_RESPONSE),
        ]
        self.addCleanup(p.stop)

        p = mock.patch.object(auto_enrollment, "query_srv")
        self.m_query_srv = p.start()
        self.m_query_srv.return_value = [
            SRV(1, 33, 0, 100, 389, conftest.SERVER_FQDN)
        ]
        self.addCleanup(p.stop)

        p = mock.patch("time.sleep")
        p.start()
        self.addCleanup(p.stop)

    def parse_args(self, *args):
        # hostname is required because some test machines don't have a FQDN
        # as hostname. idmsvc-api-url default is currently set to None.
        default_args = (
            "--hostname",
            conftest.CLIENT_FQDN,
            "--idmsvc-api-url",
            IDMSVC_API_URL,
        )
        return auto_enrollment.parser.parse_args(args=default_args + args)

    def assert_args_error(self, args, expected=None):
        with self.assertRaises(SystemExit):
            with conftest.capture_output() as out:
                auto_enrollment.main(args)
        if expected is not None:
            self.assertIn(expected, out.read())
        return out

    def test_args(self):
        args = self.parse_args(
            # fmt: off
            "--timeout", "20",
            "--domain-name", conftest.DOMAIN,
            "--domain-id", conftest.DOMAIN_ID,
            "--location", "sigma",
            "--upto", "host-conf",
            "--override-ipa-server", conftest.SERVER_FQDN,
            # fmt: on
        )
        self.assertEqual(args.timeout, 20)
        self.assertEqual(args.idmsvc_api_url, IDMSVC_API_URL)
        self.assertEqual(args.dev_username, None)
        self.assertEqual(args.dev_cert_cn, None)

        if hccplatform.DEVELOPMENT_MODE:
            args = self.parse_args(
                # fmt: off
                "--dev-username", "jdoe",
                "--dev-password", "example",
                "--dev-org-id", conftest.ORG_ID,
                "--dev-cert-cn", conftest.CLIENT_RHSM_ID,
                # fmt: on
            )
            self.assertEqual(args.dev_username, "jdoe")
            self.assertEqual(args.dev_org_id, conftest.ORG_ID)
            self.assertEqual(args.dev_cert_cn, conftest.CLIENT_RHSM_ID)

        self.assert_args_error(("--hostname", "invalid_hostname"))
        self.assert_args_error(
            ("--hostname", "localhost"), "FQDN is not configured"
        )
        self.assert_args_error(
            ("--hostname", "localhost.localdomain"), "FQDN is not configured"
        )
        self.assert_args_error(("--domain-name", "invalid_domain"))
        self.assert_args_error(("--domain-id", "invalid_domain"))
        self.assert_args_error(("--location", "invalid.location"))

    def test_system_state_error(self):
        args = (
            "--idmsvc-api-url",
            IDMSVC_API_URL,
            "--hostname",
            conftest.CLIENT_FQDN,
        )

        # any file
        with mock.patch("ipaplatform.paths.paths.IPA_DEFAULT_CONF", __file__):
            self.assert_args_error(
                args, expected="Host is already an IPA client."
            )

        # module vars are already mocked
        hccplatform.INSIGHTS_MACHINE_ID = conftest.NO_FILE
        self.assert_args_error(
            args, expected="Host is not registered with Insights."
        )
        hccplatform.RHSM_CERT = conftest.NO_FILE
        self.assert_args_error(
            args,
            expected="Host is not registered with subscription-manager.",
        )

    def test_sort_servers(self):
        p = mock.patch("random.random", return_value=0.5)
        p.start()
        self.addCleanup(p.stop)
        # pylint: disable=protected-access
        sort_servers = auto_enrollment.AutoEnrollment._sort_servers
        # pylint: enable=protected-access
        s1 = "srv1.ipa.example"
        s2 = "srv2.ipa.example"
        s3 = "srv3.ipa.example"
        s4 = "srv4.ipa.example"
        a = "other.ipa.example"
        server_list = [
            {"fqdn": s1},
            {"fqdn": s2, "location": "sigma"},
            {"fqdn": s3, "location": "tau"},
            {"fqdn": s4, "location": "sigma"},
        ]
        r = sort_servers(server_list, [])
        self.assertEqual(r, [s1, s2, s3, s4])
        r = sort_servers(server_list, [s1, a, s4, s3])
        self.assertEqual(r, [s1, s4, s3, s2])
        r = sort_servers(server_list, [], "sigma")
        self.assertEqual(r, [s2, s4, s1, s3])
        r = sort_servers(server_list, [], "kappa")
        self.assertEqual(r, [s1, s2, s3, s4])
        r = sort_servers(server_list, [s1, a, s4, s3], "sigma")
        self.assertEqual(r, [s4, s2, s1, s3])
        r = sort_servers(server_list, [s1, a, s4, s3], "kappa")
        self.assertEqual(r, [s1, s4, s3, s2])

    def test_basic(self):
        args = self.parse_args()
        ae = auto_enrollment.AutoEnrollment(args)
        self.assertEqual(ae.tmpdir, None)
        with ae:
            tmpdir = ae.tmpdir
            assert tmpdir
            self.assertTrue(os.path.isdir(tmpdir))

        self.assertEqual(ae.tmpdir, None)
        self.assertFalse(os.path.isdir(tmpdir))

    def test_inventory_from_host_details(self):
        args = self.parse_args()
        ae = auto_enrollment.AutoEnrollment(args)
        with ae:
            self.assertEqual(ae.inventory_id, None)
            ae.get_host_details()
            self.assertEqual(ae.inventory_id, conftest.CLIENT_INVENTORY_ID)

    def test_inventory_from_api(self):
        args = self.parse_args()
        hccplatform.INSIGHTS_HOST_DETAILS = conftest.NO_FILE
        # first call to urlopen gets host details from API
        with open(conftest.HOST_DETAILS, encoding="utf-8") as f:
            host_details = json.load(f)
        self.m_urlopen.side_effect = [
            conftest.jsonio(host_details),
            Exception,
        ]
        ae = auto_enrollment.AutoEnrollment(args)
        with ae:
            self.assertEqual(ae.inventory_id, None)
            ae.get_host_details()
            self.assertEqual(ae.inventory_id, conftest.CLIENT_INVENTORY_ID)

        self.assertEqual(self.m_urlopen.call_count, 1)
        req = self.m_urlopen.call_args[0][0]
        self.assertEqual(
            req.get_full_url(),
            "https://cert.console.redhat.com/api"
            "/inventory/v1/hosts?insights_id=96aac268-e7b8-429a-8c86-f498b96fe1f9",
        )
        self.assertEqual(req.get_method(), "GET")

    def test_hcc_host_conf(self):
        args = self.parse_args()
        ae = auto_enrollment.AutoEnrollment(args)
        with ae:
            ae.get_host_details()

            urlopen = self.m_urlopen
            ae.hcc_host_conf()
            self.assertEqual(urlopen.call_count, 1)
            req = urlopen.call_args[0][0]
            self.assertEqual(
                req.get_full_url(),
                "https://{}/api/idmsvc/v1/host-conf/{}/{}".format(
                    conftest.SERVER_FQDN,
                    conftest.CLIENT_INVENTORY_ID,
                    conftest.CLIENT_FQDN,
                ),
            )
            self.assertEqual(
                req.data, json.dumps(HOST_CONF_REQUEST).encode("utf-8")
            )
            self.assertEqual(
                req.get_header("Content-type"), "application/json"
            )
            self.assertEqual(urlopen.call_args[1]["timeout"], ae.args.timeout)
            self.assertEqual(ae.domain, conftest.DOMAIN)
            self.assertEqual(ae.domain_id, conftest.DOMAIN_ID)
            self.assertEqual(ae.realm, conftest.REALM)
            self.assertEqual(ae.servers, None)
            self.assertEqual(ae.server, None)
            ae.update_serverlist()
            self.assertEqual(ae.servers, [conftest.SERVER_FQDN])
            self.assertEqual(ae.server, conftest.SERVER_FQDN)

    def test_hcc_register(self):
        args = self.parse_args()
        ae = auto_enrollment.AutoEnrollment(args)
        with ae:
            ae.get_host_details()
            urlopen = self.m_urlopen
            ae.hcc_host_conf()
            self.assertEqual(urlopen.call_count, 1)
            ae.update_serverlist()

            ae.hcc_register()
            self.assertEqual(urlopen.call_count, 2)
            req = urlopen.call_args[0][0]
            self.assertEqual(
                req.get_full_url(),
                "https://{}/hcc/{}/{}".format(
                    conftest.SERVER_FQDN,
                    conftest.CLIENT_INVENTORY_ID,
                    conftest.CLIENT_FQDN,
                ),
            )
            self.assertTrue(os.path.isfile(ae.ipa_cacert))
            self.assertTrue(os.path.isfile(ae.kdc_cacert))

            with open(ae.ipa_cacert, encoding="utf-8") as f:
                data = f.read()
            self.assertEqual(data, conftest.IPA_CA_DATA)
            with open(ae.kdc_cacert, encoding="utf-8") as f:
                data = f.read()
            self.assertEqual(data, conftest.KDC_CA_DATA)

    def test_enroll_host(self):
        args = self.parse_args()

        ae = auto_enrollment.AutoEnrollment(args)
        with ae:
            tmpdir = ae.tmpdir
            ae.enroll_host()
            self.assertTrue(os.path.isfile(ae.ipa_cacert))
            self.assertTrue(os.path.isfile(ae.kdc_cacert))

        self.assertEqual(self.m_urlopen.call_count, 2)
        # ipa-client-install, ipa-client-automount, selinuxenabled,
        # getsebool, setsebool
        self.assertEqual(self.m_run.call_count, 5)

        args, kwargs = self.m_run.call_args_list[0]
        self.assertEqual(
            args[0],
            [
                paths.IPA_CLIENT_INSTALL,
                "--ca-cert-file",
                f"{tmpdir}/ipa_ca.crt",
                "--hostname",
                conftest.CLIENT_FQDN,
                "--domain",
                conftest.DOMAIN,
                "--realm",
                conftest.REALM,
                "--pkinit-identity",
                f"FILE:{hccplatform.RHSM_CERT},{hccplatform.RHSM_KEY}",
                "--pkinit-anchor",
                f"FILE:{tmpdir}/kdc_ca.crt",
                "--pkinit-anchor",
                f"FILE:{tmpdir}/ipa_ca.crt",
                "--unattended",
                "--enable-dns-updates",
            ],
        )
        self.assertEqual(
            kwargs, {"stdin": None, "env": None, "raiseonerr": True}
        )

        self.assertEqual(
            self.m_run.call_args_list[1][0][0],
            [
                paths.IPA_CLIENT_AUTOMOUNT,
                "--unattended",
                "--location",
                "default",
                "--server",
                conftest.SERVER_FQDN,
            ],
        )
        self.assertEqual(
            self.m_run.call_args_list[4][0][0],
            [
                "/usr/sbin/setsebool",
                "-P",
                "use_nfs_home_dirs=on",
            ],
        )

    def test_json_error(self):
        msg = Message()
        msg.add_header("content-type", "application/json")
        self.m_urlopen.side_effect = HTTPError(
            url=IDMSVC_API_URL,
            code=403,
            msg="Forbidden",
            hdrs=msg,
            fp=conftest.jsonio(
                {
                    "errors": [
                        {
                            "id": "id",
                            "status": "403",
                            "title": "Forbidden",
                            "detail": "Internal Error",
                            "code": "internal code",
                        }
                    ]
                }
            ),
        )
        args = self.parse_args()
        ae = auto_enrollment.AutoEnrollment(args)
        with ae:
            with self.assertRaises(SystemExit):
                ae.hcc_host_conf()

        # check for expected HTTP error and JSON error outputs
        logs = self.get_logs()
        self.assertIn(
            "HTTPError 403: Forbidden "
            f"(POST {IDMSVC_API_URL}/host-conf/None/{args.hostname})",
            logs,
        )
        self.assertIn(
            "Error status=403, title='Forbidden', detail='Internal Error', "
            "code='internal code'",
            logs,
        )
