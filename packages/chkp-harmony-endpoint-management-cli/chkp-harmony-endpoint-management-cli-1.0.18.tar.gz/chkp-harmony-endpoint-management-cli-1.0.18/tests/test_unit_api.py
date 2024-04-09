import unittest
from unittest.mock import patch
from chkp_harmony_endpoint_management_cli.index import main_function
from tests.test_unit_global import EndpointTestCase


class TestUnitCloudUses(EndpointTestCase):
    @patch('sys.argv', [
        'index.py',
        '--operation', 'get_all_rules_metadata',
        '--header-params', '{ "x-mgmt-run-as-job": "off"}',
        '--verbose', '*'
    ])
    def test_job_off(self):
        main_function()

    @patch('sys.argv', [
        'index.py',
        '--operation', 'get_all_rules_metadata',
        '--header-params', '{ "x-mgmt-run-as-job": "on"}',
        '--verbose', '*'
    ])
    def test_job_with_payload_on(self):
        main_function()

    @patch('sys.argv', [
        'index.py',
        '--operation', 'install_all_policies',
        '--header-params', '{ "x-mgmt-run-as-job": "off"}',
        '--verbose', '*'
    ])
    def test_operation_wo_job(self):
        main_function()

    @patch('sys.argv', [
        'index.py',
        '--operation', 'install_all_policies',
        '--header-params', '{ "x-mgmt-run-as-job": "on"}',
        '--verbose', '*'
    ])
    def test_operation_with_job(self):
        main_function()


class TestUnitSAASUses(EndpointTestCase):
    @patch('sys.argv', [
        'index.py',
        '--operation', 'public_machines_single_status',
        '--target', 'saas',
        '--verbose', '*'
    ])
    def test_operation(self):
        main_function()


if __name__ == "__main__":
    unittest.main()
