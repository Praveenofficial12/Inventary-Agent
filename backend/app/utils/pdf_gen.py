from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

def generate_inventory_pdf(report_data: dict) -> io.BytesIO:
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, height - 50, report_data.get("title", "Inventory Report"))
    
    p.setFont("Helvetica", 12)
    y = height - 80
    p.drawString(100, y, f"Summary: {report_data.get('summary', '')[:80]}...")
    
    y -= 30
    metrics = report_data.get("key_metrics", {})
    p.drawString(100, y, f"Total Value: ${metrics.get('total_value', 0)}")
    p.drawString(300, y, f"Low Stock Items: {metrics.get('low_stock_count', 0)}")
    
    y -= 50
    for section in report_data.get("sections", []):
        if y < 100:
            p.showPage()
            p.setFont("Helvetica-Bold", 14)
            y = height - 50
        else:
            p.setFont("Helvetica-Bold", 14)
            y -= 20
            p.drawString(100, y, section.get("heading", ""))
            p.setFont("Helvetica", 10)
            y -= 15
            p.drawString(100, y, section.get("content", "")[:90])
            y -= 20

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer
