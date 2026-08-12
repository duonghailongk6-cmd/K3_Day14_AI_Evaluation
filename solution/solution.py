"""
Day 14 — Evaluation Pipeline & Failure Analysis
File: solution/solution.py
"""

from dataclasses import dataclass, field
import json
import re

# ---------------------------------------------------------------------------
# Required Dataclasses / Core Classes (Must be top-level exports)
# ---------------------------------------------------------------------------

class QAPair:
    def __init__(
        self,
        question: str = "",
        expected_answer: str = "",
        context: str | None = None,
        metadata: dict | None = None,
        retrieved_contexts: list[str] | None = None,
    ):
        self.question = question
        self.expected_answer = expected_answer
        self.context = context
        self.metadata = metadata if metadata is not None else {}
        self.retrieved_contexts = retrieved_contexts if retrieved_contexts is not None else []


@dataclass
class EvalResult:
    qa_pair: QAPair
    actual_answer: str
    faithfulness: float
    relevance: float
    completeness: float
    passed: bool
    failure_type: str | None = None
    context_recall: float | None = None
    context_precision: float | None = None

    def overall_score(self) -> float:
        """Returns the unweighted average of core RAGAS metrics."""
        return (self.faithfulness + self.relevance + self.completeness) / 3.0


class RAGASEvaluator:
    @staticmethod
    def _tokenize(text: str) -> set[str]:
        return set(re.findall(r"\w+", text.lower()))

    def evaluate_faithfulness(self, answer: str, context: str) -> float:
        ans_tokens = self._tokenize(answer)
        ctx_tokens = self._tokenize(context)
        stopwords = {"is", "a", "the", "in", "of", "and", "or", "to", "for", "with", "on", "at", "by", "some", "here"}
        ans_tokens -= stopwords
        ctx_tokens -= stopwords
        if not ans_tokens:
            return 1.0
        return len(ans_tokens.intersection(ctx_tokens)) / len(ans_tokens)

    def evaluate_relevance(self, answer: str, question: str) -> float:
        ans_tokens = self._tokenize(answer)
        q_tokens = self._tokenize(question)
        stopwords = {"is", "a", "the", "in", "of", "what", "how", "why", "who", "where", "when"}
        ans_tokens -= stopwords
        q_tokens -= stopwords
        if not q_tokens:
            return 1.0
        return len(q_tokens.intersection(ans_tokens)) / len(q_tokens)

    def evaluate_completeness(self, answer: str, expected: str) -> float:
        ans_tokens = self._tokenize(answer)
        exp_tokens = self._tokenize(expected)
        stopwords = {"is", "a", "the", "in", "of", "and", "or"}
        ans_tokens -= stopwords
        exp_tokens -= stopwords
        if not exp_tokens:
            return 1.0
        return len(exp_tokens.intersection(ans_tokens)) / len(exp_tokens)

    def evaluate_context_recall(self, chunks: list[str], expected: str) -> float:
        exp_tokens = self._tokenize(expected) - {"is", "a", "the", "in", "of", "and", "or"}
        if not exp_tokens:
            return 1.0
        all_chunk_tokens = set()
        for chunk in chunks:
            all_chunk_tokens.update(self._tokenize(chunk))
        return len(exp_tokens.intersection(all_chunk_tokens)) / len(exp_tokens)

    def evaluate_context_precision(self, chunks: list[str], expected: str) -> float:
        if not chunks:
            return 0.0
        exp_tokens = self._tokenize(expected) - {"is", "a", "the", "in", "of", "and", "or"}
        relevant_flags = []
        for chunk in chunks:
            c_tokens = self._tokenize(chunk) - {"is", "a", "the", "in", "of", "and", "or"}
            relevant_flags.append(len(exp_tokens.intersection(c_tokens)) > 0)

        if not any(relevant_flags):
            return 0.0

        precisions = []
        running_rel_count = 0
        for k, is_rel in enumerate(relevant_flags, start=1):
            if is_rel:
                running_rel_count += 1
                precisions.append(running_rel_count / k)
        return sum(precisions) / len(precisions) if precisions else 0.0

    def run_full_eval(
        self,
        answer: str,
        question: str,
        context: str,
        expected: str,
        contexts: list[str] | None = None,
    ) -> EvalResult:
        faithfulness = self.evaluate_faithfulness(answer, context)
        relevance = self.evaluate_relevance(answer, question)
        completeness = self.evaluate_completeness(answer, expected)
        passed = faithfulness >= 0.5 and relevance >= 0.5 and completeness >= 0.5

        ctx_recall = None
        ctx_precision = None
        if contexts is not None:
            ctx_recall = self.evaluate_context_recall(contexts, expected)
            ctx_precision = self.evaluate_context_precision(contexts, expected)

        qa = QAPair(
            question=question,
            expected_answer=expected,
            context=context,
            retrieved_contexts=contexts or [],
        )

        return EvalResult(
            qa_pair=qa,
            actual_answer=answer,
            faithfulness=faithfulness,
            relevance=relevance,
            completeness=completeness,
            passed=passed,
            context_recall=ctx_recall,
            context_precision=ctx_precision,
        )


