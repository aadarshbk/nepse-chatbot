"""Advanced retrieval optimization utilities for Hybrid RAG."""
import logging
from typing import Any
from collections import defaultdict

logger = logging.getLogger(__name__)


class QueryExpander:
    """Expand queries with synonyms and related terms for better retrieval."""

    # Domain-specific synonyms and related terms for NEPSE
    SYNONYMS = {
        "buy": ["purchase", "invest", "long"],
        "sell": ["offload", "exit", "short"],
        "stock": ["share", "kitta", "security"],
        "price": ["rate", "cost", "ltp"],
        "tax": ["taxation", "duty", "levy"],
        "dividend": ["income", "distribution", "payout"],
        "trading": ["investment", "dealing", "transaction"],
        "market": ["exchange", "nepse", "bourse"],
        "risk": ["danger", "hazard", "volatility"],
        "profit": ["gain", "return", "earnings"],
        "loss": ["drawdown", "decline", "drop"],
    }

    @staticmethod
    def expand_query(query: str, max_expansions: int = 3) -> list[str]:
        """
        Expand a query with synonyms.

        Args:
            query: Original query
            max_expansions: Maximum number of expanded queries

        Returns:
            List of expanded queries
        """
        expanded = [query]  # Include original
        query_lower = query.lower()
        expansion_count = 0

        for term, synonyms in QueryExpander.SYNONYMS.items():
            if term in query_lower and expansion_count < max_expansions:
                for syn in synonyms[:2]:  # Use top 2 synonyms
                    expanded_query = query_lower.replace(term, syn)
                    if expanded_query not in expanded:
                        expanded.append(expanded_query)
                        expansion_count += 1

        return expanded[:max_expansions + 1]  # Return original + expansions


class ResultDeduplicator:
    """Deduplicate and merge highly similar results."""

    @staticmethod
    def deduplicate(
        results: list[dict[str, Any]], similarity_threshold: float = 0.9
    ) -> list[dict[str, Any]]:
        """
        Remove duplicate/highly similar results.

        Args:
            results: List of retrieved results
            similarity_threshold: Threshold for considering results similar

        Returns:
            Deduplicated results list
        """
        if not results:
            return results

        deduplicated = []
        seen_docs = {}

        for result in sorted(results, key=lambda x: x.get("score", 0), reverse=True):
            doc_id = result.get("doc_id")
            is_duplicate = False

            # Check against seen documents
            for seen_id, seen_score in seen_docs.items():
                # Simple heuristic: same KB ID = duplicate
                if doc_id == seen_id:
                    is_duplicate = True
                    break

            if not is_duplicate:
                deduplicated.append(result)
                seen_docs[doc_id] = result.get("score", 0)

        return deduplicated

    @staticmethod
    def merge_results(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Merge similar results into consolidated entries.

        Args:
            results: List of results to merge

        Returns:
            Merged results
        """
        if not results:
            return results

        merged = {}

        for result in results:
            doc_id = result.get("doc_id", "unknown")

            if doc_id not in merged:
                merged[doc_id] = result.copy()
            else:
                # Update with higher score
                if result.get("score", 0) > merged[doc_id].get("score", 0):
                    merged[doc_id] = result.copy()

        return list(merged.values())


class RelevanceAnalyzer:
    """Analyze and score result relevance."""

    @staticmethod
    def analyze_result_quality(
        result: dict[str, Any], query: str
    ) -> dict[str, Any]:
        """
        Analyze quality of a single result.

        Args:
            result: Retrieved result
            query: Original query

        Returns:
            Result with quality metrics
        """
        enhanced_result = result.copy()

        # Add quality indicators
        score = result.get("score", 0)
        enhanced_result["quality_score"] = min(score * 1.1, 1.0)  # Boost high scores

        # Check if query terms appear in result
        query_terms = set(query.lower().split())
        result_text = f"{result.get('title', '')} {result.get('content', '')}".lower()
        matching_terms = sum(1 for term in query_terms if term in result_text)

        enhanced_result["term_match_ratio"] = (
            matching_terms / len(query_terms) if query_terms else 0
        )

        return enhanced_result

    @staticmethod
    def rank_by_quality(results: list[dict[str, Any]], query: str) -> list[dict[str, Any]]:
        """
        Rerank results by quality metrics.

        Args:
            results: Retrieved results
            query: Original query

        Returns:
            Reranked results
        """
        analyzed = [
            RelevanceAnalyzer.analyze_result_quality(r, query) for r in results
        ]

        # Sort by combined score: main score (60%) + term match (40%)
        scored = [
            {
                **r,
                "final_score": (0.6 * r.get("score", 0)) + (0.4 * r.get("term_match_ratio", 0)),
            }
            for r in analyzed
        ]

        return sorted(scored, key=lambda x: x.get("final_score", 0), reverse=True)


class QueryContextAnalyzer:
    """Analyze query context to improve retrieval."""

    # Intent patterns for common queries
    INTENT_PATTERNS = {
        "invest": r"\b(invest|buy|purchase|long)\b",
        "exit": r"\b(sell|exit|offload|short)\b",
        "analysis": r"\b(analyze|analysis|trend|pattern|technical)\b",
        "regulation": r"\b(rule|regulation|law|requirement|sebon)\b",
        "tax": r"\b(tax|taxation|duty|levy|cgt)\b",
        "dividend": r"\b(dividend|distribution|payout|income)\b",
    }

    @staticmethod
    def detect_intent(query: str) -> list[str]:
        """
        Detect user intent from query.

        Args:
            query: User query

        Returns:
            List of detected intents
        """
        import re

        query_lower = query.lower()
        detected_intents = []

        for intent, pattern in QueryContextAnalyzer.INTENT_PATTERNS.items():
            if re.search(pattern, query_lower):
                detected_intents.append(intent)

        return detected_intents or ["general"]


class HybridRAGOptimizer:
    """Orchestrates advanced retrieval optimization."""

    def __init__(self):
        self.query_expander = QueryExpander()
        self.deduplicator = ResultDeduplicator()
        self.relevance_analyzer = RelevanceAnalyzer()
        self.context_analyzer = QueryContextAnalyzer()

    def optimize_retrieval(
        self,
        query: str,
        initial_results: list[dict[str, Any]],
        use_expansion: bool = True,
        use_deduplication: bool = True,
        use_reranking: bool = True,
    ) -> list[dict[str, Any]]:
        """
        Apply optimization techniques to improve retrieval results.

        Args:
            query: Original query
            initial_results: Initial retrieval results
            use_expansion: Apply query expansion
            use_deduplication: Remove duplicates
            use_reranking: Rerank by quality

        Returns:
            Optimized results
        """
        results = initial_results.copy()

        # 1. Deduplicate
        if use_deduplication:
            results = self.deduplicator.deduplicate(results)

        # 2. Rerank by quality
        if use_reranking:
            results = self.relevance_analyzer.rank_by_quality(results, query)

        # 3. Detect intent (for context awareness)
        intents = self.context_analyzer.detect_intent(query)
        for result in results:
            result["detected_intents"] = intents

        logger.debug(
            f"Optimization complete: {len(results)} results, intents: {intents}"
        )

        return results


# Global optimizer instance
_optimizer = None


def get_optimizer() -> HybridRAGOptimizer:
    """Get or create global optimizer instance."""
    global _optimizer
    if _optimizer is None:
        _optimizer = HybridRAGOptimizer()
    return _optimizer
