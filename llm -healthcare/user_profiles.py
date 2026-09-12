"""
user_profiles.py
-----------------
Sample user profiles representing the "personalization layer" input.
In a real deployment these would come from onboarding forms, wearable
device data, or prior conversation history (stored with the user's
consent, per privacy requirements discussed in the report).
"""

USER_PROFILES = {
    "athlete_23": {
        "name": "Aarav",
        "age_group": "18-25",
        "goal": "improve athletic performance and recovery",
        "tone_preference": "energetic, concise, uses fitness terminology",
        "relevant_topics": ["exercise", "nutrition", "sleep"],
    },
    "office_worker_stressed": {
        "name": "Meera",
        "age_group": "35-45",
        "goal": "manage work-related stress and improve sleep",
        "tone_preference": "calm, supportive, non-clinical",
        "relevant_topics": ["stress", "sleep", "mental_health"],
    },
    "senior_diabetic_caregiver": {
        "name": "Ramesh",
        "age_group": "60+",
        "goal": "understand general wellness info for managing blood sugar",
        "tone_preference": "simple language, extra clarity, gentle disclaimers",
        "relevant_topics": ["chronic_condition_general_info", "nutrition"],
    },
}
