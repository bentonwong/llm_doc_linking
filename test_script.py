import json
import requests
from typing import List
from pathlib import Path

API_URL = "http://localhost:8000/analyze"
DATA_PATH = Path("sample_briefs.json")


def load_briefs():
    with open(DATA_PATH, "r") as f:
        return json.load(f)


def send_brief_pair(moving_brief, response_brief, top_n=1):
    payload = {
        "moving_brief": moving_brief,
        "response_brief": response_brief,
        "top_n": top_n
    }
    response = requests.post(API_URL, json=payload)
    response.raise_for_status()
    return response.json()


def match_true_links_format(top_links):
    return [(
        link["moving_heading"],
        link["response_heading"]
    ) for link in top_links]


def evaluate(predictions, ground_truth):
    correct = 0
    total = len(ground_truth)
    matched_preds = set(predictions)
    matched_truth = set(tuple(pair) for pair in ground_truth)

    correct = len(matched_preds & matched_truth)

    accuracy = correct / total if total > 0 else 0
    return accuracy, correct, total


def main():
    data = load_briefs()
    training_pairs = [pair for pair in data if pair.get("split") == "train"]

    total_correct = 0
    total_links = 0

    for i, pair in enumerate(training_pairs):
        moving = pair["moving_brief"]
        response = pair["response_brief"]
        true_links = pair.get("true_links", [])

        result = send_brief_pair(moving, response, top_n=1)
        top_links = result["top_links"]

        predicted_pairs = match_true_links_format(top_links)
        accuracy, correct, total = evaluate(predicted_pairs, true_links)

        print(f"\n=== Pair {i+1} ===")
        print(f"Brief ID: {pair['moving_brief']['brief_id']} vs {pair['response_brief']['brief_id']}")
        print(f"Accuracy: {accuracy:.2f} ({correct}/{total})")
        for link in top_links:
            print(f"\nMatched: {link['moving_heading']} => {link['response_heading']}")
            print(f"Score: {link['score']:.4f}")

        total_correct += correct
        total_links += total

    print("\n====================")
    print(f"Overall Accuracy: {total_correct / total_links:.2f} ({total_correct}/{total_links})")


if __name__ == "__main__":
    main()
