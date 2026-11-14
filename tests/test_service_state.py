
import io
import subprocess
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from forgestack.cli import main
from forgestack.node import Node
from forgestack.service_state import (
    ServiceState,
    check_service,
    normalize_service_state,
    parse_properties,
)
from forgestack.ssh import SSHResult, run_ssh


class ServiceStateTests(unittest.TestCase):

    def test_parse_properties(self):
        output = (
            "LoadState=loaded\n"
            "ActiveState=active\n"
            "SubState=running\n"
        )

        properties = parse_properties(output)

        self.assertEqual(properties["LoadState"], "loaded")
        self.assertEqual(properties["ActiveState"], "active")
        self.assertEqual(properties["SubState"], "running")

    def test_normalize_service_states(self):
        cases = [
            ("loaded", "active", "running", "RUNNING"),
            ("loaded", "active", "exited", "ACTIVE"),
            ("loaded", "inactive", "dead", "STOPPED"),
            ("loaded", "failed", "failed", "FAILED"),
            ("not-found", "inactive", "dead", "NOT_FOUND"),
            ("loaded", "activating", "start", "UNKNOWN"),
        ]

        for load, active, sub, expected in cases:
            with self.subTest(expected=expected):
                result = SSHResult(
                    returncode=0,
                    stdout=(
                        f"LoadState={load}\n"
                        f"ActiveState={active}\n"
                        f"SubState={sub}\n"
                    )
                )

                state = normalize_service_state(
                    "nginx.service", result
                )

                self.assertEqual(state.status, expected)
                self.assertEqual(state.load_state, load)
                self.assertEqual(state.active_state, active)
                self.assertEqual(state.sub_state, sub)

    def test_not_found_with_nonzero_exit(self):
        result = SSHResult(
            returncode=1,
            stdout=(
                "LoadState=not-found\n"
                "ActiveState=inactive\n"
                "SubState=dead\n"
            )
        )

        state = normalize_service_state(
            "nginx.service", result
        )

        self.assertEqual(state.status, "NOT_FOUND")

    def test_incomplete_properties(self):
        result = SSHResult(
            returncode=0,
            stdout="LoadState=loaded\n"
        )

        state = normalize_service_state(
            "nginx.service", result
        )

        self.assertEqual(state.status, "UNKNOWN")

    def test_ssh_failure_is_not_stopped(self):
        result = SSHResult(
            returncode=255,
            stderr="Permission denied (publickey)."
        )

        state = normalize_service_state(
            "nginx.service", result
        )

        self.assertEqual(state.status, "ERROR")
        self.assertIsNone(state.active_state)

    def test_timeout(self):
        result = SSHResult(
            failure="TIMEOUT",
            reason="SSH process exceeded 10 seconds"
        )

        state = normalize_service_state(
            "nginx.service", result
        )

        self.assertEqual(state.status, "TIMEOUT")

    @patch("forgestack.service_state.run_ssh")
    def test_invalid_service_name(self, mock_ssh):
        node = Node("node-a", "192.0.2.1", "nam")

        with self.assertRaises(ValueError):
            check_service(node, "nginx")

        mock_ssh.assert_not_called()


class SSHExecutionTests(unittest.TestCase):

    @patch("forgestack.ssh.subprocess.run")
    def test_subprocess_timeout(self, mock_run):
        mock_run.side_effect = subprocess.TimeoutExpired(
            cmd="ssh",
            timeout=10
        )

        node = Node("node-a", "192.0.2.1", "nam")
        result = run_ssh(node, "hostname")

        self.assertEqual(result.failure, "TIMEOUT")
        self.assertIsNone(result.returncode)

    @patch("forgestack.ssh.subprocess.run")
    def test_missing_ssh_client(self, mock_run):
        mock_run.side_effect = FileNotFoundError()

        node = Node("node-a", "192.0.2.1", "nam")
        result = run_ssh(node, "hostname")

        self.assertEqual(result.failure, "ERROR")
        self.assertIsNone(result.returncode)


class ServiceCLITests(unittest.TestCase):

    def setUp(self):
        self.nodes = [
            Node("node-a", "192.0.2.1", "nam"),
            Node("node-b", "192.0.2.2", "namb")
        ]

    def run_services(self, states, inventory_errors=None):
        argv = [
            "forgestack",
            "--inventory",
            "config/nodes.yaml",
            "services",
            "nginx.service"
        ]

        output = io.StringIO()

        with (
            patch("sys.argv", argv),
            patch(
                "forgestack.cli.load_nodes",
                return_value=(
                        self.nodes,
                        inventory_errors or []
                )
            ),
            patch(
                "forgestack.cli.check_service",
                side_effect=states
            ) as mock_check,
            redirect_stdout(output)
        ):
            exit_code = main()

        return exit_code, output.getvalue(), mock_check

    def test_successful_inspection(self):
        states = [
            ServiceState(
                "nginx.service",
                "RUNNING",
                "Service is active and running"
            ),
            ServiceState(
                "nginx.service",
                "NOT_FOUND",
                "Service unit does not exist"
            )
        ]

        code, output, mock_check = self.run_services(states)

        self.assertEqual(code, 0)
        self.assertIn("RUNNING", output)
        self.assertIn("NOT_FOUND", output)
        self.assertEqual(mock_check.call_count, 2)

    def test_failure_isolation(self):
        states = [
            ServiceState(
                "nginx.service",
                "ERROR",
                "SSH execution failed"
            ),
            ServiceState(
                "nginx.service",
                "RUNNING",
                "Service is active and running"
            )
        ]

        code, output, mock_check = self.run_services(states)

        self.assertEqual(code, 1)
        self.assertIn("node-a", output)
        self.assertIn("node-b", output)
        self.assertIn("ERROR", output)
        self.assertIn("RUNNING", output)
        self.assertEqual(mock_check.call_count, 2)

    def test_inventory_error_exit_priority(self):
        states = [
            ServiceState(
                "nginx.service",
                "ERROR",
                "SSH execution failed"
            ),
            ServiceState(
                "nginx.service",
                "RUNNING",
                "Service is active and running"
            )
        ]

        code, output, _ = self.run_services(
            states,
            inventory_errors=["Invalid inventory record"]
        )

        self.assertEqual(code, 2)
        self.assertIn("WARNING:", output)
        self.assertIn("RUNNING", output)


if __name__ == "__main__":
    unittest.main()
