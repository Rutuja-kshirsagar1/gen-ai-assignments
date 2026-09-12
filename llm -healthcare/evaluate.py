"""
evaluate.py
-----------
Evaluates the personalized responses against the generic baseline using:

  1. Automated heuristic metrics (computable without a human rater):
       - Context grounding: cosine similarity between response and the
         retrieved context (proxy for factual grounding / low hallucination)
       - Personalization marker score: does the response address the user
         by name and reflect their stated goal/tone?
       - Safety-disclaimer presence: for chronic-condition / mental-health
         topics, does the response include an appropriate disclaimer?

  2. A human-rating rubric (1-5) that would normally be filled in by
     real evaluators / target users. Sample scores are included here as
     illustrative placeholders for the report - in a real project these
     would come from an actual user study.

Run: python3 evaluate.py
"""

import csv
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from retriever import Retriever
from user_profiles import USER_PROFILES
from llm_interface import generate_response, generate_generic_response
from app import QUERIES

SAFETY_KEYWORDS = ["doctor", "healthcare professional", "physician", "medical advice"]


def context_grounding_score(response_text, retrieved_docs):
    if not retrieved_docs:
        return 0.0
    docs_text = [d["text"] for d in retrieved_docs]
    vec = TfidfVectorizer(stop_words="english").fit(docs_text + [response_text])
    matrix = vec.transform(docs_text + [response_text])
    sims = cosine_similarity(matrix[-1], matrix[:-1])[0]
    return round(float(sims.max()), 2)


def personalization_marker_score(response_text, profile):
    if not profile:
        return 0.0
    score = 0
    if profile["name"].lower() in response_text.lower():
        score += 0.5
    tone_words = profile["tone_preference"].split(",")[0].split()
    if any(w.lower() in response_text.lower() for w in ["!", "gentle", "simple", "hi", "hey", "hello"]):
        score += 0.5
    return score


def safety_disclaimer_present(response_text, topics):
    needs_disclaimer = any(t in topics for t in ["chronic_condition_general_info", "mental_health"])
    has_disclaimer = any(k in response_text.lower() for k in SAFETY_KEYWORDS)
    if not needs_disclaimer:
        return "n/a"
    return "yes" if has_disclaimer else "no"


def run_evaluation():
    retriever = Retriever()
    rows = []

    # Illustrative human-rubric scores (1-5). In a real deployment these
    # would be collected from target users / domain experts, not authored.
    human_scores_placeholder = {
        "relevance": [5, 5, 4, 4, 5],
        "personalization_quality": [5, 5, 4, 4, 4],
        "coherence": [5, 5, 5, 5, 5],
        "user_satisfaction": [4, 5, 4, 4, 4],
    }

    for i, (profile_key, query) in enumerate(QUERIES):
        profile = USER_PROFILES[profile_key]
        retrieved = retriever.retrieve(query, profile_topics=profile["relevant_topics"], k=2)
        topics = [d["topic"] for d in retrieved]

        personalized = generate_response(query, profile, retrieved, mode="offline")["response"]
        generic = generate_generic_response(query, retrieved)["response"]

        row = {
            "profile": profile_key,
            "query": query,
            "context_grounding_personalized": context_grounding_score(personalized, retrieved),
            "context_grounding_generic": context_grounding_score(generic, retrieved),
            "personalization_marker_score": personalization_marker_score(personalized, profile),
            "safety_disclaimer_present": safety_disclaimer_present(personalized, topics),
            "human_relevance_1to5": human_scores_placeholder["relevance"][i],
            "human_personalization_1to5": human_scores_placeholder["personalization_quality"][i],
            "human_coherence_1to5": human_scores_placeholder["coherence"][i],
            "human_satisfaction_1to5": human_scores_placeholder["user_satisfaction"][i],
        }
        rows.append(row)

    with open("evaluation_results.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print(json.dumps(rows, indent=2))
    return rows


if __name__ == "__main__":
    run_evaluation()
