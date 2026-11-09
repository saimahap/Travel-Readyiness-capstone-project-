import os
from datetime import datetime

class TravelReportPDF:
    """
    A standalone, pure-Python PDF 1.4 generator for BriefIQ Travel Readiness Reports.
    Generates fully compliant PDF documents without external dependency barriers.
    """
    def __init__(self, filename):
        self.filename = filename
        self.objects = []
        self.stream_commands = []
        self.page_width = 595.28   # Standard A4 width in pt
        self.page_height = 841.89  # Standard A4 height in pt

    def _rgb(self, r, g, b):
        return f"{r/255.0:.3f} {g/255.0:.3f} {b/255.0:.3f}"

    def rect(self, x, y, w, h, fill_rgb=None, stroke_rgb=None, stroke_w=1):
        cmds = []
        if stroke_rgb:
            cmds.append(f"{self._rgb(*stroke_rgb)} RG {stroke_w} w")
        if fill_rgb:
            cmds.append(f"{self._rgb(*fill_rgb)} rg")
        op = "B" if (fill_rgb and stroke_rgb) else ("f" if fill_rgb else "S")
        cmds.append(f"{x:.2f} {y:.2f} {w:.2f} {h:.2f} re {op}")
        self.stream_commands.append(" ".join(cmds))

    def line(self, x1, y1, x2, y2, stroke_rgb=(200, 200, 200), stroke_w=1):
        cmd = f"{self._rgb(*stroke_rgb)} RG {stroke_w} w {x1:.2f} {y1:.2f} m {x2:.2f} {y2:.2f} l S"
        self.stream_commands.append(cmd)

    def text(self, x, y, text_str, font="F1", size=10, fill_rgb=(30, 41, 59)):
        # Escape special PDF characters: (, ), \
        safe_text = str(text_str).replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')
        cmd = (
            f"BT "
            f"/{font} {size} Tf "
            f"{self._rgb(*fill_rgb)} rg "
            f"{x:.2f} {y:.2f} Td "
            f"({safe_text}) Tj "
            f"ET"
        )
        self.stream_commands.append(cmd)

    def wrap_text(self, text_str, max_chars=80):
        words = text_str.split(' ')
        lines = []
        curr = []
        curr_len = 0
        for w in words:
            if curr_len + len(w) + 1 <= max_chars:
                curr.append(w)
                curr_len += len(w) + 1
            else:
                lines.append(' '.join(curr))
                curr = [w]
                curr_len = len(w)
        if curr:
            lines.append(' '.join(curr))
        return lines

    def build_report(self, user_name, assessment_data, missing_items, recommendations):
        # 1. Background Header Banner (Navy Blue)
        self.rect(0, 740, self.page_width, 102, fill_rgb=(15, 23, 42))
        
        # Header Brand & Document Title
        self.text(40, 805, "BRIEFIQ - AI SUMMARY & REPORT GENERATOR", font="F2", size=15, fill_rgb=(250, 204, 21))
        self.text(40, 788, "AI-Based Pre-Travel Readiness Assessment Report", font="F2", size=12, fill_rgb=(255, 255, 255))
        self.text(40, 772, f"Document: Travel_Readiness_Report.pdf  |  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", font="F1", size=8.5, fill_rgb=(203, 213, 225))
        self.text(40, 756, f"Passenger / Traveler: {user_name}  |  Destination: {assessment_data['destination_country']}", font="F1", size=8.5, fill_rgb=(203, 213, 225))

        # Status Banner
        is_ready = 'Ready' in assessment_data['prediction_result'] and 'Not' not in assessment_data['prediction_result']
        status_bg = (220, 252, 231) if is_ready else (254, 226, 226)
        status_border = (34, 197, 94) if is_ready else (239, 68, 68)
        status_text_color = (22, 101, 52) if is_ready else (153, 27, 27)

        self.rect(40, 680, self.page_width - 80, 48, fill_rgb=status_bg, stroke_rgb=status_border, stroke_w=1.5)
        self.text(55, 708, "AI PREDICTION RESULT:", font="F2", size=10, fill_rgb=status_text_color)
        status_display = assessment_data['prediction_result'].upper()
        self.text(55, 690, f"{status_display} (Score: {assessment_data['readiness_score']} / 100)", font="F2", size=14, fill_rgb=status_text_color)

        # 2. Executive Summary Box
        self.rect(40, 565, self.page_width - 80, 105, fill_rgb=(248, 250, 252), stroke_rgb=(226, 232, 240), stroke_w=1)
        self.text(52, 652, "EXECUTIVE SUMMARY", font="F2", size=11, fill_rgb=(15, 23, 42))
        self.line(52, 646, 540, 646, stroke_rgb=(226, 232, 240))

        # Executive summary text
        dest = assessment_data['destination_country']
        t_date = assessment_data['travel_date']
        completed_cnt = 6 - len(missing_items)
        exec_text = (
            f"The traveler ({user_name}) has completed a pre-departure compliance assessment for travel to {dest} on {t_date}. "
            f"The AI Decision Tree model evaluated six essential regulatory factors and determined the overall readiness status as {assessment_data['prediction_result']}. "
            f"A total of {completed_cnt} out of 6 requirements are fully verified, leaving {len(missing_items)} pending items requiring traveler attention prior to departure."
        )
        lines = self.wrap_text(exec_text, max_chars=88)
        y_pos = 630
        for l in lines:
            self.text(52, y_pos, l, font="F1", size=8.5, fill_rgb=(51, 65, 85))
            y_pos -= 13

        # 3. Metrics & KPIs Table
        self.rect(40, 440, self.page_width - 80, 115, fill_rgb=(255, 255, 255), stroke_rgb=(226, 232, 240), stroke_w=1)
        self.text(52, 537, "METRICS & KEY PERFORMANCE INDICATORS (KPIs)", font="F2", size=11, fill_rgb=(15, 23, 42))
        self.line(52, 531, 540, 531, stroke_rgb=(226, 232, 240))

        kpis = [
            ("Total Requirements:", "6 Essential Checks", "Travel Destination:", str(assessment_data['destination_country'])),
            ("Completed Requirements:", f"{completed_cnt} Verified", "Travel Departure Date:", str(assessment_data['travel_date'])),
            ("Missing Requirements:", f"{len(missing_items)} Detected", "Return / Onward Date:", str(assessment_data['return_date'])),
            ("Readiness Score:", f"{assessment_data['readiness_score']}%", "ML Algorithm:", "Decision Tree Classifier"),
            ("Readiness Prediction:", str(assessment_data['prediction_result']), "Evaluation Status:", "Complete & Certified")
        ]
        
        k_y = 515
        for col1_lbl, col1_val, col2_lbl, col2_val in kpis:
            self.text(52, k_y, col1_lbl, font="F2", size=8, fill_rgb=(100, 116, 139))
            self.text(180, k_y, col1_val, font="F1", size=8, fill_rgb=(15, 23, 42))
            self.text(310, k_y, col2_lbl, font="F2", size=8, fill_rgb=(100, 116, 139))
            self.text(430, k_y, col2_val, font="F1", size=8, fill_rgb=(15, 23, 42))
            k_y -= 14

        # 4. Six Requirements Checklist
        self.rect(40, 270, self.page_width - 80, 160, fill_rgb=(248, 250, 252), stroke_rgb=(226, 232, 240), stroke_w=1)
        self.text(52, 412, "ESSENTIAL PRE-TRAVEL REQUIREMENTS BREAKDOWN", font="F2", size=11, fill_rgb=(15, 23, 42))
        self.line(52, 406, 540, 406, stroke_rgb=(226, 232, 240))

        factors = [
            ("1. Passport Validity (>= 6 Months)", assessment_data['passport_status'] == 'Valid'),
            ("2. Visa Availability & Status", assessment_data['visa_status'] in ['Approved', 'Visa-Free']),
            ("3. Return / Onward Flight Ticket", assessment_data['return_ticket'] == 'Yes'),
            ("4. Confirmed Hotel Accommodation", assessment_data['hotel_booking'] == 'Yes'),
            ("5. Travel Medical Insurance", assessment_data['travel_insurance'] == 'Yes'),
            ("6. Vaccination / Health Compliance", assessment_data['vaccination_status'] == 'Yes')
        ]

        f_y = 388
        for name, passed in factors:
            badge_color = (22, 163, 74) if passed else (220, 38, 38)
            status_tag = "[PASS] VERIFIED" if passed else "[FAIL] MISSING / INCOMPLETE"
            self.text(52, f_y, name, font="F1", size=8.5, fill_rgb=(30, 41, 59))
            self.text(420, f_y, status_tag, font="F2", size=8.5, fill_rgb=badge_color)
            f_y -= 18

        # 5. Recommendations Box
        self.rect(40, 95, self.page_width - 80, 165, fill_rgb=(255, 255, 255), stroke_rgb=(226, 232, 240), stroke_w=1)
        self.text(52, 242, "AI-GENERATED ACTIONABLE RECOMMENDATIONS", font="F2", size=11, fill_rgb=(15, 23, 42))
        self.line(52, 236, 540, 236, stroke_rgb=(226, 232, 240))

        rec_y = 220
        if recommendations:
            for rec in recommendations[:5]:
                bullet_lines = self.wrap_text(f"- {rec}", max_chars=88)
                for bl in bullet_lines:
                    self.text(52, rec_y, bl, font="F1", size=8, fill_rgb=(180, 83, 9))
                    rec_y -= 12
        else:
            self.text(52, rec_y, "All standard travel requirements have been successfully satisfied. Safe travels!", font="F1", size=8.5, fill_rgb=(22, 101, 52))

        # Footer
        self.line(40, 60, self.page_width - 40, 60, stroke_rgb=(203, 213, 225))
        self.text(40, 45, "Generated automatically by AI-Based Pre-Travel Readiness Prediction System", font="F1", size=7.5, fill_rgb=(148, 163, 184))
        self.text(420, 45, "B.Sc. AIML Capstone Project | BriefIQ", font="F1", size=7.5, fill_rgb=(148, 163, 184))

    def save(self):
        stream_data = "\n".join(self.stream_commands).encode('latin-1')
        stream_len = len(stream_data)

        catalog_obj = b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
        pages_obj = b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
        page_obj = (
            f"3 0 obj\n"
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {self.page_width:.2f} {self.page_height:.2f}] "
            f"/Resources << /Font << /F1 4 0 R /F2 5 0 R >> >> /Contents 6 0 R >>\n"
            f"endobj\n"
        ).encode('latin-1')
        font1_obj = b"4 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n"
        font2_obj = b"5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>\nendobj\n"
        content_obj = (
            f"6 0 obj\n<< /Length {stream_len} >>\nstream\n"
        ).encode('latin-1') + stream_data + b"\nendstream\nendobj\n"

        objects = [catalog_obj, pages_obj, page_obj, font1_obj, font2_obj, content_obj]

        header = b"%PDF-1.4\n"
        offsets = [0]
        curr_offset = len(header)
        body = b""
        for obj in objects:
            offsets.append(curr_offset)
            curr_offset += len(obj)
            body += obj

        xref = f"xref\n0 {len(offsets)}\n0000000000 65535 f \n".encode('latin-1')
        for off in offsets[1:]:
            xref += f"{off:010d} 00000 n \n".encode('latin-1')

        startxref = len(header) + len(body)
        trailer = (
            f"trailer\n"
            f"<< /Size {len(offsets)} /Root 1 0 R >>\n"
            f"startxref\n{startxref}\n%%EOF\n"
        ).encode('latin-1')

        os.makedirs(os.path.dirname(self.filename), exist_ok=True)
        with open(self.filename, 'wb') as f:
            f.write(header + body + xref + trailer)
            
        return self.filename

def generate_pdf_report(user_name, assessment_data, missing_items, recommendations, output_dir='reports'):
    os.makedirs(output_dir, exist_ok=True)
    report_filename = f"Travel_Readiness_Report_{assessment_data['assessment_id']}.pdf"
    full_path = os.path.join(output_dir, report_filename)
    
    doc = TravelReportPDF(full_path)
    doc.build_report(user_name, assessment_data, missing_items, recommendations)
    doc.save()
    return full_path

