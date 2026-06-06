import os
import cv2
import requests
import pytesseract

from PIL import Image
from config import BOT_TOKEN


pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)


class OCRPointsHandler:

    def __init__(self, bot, group_chat_id):

        self.bot = bot
        self.group_chat_id = group_chat_id

    def preprocess(self, path):

        img = cv2.imread(path)

        # upscale image
        img = cv2.resize(
            img,
            None,
            fx=3,
            fy=3,
            interpolation=cv2.INTER_CUBIC
        )

        # grayscale
        gray = cv2.cvtColor(
            img,
            cv2.COLOR_BGR2GRAY
        )

        # denoise
        gray = cv2.fastNlMeansDenoising(
            gray,
            None,
            10,
            7,
            21
        )

        # threshold
        thresh = cv2.threshold(
            gray,
            180,
            255,
            cv2.THRESH_BINARY
        )[1]

        output_path = (
            f"processed_{os.path.basename(path)}"
        )

        cv2.imwrite(output_path, thresh)

        return output_path

    def clean_line(self, line):

        bad_chars = [
            "|",
            "©",
            "«",
            "»",
            "_",
            "~",
            "*"
        ]

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

            # crop main slide area only
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

            os.remove(image_path)
            os.remove(cropped_path)
            os.remove(processed)

            raw_lines = text.split("\n")

            ignore_words = [
                "file",
                "edit",
                "format",
                "view",
                "help",
                "telegram",
                "slide generator",
                "open with",
                "comments",
                "notes",
                "protected view",
                "powerpoint",
                "sign in",
                "untitled",
                "notepad"
            ]

            lines = []

            for line in raw_lines:

                line = self.clean_line(line)

                if len(line) < 15:
                    continue

                lower = line.lower()

                skip = False

                for word in ignore_words:

                    if word in lower:
                        skip = True
                        break

                if skip:
                    continue

                if len(line) > 120:

                    split_lines = self.split_large_line(
                        line,
                        80
                    )

                    lines.extend(split_lines)

                else:
                    lines.append(line)

            if not lines:
                return None

            heading = "Topic"

            points = []

            for line in lines:

                lower = line.lower()

                if (
                    "covid" in lower
                    or "impact" in lower
                    or "introduction" in lower
                    or "#" in line
                ):

                    heading = line.replace("#", "").strip()

                    continue

                if len(points) >= 5:
                    break

                points.append(line)

            return {
                "heading": heading,
                "points": points
            }

        except Exception as e:

            print("OCR ERROR:", e)

            return None

    def accumulate_points(self, extracted_data, points_list):

        if extracted_data:
            points_list.append(extracted_data)

    def parse_markdown_to_slides(self, text, topic):
        """
        Parses Markdown-formatted text (## headings + paragraphs)
        into clean slide dicts. Each ## section becomes its own slide(s).
        Long sections automatically overflow to additional slides.
        """
        import re

        lines = text.splitlines()
        slides = []

        current_heading = topic
        current_points = []

        def flush(heading, points):
            """Split accumulated points into slides of 4 each."""
            chunk_size = 4
            for i in range(0, max(len(points), 1), chunk_size):
                chunk = points[i: i + chunk_size]
                if chunk:
                    label = heading if i == 0 else f"{heading} (cont.)"
                    slides.append({"heading": label, "points": chunk})

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Detect Markdown headings: # Title  or  ## Section
            heading_match = re.match(r'^#{1,3}\s+(.*)', line)
            if heading_match:
                # Save previous section
                if current_points:
                    flush(current_heading, current_points)
                    current_points = []
                current_heading = heading_match.group(1).strip()
                continue

            # Skip very short noise lines
            if len(line) < 15:
                continue

            # Clean up line
            line = re.sub(r'\s+', ' ', line)
            current_points.append(line)

        # Flush last section
        if current_points:
            flush(current_heading, current_points)

        if not slides:
            slides.append({"heading": topic, "points": ["No content found."]})

        return slides