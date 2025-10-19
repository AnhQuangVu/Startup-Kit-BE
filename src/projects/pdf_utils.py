from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import Color, HexColor
import os
from src.projects.schemas import ProjectRead
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.lib.enums import TA_LEFT


def wrap_text(c, text, x, y, max_width, font_name, font_size, line_height=12):
    """Tự động xuống dòng text để không bị tràn"""
    if not text:
        return y

    c.setFont(font_name, font_size)
    words = str(text).split()
    lines = []
    current_line = ""

    for word in words:
        test_line = current_line + word + " "
        text_width = c.stringWidth(test_line, font_name, font_size)

        if text_width <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line.strip())
            current_line = word + " "

    if current_line:
        lines.append(current_line.strip())

    for line in lines:
        c.drawString(x, y, line)
        y -= line_height

    return y


def create_project_pdf(project: ProjectRead, output_path: str, watermark_path: str):
    # Đăng ký font Unicode hỗ trợ tiếng Việt
    font_path = os.path.join("static", "ttf", "DejaVuSerif.ttf")
    font_bold_path = os.path.join("static", "ttf", "DejaVuSerif-Bold.ttf")
    if not os.path.exists(font_path):
        raise FileNotFoundError(f"Font file not found: {font_path}")
    pdfmetrics.registerFont(TTFont("DejaVuSerif", font_path))
    if os.path.exists(font_bold_path):
        pdfmetrics.registerFont(TTFont("DejaVuSerif-Bold", font_bold_path))
        bold_font = "DejaVuSerif-Bold"
    else:
        bold_font = "DejaVuSerif"

    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4

    # Thêm logo nhỏ ở góc trên bên trái
    logo_path = os.path.join("static", "logo.png")
    if os.path.exists(logo_path):
        c.drawImage(logo_path, 30, height - 70, width=50, height=50, mask='auto')

    # Vẽ ảnh chìm (watermark)
    if os.path.exists(watermark_path):
        watermark = ImageReader(watermark_path)
        c.saveState()
        c.translate(width / 2, height / 2)
        c.rotate(30)
        c.setFillAlpha(0.1)
        c.drawImage(watermark, -200, -200, width=400, height=400, mask='auto')
        c.restoreState()

    # Ghi thông tin project
    y = height - 50
    c.setFont(bold_font, 16)
    c.drawString(100, y, f"Project: {project.name}")
    y -= 30
    c.setFont("DejaVuSerif", 13)
    fields = [
        ("Tagline", project.tagline),
        ("Stage", getattr(project.stage, 'value', str(project.stage))),
        ("Description", project.description),
        ("Industry", project.industry),
        ("Pain Point", project.pain_point),
        ("Solution", project.solution),
        ("Product", project.product),
        ("Customer Segment", project.customer_segment),
        ("Customer Features", project.customer_features),
        ("Market Size", project.market_size),
        ("Market Area", project.market_area),
        ("Business Model", project.business_model),
        ("Revenue Method", project.revenue_method),
        ("Distribution Channel", project.distribution_channel),
        ("Partners", project.partners),
        ("Cost Estimate", project.cost_estimate),
        ("Capital Source", project.capital_source),
        ("Revenue Goal", project.revenue_goal),
        ("Member Count", project.member_count),
        ("Member Skills", project.member_skills),
        ("Resources", project.resources),
        ("Deployment Location", project.deployment_location),
        ("Website", project.website_url),
        ("Use AI", str(project.use_ai)),
    ]
    for label, value in fields:
        if value:
            c.drawString(50, y, f"{label}: {value}")
            y -= 20
            if y < 80:
                c.showPage()
                y = height - 50
                if os.path.exists(logo_path):
                    c.drawImage(logo_path, 30, height - 70, width=50, height=50, mask='auto')
                c.setFont("DejaVuSerif", 13)

    # --- Thêm trang Lean Canvas ---
    bmc_section = None
    if hasattr(project, 'sections'):
        for section in project.sections:
            if getattr(section, 'type', None) == "BUSINESS_MODEL_CANVAS":
                bmc_section = section
                break

    if bmc_section and bmc_section.content:
        table = bmc_section.content["table"] if isinstance(bmc_section.content,
                                                           dict) and "table" in bmc_section.content else bmc_section.content
        block_map = {row["block"]: row["value"] for row in table}

        # Tạo trang mới với landscape
        c.showPage()
        c.setPageSize(landscape(A4))
        page_width, page_height = landscape(A4)

        # Màu sắc
        border_color = HexColor("#999999")
        title_color = HexColor("#333333")
        subtitle_color = HexColor("#666666")

        # Thiết lập vùng vẽ
        margin = 25
        canvas_width = page_width - 2 * margin
        canvas_height = page_height - 110
        top = page_height - 50
        left = margin

        # --- Lean Canvas layout: Professional, Centered UVP ---
        # Kích thước và vị trí các block
        margin = 25
        page_width, page_height = landscape(A4)
        canvas_width = page_width - 2 * margin
        canvas_height = page_height - 110
        top = page_height - 50
        left = margin

        # Chiều cao các hàng
        row1_h = canvas_height * 0.36
        row2_h = canvas_height * 0.18
        row3_h = canvas_height * 0.22
        gap = 6  # khoảng cách giữa các block

        # Chiều rộng các cột
        col_w = canvas_width / 6
        uvp_w = col_w * 2
        cost_w = canvas_width / 2
        revenue_w = canvas_width / 2

        def draw_lean_cell(x, y, w, h, title, subtitle, content):
            """Vẽ một ô Lean Canvas với border và nội dung"""
            # Vẽ border
            c.setStrokeColor(border_color)
            c.setLineWidth(0.8)
            c.rect(x, y, w, h, fill=0, stroke=1)

            # Vẽ tiêu đề
            c.setFillColor(title_color)
            c.setFont(bold_font, 10)
            title_y = y + h - 15
            c.drawString(x + 6, title_y, title)

            # Vẽ subtitle nếu có
            content_start_y = title_y - 12
            if subtitle:
                c.setFont("DejaVuSerif", 7)
                c.setFillColor(subtitle_color)
                # Wrap subtitle
                sub_lines = subtitle.split('\n')
                for i, sub_line in enumerate(sub_lines):
                    if i > 2:  # Giới hạn 3 dòng subtitle
                        break
                    c.drawString(x + 6, content_start_y - i * 9, sub_line)
                content_start_y -= (len(sub_lines[:3]) * 9 + 5)

            # Vẽ nội dung
            if content:
                c.setFillColor(HexColor("#000000"))
                c.setFont("DejaVuSerif", 8)

                # Tính toán không gian còn lại
                available_height = content_start_y - y - 8
                line_height = 10
                max_lines = int(available_height / line_height)

                # Xử lý nội dung
                lines = str(content).split('\n')
                content_y = content_start_y
                lines_drawn = 0

                for line in lines:
                    if lines_drawn >= max_lines:
                        break

                    line = line.strip()
                    if not line:
                        continue

                    # Tính độ rộng tối đa cho text (trừ padding)
                    max_width = w - 16

                    # Wrap dòng dài
                    words = line.split()
                    current_line = ""

                    for word in words:
                        test_line = current_line + word + " "
                        if c.stringWidth(test_line, "DejaVuSerif", 8) <= max_width:
                            current_line = test_line
                        else:
                            if current_line:
                                c.drawString(x + 8, content_y, current_line.strip())
                                content_y -= line_height
                                lines_drawn += 1
                                if lines_drawn >= max_lines:
                                    break
                            current_line = word + " "

                    if current_line and lines_drawn < max_lines:
                        c.drawString(x + 8, content_y, current_line.strip())
                        content_y -= line_height
                        lines_drawn += 1

        # HÀNG 1: Problem | Solution | Unique Value Proposition (2 col) | Unfair Advantage | Customer Segments
        y1 = top
        x = left
        draw_lean_cell(x, y1 - row1_h, col_w, row1_h, "Problem", "Top 3 problems", block_map.get("Problem", ""))
        draw_lean_cell(x + col_w + gap, y1 - row1_h, col_w, row1_h, "Solution", "Top 3 features", block_map.get("Solution", ""))
        draw_lean_cell(x + 2*col_w + 2*gap, y1 - row1_h, uvp_w - gap, row1_h, "Unique Value Proposition", "Single, clear, compelling message that states why you are different and worth buying", block_map.get("Unique Value Proposition", ""))
        draw_lean_cell(x + 4*col_w + 3*gap, y1 - row1_h, col_w, row1_h, "Unfair Advantage", "Can't be easily copied or bought", block_map.get("Unfair Advantage", ""))
        draw_lean_cell(x + 5*col_w + 4*gap, y1 - row1_h, col_w, row1_h, "Customer Segments", "Target customers", block_map.get("Customer Segments", ""))

        # HÀNG 2: Existing Alternatives | Key Metrics | High-Level Concept | Channels | Early Adopters
        y2 = y1 - row1_h - gap
        draw_lean_cell(x, y2 - row2_h, col_w, row2_h, "Existing Alternatives", "", block_map.get("Existing Alternatives", ""))
        draw_lean_cell(x + col_w + gap, y2 - row2_h, col_w, row2_h, "Key Metrics", "Key activities you measure", block_map.get("Key Metrics", ""))
        draw_lean_cell(x + 2*col_w + 2*gap, y2 - row2_h, uvp_w - gap, row2_h, "High-Level Concept", "", block_map.get("High-Level Concept", ""))
        draw_lean_cell(x + 4*col_w + 3*gap, y2 - row2_h, col_w, row2_h, "Channels", "Path to customers", block_map.get("Channels", ""))
        draw_lean_cell(x + 5*col_w + 4*gap, y2 - row2_h, col_w, row2_h, "Early Adopters", "", block_map.get("Early Adopters", ""))

        # HÀNG 3: Cost Structure | Revenue Streams
        y3 = y2 - row2_h - gap
        draw_lean_cell(x, y3 - row3_h, cost_w - gap//2, row3_h, "Cost Structure", "Customer acquisition costs, Distribution costs, Hosting, People, etc.", block_map.get("Cost Structure", ""))
        draw_lean_cell(x + cost_w + gap//2, y3 - row3_h, revenue_w - gap//2, row3_h, "Revenue Streams", "Revenue model, Life time value, Revenue, Gross margin", block_map.get("Revenue Streams", ""))

        # Footer
        c.setFont("DejaVuSerif", 7)
        c.setFillColor(subtitle_color)
        footer_y = y3 - row3_h - 12
        c.drawString(left, footer_y, "Lean Canvas - Startup Kit")

    c.save()

# Hướng dẫn sử dụng:
# from src.projects.pdf_utils import create_project_pdf
# create_project_pdf(project, "output.pdf", "static/logo.png")