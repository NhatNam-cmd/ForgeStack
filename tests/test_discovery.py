
import unittest

from forgestack.discovery import parse_running_services
from unittest.mock import patch

from forgestack.node import Node
from forgestack.ssh import SSHResult
from forgestack.discovery import discover_node

class DiscoveryParserTests(unittest.TestCase):

    def test_two_services_and_descriptions(self):
        output = (
            "nginx.service loaded active running "
            "A high performance web server and a reverse proxy server\n"
            "l16-portal.service loaded active running "
            "L16 Internal Portal (training fixture)\n"
        )

        services = parse_running_services(output)

        self.assertEqual(len(services), 2)
        self.assertEqual(services[0].name, "nginx.service")
        self.assertEqual(
            services[0].description,
            "A high performance web server and a reverse proxy server"
        )
        self.assertEqual(
            services[1].description,
            "L16 Internal Portal (training fixture)"
        )
        self.assertEqual(services[0].active_state, "active")

    def test_blank_lines_are_skipped(self):
        output = (
            "\n  \n"
            "ssh.service loaded active running "
            "OpenBSD Secure Shell server\n\n"
        )

        services = parse_running_services(output)

        self.assertEqual(len(services), 1)
        self.assertEqual(services[0].name, "ssh.service")

    def test_empty_output_returns_empty_list(self):
        self.assertEqual(parse_running_services("\n  \n"), [])

    def test_malformed_row_raises_error(self):
        output = "nginx.service loaded active running\n"

        with self.assertRaisesRegex(ValueError, "Line 1"):
            parse_running_services(output)

    def test_unexpected_state_raises_error(self):
        output = "nginx.service loaded inactive dead Nginx web server\n"

        with self.assertRaisesRegex(ValueError, "unexpected state"):
            parse_running_services(output)

    def test_invalid_unit_raises_error(self):
        output = "nginx.socket loaded active running Nginx socket\n"

        with self.assertRaisesRegex(ValueError, "invalid service unit"):
            parse_running_services(output)


