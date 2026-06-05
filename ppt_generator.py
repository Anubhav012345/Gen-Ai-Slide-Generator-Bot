from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import MSO_AUTO_SIZE


class PPTHandler:

    def __init__(self):
        pass

    def set_background(self, slide):

        fill = slide.background.fill

        fill.solid()

        fill.fore_color.rgb = RGBColor(0, 0, 0)

    def create_title_slide(
        self,
        prs,
        title,
        topic,
        teacher_name
    ):

        slide = prs.slides.add_slide(
            prs.slide_layouts[6]
        )

        self.set_background(slide)

        textbox = slide.shapes.add_textbox(
            Inches(1),
            Inches(2),
            Inches(10),
            Inches(2)
        )

        tf = textbox.text_frame

        tf.word_wrap = True

        p = tf.paragraphs[0]

        p.text = title

        p.font.size = Pt(28)
        p.font.bold = True
        p.font.color.rgb = RGBColor(255, 255, 0)

        p2 = tf.add_paragraph()

        p2.text = f"Topic: {topic}"

        p2.font.size = Pt(20)
        p2.font.color.rgb = RGBColor(255, 255, 255)

        p3 = tf.add_paragraph()

        p3.text = f"By: {teacher_name}"

        p3.font.size = Pt(16)
        p3.font.color.rgb = RGBColor(200, 200, 200)

    def add_content_slide(
        self,
        prs,
        heading,
        points
    ):

        slide = prs.slides.add_slide(
            prs.slide_layouts[6]
        )

        self.set_background(slide)

        # heading
        heading_box = slide.shapes.add_textbox(
            Inches(0.5),
            Inches(0.3),
            Inches(12),
            Inches(0.7)
        )

        ht = heading_box.text_frame

        hp = ht.paragraphs[0]

        hp.text = heading

        hp.font.size = Pt(22)
        hp.font.bold = True
        hp.font.color.rgb = RGBColor(255, 255, 0)

        # content
        content_box = slide.shapes.add_textbox(
            Inches(0.6),
            Inches(1.1),
            Inches(11.6),
            Inches(5.4)
        )

        tf = content_box.text_frame

        tf.word_wrap = True

        tf.auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE

        clean_points = []

        for pt in points:

            pt = pt.strip()

            if len(pt) < 8:
                continue

            if len(pt) > 90:
                pt = pt[:90] + "..."

            clean_points.append(pt)

        clean_points = clean_points[:5]

        for idx, pt in enumerate(clean_points):

            if idx == 0:
                p = tf.paragraphs[0]
            else:
                p = tf.add_paragraph()

            p.text = f"• {pt}"

            p.font.size = Pt(18)
            p.font.color.rgb = RGBColor(255, 255, 255)

            p.space_after = Pt(10)

    def create_points_presentation(
        self,
        points_list,
        title,
        topic,
        teacher_name
    ):

        prs = Presentation()

        prs.slide_width = Inches(13.33)
        prs.slide_height = Inches(7.5)

        self.create_title_slide(
            prs,
            title,
            topic,
            teacher_name
        )

        for item in points_list:

            heading = item.get(
                "heading",
                "Topic"
            )

            points = item.get(
                "points",
                []
            )

            self.add_content_slide(
                prs,
                heading,
                points
            )

        output_file = (
            f"{topic.replace(' ', '_')}_points.pptx"
        )

        prs.save(output_file)

        return output_file