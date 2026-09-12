"""
app.py
------
End-to-end demo of the pipeline:

    user input -> personalization layer (profile + RAG retrieval)
              -> LLM (generate_response)
              -> generated response

Run: python3 app.py
Produces sample_interactions.txt used in the report.
"""

import json
from retriever import Retriever
from user_profiles import USER_PROFILES
from llm_interface import generate_response, generate_generic_response

QUERIES = [
    ("athlete_23", "What should I eat to recover better after training?"),
    ("athlete_23", "How much should I sleep to perform at my best?"),
    ("office_worker_stressed", "I feel really stressed at work, what can I do?"),
    ("office_worker_stressed", "I'm having trouble sleeping lately."),
    ("senior_diabetic_caregiver", "What kind of food is good for managing blood sugar?"),
]


def run_demo():
    retriever = Retriever()
    output_lines = []

    for profile_key, query in QUERIES:
        profile = USER_PROFILES[profile_key]
        retrieved = retriever.retrieve(query, profile_topics=profile["relevant_topics"], k=2)

        personalized = generate_response(query, profile, retrieved, mode="offline")
        generic = generate_generic_response(query, retrieved)

        block = []
        block.append("=" * 80)
        block.append(f"USER PROFILE: {profile_key}  ({profile['name']}, goal: {profile['goal']})")
        block.append(f"QUERY: {query}")
        block.append("-" * 80)
        block.append("RETRIEVED CONTEXT:")
        for d in retrieved:
            block.append(f"  [{d['id']}] {d['text']}")
        block.append("-" * 80)
        block.append("GENERIC (non-personalized) RESPONSE:")
        block.append(f"  {generic['response']}")
        block.append("-" * 80)
        block.append("PERSONALIZED RESPONSE:")
        block.append(f"  {personalized['response']}")
        block.append("")
        output_lines.extend(block)
        print("\n".join(block))

    with open("sample_interactions.txt", "w") as f:
        f.write("\n".join(output_lines))


if __name__ == "__main__":
    run_demo()
