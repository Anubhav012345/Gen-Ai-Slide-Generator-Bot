import cv2
import easyocr
import os
import requests
import datetime
from config import BOT_TOKEN, GROUP_CHAT_ID
from validate_data import get_single_question_data


class OCRHandler:
    def __init__(self, bot, group_chat_id):
        self.bot = bot
        self.group_chat_id = group_chat_id
        self.reader = easyocr.Reader(['en', 'hi'])

    def preprocess_image(self, image_path):
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        img = cv2.resize(img, (1080, 1080))
        img = cv2.GaussianBlur(img, (5, 5), 0)
        _, img = cv2.threshold(img, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        processed_path = "processed_" + image_path
        cv2.imwrite(processed_path, img)
        return processed_path

    def extract_text_from_image(self, file_id):
        local_file_path = None
        processed_path = None
        try:
            file_info = self.bot.get_file(file_id)
            file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_info.file_path}"
            local_file_path = f"temp_image_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"

            response = requests.get(file_url, stream=True)
            response.raise_for_status()
            with open(local_file_path, "wb") as f:
                f.write(response.content)

            processed_path = self.preprocess_image(local_file_path)

            # Use EasyOCR instead of OpenAI Vision
            results = self.reader.readtext(processed_path, detail=0)
            extracted_text = "\n".join(results)

            if extracted_text.strip():
                return extracted_text
            else:
                raise ValueError("No text detected in the image.")

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
            self.bot.send_message(self.group_chat_id, f"Error processing extracted data: {e}")
