import importlib.util
import unittest
from types import SimpleNamespace


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


node_module = load(
    "node_network_manager",
    "sigma-core/managers/node_network_manager.py",
)


class NodeContractsTests(unittest.TestCase):

    def setUp(self):
        self.manager = node_module.NodeNetworkManager(
            SimpleNamespace(
                now=lambda: "2026-07-15T00:00:00+00:00"
            )
        )

    def test_validate(self):
        result = self.manager.validate()

        self.assertTrue(result["valid"])
        self.assertIn("online", result["states"])
        self.assertIn("core", result["roles"])

    def test_snapshot(self):
        self.assertTrue(
            self.manager.snapshot()["validation"]["valid"]
        )


    def test_default_policy(self):
        policy = self.manager.default_policy()

        self.assertTrue(policy.allow_cluster_join)
        self.assertTrue(policy.allow_remote_management)
        self.assertTrue(policy.validate()["valid"])

    def test_new_node(self):
        node = self.manager.new_node(
            node_id="NODE-1",
            role="core",
            hostname="alpha",
            address="10.0.0.1",
        )

        self.assertEqual(node.id, "NODE-1")
        self.assertEqual(node.role, "core")
        self.assertEqual(node.state, "online")
        self.assertEqual(node.health, "unknown")
        self.assertEqual(node.version, 1)

    def test_node_as_dict(self):
        node = self.manager.new_node(
            node_id="NODE-2",
            role="edge",
        )

        self.assertEqual(
            node.as_dict()["id"],
            "NODE-2",
        )


    def test_repository_empty(self):
        self.assertEqual(
            self.manager.repository.count(),
            0,
        )

    def test_repository_create(self):
        node = self.manager.new_node(
            node_id="NODE-1",
            role="core",
        )

        self.manager.repository.create(node)

        self.assertTrue(
            self.manager.repository.exists(
                "NODE-1"
            )
        )

    def test_repository_get(self):
        node = self.manager.new_node(
            node_id="NODE-2",
            role="edge",
        )

        self.manager.repository.create(node)

        self.assertEqual(
            self.manager.repository.get("NODE-2").id,
            "NODE-2",
        )

    def test_repository_delete(self):
        node = self.manager.new_node(
            node_id="NODE-3",
            role="worker",
        )

        self.manager.repository.create(node)
        self.manager.repository.delete("NODE-3")

        self.assertFalse(
            self.manager.repository.exists(
                "NODE-3"
            )
        )


    def create_repository_node(
        self,
        node_id="NODE-1",
        role="core",
        state="online",
        hostname="alpha",
    ):
        node = self.manager.new_node(
            node_id=node_id,
            role=role,
            hostname=hostname,
            state=state,
        )

        return self.manager.create_node(node)

    def test_manager_repository_empty(self):
        self.assertEqual(
            self.manager.count(),
            0,
        )

    def test_manager_create_and_get(self):
        node = self.create_repository_node()

        self.assertEqual(
            self.manager.get("NODE-1"),
            node,
        )

    def test_manager_delete(self):
        self.create_repository_node()

        self.manager.delete("NODE-1")

        self.assertFalse(
            self.manager.exists("NODE-1")
        )

    def test_find_by_role(self):
        self.create_repository_node(
            node_id="NODE-1",
            role="core",
        )

        self.create_repository_node(
            node_id="NODE-2",
            role="worker",
        )

        result = self.manager.find(
            role="core",
        )

        self.assertEqual(
            [n.id for n in result],
            ["NODE-1"],
        )

    def test_find_by_state(self):
        self.create_repository_node(
            node_id="NODE-1",
            state="online",
        )

        self.create_repository_node(
            node_id="NODE-2",
            state="offline",
        )

        result = self.manager.find(
            state="offline",
        )

        self.assertEqual(
            result[0].id,
            "NODE-2",
        )


    def test_register(self):
        node = self.manager.new_node(
            node_id="NODE-R",
            role="core",
        )

        self.manager.register(node)

        self.assertTrue(
            self.manager.exists("NODE-R")
        )

    def test_disconnect(self):
        node = self.manager.new_node(
            node_id="NODE-D",
            role="core",
        )

        self.manager.register(node)

        node = self.manager.disconnect("NODE-D")

        self.assertEqual(
            node.state,
            "offline",
        )

    def test_maintenance(self):
        node = self.manager.new_node(
            node_id="NODE-M",
            role="core",
        )

        self.manager.register(node)

        node = self.manager.maintenance("NODE-M")

        self.assertEqual(
            node.state,
            "maintenance",
        )

    def test_reconnect(self):
        node = self.manager.new_node(
            node_id="NODE-C",
            role="core",
        )

        self.manager.register(node)

        self.manager.disconnect("NODE-C")

        node = self.manager.reconnect("NODE-C")

        self.assertEqual(
            node.state,
            "online",
        )



    def test_new_endpoint(self):
        endpoint = self.manager.new_endpoint(
            node_id="NODE-E",
            protocol="https",
            host="node-e.local",
            port=8443,
            priority=10,
            security={"tls": True},
            status="declared",
        )

        self.assertEqual(
            endpoint.as_dict(),
            {
                "node_id": "NODE-E",
                "protocol": "https",
                "host": "node-e.local",
                "port": 8443,
                "priority": 10,
                "security": {"tls": True},
                "status": "declared",
            },
        )

    def test_new_endpoint_normalizes_declarative_fields(self):
        endpoint = self.manager.new_endpoint(
            node_id=" NODE-E ",
            protocol=" HTTPS ",
            host=" node-e.local ",
            port=443,
            priority=0,
            security={},
            status=" DECLARED ",
        )

        self.assertEqual(endpoint.node_id, "NODE-E")
        self.assertEqual(endpoint.protocol, "https")
        self.assertEqual(endpoint.host, "node-e.local")
        self.assertEqual(endpoint.status, "declared")

    def test_new_endpoint_rejects_invalid_port(self):
        for invalid_port in (
            0,
            65536,
            "443",
            True,
        ):
            with self.subTest(port=invalid_port):
                with self.assertRaises(
                    node_module.InvalidNodeError
                ):
                    self.manager.new_endpoint(
                        node_id="NODE-E",
                        protocol="https",
                        host="node-e.local",
                        port=invalid_port,
                        priority=0,
                        security={},
                        status="declared",
                    )

    def test_new_endpoint_rejects_invalid_priority(self):
        for invalid_priority in (
            -1,
            1.5,
            True,
        ):
            with self.subTest(
                priority=invalid_priority
            ):
                with self.assertRaises(
                    node_module.InvalidNodeError
                ):
                    self.manager.new_endpoint(
                        node_id="NODE-E",
                        protocol="https",
                        host="node-e.local",
                        port=443,
                        priority=invalid_priority,
                        security={},
                        status="declared",
                    )

    def test_new_endpoint_rejects_missing_required_fields(self):
        invalid_values = (
            {
                "node_id": "",
                "protocol": "https",
                "host": "node-e.local",
                "status": "declared",
            },
            {
                "node_id": "NODE-E",
                "protocol": "",
                "host": "node-e.local",
                "status": "declared",
            },
            {
                "node_id": "NODE-E",
                "protocol": "https",
                "host": "",
                "status": "declared",
            },
            {
                "node_id": "NODE-E",
                "protocol": "https",
                "host": "node-e.local",
                "status": "",
            },
        )

        for values in invalid_values:
            with self.subTest(values=values):
                with self.assertRaises(
                    node_module.InvalidNodeError
                ):
                    self.manager.new_endpoint(
                        port=443,
                        priority=0,
                        security={},
                        **values,
                    )

    def test_new_endpoint_requires_security_mapping(self):
        with self.assertRaises(
            node_module.InvalidNodeError
        ):
            self.manager.new_endpoint(
                node_id="NODE-E",
                protocol="https",
                host="node-e.local",
                port=443,
                priority=0,
                security=["tls"],
                status="declared",
            )

    def test_new_endpoint_copies_security_parameters(self):
        security = {
            "tls": True,
            "mode": "declared",
        }

        endpoint = self.manager.new_endpoint(
            node_id="NODE-E",
            protocol="https",
            host="node-e.local",
            port=443,
            priority=0,
            security=security,
            status="declared",
        )

        security["tls"] = False

        self.assertEqual(
            endpoint.security,
            {
                "tls": True,
                "mode": "declared",
            },
        )



    def test_new_capability(self):
        capability = self.manager.new_capability(
            name="telemetry",
            version="1.0",
            state="declared",
            metadata={"format": "json"},
        )

        self.assertEqual(capability.name, "telemetry")
        self.assertEqual(capability.version, "1.0")
        self.assertEqual(capability.state, "declared")
        self.assertEqual(
            capability.metadata,
            {"format": "json"},
        )

    def test_new_capability_copies_metadata(self):
        metadata = {"encoding": "utf-8"}

        capability = self.manager.new_capability(
            name="logging",
            version="2.1",
            state="declared",
            metadata=metadata,
        )

        metadata["encoding"] = "binary"

        self.assertEqual(
            capability.metadata,
            {"encoding": "utf-8"},
        )


    def test_new_link(self):
        link = self.manager.new_link(
            source_node="node-a",
            destination_node="node-b",
            logical_cost=10,
            latency=5,
            priority=100,
            status="declared",
            metadata={"medium": "ethernet"},
        )

        self.assertEqual(link.source_node, "node-a")
        self.assertEqual(link.destination_node, "node-b")
        self.assertEqual(link.logical_cost, 10)
        self.assertEqual(link.latency, 5)
        self.assertEqual(link.priority, 100)
        self.assertEqual(link.status, "declared")
        self.assertEqual(link.metadata, {"medium": "ethernet"})

    def test_new_link_copies_metadata(self):
        metadata = {"type": "fiber"}

        link = self.manager.new_link(
            source_node="A",
            destination_node="B",
            logical_cost=1,
            latency=0,
            priority=1,
            metadata=metadata,
        )

        metadata["type"] = "wifi"

        self.assertEqual(
            link.metadata,
            {"type": "fiber"},
        )


    def test_new_zone(self):
        zone = self.manager.new_zone(
            name="Zone-A",
            kind="logical",
            metadata={"site": "Tangier"},
        )

        self.assertEqual(zone.name, "Zone-A")
        self.assertEqual(zone.kind, "logical")
        self.assertEqual(
            zone.metadata,
            {"site": "Tangier"},
        )

    def test_new_zone_copies_metadata(self):
        metadata = {"country": "Morocco"}

        zone = self.manager.new_zone(
            name="Zone-B",
            kind="geographic",
            metadata=metadata,
        )

        metadata["country"] = "France"

        self.assertEqual(
            zone.metadata,
            {"country": "Morocco"},
        )


    def test_new_region(self):
        region = self.manager.new_region(
            name="North",
            metadata={"country": "Morocco"},
        )

        self.assertEqual(region.name, "North")
        self.assertEqual(
            region.metadata,
            {"country": "Morocco"},
        )

    def test_new_region_copies_metadata(self):
        metadata = {"continent": "Africa"}

        region = self.manager.new_region(
            name="North",
            metadata=metadata,
        )

        metadata["continent"] = "Europe"

        self.assertEqual(
            region.metadata,
            {"continent": "Africa"},
        )


    def test_new_topology_snapshot(self):
        snapshot = self.manager.new_topology_snapshot(
            nodes=["N1", "N2"],
            links=["L1"],
            metadata={"version": 1},
        )

        self.assertEqual(snapshot.nodes, ["N1", "N2"])
        self.assertEqual(snapshot.links, ["L1"])
        self.assertEqual(snapshot.metadata, {"version": 1})

    def test_new_topology_snapshot_copies_data(self):
        nodes = ["N1"]
        links = ["L1"]
        metadata = {"v": 1}

        snapshot = self.manager.new_topology_snapshot(
            nodes=nodes,
            links=links,
            metadata=metadata,
        )

        nodes.append("N2")
        links.append("L2")
        metadata["v"] = 2

        self.assertEqual(snapshot.nodes, ["N1"])
        self.assertEqual(snapshot.links, ["L1"])
        self.assertEqual(snapshot.metadata, {"v": 1})


    def test_find_by_zone(self):
        self.assertEqual(
            self.manager.find_by_zone("Production"),
            [],
        )


    def test_find_by_region(self):
        self.assertEqual(
            self.manager.find_by_region("North"),
            [],
        )


    def test_find_by_capability(self):
        self.assertEqual(
            self.manager.find_by_capability("mqtt"),
            [],
        )


    def test_find_by_endpoint(self):
        self.assertEqual(
            self.manager.find_by_endpoint("api"),
            [],
        )


    def test_find_incoming_links(self):
        self.assertEqual(
            self.manager.find_incoming_links("node-1"),
            [],
        )


    def test_find_outgoing_links(self):
        self.assertEqual(
            self.manager.find_outgoing_links("node-1"),
            [],
        )


    def test_validate_rejects_duplicate_node_ids(self):
        with self.assertRaises(NotImplementedError):
            self.manager.validate_duplicate_node_ids()


    def test_validate_rejects_duplicate_endpoint_ids(self):
        with self.assertRaises(NotImplementedError):
            self.manager.validate_duplicate_endpoint_ids()


    def test_validate_rejects_duplicate_link_ids(self):
        with self.assertRaises(NotImplementedError):
            self.manager.validate_duplicate_link_ids()


    def test_validate_rejects_duplicate_zone_ids(self):
        with self.assertRaises(NotImplementedError):
            self.manager.validate_duplicate_zone_ids()


    def test_validate_rejects_duplicate_region_ids(self):
        with self.assertRaises(NotImplementedError):
            self.manager.validate_duplicate_region_ids()


    def test_validate_rejects_duplicate_capability_ids(self):
        with self.assertRaises(NotImplementedError):
            self.manager.validate_duplicate_capability_ids()


    def test_validate_rejects_orphan_link_references(self):
        with self.assertRaises(NotImplementedError):
            self.manager.validate_orphan_link_references()


