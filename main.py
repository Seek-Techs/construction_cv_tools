from pdf_processor import PDFProcessor
from site_comparator import SiteComparator
from utils import load_config, setup_logging

config = load_config()
logger = setup_logging(config['log_level'])

print("\n" + "="*60)
print("🏗️  CONSTRUCTION CV INSPECTOR - PHASES 1-3")
print("="*60)

# PDF part
print("\n📄 PHASE 0: PDF Processing (Current)")
print("-" * 60)
pdf_proc = PDFProcessor(config)
images = pdf_proc.convert_pdf_to_images()
for img in images:
    pdf_proc.detect_lines(img)
    measurements = pdf_proc.read_measurements(img)
    pdf_proc.calculate_quantities(measurements)

# Site part with Phase 1, 2, & 3
print("\n📸 PHASE 1: Reference Scale Detection (Implemented)")
print("-" * 60)
print("Automatic detection of scale references (tape measure, brick, ruler)")
print("Ensures accurate pixel-to-meter conversions for all measurements")

print("\n📊 PHASE 2: Better Measurement Extraction (Implemented)")
print("-" * 60)
print("Advanced OCR preprocessing and measurement parsing")
print("Extracts dimensions from both PDFs and site photos")
print("Supports multiple units and measurement types")

print("\n🔗 PHASE 3: Smart Element Matching (NEW)")
print("-" * 60)
print("Intelligent matching of site measurements to PDF elements")
print("Three-pass matching: type → proximity → value-based")
print("Anomaly detection and relationship inference")

comparator = SiteComparator(config, logger)

# Example: Complete Phase 1-3 workflow
site_photo = 'site_photo.jpg'
pdf_photo = 'blueprint.jpg'

print(f"\n🔄 Running complete Phase 1-3 analysis...")
print(f"   Site: {site_photo}")
print(f"   PDF: {pdf_photo}")

# Phase 3: Match and analyze (includes 1 and 2)
report = comparator.match_and_analyze(site_photo, pdf_photo)

if report:
    print(f"\n✅ Phase 3 Complete - Report Generated")
    print(f"   Matches: {report['summary']['total_matches']}")
    print(f"   Missing: {report['anomalies']['summary']['missing_count']}")
    print(f"   Extra: {report['anomalies']['summary']['extra_count']}")
    print(f"   Mismatches: {report['anomalies']['summary']['mismatch_count']}")
    
    # Save report
    comparator.element_matcher.save_report(report, 'analysis_report.json')
    print(f"   Report: analysis_report.json")

print("\n" + "="*60)
print("✨ Phases 1-3 Implementation Complete!")
print("="*60 + "\n")
 
print("\n📄 PHASE 4: Report Generation (NEW)")
print("-" * 60)
print("If Phase 3 produced a report, PDF/CSV will be saved under the 'reports' folder")

print("\n🔁 Running full match_and_analyze (will also generate report if possible)")
report = comparator.match_and_analyze(site_photo, pdf_photo)
print(f"\n✅ Report generated (if dependencies installed). Summary: {report['summary'] if report else 'No report'}")