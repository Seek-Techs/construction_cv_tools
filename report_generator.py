from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
import os
import csv
import logging
from typing import Dict

class ReportGenerator:
    def __init__(self, logger: logging.Logger = None):
        self.logger = logger or logging.getLogger(__name__)

    def create_pdf_report(self, report: Dict, output_path: str):
        """Create a simple PDF report summarizing matches and anomalies."""
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
        except Exception:
            pass

        doc = SimpleDocTemplate(output_path, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []

        title = Paragraph("Construction CV Inspector - Analysis Report", styles['Title'])
        story.append(title)
        story.append(Spacer(1, 12))

        # Summary
        summary = report.get('summary', {})
        summary_text = Paragraph(
            f"<b>Total Matches:</b> {summary.get('total_matches', 0)} &nbsp;&nbsp;"
            f"<b>Unmatched PDF:</b> {summary.get('unmatched_pdf', 0)} &nbsp;&nbsp;"
            f"<b>Unmatched Site:</b> {summary.get('unmatched_site', 0)}",
            styles['Normal']
        )
        story.append(summary_text)
        story.append(Spacer(1, 12))

        # Anomalies
        anomalies = report.get('anomalies', {})
        anom_summary = anomalies.get('summary', {})
        anom_text = Paragraph(
            f"<b>Missing:</b> {anom_summary.get('missing_count', 0)} &nbsp;&nbsp;"
            f"<b>Extra:</b> {anom_summary.get('extra_count', 0)} &nbsp;&nbsp;"
            f"<b>Mismatches:</b> {anom_summary.get('mismatch_count', 0)}",
            styles['Normal']
        )
        story.append(anom_text)
        story.append(Spacer(1, 16))

        # Matches table (first 20 rows)
        matches = report.get('matches', [])
        if matches:
            data = [["Site Type", "Site (m)", "PDF Type", "PDF (m)", "Status", "Diff %"]]
            for m in matches[:20]:
                site = m.get('site', {})
                pdf = m.get('pdf', {})
                data.append([
                    site.get('type', ''),
                    f"{site.get('value_m', 0):.3f}",
                    pdf.get('type', ''),
                    f"{pdf.get('value_m', 0):.3f}",
                    m.get('status', ''),
                    f"{m.get('difference_percent', 0):.1f}%"
                ])

            table = Table(data, hAlign='LEFT')
            table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.grey),
                ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
                ('GRID', (0,0), (-1,-1), 0.5, colors.black),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold')
            ]))
            story.append(table)
            story.append(Spacer(1, 12))

        # Save
        doc.build(story)
        self.logger.info(f"✅ PDF report saved to: {output_path}")

    def save_report_csv(self, report: Dict, output_csv: str):
        try:
            os.makedirs(os.path.dirname(output_csv), exist_ok=True)
        except Exception:
            pass

        matches = report.get('matches', [])
        if not matches:
            self.logger.warning("⚠️ No matches to save to CSV")
            return

        fieldnames = ['site_type','site_value_m','pdf_type','pdf_value_m','status','difference_percent']
        try:
            with open(output_csv, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for m in matches:
                    site = m.get('site', {})
                    pdf = m.get('pdf', {})
                    writer.writerow({
                        'site_type': site.get('type',''),
                        'site_value_m': site.get('value_m', 0),
                        'pdf_type': pdf.get('type',''),
                        'pdf_value_m': pdf.get('value_m', 0),
                        'status': m.get('status',''),
                        'difference_percent': m.get('difference_percent', 0)
                    })
            self.logger.info(f"✅ CSV report saved to: {output_csv}")
        except Exception as e:
            self.logger.error(f"❌ Failed to save CSV: {e}")


def create_and_save_reports(report: Dict, out_dir: str = 'reports', logger: logging.Logger = None):
    rg = ReportGenerator(logger)
    pdf_path = os.path.join(out_dir, 'analysis_report.pdf')
    csv_path = os.path.join(out_dir, 'analysis_report.csv')
    rg.create_pdf_report(report, pdf_path)
    rg.save_report_csv(report, csv_path)
