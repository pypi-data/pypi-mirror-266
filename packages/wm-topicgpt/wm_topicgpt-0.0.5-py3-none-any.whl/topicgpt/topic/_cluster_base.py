from typing import List, Any
from dataclasses import dataclass, field


@dataclass
class Cluster:
    texts: List[str] = None
    embeddings: List[float] = None
    children: List[Any] = field(default_factory=list)

    topic: str = None
    description: str = None
    keywords: List[str] = None

    size: int = None
    percent: float = None

    centroid: List[float] = None
    closest: List[str] = None
    within_cluster_dist: int = None