class NodeHealthContractsTests(unittest.TestCase):

    def test_node_health_values(self):
        self.assertEqual(
            node_module.NodeHealth.UNKNOWN.value,
            "unknown",
        )

        self.assertEqual(
            node_module.NodeHealth.HEALTHY.value,
            "healthy",
        )

        self.assertEqual(
            node_module.NodeHealth.DEGRADED.value,
            "degraded",
        )

        self.assertEqual(
            node_module.NodeHealth.UNREACHABLE.value,
            "unreachable",
        )

        self.assertEqual(
            node_module.NodeHealth.DISABLED.value,
            "disabled",
        )

        self.assertEqual(
            node_module.NodeHealth.REVOKED.value,
            "revoked",
        )



class HeartbeatContractsTests(unittest.TestCase):

    def setUp(self):
        self.manager = node_module.NodeNetworkManager(
            SimpleNamespace(
                now=lambda: "2026-07-20T13:40:00+00:00"
            )
        )

    def test_new_heartbeat(self):
        heartbeat = self.manager.new_heartbeat(
            node_id="NODE-1",
        )

        self.assertEqual(
            heartbeat.node_id,
            "NODE-1",
        )

        self.assertEqual(
            heartbeat.health,
            "healthy",
        )

    def test_new_heartbeat_records_timestamp(self):
        heartbeat = self.manager.new_heartbeat(
            node_id="NODE-1",
        )

        self.assertEqual(
            heartbeat.occurred_at,
            "2026-07-20T13:40:00+00:00",
        )

    def test_new_heartbeat_rejects_empty_node_id(self):
        with self.assertRaises(
            node_module.InvalidNodeError,
        ):
            self.manager.new_heartbeat(
                node_id="",
            )


    def test_node_defaults_to_unknown_health(self):
        node = self.manager.new_node(
            node_id="NODE-1",
            role="worker",
        )

        self.assertEqual(
            node.health,
            node_module.NodeHealth.UNKNOWN.value,
        )


