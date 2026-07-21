from dataclasses import dataclass

@dataclass
class Node:
    id: str
    debate_id: str
    author_id: str
    claim: str
    falsification_condition: str
    status: str
    round: int

    @classmethod
    def from_row(cls, row: dict) -> "Node":
        return cls(**row)

@dataclass
class Edge:
    id: str
    debate_id: str
    author_id: str
    source_node_id: str
    target_node_id: str
    type: str
    round: int

    @classmethod
    def from_row(cls, row: dict) -> "Edge":
        return cls(**row)
    

@dataclass
class Agent:
    id: str
    name: str
    type: str
    system_prompt: str

    @classmethod
    def from_row(cls, row: dict) -> "Agent":
        return cls(**row)


@dataclass
class Debate:
    id: str
    topic: str
    status: str
    max_turns: int
    pro_id: str
    anti_id: str
    created_at: str
    updated_at: str
    archived_at: str | None

    @classmethod
    def from_row(cls, row: dict) -> "Debate":
        return cls(**row)