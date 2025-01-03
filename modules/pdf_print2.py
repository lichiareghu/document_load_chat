from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)  # Set the font first
        self.cell(200, 10, ln=True)
        self.cell(0, 10, "ESG Report", 0, 1, 'C')  # Add title in header
        self.ln(10)  # Line break

    def chapter_title(self, chapter, title):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, f"{chapter}. {title}", 0, 1, 'L')
        self.ln(5)

    def subchapter_title(self, subchapter, title):
        self.set_font('Arial', 'B', 11)
        self.cell(0, 10, f"{subchapter}. {title}", 0, 1, 'L')
        self.ln(5)

    def question(self, subsubchapter, question):
        self.set_font('Arial', 'I', 10)
        self.cell(0, 10, f"{subsubchapter}. {question}", 0, 1, 'L')
        self.ln(5)

    def content(self, text):
        self.set_font('Arial', '', 10)
        self.multi_cell(0, 10, text)
        self.ln(10)


# # Example dynamic data structure
# report_data = {
#     "1": {
#         "title": "Introduction",
#         "content": "Include a brief introduction about the company, its mission, and its key operational areas."
#     },
#     "2": {
#         "title": "[Category Name]",
#         "subsections": {
#             "2.1": {
#                 "title": "[ESRS Standard]",
#                 "content": "The ESRS (European Sustainability Reporting Standards) aim to provide a clear framework for organizations to disclose their sustainability performance and impacts in alignment with European regulations.",
#                 "questions": {
#                     "2.1.1": {
#                         "question": "[Question]",
#                         "content": "Findings: Provide detailed findings about the company related to this question. This should include at least 50 words to ensure depth and clarity. Highlight significant insights and context."
#                     }
#                 }
#             },
#             "2.2": {
#                 "title": "[ESRS Standard]",
#                 "content": "The ESRS (European Sustainability Reporting Standards) aim to provide a clear framework for organizations to disclose their sustainability performance and impacts in alignment with European regulations.",
#                 "questions": {
#                     "2.2.1": {
#                         "question": "[Question]",
#                         "content": "Findings: Provide detailed findings about the company related to this question. This should include at least 50 words to ensure depth and clarity. Highlight significant insights and context."
#                     }
#                 }
#             }
#         }
#     }
# }

# # Generate PDF dynamically
# pdf = PDF()
# pdf.add_page()
#
# for chapter, chapter_data in report_data.items():
#     pdf.chapter_title(chapter, chapter_data['title'])
#     if 'content' in chapter_data:
#         pdf.content(chapter_data['content'])
#
#     if 'subsections' in chapter_data:
#         for subsection, subsection_data in chapter_data['subsections'].items():
#             pdf.subchapter_title(subsection, subsection_data['title'])
#             pdf.content(subsection_data['content'])
#
#             if 'questions' in subsection_data:
#                 for subsubsection, question_data in subsection_data['questions'].items():
#                     pdf.question(subsubsection, question_data['question'])
#                     pdf.content(question_data['content'])
#
# # Save PDF
# pdf.output("dynamic_report.pdf")
# print("Dynamic PDF has been created as 'dynamic_report.pdf'.")
