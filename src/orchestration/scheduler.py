from ..db.models import Edge, Node, Debate


def score_node(node: Node, edges: list[Edge], current_round: int, decay_base: float) -> float:
    score = 0.0
    for edge in edges:
        if edge.type == "attacks" and edge.target_node_id == node.id:
            score += decay_base ** (current_round - edge.round)

    return score


def rank_nodes(nodes: list[Node], edges: list[Edge], current_round: int, decay_base: float) -> list[Node]:
    open_nodes = []

    for node in nodes:
        if node.status == "open":
            open_nodes.append(node)

    open_nodes.sort(key=lambda node: (
        -score_node(node, edges, current_round, decay_base),
        node.round,
        node.id
    ))

    return open_nodes


def add_guaranteed(ranked_top3: list[Node], guaranteed_node: Node | None) -> list[Node]:
    candidates = list(ranked_top3)

    if guaranteed_node is None:
        return candidates

    if guaranteed_node.id not in {node.id for node in candidates}:
        candidates.append(guaranteed_node)

    return candidates


def has_acted_this_round(agent_id: str, transcript_rows: list[dict], current_round: int) -> bool:
    for row in transcript_rows:
        if row["round"] == current_round and row["agent_id"] == agent_id and row["accepted"]:
            return True

    return False


def _current_round(debate: Debate, transcript_rows: list[dict]) -> int:
    accepted_rows = [row for row in transcript_rows if row["accepted"]]

    if not accepted_rows:
        return 1

    latest_round = max(row["round"] for row in accepted_rows)
    both_acted = has_acted_this_round(debate.pro_id, accepted_rows, latest_round) and has_acted_this_round(
        debate.anti_id,
        accepted_rows,
        latest_round
    )

    if both_acted:
        return latest_round + 1

    return latest_round


def _next_agent(debate: Debate, transcript_rows: list[dict], current_round: int) -> str:
    for agent_id in [debate.pro_id, debate.anti_id]:
        if not has_acted_this_round(agent_id, transcript_rows, current_round):
            return agent_id

    raise RuntimeError(f"Both agents have already acted in round {current_round}")


def _most_recent_node(
    agent_id: str,
    nodes_by_id: dict[str, Node],
    transcript_rows: list[dict]
) -> Node | None:
    for row in reversed(transcript_rows):
        node_id = row["node_id"]
        if row["accepted"] and row["agent_id"] == agent_id and node_id in nodes_by_id:
            return nodes_by_id[node_id]

    return None


def _most_recent_attacked_node(
    agent_id: str,
    opponent_id: str,
    nodes_by_id: dict[str, Node],
    edges_by_id: dict[str, Edge],
    transcript_rows: list[dict]
) -> Node | None:
    for row in reversed(transcript_rows):
        edge_id = row["edge_id"]

        if not row["accepted"] or row["agent_id"] != opponent_id or edge_id not in edges_by_id:
            continue

        edge = edges_by_id[edge_id]
        target = nodes_by_id.get(edge.target_node_id)

        if edge.type == "attacks" and target is not None and target.author_id == agent_id:
            return target

    return None


def _attacking_claims(node: Node, edges: list[Edge], nodes_by_id: dict[str, Node]) -> list[Node]:
    attacking_edges = []

    for edge in edges:
        if edge.type == "attacks" and edge.target_node_id == node.id and edge.source_node_id in nodes_by_id:
            attacking_edges.append(edge)

    attacking_edges.sort(key=lambda edge: (edge.round, edge.id), reverse=True)
    return [nodes_by_id[edge.source_node_id] for edge in attacking_edges]


def build_candidates(
    agent_id: str,
    nodes: list[Node],
    edges: list[Edge],
    transcript_rows: list[dict],
    current_round: int,
    decay_base: float
) -> dict:
    author_ids = {node.author_id for node in nodes}

    if agent_id not in author_ids and len(author_ids) > 1:
        raise ValueError(f"Agent {agent_id} does not belong to this debate")

    opponent_ids = author_ids - {agent_id}

    if len(opponent_ids) > 1:
        raise ValueError("Debate nodes contain more than two authors")

    opponent_id = next(iter(opponent_ids), None)
    own_nodes = [node for node in nodes if node.author_id == agent_id]
    opponent_nodes = [node for node in nodes if node.author_id == opponent_id]
    nodes_by_id = {node.id: node for node in nodes}
    edges_by_id = {edge.id: edge for edge in edges}

    recent_reply = None
    recent_attacked_node = None

    if opponent_id is not None:
        recent_reply = _most_recent_node(opponent_id, nodes_by_id, transcript_rows)
        recent_attacked_node = _most_recent_attacked_node(
            agent_id,
            opponent_id,
            nodes_by_id,
            edges_by_id,
            transcript_rows
        )

    attack_nodes = add_guaranteed(
        rank_nodes(opponent_nodes, edges, current_round, decay_base)[:3],
        recent_reply
    )
    defend_nodes = add_guaranteed(
        rank_nodes(own_nodes, edges, current_round, decay_base)[:3],
        recent_attacked_node
    )
    defend_candidates = []

    for node in defend_nodes:
        defend_candidates.append({
            "node": node,
            "attacking_claims": _attacking_claims(node, edges, nodes_by_id)
        })

    return {
        "attack_candidates": attack_nodes,
        "defend_candidates": defend_candidates,
        "propose_available": True
    }


async def schedule_next(debate_id: str, decay_base: float = 0.8) -> dict:
    from ..db.repositories.debates import get_by_id as get_debate
    from ..db.repositories.nodes import get_by_debate as get_nodes
    from ..db.repositories.edges import get_by_debate as get_edges
    from ..db.repositories.transcript import get_by_debate as get_transcript

    if not 0 < decay_base <= 1:
        raise ValueError("decay_base must be greater than 0 and at most 1")

    debate_row = await get_debate(debate_id)
    debate = Debate.from_row(debate_row)

    if debate.status != "running":
        raise ValueError(f"Debate {debate_id} is not running")

    node_rows = await get_nodes(debate_id)
    edge_rows = await get_edges(debate_id)
    transcript_rows = await get_transcript(debate_id)
    accepted_turns = [row for row in transcript_rows if row["accepted"] and row["agent_id"] is not None]

    if len(accepted_turns) >= debate.max_turns:
        raise RuntimeError(f"Debate {debate_id} has reached its maximum turn count")

    nodes = [Node.from_row(row) for row in node_rows]
    edges = [Edge.from_row(row) for row in edge_rows]
    current_round = _current_round(debate, transcript_rows)
    agent_id = _next_agent(debate, transcript_rows, current_round)
    opponent_id = debate.anti_id if agent_id == debate.pro_id else debate.pro_id
    candidates = build_candidates(
        agent_id,
        nodes,
        edges,
        transcript_rows,
        current_round,
        decay_base
    )

    return {
        "debate_id": debate.id,
        "topic": debate.topic,
        "round": current_round,
        "agent_id": agent_id,
        "opponent_id": opponent_id,
        **candidates
    }
