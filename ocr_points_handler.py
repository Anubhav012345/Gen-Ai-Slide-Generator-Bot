import os
import re
import cv2
import requests
import pytesseract

from PIL import Image
from config import BOT_TOKEN

# Auto-detect Tesseract path: Windows vs Linux (Render)
if os.name == "nt":
    pytesseract.pytesseract.tesseract_cmd = (
        r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    )


class OCRPointsHandler:

    def __init__(self, bot, group_chat_id):
        self.bot = bot
        self.group_chat_id = group_chat_id

    def preprocess(self, path):
        img = cv2.imread(path)
        img = cv2.resize(img, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
        thresh = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)[1]
        output_path = f"processed_{os.path.basename(path)}"
        cv2.imwrite(output_path, thresh)
        return output_path

    def clean_line(self, line):
        bad_chars = ["|", "©", "«", "»", "_", "~", "*"]
        for ch in bad_chars:
            line = line.replace(ch, "")
        return line.strip()

    def split_large_line(self, text, max_len=80):
        words = text.split()
        chunks = []
        current = ""
        for word in words:
            if len(current + " " + word) <= max_len:
                current += " " + word
            else:
                chunks.append(current.strip())
                current = word
        if current:
            chunks.append(current.strip())
        return chunks

    def extract_text_from_image(self, file_id):
        image_path = None
        cropped_path = None
        processed = None
        try:
            file_info = self.bot.get_file(file_id)
            file_url = (
                f"https://api.telegram.org/file/bot{BOT_TOKEN}/"
                f"{file_info.file_path}"
            )
            image_path = f"{file_id}.jpg"
            response = requests.get(file_url)
            with open(image_path, "wb") as f:
                f.write(response.content)

            img = cv2.imread(image_path)
            h, w = img.shape[:2]
            cropped = img[
                int(h * 0.10): int(h * 0.92),
                int(w * 0.20): int(w * 0.96)
            ]
            cropped_path = f"crop_{file_id}.jpg"
            cv2.imwrite(cropped_path, cropped)
            processed = self.preprocess(cropped_path)

            text = pytesseract.image_to_string(
                Image.open(processed),
                config="--oem 3 --psm 6"
            )
            return text

        except Exception as e:
            print("OCR ERROR:", e)
            return None

        finally:
            for path in [image_path, cropped_path, processed]:
                if path and os.path.exists(path):
                    try:
                        os.remove(path)
                    except Exception:
                        pass

    def parse_text_to_slides(self, full_text, topic):
        """
        Converts raw OCR text from an image into slide dicts.
        Joins broken lines, splits into slides of max 5 points each.
        """
        ignore_words = [
            "file", "edit", "format", "view", "help",
            "telegram", "slide generator", "open with",
            "comments", "notes", "protected view",
            "powerpoint", "sign in", "untitled", "notepad",
            "enable editing", "protected"
        ]

        raw_lines = full_text.split("\n")
        clean_lines = []

        for line in raw_lines:
            line = self.clean_line(line)
            if len(line) < 10:
                continue
            lower = line.lower()
            skip = any(word in lower for word in ignore_words)
            if skip:
                continue
            clean_lines.append(line)

        # Join broken lines that don't end with sentence punctuation
        joined = []
        buffer = ""
        for line in clean_lines:
            if buffer:
                buffer += " " + line
            else:
                buffer = line
            if re.search(r'[.!?]$', buffer.strip()) or len(buffer) > 150:
                joined.append(buffer.strip())
                buffer = ""
        if buffer:
            joined.append(buffer.strip())

        # Split into slides of max 5 points each
        slides = []
        points_per_slide = 5
        slide_number = 1

        for i in range(0, max(len(joined), 1), points_per_slide):
            chunk = joined[i: i + points_per_slide]
            if not chunk:
                continue
            heading = topic if slide_number == 1 else f"{topic} (cont.)"
            slides.append({"heading": heading, "points": chunk})
            slide_number += 1

        if not slides:
            slides.append({"heading": topic, "points": ["No content extracted."]})

        return slides

    def parse_markdown_to_slides(self, text, topic):
        """
        Handles both:
        - Markdown format: ## Section Heading
        - Plain text format: standalone short title lines + paragraphs
        Each section becomes its own slide(s), 4 points per slide max.
        Text is never truncated.
        """
        import re

        lines = text.splitlines()
        slides = []
        current_heading = topic
        current_points = []

        def flush(heading, points):
            chunk_size = 4
            for i in range(0, max(len(points), 1), chunk_size):
                chunk = points[i: i + chunk_size]
                if chunk:
                    label = heading if i == 0 else f"{heading} (cont.)"
                    slides.append({"heading": label, "points": chunk})

        def is_section_title(line):
            """
            Detects a standalone section title:
            - Short line (under 60 chars)
            - No sentence-ending punctuation
            - Not starting with a number followed by content
            - Not a bullet point
            """
            stripped = line.strip()
            if len(stripped) > 60:
                return False
            if stripped.endswith(('.', ',', ':', ';', '?', '!')):
                return False
            if re.match(r'^\d+\.', stripped):
                return False
            if stripped.startswith(('-', '*', '•')):
                return False
            # Must have at least 2 words to be a real heading
            if len(stripped.split()) < 2:
                return False
            return True

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Detect Markdown ## headings
            heading_match = re.match(r'^#{1,3}\s+(.*)', line)
            if heading_match:
                if current_points:
                    flush(current_heading, current_points)
                    current_points = []
                current_heading = heading_match.group(1).strip()
                continue

            # Skip very short noise
            if len(line) < 10:
                continue

            # Detect plain-text standalone title lines
            if is_section_title(line):
                if current_points:
                    flush(current_heading, current_points)
                    current_points = []
                current_heading = line
                continue

            # Regular content line — clean and add
            line = re.sub(r'\s+', ' ', line)
            current_points.append(line)

        # Flush final section
        if current_points:
            flush(current_heading, current_points)

        if not slides:
            slides.append({
                "heading": topic,
                "points": ["No content found."]
            })

        return slides

    def accumulate_points(self, extracted_data, points_list):
        if extracted_data:
            points_list.append(extracted_data)