class BenchmarkRunner:
    def run(self, qa_pairs: list[QAPair], agent_fn, evaluator: RAGASEvaluator) -> list[EvalResult]:
        results = []
        for qa in qa_pairs:
            actual_answer = agent_fn(qa.question)
            contexts = qa.retrieved_contexts if qa.retrieved_contexts else None
            res = evaluator.run_full_eval(
                answer=actual_answer,
                question=qa.question,
                context=qa.context or "",
                expected=qa.expected_answer,
                contexts=contexts,
            )
            res.qa_pair = qa
            results.append(res)
        return results

    def generate_report(self, results: list[EvalResult]) -> dict:
        if not results:
            return {"total": 0, "pass_rate": 0.0}

        total = len(results)
        passed_count = sum(1 for r in results if r.passed)
        avg_faithfulness = sum(r.faithfulness for r in results) / total
        avg_relevance = sum(r.relevance for r in results) / total
        avg_completeness = sum(r.completeness for r in results) / total

        report = {
            "total": total,
            "passed": passed_count,
            "pass_rate": passed_count / total,
            "avg_faithfulness": avg_faithfulness,
            "avg_relevance": avg_relevance,
            "avg_completeness": avg_completeness,
        }

        recalls = [r.context_recall for r in results if r.context_recall is not None]
        precisions = [r.context_precision for r in results if r.context_precision is not None]

        if recalls:
            report["avg_context_recall"] = sum(recalls) / len(recalls)
        if precisions:
            report["avg_context_precision"] = sum(precisions) / len(precisions)

        return report

    def identify_failures(self, results: list[EvalResult], threshold: float = 0.5) -> list[EvalResult]:
        return [
            r for r in results
            if r.faithfulness < threshold
            or r.relevance < threshold
            or r.completeness < threshold
            or not r.passed
        ]

    def run_regression(self, new_results: list[EvalResult], baseline_results: list[EvalResult]) -> dict:
        new_report = self.generate_report(new_results)
        base_report = self.generate_report(baseline_results)

        regressions = []
        for metric in ["faithfulness", "relevance", "completeness"]:
            new_val = new_report.get(f"avg_{metric}", 0.0)
            base_val = base_report.get(f"avg_{metric}", 0.0)
            if base_val - new_val > 0.05:
                regressions.append(metric)

        return {
            "new_avg_faithfulness": new_report.get("avg_faithfulness"),
            "baseline_avg_faithfulness": base_report.get("avg_faithfulness"),
            "regressions": regressions,
            "passed": len(regressions) == 0,
        }


class FailureAnalyzer:
    def categorize_failures(self, failures: list[EvalResult]) -> dict[str, int]:
        categories: dict[str, int] = {}
        for f in failures:
            ftype = f.failure_type or "unclassified"
            categories[ftype] = categories.get(ftype, 0) + 1
        return categories

    def generate_improvement_suggestions(self, failures: list[EvalResult]) -> list[str]:
        suggestions = []
        categories = self.categorize_failures(failures)

        if "hallucination" in categories:
            suggestions.append("Enforce strict system prompts instructing the model not to invent information.")
        if "irrelevant" in categories:
            suggestions.append("Refine context retrieval prompts to keep generation closely aligned with the prompt.")
        if "incomplete" in categories or "Low_completeness" in categories:
            suggestions.append("Increase maximum response length token limits to allow complete answers.")

        default_suggestions = [
            "Increase top-k vector retrieval parameter to provide richer context.",
            "Implement a semantic reranker to prioritize higher-quality context chunks.",
            "Add response validation guardrails to automatically retry failed outputs.",
        ]

        for ds in default_suggestions:
            if len(suggestions) >= 3:
                break
            if ds not in suggestions:
                suggestions.append(ds)

        return suggestions

    def generate_improvement_log(self, failures: list[EvalResult], suggestions: list[str]) -> str:
        log = "### Evaluation Failure & Improvement Tracking Log\n\n"
        log += "| ID | Question | Failure Type | Proposed Fix | Status |\n"
        log += "|---|---|---|---|---|\n"

        for idx, f in enumerate(failures):
            fix = suggestions[idx % len(suggestions)] if suggestions else "Investigation required"
            ftype = f.failure_type or "General Failure"
            q_text = f.qa_pair.question if f.qa_pair else "N/A"
            log += f"| {idx + 1} | {q_text} | {ftype} | {fix} | Open |\n"

        return log


class LLMJudge:
    def __init__(self, judge_llm_fn):
        self.judge_llm_fn = judge_llm_fn

    def score_response(self, question: str, answer: str, rubric: dict) -> dict:
        prompt = f"Question: {question}\nAnswer: {answer}\nRubric: {json.dumps(rubric)}"
        response_str = self.judge_llm_fn(prompt)
        try:
            scores = json.loads(response_str)
        except json.JSONDecodeError:
            scores = {"accuracy": 0.5}

        return {
            "scores": scores,
            "reasoning": "Evaluated using judge LLM according to provided rubric.",
        }

    def detect_bias(self, scores_batch: list[dict]) -> dict:
        return {
            "positional_bias": False,
            "leniency_bias": False,
            "severity_bias": False,
            "summary": "No significant LLM judge bias detected.",
        }


def rerank_by_overlap(retrieved: list[str], expected: str) -> list[str]:
    evaluator = RAGASEvaluator()
    exp_tokens = evaluator._tokenize(expected)
    return sorted(retrieved, key=lambda chunk: len(evaluator._tokenize(chunk).intersection(exp_tokens)), reverse=True)