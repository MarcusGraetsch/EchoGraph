import numpy as np
from qdrant_client.http.models import ScoredPoint

from processing.matching import MatchResult, RelationshipMatcher


class DummyClient:
    def __init__(self, points):
        self.points = points

    def search(self, collection_name, query_vector, limit, query_filter=None):
        return self.points


def test_relationship_matcher_builds_results():
    points = [
        ScoredPoint(
            id=1,
            version=1,
            score=0.9,
            payload={"id": "reg-1", "confidence": 0.8},
            vector=None,
        )
    ]
    client = DummyClient(points)
    matcher = RelationshipMatcher(client=client, collection_name="demo")

    def lookup(guideline_id):
        return np.ones(3)

    def rationale_fn(chunk, payload):
        return f"Match for {chunk['id']} vs {payload['id']}"

    results = matcher.match(
        [{"id": "guideline-1", "title": "Test"}],
        embedding_lookup=lookup,
        rationale_fn=rationale_fn,
    )
    assert results == [
        MatchResult(
            guideline_id="guideline-1",
            regulation_id="reg-1",
            score=0.9,
            rationale="Match for guideline-1 vs reg-1",
            confidence=0.8,
        )
    ]
