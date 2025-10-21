from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import HexColor
import os
from src.projects.schemas import ProjectRead
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


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

        # Normalize keys for more robust lookup (case-insensitive, trimmed)
        normalized = {k.lower().strip(): v for k, v in block_map.items()}

        def get_block(*aliases):
            for a in aliases:
                key = a.lower().strip()
                if key in normalized:
                    return normalized[key]
            return ""

        # Start a new page for the canvas and set to landscape A4
        c.showPage()
        c.setPageSize(landscape(A4))
        page_width, page_height = landscape(A4)

        # Colors
        border_color = HexColor("#999999")
        title_color = HexColor("#333333")
        subtitle_color = HexColor("#666666")

        # Layout margins and drawing area
        margin = 22
        gap = 6  # gap between columns/rows
        left = margin
        right = page_width - margin
        top = page_height - margin
        bottom = margin
        canvas_width = right - left
        canvas_height = top - bottom

        # Compute unit width for a 6-column grid where UVP spans two units
        unit_w = (canvas_width - gap * 5) / 6.0

        # Column x positions
        col_x = [left + i * (unit_w + gap) for i in range(6)]

        # Column widths (single unit); UVP will span two units
        col_w = unit_w
        uvp_w = unit_w * 2 + gap

        # Row heights (three rows) - tuned so content fits comfortably on a single page
        row1_h = canvas_height * 0.48
        row2_h = canvas_height * 0.30
        row3_h = canvas_height * 0.20

        # Small helper to draw text wrapped inside a width/height area
        def draw_wrapped_text(x, y_top, w, h, text, font_name="DejaVuSerif", font_size=8, leading=10, left_padding=6):
            if not text:
                return
            c.setFont(font_name, font_size)
            available_width = w - left_padding - 6
            # build words
            lines = []
            for paragraph in str(text).split('\n'):
                words = paragraph.split()
                if not words:
                    lines.append("")
                    continue
                cur = words[0]
                for word in words[1:]:
                    test = cur + ' ' + word
                    if c.stringWidth(test, font_name, font_size) <= available_width:
                        cur = test
                    else:
                        lines.append(cur)
                        cur = word
                lines.append(cur)

            max_lines = int((h - 6) / leading)
            y = y_top
            drawn = 0
            for line in lines:
                if drawn >= max_lines:
                    break
                c.drawString(x + left_padding, y, line)
                y -= leading
                drawn += 1

        def draw_lean_cell(x, y, w, h, title, subtitle, content):
            """Draw a cell with title/subtitle/content. Coordinates: x,y is bottom-left."""
            # Outer border
            c.setStrokeColor(border_color)
            c.setLineWidth(0.8)
            c.rect(x, y, w, h, fill=0, stroke=1)

            # Title
            title_y = y + h - 12
            c.setFillColor(title_color)
            c.setFont(bold_font, 10)
            c.drawString(x + 6, title_y, title)

            # Subtitle (small)
            sub_start_y = title_y - 12
            if subtitle:
                c.setFont("DejaVuSerif", 7)
                c.setFillColor(subtitle_color)
                # wrap subtitle to max 3 lines
                sub_lines = []
                for p in str(subtitle).split('\n'):
                    words = p.split()
                    cur = ''
                    for wword in words:
                        test = (cur + ' ' + wword).strip()
                        if c.stringWidth(test, "DejaVuSerif", 7) <= w - 12:
                            cur = test
                        else:
                            sub_lines.append(cur)
                            cur = wword
                    if cur:
                        sub_lines.append(cur)
                for i, sl in enumerate(sub_lines[:3]):
                    c.drawString(x + 6, sub_start_y - i * 9, sl)
                content_start_y = sub_start_y - (len(sub_lines[:3]) * 9 + 6)
            else:
                content_start_y = sub_start_y

            # Content area
            content_h = content_start_y - (y + 6)
            if content_h > 8 and content:
                c.setFillColor(HexColor("#000000"))
                # use slightly smaller font for dense cells
                draw_wrapped_text(x, content_start_y, w, content_h, content, font_name="DejaVuSerif", font_size=8, leading=9)

        # Fetch blocks with common alias names (support different naming)
        P = get_block('Problem', 'Problems', 'Problems/Needs')
        S = get_block('Solution', 'Solutions')
        UVP = get_block('Unique Value Proposition', 'Unique Value', 'Value Proposition', 'UVP')
        UA = get_block('Unfair Advantage', 'Unfair Advantage/Edge')
        CS = get_block('Customer Segments', 'Customers', 'Customer Segment')

        EA = get_block('Existing Alternatives', 'Existing Alternatives/Competitors', 'Alternatives')
        KM = get_block('Key Metrics', 'Key Metrics/Measures')
        HLC = get_block('High-Level Concept', 'High-Level Concept/Concept')
        CH = get_block('Channels', 'Distribution Channel', 'Channel')
        EA2 = get_block('Early Adopters', 'Early Adopter', 'Initial Users')

        COST = get_block('Cost Structure', 'Costs', 'Cost')
        REV = get_block('Revenue Streams', 'Revenue', 'Revenue Model')

        # Row 1: Problem | Solution | UVP (2 units) | Unfair Advantage | Customer Segments
        y1_bottom = top - row1_h
        # Problem
        draw_lean_cell(col_x[0], y1_bottom, col_w, row1_h, "Problem", "Top 3 problems", P)
        # Solution
        draw_lean_cell(col_x[1], y1_bottom, col_w, row1_h, "Solution", "Top 3 features", S)
        # UVP spans columns 2 and 3
        draw_lean_cell(col_x[2], y1_bottom, uvp_w, row1_h, "Unique Value Proposition", "Single, clear, compelling message that states why you are different and worth buying", UVP)
        # Unfair Advantage (column 4)
        draw_lean_cell(col_x[4], y1_bottom, col_w, row1_h, "Unfair Advantage", "Can't be easily copied or bought", UA)
        # Customer Segments (column 5)
        draw_lean_cell(col_x[5], y1_bottom, col_w, row1_h, "Customer Segments", "Target customers", CS)

        # Row 2: Existing Alternatives | Key Metrics | High-Level Concept (spans 2 units) | Channels | Early Adopters
        y2_bottom = y1_bottom - gap - row2_h
        draw_lean_cell(col_x[0], y2_bottom, col_w, row2_h, "Existing Alternatives", "", EA)
        draw_lean_cell(col_x[1], y2_bottom, col_w, row2_h, "Key Metrics", "Key activities you measure", KM)
        draw_lean_cell(col_x[2], y2_bottom, uvp_w, row2_h, "High-Level Concept", "", HLC)
        draw_lean_cell(col_x[4], y2_bottom, col_w, row2_h, "Channels", "Path to customers", CH)
        draw_lean_cell(col_x[5], y2_bottom, col_w, row2_h, "Early Adopters", "", EA2)

        # Row 3: Cost Structure | Revenue Streams (each half width)
        y3_bottom = y2_bottom - gap - row3_h
        half_w = (canvas_width - gap) / 2.0
        draw_lean_cell(left, y3_bottom, half_w, row3_h, "Cost Structure", "Customer acquisition costs, Distribution costs, Hosting, People, etc.", COST)
        draw_lean_cell(left + half_w + gap, y3_bottom, half_w, row3_h, "Revenue Streams", "Revenue model, Life time value, Revenue, Gross margin", REV)

        # Footer
        c.setFont("DejaVuSerif", 7)
        c.setFillColor(subtitle_color)
        footer_y = y3_bottom - 12
        c.drawString(left, footer_y, "Lean Canvas - Startup Kit")

    c.save()

# Hướng dẫn sử dụng:
# from src.projects.pdf_utils import create_project_pdf
# create_project_pdf(project, "output.pdf", "static/logo.png")