class DiscoveryCollectionTests(unittest.TestCase):

    def setUp(self):
        self.node = Node("node-a", "192.0.2.10", "testuser")

    @patch("forgestack.discovery.run_ssh")
    def test_successful_discovery(self, mock_ssh):
        mock_ssh.side_effect = [
            SSHResult(returncode=0, stdout="forgestack-node-a\n"),
            SSHResult(returncode=0, stdout="7.0.0-43-generic\n"),
            SSHResult(
                returncode=0,
                stdout=(
                    "nginx.service loaded active running "
                    "A high performance web server\n"
                ),
            ),
        ]

        result = discover_node(self.node)

        self.assertEqual(result.hostname, "forgestack-node-a")
        self.assertEqual(result.kernel, "7.0.0-43-generic")
        self.assertEqual(len(result.running_services), 1)
        self.assertEqual(result.running_services[0].name, "nginx.service")
        self.assertEqual(result.errors, {})
        self.assertEqual(mock_ssh.call_count, 3)

    @patch("forgestack.discovery.run_ssh")
    def test_offline_node(self, mock_ssh):
        mock_ssh.return_value = SSHResult(
            failure="TIMEOUT",
            reason="SSH process exceeded 10 seconds",
        )

        result = discover_node(self.node)

        self.assertIsNone(result.hostname)
        self.assertIsNone(result.kernel)
        self.assertIsNone(result.running_services)
        self.assertIn("TIMEOUT", result.errors["hostname"])
        self.assertIn("NOT_COLLECTED", result.errors["services"])
        self.assertEqual(mock_ssh.call_count, 1)

    @patch("forgestack.discovery.run_ssh")
    def test_systemctl_failure(self, mock_ssh):
        mock_ssh.side_effect = [
            SSHResult(returncode=0, stdout="node-a\n"),
            SSHResult(returncode=0, stdout="7.0.0\n"),
            SSHResult(returncode=1, stderr="Access denied"),
        ]

        result = discover_node(self.node)

        self.assertEqual(result.hostname, "node-a")
        self.assertEqual(result.kernel, "7.0.0")
        self.assertIsNone(result.running_services)
        self.assertIn("Access denied", result.errors["services"])

    @patch("forgestack.discovery.run_ssh")
    def test_malformed_services_output(self, mock_ssh):
        mock_ssh.side_effect = [
            SSHResult(returncode=0, stdout="node-a\n"),
            SSHResult(returncode=0, stdout="7.0.0\n"),
            SSHResult(
                returncode=0,
                stdout="nginx.service loaded active running\n",
            ),
        ]

        result = discover_node(self.node)

        self.assertIsNone(result.running_services)
        self.assertIn("invalid systemd service row", result.errors["services"])

    @patch("forgestack.discovery.run_ssh")
    def test_kernel_failure_does_not_block_services(self, mock_ssh):
        mock_ssh.side_effect = [
            SSHResult(returncode=0, stdout="node-a\n"),
            SSHResult(returncode=1, stderr="Kernel query failed"),
            SSHResult(returncode=0, stdout=""),
        ]

        result = discover_node(self.node)

        self.assertEqual(result.hostname, "node-a")
        self.assertIsNone(result.kernel)
        self.assertEqual(result.running_services, [])
        self.assertIn("Kernel query failed", result.errors["kernel"])
        self.assertEqual(mock_ssh.call_count, 3)

    @patch("forgestack.discovery.run_ssh")
    def test_hostname_failure_does_not_block_other_fields(self, mock_ssh):
        mock_ssh.side_effect = [
            SSHResult(returncode=1, stderr="Hostname command failed"),
            SSHResult(returncode=0, stdout="7.0.0\n"),
            SSHResult(
                returncode=0,
                stdout=(
                    "ssh.service loaded active running "
                    "OpenBSD SSH server\n"
                ),
            ),
        ]

        result = discover_node(self.node)

        self.assertIsNone(result.hostname)
        self.assertEqual(result.kernel, "7.0.0")
        self.assertEqual(len(result.running_services), 1)
        self.assertIn("Hostname command failed", result.errors["hostname"])
        self.assertEqual(mock_ssh.call_count, 3)

    @patch("forgestack.discovery.run_ssh")
    def test_empty_hostname_does_not_block_other_fields(self, mock_ssh):
        mock_ssh.side_effect = [
            SSHResult(returncode=0, stdout="\n"),
            SSHResult(returncode=0, stdout="7.0.0\n"),
            SSHResult(returncode=0, stdout=""),
        ]

        result = discover_node(self.node)

        self.assertIsNone(result.hostname)
        self.assertEqual(result.kernel, "7.0.0")
        self.assertEqual(result.running_services, [])
        self.assertIn("Empty command output", result.errors["hostname"])

    @patch("forgestack.discovery.run_ssh")
    def test_exit_255_does_not_prove_connection_failure(self, mock_ssh):
        mock_ssh.side_effect = [
            SSHResult(returncode=255, stderr="SSH or remote command error"),
            SSHResult(returncode=0, stdout="7.0.0\n"),
            SSHResult(returncode=0, stdout=""),
        ]

        result = discover_node(self.node)

        self.assertIsNone(result.hostname)
        self.assertEqual(result.kernel, "7.0.0")
        self.assertEqual(result.running_services, [])
        self.assertIn("Exit 255", result.errors["hostname"])
        self.assertEqual(mock_ssh.call_count, 3)

    @patch("forgestack.discovery.run_ssh")
    def test_ssh_connection_failure_skips_followups(self, mock_ssh):
        mock_ssh.return_value = SSHResult(
            returncode=255,
            stderr=(
                "ssh: connect to host 192.0.2.123 "
                "port 22: Connection timed out"
            ),
        )

        result = discover_node(self.node)

        self.assertIsNone(result.hostname)
        self.assertIsNone(result.kernel)
        self.assertIsNone(result.running_services)

        self.assertIn("Connection timed out", result.errors["hostname"])
        self.assertIn("NOT_COLLECTED", result.errors["kernel"])
        self.assertIn("NOT_COLLECTED", result.errors["services"])

        mock_ssh.assert_called_once()

if __name__ == "__main__":
    unittest.main()