class TTLContractsTests(unittest.TestCase):

    def setUp(self):
        self.manager = node_module.NodeNetworkManager(
            SimpleNamespace(
                now=lambda: "2026-07-20T13:45:00+00:00"
            )
        )

    def test_default_policy_has_positive_heartbeat_ttl(self):
        policy = self.manager.default_policy()

        self.assertGreater(
            policy.heartbeat_ttl_seconds,
            0,
        )

    def test_default_network_policy_ttl(self):
        policy = self.manager.default_policy()

        self.assertEqual(
            policy.heartbeat_ttl_seconds,
            30,
        )

    def test_default_policy_validate_includes_heartbeat_ttl(self):
        policy = self.manager.default_policy()
        result = policy.validate()

        self.assertTrue(result["valid"])
        self.assertIn(
            "heartbeat_ttl_seconds",
            result,
        )
        self.assertEqual(
            result["heartbeat_ttl_seconds"],
            30,
        )



class HeartbeatTTLContractsTests(unittest.TestCase):

    def setUp(self):
        self.manager = node_module.NodeNetworkManager(
            SimpleNamespace(
                now=lambda: "2026-07-20T13:45:00+00:00"
            )
        )

    def test_manager_exposes_heartbeat_ttl(self):
        policy = self.manager.default_policy()

        self.assertEqual(
            policy.heartbeat_ttl_seconds,
            30,
        )



    def test_manager_has_expire_heartbeats(self):
        self.assertTrue(
            hasattr(
                self.manager,
                "expire_heartbeats",
            )
        )


    def test_expire_heartbeats_returns_list(self):
        expired = self.manager.expire_heartbeats()

        self.assertIsInstance(
            expired,
            list,
        )


    def test_manager_has_heartbeat_registry(self):
        self.assertTrue(
            hasattr(
                self.manager,
                "_heartbeats",
            )
        )



    def test_new_heartbeat_is_registered(self):
        heartbeat = self.manager.new_heartbeat(
            node_id="NODE-1",
        )

        self.assertIn(
            "NODE-1",
            self.manager._heartbeats,
        )

        self.assertIs(
            self.manager._heartbeats["NODE-1"],
            heartbeat,
        )



    def test_expire_heartbeats_empty_registry(self):
        expired = self.manager.expire_heartbeats()

        self.assertEqual(
            expired,
            [],
        )



    def test_fresh_heartbeat_is_not_expired(self):
        self.manager.new_heartbeat(
            node_id="NODE-1",
        )

        expired = self.manager.expire_heartbeats()

        self.assertNotIn(
            "NODE-1",
            expired,
        )



    def test_expired_heartbeat_is_reported(self):
        heartbeat = node_module.Heartbeat(
            node_id="NODE-1",
            occurred_at="2026-07-20T13:00:00+00:00",
            health=node_module.NodeHealth.HEALTHY.value,
        )

        self.manager._heartbeats["NODE-1"] = heartbeat

        expired = self.manager.expire_heartbeats()

        self.assertIn(
            "NODE-1",
            expired,
        )



    def test_future_heartbeat_is_not_reported(self):
        heartbeat = node_module.Heartbeat(
            node_id="NODE-2",
            occurred_at="2026-07-20T14:30:00+00:00",
            health=node_module.NodeHealth.HEALTHY.value,
        )

        self.manager._heartbeats["NODE-2"] = heartbeat

        expired = self.manager.expire_heartbeats()

        self.assertNotIn(
            "NODE-2",
            expired,
        )



    def test_ttl_policy_expires_old_heartbeat(self):
        self.manager.policy = node_module.NodeNetworkPolicy(
            heartbeat_ttl_seconds=30,
        )

        heartbeat = node_module.Heartbeat(
            node_id="NODE-TTL",
            occurred_at="2026-07-20T13:00:00+00:00",
            health=node_module.NodeHealth.HEALTHY.value,
        )

        self.manager._heartbeats["NODE-TTL"] = heartbeat

        expired = self.manager.expire_heartbeats()

        self.assertIn(
            "NODE-TTL",
            expired,
        )



    def test_large_ttl_keeps_old_heartbeat_alive(self):
        self.manager.policy = node_module.NodeNetworkPolicy(
            heartbeat_ttl_seconds=999999999,
        )

        heartbeat = node_module.Heartbeat(
            node_id="NODE-LONG",
            occurred_at="2026-07-20T13:00:00+00:00",
            health=node_module.NodeHealth.HEALTHY.value,
        )

        self.manager._heartbeats["NODE-LONG"] = heartbeat

        expired = self.manager.expire_heartbeats()

        self.assertNotIn(
            "NODE-LONG",
            expired,
        )



    def test_expired_node_becomes_unreachable(self):
        node = self.manager.new_node(
            node_id="NODE-STATE",
            role=node_module.NodeRole.WORKER.value,
        )

        self.manager.repository.create(node)

        heartbeat = node_module.Heartbeat(
            node_id="NODE-STATE",
            occurred_at="2026-07-20T13:00:00+00:00",
            health=node_module.NodeHealth.HEALTHY.value,
        )

        self.manager._heartbeats["NODE-STATE"] = heartbeat

        self.manager.expire_heartbeats()

        node = self.manager.repository.get("NODE-STATE")

        self.assertEqual(
            node.health,
            node_module.NodeHealth.UNREACHABLE.value,
        )



    def test_new_heartbeat_recovers_node_health(self):
        node = self.manager.new_node(
            node_id="NODE-RECOVER",
            role=node_module.NodeRole.WORKER.value,
        )

        self.manager.repository.create(node)

        self.manager._heartbeats["NODE-RECOVER"] = (
            node_module.Heartbeat(
                node_id="NODE-RECOVER",
                occurred_at="2026-07-20T13:00:00+00:00",
                health=node_module.NodeHealth.HEALTHY.value,
            )
        )

        self.manager.expire_heartbeats()

        self.manager.new_heartbeat(
            node_id="NODE-RECOVER",
        )

        node = self.manager.repository.get("NODE-RECOVER")

        self.assertEqual(
            node.health,
            node_module.NodeHealth.HEALTHY.value,
        )


    def test_unreachable_node_emits_event(self):
        node = self.manager.new_node(
            node_id="NODE-EVENT",
            role=node_module.NodeRole.WORKER.value,
        )

        self.manager.repository.create(node)

        heartbeat = node_module.Heartbeat(
            node_id="NODE-EVENT",
            occurred_at="2026-07-20T13:00:00+00:00",
            health=node_module.NodeHealth.HEALTHY.value,
        )

        self.manager._heartbeats["NODE-EVENT"] = heartbeat

        self.manager.expire_heartbeats()

        self.assertIn(
            "node.unreachable",
            self.manager.events,
        )


    def test_recovered_node_emits_event(self):
        node = self.manager.new_node(
            node_id="NODE-RECOVER-EVENT",
            role=node_module.NodeRole.WORKER.value,
        )

        self.manager.repository.create(node)

        self.manager._heartbeats["NODE-RECOVER-EVENT"] = (
            node_module.Heartbeat(
                node_id="NODE-RECOVER-EVENT",
                occurred_at="2026-07-20T13:00:00+00:00",
                health=node_module.NodeHealth.HEALTHY.value,
            )
        )

        self.manager.expire_heartbeats()

        self.manager.new_heartbeat(
            node_id="NODE-RECOVER-EVENT",
        )

        self.assertIn(
            "node.recovered",
            self.manager.events,
        )


    def test_publish_adds_event_to_log(self):
        self.manager.publish("node.test")

        self.assertEqual(
            self.manager.events[-1],
            "node.test",
        )


    def test_publish_notifies_subscriber(self):
        received = []

        def subscriber(event):
            received.append(event)

        self.manager.subscribe(subscriber)
        self.manager.publish("node.test")

        self.assertEqual(
            received,
            ["node.test"],
        )

    def test_publish_structured_event(self):
        received = []

        def subscriber(event):
            received.append(event)

        event = {
            "type": "node.test",
            "node_id": "node-01",
        }

        self.manager.subscribe(subscriber)
        self.manager.publish(event)

        self.assertEqual(received[0]['type'], 'node.test')
        self.assertEqual(received[0]['node_id'], 'node-01')


    def test_node_event_to_dict(self):
        NodeEvent = node_module.NodeEvent

        event = NodeEvent(
            event_type="node.test",
            node_id="node-01",
            occurred_at=0,
            details={},
        )

        data = event.as_dict()

        self.assertIsInstance(data.get("id"), str)
        self.assertGreater(len(data["id"]), 10)

        self.assertEqual(
            {k: v for k, v in data.items() if k != "id"},
            {
                "event_type": "node.test",
                "node_id": "node-01",
                "occurred_at": 0,
                "details": {},
                "severity": "INFO",
            },
        )


    def test_node_event_auto_timestamp(self):
        NodeEvent = node_module.NodeEvent

        event = NodeEvent(
            event_type="node.test",
            node_id="node-01",
            occurred_at=None,
            details={},
        )

        self.assertIsNotNone(event.occurred_at)
        self.assertIsInstance(event.occurred_at, (int, float))


    def test_node_event_default_severity(self):
        NodeEvent = node_module.NodeEvent

        event = NodeEvent(
            event_type="node.test",
            node_id="node-01",
            occurred_at=0,
            details={},
        )

        self.assertEqual(event.as_dict().get("severity"), "INFO")


    def test_node_event_auto_uuid(self):
        NodeEvent = node_module.NodeEvent

        event = NodeEvent(
            event_type="node.test",
            node_id="node-01",
            occurred_at=0,
            details={},
        )

        self.assertIsNotNone(event.as_dict().get("id"))
        self.assertIsInstance(event.as_dict().get("id"), str)
        self.assertGreater(len(event.as_dict().get("id")), 10)

if __name__ == "__main__":
    unittest.main()


