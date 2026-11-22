#Now create the translation service named translator.py.
from google import genai
from pydantic import BaseModel

class TranslatedSegment(BaseModel):
    start: float
    end: float
    telugu_text: str

class TranslationBatch(BaseModel):
    segments: list[TranslatedSegment]

def translate_to_simple_telugu(segments: list[dict], api_key: str) -> list[TranslatedSegment]:
    client = genai.Client(api_key=api_key)
    system_instruction = (
        "You are an expert Telugu dialogue writer. Translate the provided timestamped English/Hindi "
        "transcript segments into natural, everyday conversational Telugu (Vyavaharika Bhasha). "
        "STRICT RULES:\n"
        "1. Use simple, commonly spoken Telugu words that an ordinary person uses daily.\n"
        "2. Strictly AVOID complex, archaic, or heavy Sanskrit-derived words (Granthika / tough Tatsama terms). "
        "For example, use 'వాడండి' instead of 'వినియోగించండి', 'సాయం' instead of 'సహకారం', 'మొదలుపెట్టు' instead of 'ప్రారంభించు'.\n"
        "3. Keep common English technical/modern nouns transliterated in Telugu script if natural in speech (e.g., 'ఫోన్', 'వీడియో', 'లింక్').\n"
        "4. Match syllable count and phrasing length closely to each segment's start/end duration so dubbed audio stays synchronized."
    )
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"Translate these segments to simple spoken Telugu:\n{segments}",
        config={
            "system_instruction": system_instruction,
            "response_mime_type": "application/json",
            "response_schema": TranslationBatch,
        },
    )
    return response.parsed.segments
