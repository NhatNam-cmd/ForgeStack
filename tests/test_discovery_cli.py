
import io
import unittest

from contextlib import redirect_stdout
from unittest.mock import patch

from forgestack.cli import main
from forgestack.discovery import NodeDiscovery, RunningService
from forgestack.node import Node


class DiscoveryCLITests(unittest.TestCase):

    def setUp(self):
        self.nodes = [
            Node("node-a", "192.0.2.10", "testuser"),
            Node("node-b", "192.0.2.11", "testuser"),
        ]

    def run_discover(self, discoveries, inventory_errors=None):
        output = io.StringIO()

        with (
            patch(
                "sys.argv",
                [
                    "forgestack",
                    "--inventory",
                    "config/nodes.yaml",
                    "discover",
                ],
            ),
            patch(
                "forgestack.cli.load_nodes",
                return_value=(self.nodes, inventory_errors or []),
            ),
            patch(
                "forgestack.cli.discover_node",
                side_effect=discoveries,
            ) as mock_discover,
            redirect_stdout(output),
        ):
            exit_code = main()

        return exit_code, output.getvalue(), mock_discover

    def test_discover_successful_for_both_nodes(self):
        discoveries = [
            NodeDiscovery(
                node=self.nodes[0],
                hostname="forgestack-node-a",
                kernel="7.0.0-43-generic",
                running_services=[
                    RunningService(
                        "nginx.service",
                        "loaded",
                        "active",
                        "running",
                        "A high performance web server",
                    )
                ],
            ),
            NodeDiscovery(
                node=self.nodes[1],
                hostname="forgestack-node-b",
                kernel="7.0.0-43-generic",
                running_services=[],
            ),
        ]

        code, output, mock_discover = self.run_discover(discoveries)

        self.assertEqual(code, 0)
        self.assertIn("COMPLETE", output)
        self.assertIn("forgestack-node-a", output)
        self.assertIn("forgestack-node-b", output)
        self.assertIn("nginx.service", output)
        self.assertIn("0 observed", output)
        self.assertEqual(mock_discover.call_count, 2)

    def test_offline_node_does_not_block_other_node(self):
        discoveries = [
            NodeDiscovery(
                node=self.nodes[0],
                errors={
                    "hostname": "TIMEOUT: SSH process exceeded 10 seconds",
                    "kernel": "NOT_COLLECTED: SSH unavailable",
                    "services": "NOT_COLLECTED: SSH unavailable",
                },
            ),
            NodeDiscovery(
                node=self.nodes[1],
                hostname="forgestack-node-b",
                kernel="7.0.0-43-generic",
                running_services=[],
            ),
        ]

        code, output, mock_discover = self.run_discover(discoveries)

        self.assertEqual(code, 1)
        self.assertIn("INCOMPLETE", output)
        self.assertIn("TIMEOUT", output)
        self.assertIn("UNKNOWN (not collected)", output)
        self.assertIn("forgestack-node-b", output)
        self.assertEqual(mock_discover.call_count, 2)

    def test_inventory_error_takes_priority(self):
        discoveries = [
            NodeDiscovery(
                node=self.nodes[0],
                hostname="node-a",
                kernel="7.0",
                running_services=[],
            ),
            NodeDiscovery(
                node=self.nodes[1],
                hostname="node-b",
                kernel="7.0",
                running_services=[],
            ),
        ]

        code, output, mock_discover = self.run_discover(
            discoveries,
            inventory_errors=["Record 3: invalid node"],
        )

        self.assertEqual(code, 2)
        self.assertIn("WARNING: Record 3: invalid node", output)
        self.assertEqual(mock_discover.call_count, 2)


if __name__ == "__main__":
    unittest.main()
