from ..db.models import Node
from sentence_transformers import CrossEncoder, util
from ..embeddings import embed_batch
from .generic_corpus import GENERIC_EMBEDDINGS
import re

nli_model = CrossEncoder("cross-encoder/nli-deberta-v3-base")
NLI_LABELS = ["contradiction", "entailment", "neutral"]
FALSIFICATION_GENERICNESS_THRESHOLD = 0.75
ENGAGEMENT_THRESHOLD = 0.5

def check_edge_target(
    mode: str,
    target_node_id: str | None,
    attack_candidates: list[Node],
    defend_candidates: list[dict]
) -> bool:
    if mode == "propose" :
        return target_node_id is None

    if mode == "attack" :
        return target_node_id in [node.id for node in attack_candidates]

    if mode == "defend" :
        return target_node_id in [candidate["node"].id for candidate in defend_candidates]

    return False


def check_falsifiability(claim : str , falsification_condition: str) -> tuple[bool , str | None] :
    if not claim.strip() :
        return False , "claim is empty or missing"

    if not falsification_condition.strip() :
        return False , "falsification_condition is empty or missing"

    condition = falsification_condition.strip()
    condition_parts = [
        part.strip()
        for part in re.split(r"(?<=[.!?;])\s+|\n+", condition)
        if part.strip()
    ]
    condition_embeddings = embed_batch(condition_parts)
    similarities = util.cos_sim(condition_embeddings, GENERIC_EMBEDDINGS)
    highest_similarities = similarities.max(dim=1).values
    generic_parts = sum(
        float(similarity) >= FALSIFICATION_GENERICNESS_THRESHOLD
        for similarity in highest_similarities
    )

    if generic_parts / len(condition_parts) >= 1 / 3 :
        return False , "falsification_condition is generic or vague and does not describe specific evidence against the claim"

    scores = nli_model.predict([(claim.strip(), condition)])
    label_index = int(scores[0].argmax())
    label = NLI_LABELS[label_index]

    if label == "entailment" :
        return False , "falsification_condition restates or follows from the claim instead of describing evidence against it"

    return True , None


def check_engagement(
    mode: str,
    claim: str,
    target_node_id: str | None,
    attack_candidates: list[Node],
    defend_candidates: list[dict]
) -> tuple[bool, str | None]:
    if not claim.strip() :
        return False , "claim is empty or missing"

    if mode == "propose" :
        return True , None

    target_contents = []

    if mode == "attack" :
        for node in attack_candidates :
            if target_node_id == node.id :
                target_contents.append(node.claim)
                break

    elif mode == "defend" :
        for candidate in defend_candidates :
            if target_node_id == candidate["node"].id :
                target_contents.extend(
                    attacking_claim.claim
                    for attacking_claim in candidate["attacking_claims"]
                )
                break

    else :
        return False , "mode must be attack, defend, or propose"

    if not target_contents :
        return False , "no valid target content found for the selected target_node_id"

    claim_text = claim.strip()
    embeddings = embed_batch([claim_text, *target_contents])
    similarity = float(util.cos_sim([embeddings[0]], embeddings[1:]).max())
    scores = nli_model.predict([
        (claim_text, target_content)
        for target_content in target_contents
    ])
    labels = [NLI_LABELS[int(score.argmax())] for score in scores]

    if similarity < ENGAGEMENT_THRESHOLD and "contradiction" not in labels :
        return False , "claim does not directly engage the selected target's reasoning"

    return True , None


        
