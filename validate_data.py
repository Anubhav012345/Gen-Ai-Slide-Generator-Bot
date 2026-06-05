import re
import json
from google import genai
from config import GEMINI_API_KEY

client = genai.Client(api_key=GEMINI_API_KEY)


def clean_json_response(formatted_data):
    formatted_data = formatted_data.strip("`").strip()
    formatted_data = formatted_data.replace("```json", "").replace("```", "").strip()
    json_match = re.search(r'(\[\s*\{[\s\S]*?\}\s*\])', formatted_data, re.UNICODE)
    if json_match:
        json_content = json_match.group(1).strip()
        try:
            return json.loads(json_content)
        except json.JSONDecodeError as e:
            print(f"JSON Parsing Error: {e}")
            return None
    else:
        print("No valid JSON detected in response.")
        return None


def get_single_question_data(extracted_text, max_retries=3):
    all_data = {
        "Question": [],
        "Options": [],
    }

    prompt = (
        "Extract all MCQ questions from the following text. "
        "Return ONLY a JSON array in this exact format, no extra text:\n"
        "[\n"
        "  {\n"
        "    \"Question\": \"Full question text here\",\n"
        "    \"Options\": [\"(a) option\", \"(b) option\", \"(c) option\", \"(d) option\"]\n"
        "  }\n"
        "]\n\n"
        f"Text:\n{extracted_text}"
    )

    attempts = 0
    while attempts < max_retries:
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt
            )
            formatted_data = response.text
            cleaned_data = clean_json_response(formatted_data)

            if not cleaned_data:
                attempts += 1
                continue

            for question_data in cleaned_data:
                all_data["Question"].append(question_data.get("Question", ""))
                all_data["Options"].append(question_data.get("Options", []))

            break

        except Exception as e:
            print(f"Error attempt {attempts + 1}: {e}")
            attempts += 1

    return all_data
