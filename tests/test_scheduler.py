import os
import unittest

os.environ.setdefault("SUPABASE_KEY", "test")
os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("GROQ_API_KEY", "test")
os.environ.setdefault("TAVILY_API_KEY", "test")

from src.db.models import Debate, Edge, Node
from src.orchestration.scheduler import (
    _current_round,
    _next_agent,
    add_guaranteed,
    build_candidates,
    has_acted_this_round,
    rank_nodes
)


def make_node(node_id: str, author_id: str, round: int, status: str = "open") -> Node:
    return Node(node_id, "debate", author_id, f"claim {node_id}", f"falsify {node_id}", status, round)


def make_edge(edge_id: str, source: str, target: str, author_id: str, round: int) -> Edge:
    return Edge(edge_id, "debate", author_id, source, target, "attacks", round)


class SchedulerTests(unittest.TestCase):
    def setUp(self):
        self.debate = Debate("debate", "topic", "running", 8, "pro", "anti", "", "", None)

    def test_rank_nodes_scores_attacks_and_excludes_closed_nodes(self):
        nodes = [make_node("a", "pro", 1), make_node("b", "pro", 2), make_node("c", "pro", 1, "resolved")]
        edges = [make_edge("e1", "x", "b", "anti", 2), make_edge("e2", "y", "a", "anti", 1)]

        ranked = rank_nodes(nodes, edges, 2, 0.5)

        self.assertEqual([node.id for node in ranked], ["b", "a"])

    def test_add_guaranteed_deduplicates_and_allows_short_lists(self):
        first = make_node("a", "pro", 1)
        second = make_node("b", "pro", 1)

        self.assertEqual(add_guaranteed([first], first), [first])
        self.assertEqual(add_guaranteed([first], second), [first, second])
        self.assertEqual(add_guaranteed([], None), [])

    def test_round_progression_uses_only_accepted_turns(self):
        rows = [
            {"round": 1, "agent_id": "pro", "accepted": True},
            {"round": 1, "agent_id": "anti", "accepted": False}
        ]

        self.assertTrue(has_acted_this_round("pro", rows, 1))
        self.assertFalse(has_acted_this_round("anti", rows, 1))
        self.assertEqual(_current_round(self.debate, rows), 1)
        self.assertEqual(_next_agent(self.debate, rows, 1), "anti")

        rows[1]["accepted"] = True
        self.assertEqual(_current_round(self.debate, rows), 2)
        self.assertEqual(_next_agent(self.debate, rows, 2), "pro")

    def test_candidates_include_recent_reply_and_recently_attacked_node(self):
        own_nodes = [make_node(f"p{i}", "pro", i) for i in range(1, 5)]
        opponent_nodes = [make_node(f"a{i}", "anti", i) for i in range(1, 5)]
        edges = [
            make_edge("own1", "a1", "p1", "anti", 4),
            make_edge("own2", "a2", "p2", "anti", 4),
            make_edge("own3", "a3", "p3", "anti", 4),
            make_edge("opponent1", "p1", "a1", "pro", 4),
            make_edge("opponent2", "p2", "a2", "pro", 4),
            make_edge("opponent3", "p3", "a3", "pro", 4),
            make_edge("recent", "a4", "p4", "anti", 4)
        ]
        transcript = [
            {"round": 4, "agent_id": "anti", "node_id": "a4", "edge_id": "recent", "accepted": True}
        ]

        candidates = build_candidates("pro", own_nodes + opponent_nodes, edges, transcript, 5, 0.8)

        self.assertEqual([node.id for node in candidates["attack_candidates"]], ["a1", "a2", "a3", "a4"])
        self.assertEqual([item["node"].id for item in candidates["defend_candidates"]], ["p1", "p2", "p3", "p4"])
        defended = candidates["defend_candidates"][-1]
        self.assertEqual([node.id for node in defended["attacking_claims"]], ["a4"])
        self.assertTrue(candidates["propose_available"])

    def test_first_turn_has_empty_candidates_and_propose_fallback(self):
        candidates = build_candidates("pro", [], [], [], 1, 0.8)

        self.assertEqual(candidates["attack_candidates"], [])
        self.assertEqual(candidates["defend_candidates"], [])
        self.assertTrue(candidates["propose_available"])


if __name__ == "__main__":
    unittest.main()
