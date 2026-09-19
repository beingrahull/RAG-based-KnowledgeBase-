import asyncio
import json
import sys
from pathlib import Path

from app.services.retrieval_service import retrieve
from eval.metrics.recall import is_hit


DATASET_PATH = Path("eval/datasets/qa.jsonl")


def load_dataset() -> list[dict]:
    if not DATASET_PATH.exists():
        raise FileNotFoundError(f"Dataset not found: {DATASET_PATH}")
    lines = DATASET_PATH.read_text(encoding="utf-8").splitlines()
    return [json.loads(line) for line in lines if line.strip()]


async def evaluate(top_k: int) -> float:
    questions = load_dataset()
    print(f"\nEvaluating {len(questions)} questions at top_k={top_k}\n")

    hits = 0
    for i, item in enumerate(questions, start=1):
        question = item["question"]
        keywords = item["expected_keywords"]

        chunks = await retrieve(question, top_k=top_k)
        hit = is_hit(chunks, keywords)
        hits += int(hit)

        marker = "HIT " if hit else "MISS"
        print(f"  [{i:02d}] {marker}  {question[:78]}")
    await asyncio.sleep(2.0) 
    recall = hits / len(questions) if questions else 0.0
    print(f"\nRecall@{top_k}: {recall:.2f}  ({hits}/{len(questions)})")
    return recall


if __name__ == "__main__":
    k = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    asyncio.run(evaluate(k))