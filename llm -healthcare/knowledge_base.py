"""
knowledge_base.py
------------------
A small, hand-curated wellness knowledge base used as the retrieval
corpus for the RAG (Retrieval-Augmented Generation) personalization layer.

In a production system this would be replaced by a much larger,
vetted collection of documents (e.g. from public health bodies such as
WHO / CDC / NHS) stored in a proper vector database (FAISS, Chroma,
Pinecone, etc.) with citation metadata.

IMPORTANT: This assistant is a *general wellness information* tool.
It is explicitly NOT a diagnostic or treatment tool. That constraint
is enforced in the persona/system prompt in llm_interface.py.
"""

KNOWLEDGE_BASE = [
    {
        "id": "sleep_1",
        "topic": "sleep",
        "text": (
            "Adults generally benefit from 7 to 9 hours of sleep per night. "
            "Consistent sleep and wake times, even on weekends, help regulate "
            "the body's circadian rhythm and improve sleep quality."
        ),
    },
    {
        "id": "sleep_2",
        "topic": "sleep",
        "text": (
            "Reducing screen exposure and bright light for 30-60 minutes before "
            "bed can help the body produce melatonin naturally, making it easier "
            "to fall asleep."
        ),
    },
    {
        "id": "nutrition_1",
        "topic": "nutrition",
        "text": (
            "A balanced plate is often built around roughly half vegetables and "
            "fruit, one quarter whole grains, and one quarter lean protein, "
            "though individual needs vary with age, activity level, and health "
            "conditions."
        ),
    },
    {
        "id": "nutrition_2",
        "topic": "nutrition",
        "text": (
            "Staying hydrated supports concentration, digestion, and energy "
            "levels. A commonly cited general guideline is about 2-3 liters of "
            "fluid per day for adults, adjusted for climate and activity."
        ),
    },
    {
        "id": "exercise_1",
        "topic": "exercise",
        "text": (
            "General physical activity guidelines suggest at least 150 minutes "
            "of moderate-intensity aerobic activity per week, plus muscle "
            "strengthening activities on two or more days per week."
        ),
    },
    {
        "id": "exercise_2",
        "topic": "exercise",
        "text": (
            "Short, frequent movement breaks during a sedentary workday - such "
            "as a 5 minute walk every hour - can help offset the effects of "
            "prolonged sitting."
        ),
    },
    {
        "id": "stress_1",
        "topic": "stress",
        "text": (
            "Slow, controlled breathing exercises (such as inhaling for 4 "
            "seconds, holding for 4, and exhaling for 6) can activate the "
            "parasympathetic nervous system and reduce feelings of acute stress."
        ),
    },
    {
        "id": "stress_2",
        "topic": "stress",
        "text": (
            "Regular physical activity, adequate sleep, and social connection "
            "are all associated with better long-term stress resilience."
        ),
    },
    {
        "id": "diabetes_general_1",
        "topic": "chronic_condition_general_info",
        "text": (
            "For people managing blood sugar levels, general wellness guidance "
            "often includes favoring high-fiber, minimally processed carbohydrates "
            "and pairing carbohydrates with protein or healthy fats to slow "
            "glucose absorption. This is general information, not individualized "
            "medical advice."
        ),
    },
    {
        "id": "mental_health_1",
        "topic": "mental_health",
        "text": (
            "Persistent low mood, loss of interest, or difficulty functioning "
            "for more than two weeks is a signal to speak with a licensed "
            "mental health professional or physician rather than relying on "
            "self-help strategies alone."
        ),
    },
]
