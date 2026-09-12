"""
llm_interface.py
-----------------
This module is the "customization layer" of the application. It builds
a persona-conditioned, retrieval-augmented prompt and sends it to the
base LLM.

Two customization techniques are combined here (see report for full
discussion):
  1. System-prompt / persona design  -> SYSTEM_PERSONA + per-user tone
  2. Few-shot prompting              -> FEW_SHOT_EXAMPLES
  3. Retrieval-Augmented Generation  -> retrieved_docs injected as context

--------------------------------------------------------------------
NOTE ON RUNNING MODE
--------------------------------------------------------------------
This sandbox has no internet access and no API key configured, so a real
call to GPT-4 / Gemini / Llama cannot be executed here. `generate_response()`
therefore supports two modes:

  mode="api"     -> builds the exact request that would be sent to a real
                     LLM API (OpenAI-compatible chat completion). The
                     request is constructed and shown, but not executed
                     in this offline environment.

  mode="offline" -> a small deterministic templated generator that
                     mimics how the LLM would combine persona + retrieved
                     context, so the personalization behavior can still be
                     demonstrated end-to-end without network access.

To run this for real, set mode="api" and provide an API key/base model
(see the commented `call_openai_api` function below) - no other code
needs to change, because the rest of the pipeline (retrieval, persona,
prompt assembly) is identical either way. This is the key point of the
architecture: the personalization layer is model-agnostic.
"""

import json

SYSTEM_PERSONA = """You are WellBuddy, a supportive general-wellness information \
assistant. You are NOT a doctor and you never diagnose, prescribe, or replace \
professional medical care. You answer using only the CONTEXT provided to you. \
If the user's question suggests a medical emergency or a serious/persistent \
symptom, you gently recommend they consult a licensed healthcare professional. \
You adapt your tone and level of detail to the user's stated profile."""

FEW_SHOT_EXAMPLES = [
    {
        "user": "I've been feeling tired every afternoon, any tips?",
        "assistant": (
            "A few gentle things that often help with afternoon energy dips: "
            "keeping a consistent sleep schedule, staying hydrated, and taking "
            "a short walk after lunch instead of sitting straight through. If "
            "the tiredness is persistent or severe, it's worth mentioning to a "
            "doctor, since it can have several different causes."
        ),
    }
]


def build_prompt(query, profile, retrieved_docs):
    """Assemble the final prompt sent to the LLM (personalization layer output)."""
    context_block = "\n".join(f"- {d['text']}" for d in retrieved_docs) or "(no matching context found)"

    persona_line = (
        f"User profile: name={profile.get('name')}, "
        f"age_group={profile.get('age_group')}, "
        f"goal={profile.get('goal')}, "
        f"tone_preference={profile.get('tone_preference')}."
    ) if profile else "User profile: none provided (generic user)."

    few_shot_block = "\n".join(
        f'Example -\nUser: {ex["user"]}\nAssistant: {ex["assistant"]}'
        for ex in FEW_SHOT_EXAMPLES
    )

    prompt = f"""SYSTEM:
{SYSTEM_PERSONA}

{persona_line}

FEW-SHOT EXAMPLES:
{few_shot_block}

RETRIEVED CONTEXT (use only this for facts):
{context_block}

USER QUESTION:
{query}

Respond in a tone matching the user's tone_preference, personalize the answer to their stated goal, and cite the ideas from the retrieved context in your own words.
"""
    return prompt


def call_openai_api(prompt):
    """
    Reference implementation for real API use (NOT executed in this sandbox
    - no network access / API key available here).

    import requests
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {API_KEY}"},
        json={
            "model": "gpt-4o-mini",
            "messages": [{"role": "system", "content": prompt}],
            "temperature": 0.5,
        },
    )
    return response.json()["choices"][0]["message"]["content"]
    """
    raise NotImplementedError("No network access in this environment - see docstring.")


def _offline_generate(query, profile, retrieved_docs):
    """
    Deterministic, template-based stand-in for the LLM's generation step.
    Combines persona tone + retrieved facts, purely so the full pipeline
    can be demonstrated without a live API call.
    """
    if not retrieved_docs:
        body = (
            "I don't have specific information on that in my current knowledge "
            "base. For anything specific to your health, please check with a "
            "healthcare professional."
        )
    else:
        facts = " ".join(d["text"] for d in retrieved_docs)
        body = facts

    if not profile:
        # Generic, non-personalized tone
        return f"Here is some general wellness information: {body}"

    tone = profile.get("tone_preference", "")
    name = profile.get("name", "there")
    goal = profile.get("goal", "your wellness goals")

    if "energetic" in tone:
        opener = f"Hey {name}! Great question for someone working on {goal}."
        closer = "Keep pushing - small consistent habits compound fast!"
    elif "calm" in tone or "supportive" in tone:
        opener = f"Hi {name}, thanks for asking - this is a really common concern."
        closer = "Be gentle with yourself as you work on this."
    elif "simple" in tone or "gentle" in tone:
        opener = f"Hello {name}. Here is a simple explanation."
        closer = (
            "As always, please check with your doctor before changing anything "
            "related to a medical condition."
        )
    else:
        opener = f"Hi {name},"
        closer = ""

    return f"{opener} {body} {closer}".strip()


def generate_response(query, profile, retrieved_docs, mode="offline"):
    prompt = build_prompt(query, profile, retrieved_docs)

    if mode == "api":

        text = call_openai_api(prompt)
    else:
        text = _offline_generate(query, profile, retrieved_docs)

    return {"prompt_sent": prompt, "response": text}


def generate_generic_response(query, retrieved_docs):
    """Baseline, non-personalized response (no persona, no profile) for comparison."""
    return generate_response(query, profile=None, retrieved_docs=retrieved_docs, mode="offline")
