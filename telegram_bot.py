import os
import telebot
import requests
from ocr import OCRHandler
from config import BOT_TOKEN, GROUP_CHAT_ID
from ppt_generator import PPTHandler
from ocr_points_handler import OCRPointsHandler


class TelegramBot:
    def __init__(self):
        self.bot = telebot.TeleBot(BOT_TOKEN)
        self.ocr_handler = OCRHandler(self.bot, GROUP_CHAT_ID)
        self.ocr_points_handler = OCRPointsHandler(self.bot, GROUP_CHAT_ID)
        self.ppt_handler = PPTHandler()

        self.question_data = {
            "Question": [],
            "Options": [],
            "Year": [],
            "Points": []
        }

        self.presentation_settings = {
            "title": "NEXT LEVEL ACADEMY",
            "topic": "General Questions",
            "teacher_name": "Instructor",
            "ppt_type": "mcq"
        }

        self.register_handlers()

    def generate_ppt(self, chat_id):
        try:
            ppt_type = self.presentation_settings["ppt_type"]

            if ppt_type == "mcq":
                if len(self.question_data["Question"]) == 0:
                    self.bot.send_message(chat_id, "❌ No MCQ questions added yet. Send some images first.")
                    return
                output_file = self.ppt_handler.create_custom_presentation(
                    data=self.question_data,
                    title=self.presentation_settings["title"],
                    topic=self.presentation_settings["topic"],
                    teacher_name=self.presentation_settings["teacher_name"],
                )

            elif ppt_type == "points":
                if len(self.question_data["Points"]) == 0:
                    self.bot.send_message(chat_id, "❌ No points data added yet. Send images or a .txt file first.")
                    return
                output_file = self.ppt_handler.create_points_presentation(
                    points_list=self.question_data["Points"],
                    title=self.presentation_settings["title"],
                    topic=self.presentation_settings["topic"],
                    teacher_name=self.presentation_settings["teacher_name"],
                )
            else:
                self.bot.send_message(chat_id, "❌ Unknown PPT type. Use /set_type to set 'mcq' or 'points'.")
                return

            if output_file is None:
                self.bot.send_message(chat_id, "❌ Failed to generate presentation. No data found.")
                return

            with open(output_file, "rb") as f:
                self.bot.send_document(chat_id, f)

            import os as _os
            try:
                _os.remove(output_file)
            except Exception:
                pass

            self.question_data = {"Question": [], "Options": [], "Year": [], "Points": []}
            self.presentation_settings = {
                "title": "NEXT LEVEL ACADEMY",
                "topic": "General Questions",
                "teacher_name": "Instructor",
                "ppt_type": "mcq"
            }
            self.bot.send_message(chat_id, "✅ Presentation generated and sent successfully!")

        except Exception as e:
            self.bot.send_message(chat_id, f"❌ Error generating presentation: {str(e)}")

    def register_handlers(self):

        @self.bot.message_handler(commands=['start'])
        def handle_start(message):
            welcome_text = (
                "👋 Welcome to the PPT Generator Bot!\n\n"
                "📋 Commands:\n"
                "/set_title - Set the presentation title\n"
                "/set_topic - Set the topic\n"
                "/set_teacher - Set the teacher's name\n"
                "/set_type - Set PPT type (mcq or points)\n"
                "/status - Check current settings\n\n"
                "📸 Send images OR 📄 send a .txt/.md file to add content\n"
                "✅ Send 'nextlevel' to generate the presentation"
            )
            self.bot.reply_to(message, welcome_text)

        @self.bot.message_handler(commands=['set_title'])
        def handle_set_title(message):
            self.bot.send_message(message.chat.id, "Please enter the presentation title:")
            self.bot.register_next_step_handler(message, self.save_title)

        @self.bot.message_handler(commands=['set_topic'])
        def handle_set_topic(message):
            self.bot.send_message(message.chat.id, "Please enter the topic name:")
            self.bot.register_next_step_handler(message, self.save_topic)

        @self.bot.message_handler(commands=['set_teacher'])
        def handle_set_teacher(message):
            self.bot.send_message(message.chat.id, "Please enter the teacher's name:")
            self.bot.register_next_step_handler(message, self.save_teacher)

        @self.bot.message_handler(commands=['set_type'])
        def handle_set_type(message):
            self.bot.send_message(message.chat.id, "Please enter PPT type (mcq or points):")
            self.bot.register_next_step_handler(message, self.save_type)

        @self.bot.message_handler(commands=['status'])
        def handle_status(message):
            status = (
                f"⚙️ Current Settings:\n"
                f"Title: {self.presentation_settings['title']}\n"
                f"Topic: {self.presentation_settings['topic']}\n"
                f"Teacher: {self.presentation_settings['teacher_name']}\n"
                f"Type: {self.presentation_settings['ppt_type'].upper()}\n\n"
                f"📊 Data:\n"
                f"Questions: {len(self.question_data['Question'])}\n"
                f"Points slides: {len(self.question_data['Points'])}"
            )
            self.bot.reply_to(message, status)

        # ── PHOTO handler ──────────────────────────────────────────────
        @self.bot.message_handler(content_types=['photo'])
        def handle_photo(message):
            try:
                photo = message.photo[-1]
                file_id = photo.file_id
                self.bot.send_message(message.chat.id, "📸 Image received. Processing...")

                if self.presentation_settings["ppt_type"] == "mcq":
                    extracted_text = self.ocr_handler.extract_text_from_image(file_id)
                    if extracted_text:
                        self.ocr_handler.accumulate_questions(extracted_text, self.question_data)
                        self.bot.send_message(
                            message.chat.id,
                            f"✅ Questions extracted! Total: {len(self.question_data['Question'])}"
                        )
                    else:
                        self.bot.send_message(message.chat.id, "⚠️ No questions detected in this image.")

                elif self.presentation_settings["ppt_type"] == "points":
                    topic = self.presentation_settings["topic"]
                    raw_text = self.ocr_points_handler.extract_text_from_image(file_id)
                    if raw_text:
                        slides = self.ocr_points_handler.parse_text_to_slides(raw_text, topic)
                        self.question_data["Points"].extend(slides)
                        self.bot.send_message(
                            message.chat.id,
                            f"✅ Extracted {len(slides)} slide(s) from image!\n"
                            f"Total slides ready: {len(self.question_data['Points'])}"
                        )
                    else:
                        self.bot.send_message(message.chat.id, "⚠️ No text detected in this image.")

            except Exception as e:
                self.bot.send_message(message.chat.id, f"❌ Error processing image: {str(e)}")

        # ── DOCUMENT handler (.txt / .md files) ───────────────────────
        @self.bot.message_handler(content_types=['document'])
        def handle_document(message):
            try:
                doc = message.document
                file_name = doc.file_name or ""
                ext = file_name.lower().split(".")[-1]

                if ext not in ("txt", "md"):
                    self.bot.send_message(
                        message.chat.id,
                        "⚠️ Only .txt or .md files are supported for points mode.\n"
                        "For MCQ images, send as a photo."
                    )
                    return

                if self.presentation_settings["ppt_type"] != "points":
                    self.bot.send_message(
                        message.chat.id,
                        "⚠️ Text files only work in 'points' mode.\n"
                        "Use /set_type and enter: points"
                    )
                    return

                self.bot.send_message(message.chat.id, "📄 File received. Processing...")

                # Download file
                file_info = self.bot.get_file(doc.file_id)
                file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_info.file_path}"
                response = requests.get(file_url)
                response.raise_for_status()

                # Decode text
                raw_text = response.content.decode("utf-8", errors="ignore")

                topic = self.presentation_settings["topic"]
                slides = self.ocr_points_handler.parse_markdown_to_slides(raw_text, topic)
                self.question_data["Points"].extend(slides)

                self.bot.send_message(
                    message.chat.id,
                    f"✅ File processed! Created {len(slides)} slide(s).\n"
                    f"Total slides ready: {len(self.question_data['Points'])}\n\n"
                    f"Send 'nextlevel' to generate the presentation."
                )

            except Exception as e:
                self.bot.send_message(message.chat.id, f"❌ Error processing file: {str(e)}")

        @self.bot.message_handler(func=lambda msg: msg.text and msg.text.lower() == "nextlevel")
        def handle_nextlevel(message):
            self.bot.send_message(message.chat.id, "⏳ Generating your presentation...")
            self.generate_ppt(message.chat.id)

    def save_title(self, message):
        self.presentation_settings["title"] = message.text.strip()
        self.bot.send_message(message.chat.id, f"✅ Title set: {self.presentation_settings['title']}")

    def save_topic(self, message):
        self.presentation_settings["topic"] = message.text.strip()
        self.bot.send_message(message.chat.id, f"✅ Topic set: {self.presentation_settings['topic']}")

    def save_teacher(self, message):
        self.presentation_settings["teacher_name"] = message.text.strip()
        self.bot.send_message(message.chat.id, f"✅ Teacher set: {self.presentation_settings['teacher_name']}")

    def save_type(self, message):
        ppt_type = message.text.strip().lower()
        if ppt_type not in ["mcq", "points"]:
            self.bot.send_message(message.chat.id, "❌ Invalid type. Please enter 'mcq' or 'points'.")
            return
        self.presentation_settings["ppt_type"] = ppt_type
        self.bot.send_message(message.chat.id, f"✅ PPT type set: {ppt_type.upper()}")

    def _download_file(self, save_path, file_path):
        file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
        with open(save_path, "wb") as f:
            f.write(requests.get(file_url).content)

    def start(self):
        print("🚀 Starting Gen-AI Slide Generator Bot...")
        self.bot.polling(none_stop=True)