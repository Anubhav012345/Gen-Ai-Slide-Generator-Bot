import cv2
import os
import requests
import datetime
import pytesseract

from PIL import Image
from dotenv import load_dotenv
from validate_data import get_single_question_data

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_CHAT_ID = os.getenv("GROUP_CHAT_ID")

if os.name == "nt":
    pytesseract.pytesseract.tesseract_cmd = (
        r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    )


class OCRHandler:

    def __init__(self, bot, group_chat_id):
        self.bot = bot
        self.group_chat_id = group_chat_id

    def preprocess_image(self, image_path):
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        img = cv2.resize(img, (1400, 1400))
        img = cv2.GaussianBlur(img, (3, 3), 0)
        _, img = cv2.threshold(
            img, 0, 255,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )
        processed_path = "processed_" + image_path
        cv2.imwrite(processed_path, img)
        return processed_path

    def clean_text(self, text):
        bad_words = [
            "telegram", "slide generator", "open with",
            "protected view", "powerpoint", "comments",
            "notes", "file", "edit", "format", "view", "help"
        ]
        lines = text.split("\n")
        clean_lines = []
        for line in lines:
            line = line.strip()
            if len(line) < 3:
                continue
            lower = line.lower()
            skip = any(word in lower for word in bad_words)
            if not skip:
                clean_lines.append(line)
        return "\n".join(clean_lines)

    def extract_text_from_image(self, file_id):
        local_file_path = None
        processed_path = None
        try:
            file_info = self.bot.get_file(file_id)
            file_url = (
                f"https://api.telegram.org/file/bot"
                f"{BOT_TOKEN}/{file_info.file_path}"
            )
            local_file_path = (
                f"temp_image_"
                f"{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
            )
            response = requests.get(file_url, stream=True)
            response.raise_for_status()
            with open(local_file_path, "wb") as f:
                f.write(response.content)

            processed_path = self.preprocess_image(local_file_path)

            extracted_text = pytesseract.image_to_string(
                Image.open(processed_path),
                config="--oem 3 --psm 6"
            )
            extracted_text = self.clean_text(extracted_text)

            if extracted_text.strip():
                return extracted_text

            raise ValueError("No text detected in image.")

        except Exception as e:
            error_message = f"Error during OCR processing: {str(e)}"
            print(error_message)
            self.bot.send_message(self.group_chat_id, error_message)
            return ""

        finally:
            for path in [local_file_path, processed_path]:
                if path and os.path.exists(path):
                    try:
                        os.remove(path)
                    except Exception:
                        pass

    def accumulate_questions(self, extracted_text, question_data):
        try:
            questions_data = get_single_question_data(extracted_text)
            question_data["Question"].extend(questions_data["Question"])
            question_data["Options"].extend(questions_data["Options"])
        except Exception as e:
            print(f"Error accumulating questions: {e}")
            self.bot.send_message(
                self.group_chat_id,
                f"Error processing extracted data: {e}"
            )