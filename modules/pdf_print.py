from fpdf import FPDF
import json

# # Sample JSON data
# json_data = '''
# {
#     "title": "Monthly Sales Report",
#     "date": "2025-01-01",
#     "author": "John Doe",
#     "summary": "This report summarizes the sales performance for the month.",
#     "sales_data": [
#         {"region": "North", "sales": 15000, "target": 20000},
#         {"region": "South", "sales": 12000, "target": 15000},
#         {"region": "East", "sales": 18000, "target": 18000},
#         {"region": "West", "sales": 10000, "target": 12000}
#     ]
# }
# '''
#
# # Load JSON data
# data = json.loads(json_data)

# Initialize FPDF object
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, data['title'], 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

pdf = PDF()
pdf.add_page()

# Add Report Metadata
pdf.set_font('Arial', '', 12)
pdf.cell(0, 10, f"Author: {data['author']}", 0, 1)
pdf.cell(0, 10, f"Date: {data['date']}", 0, 1)
pdf.ln(10)

# Add Summary
pdf.set_font('Arial', 'B', 12)
pdf.cell(0, 10, "Summary:", 0, 1)
pdf.set_font('Arial', '', 12)
pdf.multi_cell(0, 10, data['summary'])
pdf.ln(10)

# Add Sales Data
pdf.set_font('Arial', 'B', 12)
pdf.cell(0, 10, "Sales Data:", 0, 1)
pdf.set_font('Arial', '', 12)

# Table Headers
pdf.set_fill_color(200, 220, 255)
pdf.cell(60, 10, "Region", 1, 0, 'C', 1)
pdf.cell(60, 10, "Sales", 1, 0, 'C', 1)
pdf.cell(60, 10, "Target", 1, 1, 'C', 1)

# Table Rows
for row in data['sales_data']:
    pdf.cell(60, 10, row['region'], 1, 0, 'C')
    pdf.cell(60, 10, str(row['sales']), 1, 0, 'C')
    pdf.cell(60, 10, str(row['target']), 1, 1, 'C')

# Save PDF
output_file = "Sales_Report.pdf"
pdf.output(output_file)

print(f"PDF report generated and saved as {output_file}.")
