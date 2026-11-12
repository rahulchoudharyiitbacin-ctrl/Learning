"""Retrieval metrics and repeated-trial metrics (standard library only).

Retrieval: for one query you have the ranked list of retrieved document ids
and the set of ids that really are relevant.

    recall_at_k     of all relevant documents, how many are in the top k?
    precision_at_k  of the top k, how many are relevant?
    reciprocal_rank 1 / rank of the first relevant document (0 if none)
    mrr             the mean of reciprocal_rank over many queries

Repeated trials (agents): per-trial success probability p, k trials.

    pass_at_k   chance that at least one of k trials succeeds
    pass_pow_k  chance that all k trials succeed
"""


def recall_at_k(retrieved, relevant, k):
    relevant = set(relevant)
    if not relevant:
        raise ValueError("a query needs at least one relevant document")
    return len(set(retrieved[:k]) & relevant) / len(relevant)


def precision_at_k(retrieved, relevant, k):
    top = retrieved[:k]
    return sum(1 for d in top if d in set(relevant)) / k


def reciprocal_rank(retrieved, relevant):
    relevant = set(relevant)
    for rank, doc in enumerate(retrieved, 1):
        if doc in relevant:
            return 1 / rank
    return 0.0


def mrr(queries):
    """queries: list of (retrieved, relevant) pairs."""
    return sum(reciprocal_rank(r, rel) for r, rel in queries) / len(queries)


def pass_at_k(p, k):
    return 1 - (1 - p) ** k


def pass_pow_k(p, k):
    return p ** k
