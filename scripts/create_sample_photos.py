#!/usr/bin/env python
"""
Create realistic sample construction photos for testing
Generates a site photo with measurements and a blueprint floor plan
"""

import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import random

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils import setup_logging

logger = setup_logging('INFO')
test_dir = project_root / "test_data"
test_dir.mkdir(exist_ok=True)

print("\n" + "="*70)
print("CREATING REALISTIC SAMPLE CONSTRUCTION PHOTOS")
print("="*70 + "\n")

# ============================================================================
# CREATE SITE PHOTO (Construction site with measurements and scale reference)
# ============================================================================

print("📸 Creating site photo...")

site_img = Image.new('RGB', (1600, 1000), color=(220, 220, 220))
draw = ImageDraw.Draw(site_img)

# Try to load a font, fallback to default
try:
    title_font = ImageFont.truetype("arial.ttf", 36)
    label_font = ImageFont.truetype("arial.ttf", 32)
    small_font = ImageFont.truetype("arial.ttf", 24)
    tiny_font = ImageFont.truetype("arial.ttf", 18)
except:
    title_font = ImageFont.load_default()
    label_font = ImageFont.load_default()
    small_font = ImageFont.load_default()
    tiny_font = ImageFont.load_default()

# Draw concrete/background
draw.rectangle([0, 0, 1600, 1000], fill=(180, 175, 170))

# Draw construction elements with LARGE, CLEAR text for OCR
# External wall - left side
draw.rectangle([150, 200, 350, 800], outline=(60, 60, 60), width=12, fill=(200, 190, 180))
draw.text((200, 500), "WALL", font=label_font, fill=(0, 0, 0))

# Main structure - center
draw.rectangle([400, 100, 1100, 850], outline=(40, 40, 40), width=15, fill=(210, 205, 200))

# Window openings with CLEAR LABELS
draw.rectangle([480, 250, 620, 420], outline=(100, 150, 200), width=4, fill=(150, 180, 220))
draw.text((490, 325), "2.0m", font=label_font, fill=(255, 0, 0))  # Window height

draw.rectangle([480, 500, 620, 650], outline=(100, 150, 200), width=4, fill=(150, 180, 220))
draw.text((490, 570), "1.5m", font=label_font, fill=(255, 0, 0))  # Window 2

# Door opening
draw.rectangle([750, 750, 850, 850], outline=(139, 69, 19), width=4, fill=(180, 140, 100))
draw.text((760, 795), "1.2m", font=label_font, fill=(255, 0, 0))  # Door

# ============================================================================
# ADD LARGE MEASUREMENT ANNOTATIONS
# ============================================================================

# Top horizontal measurement - LARGE TEXT
draw.text((600, 50), "WIDTH: 5.5m", font=title_font, fill=(255, 0, 0))

# Left vertical measurement - LARGE TEXT
draw.text((50, 400), "HEIGHT: 6.0m", font=title_font, fill=(0, 0, 255))

# Additional measurements with CLEAR TEXT
draw.text((700, 300), "ROOM1", font=label_font, fill=(0, 0, 100))
draw.text((900, 300), "ROOM2", font=label_font, fill=(0, 0, 100))

# Room dimensions
draw.text((750, 450), "3.0m", font=small_font, fill=(0, 150, 0))  # Room width
draw.text((1000, 450), "2.5m", font=small_font, fill=(0, 150, 0))  # Room 2 width

# ============================================================================
# ADD SCALE REFERENCE (Large Tape Measure)
# ============================================================================

# Draw a large tape measure at the bottom (acts as scale reference)
tape_y = 920
draw.rectangle([100, tape_y - 40, 600, tape_y], fill=(255, 220, 0), outline=(200, 150, 0), width=3)
draw.text((150, tape_y - 30), "SCALE: 1m = 75px", font=label_font, fill=(0, 0, 0))

# Draw tick marks on tape
for i in range(0, 501, 50):  # Every 50 pixels = ~0.67m
    draw.line([100 + i, tape_y - 10, 100 + i, tape_y], fill=(0, 0, 0), width=2)

draw.text((100, tape_y + 5), "0m", font=small_font, fill=(0, 0, 0))
draw.text((250, tape_y + 5), "2.67m", font=small_font, fill=(0, 0, 0))
draw.text((400, tape_y + 5), "5.33m", font=small_font, fill=(0, 0, 0))

# ============================================================================
# ADD TITLE
# ============================================================================

draw.text((20, 20), "SITE PHOTO", font=title_font, fill=(0, 0, 0))

site_img.save(test_dir / "sample_site.jpg", quality=95)
logger.info(f"✅ Site photo created: {test_dir / 'sample_site.jpg'}")
logger.info(f"   Dimensions: 1600x1000")
logger.info(f"   Contains: Large clear measurements, scale reference, construction elements")

# ============================================================================
# CREATE BLUEPRINT (Floor plan with measurements)
# ============================================================================

print("\n📋 Creating blueprint...")

blueprint_img = Image.new('RGB', (1600, 1000), color=(200, 220, 245))
draw = ImageDraw.Draw(blueprint_img)

# Grid background (blueprint style)
for i in range(0, 1600, 40):
    draw.line([(i, 0), (i, 1000)], fill=(180, 200, 230), width=1)
for j in range(0, 1000, 40):
    draw.line([(0, j), (1600, j)], fill=(180, 200, 230), width=1)

# Draw title
draw.text((20, 20), "FLOOR PLAN BLUEPRINT", font=title_font, fill=(0, 0, 100))

# Draw walls (thicker lines)
draw.rectangle([150, 150, 1100, 850], outline=(0, 0, 0), width=5, fill=(240, 240, 240))

# Interior walls
draw.line([400, 150, 400, 850], fill=(0, 0, 0), width=4)  # Left interior wall
draw.line([750, 150, 750, 850], fill=(0, 0, 0), width=4)  # Right interior wall
draw.line([150, 500, 1100, 500], fill=(0, 0, 0), width=3)  # Horizontal divider

# Windows with LARGE LABELS
draw.rectangle([150, 250, 150, 370], fill=(100, 150, 220), outline=(0, 0, 0), width=2)
draw.text((120, 300), "2.0m", font=small_font, fill=(0, 0, 200))

draw.rectangle([1080, 350, 1100, 500], fill=(100, 150, 220), outline=(0, 0, 0), width=2)
draw.text((1100, 420), "1.5m", font=small_font, fill=(0, 0, 200))

# Door with CLEAR LABEL
draw.rectangle([400, 800, 500, 850], fill=(200, 170, 130), outline=(0, 0, 0), width=2)
draw.text((410, 815), "1.2m", font=small_font, fill=(0, 0, 0))

# ============================================================================
# ADD DIMENSION ANNOTATIONS (LARGE AND CLEAR)
# ============================================================================

# Top horizontal dimension
draw.text((650, 80), "WIDTH: 5.5m", font=title_font, fill=(200, 0, 0))

# Left vertical dimension
draw.text((50, 400), "HEIGHT: 6.0m", font=title_font, fill=(200, 0, 0))

# Room labels with LARGE TEXT
draw.text((280, 300), "ROOM1", font=label_font, fill=(0, 0, 100))
draw.text((550, 300), "ROOM2", font=label_font, fill=(0, 0, 100))
draw.text((900, 300), "ROOM3", font=label_font, fill=(0, 0, 100))

# Room dimensions
draw.text((320, 600), "3.0m", font=label_font, fill=(0, 100, 0))
draw.text((650, 600), "2.5m", font=label_font, fill=(0, 100, 0))
draw.text((950, 250), "1.5m", font=small_font, fill=(0, 100, 0))

# Bottom section label
draw.text((500, 700), "KITCHEN/HALL", font=label_font, fill=(0, 0, 100))

# ============================================================================
# ADD LEGEND
# ============================================================================

legend_y = 920
draw.text((200, legend_y), "LEGEND: |—| Walls  □ Windows  ⌞ Door  5.5m Dimensions", 
         font=small_font, fill=(0, 0, 0))

blueprint_img.save(test_dir / "sample_blueprint.jpg", quality=95)
logger.info(f"✅ Blueprint created: {test_dir / 'sample_blueprint.jpg'}")
logger.info(f"   Dimensions: 1600x1000")
logger.info(f"   Contains: Large clear dimensions, room labels, construction elements")

# ============================================================================
# SUMMARY
# ============================================================================

print("\n" + "="*70)
print("✅ SAMPLE PHOTOS CREATED SUCCESSFULLY")
print("="*70)
print()
print("📸 Sample Site Photo:")
print(f"   Location: {test_dir / 'sample_site.jpg'}")
print("   • Large clear measurements (OCR-friendly)")
print("   • WIDTH: 5.5m, HEIGHT: 6.0m (visible)")
print("   • Windows: 2.0m, 1.5m (marked)")
print("   • Door: 1.2m (marked)")
print("   • Scale reference: 1m = 75px")
print()
print("📋 Sample Blueprint:")
print(f"   Location: {test_dir / 'sample_blueprint.jpg'}")
print("   • Floor plan with 3 rooms")
print("   • Dimensions: WIDTH 5.5m, HEIGHT 6.0m (large text)")
print("   • Room divisions: 3.0m, 2.5m (clear)")
print("   • Windows and door marked")
print()
print("="*70)
print()


# Draw concrete/background (simulation of construction site)
draw.rectangle([0, 0, 1200, 900], fill=(200, 195, 190))

# Draw construction elements
# External wall - left side
draw.rectangle([100, 150, 300, 700], outline=(100, 100, 100), width=8, fill=(220, 210, 200))
draw.text((150, 680), "WALL 1", font=label_font, fill=(0, 0, 0))

# Main structure - center
draw.rectangle([350, 100, 900, 750], outline=(80, 80, 80), width=10, fill=(230, 225, 220))
draw.text((600, 730), "MAIN BUILDING", font=label_font, fill=(0, 0, 0))

# Window openings (left side of main structure)
draw.rectangle([420, 200, 550, 350], outline=(100, 150, 200), width=3, fill=(200, 220, 240))
draw.text((450, 360), "Window 1", font=small_font, fill=(0, 0, 100))

draw.rectangle([420, 400, 550, 550], outline=(100, 150, 200), width=3, fill=(200, 220, 240))
draw.text((450, 560), "Window 2", font=small_font, fill=(0, 0, 100))

# Door opening (center)
draw.rectangle([650, 600, 750, 750], outline=(139, 69, 19), width=3, fill=(200, 170, 140))
draw.text((660, 755), "Door", font=small_font, fill=(0, 0, 0))

# Right section
draw.rectangle([800, 200, 880, 600], outline=(100, 100, 100), width=5, fill=(210, 210, 210))
draw.text((810, 610), "Room 3", font=label_font, fill=(0, 0, 0))

# ============================================================================
# ADD MEASUREMENT ANNOTATIONS TO SITE PHOTO
# ============================================================================

# Horizontal measurements (top)
draw.line([100, 120, 300, 120], fill=(255, 0, 0), width=2)
draw.text((180, 90), "2.0m", font=label_font, fill=(255, 0, 0))

draw.line([350, 120, 900, 120], fill=(255, 0, 0), width=2)
draw.text((600, 90), "5.5m", font=label_font, fill=(255, 0, 0))

# Vertical measurements (left)
draw.line([50, 150, 50, 700], fill=(0, 0, 255), width=2)
draw.text((10, 400), "5.5m", font=label_font, fill=(0, 0, 255))

# Window measurements
draw.line([590, 200, 590, 350], fill=(255, 100, 0), width=2)
draw.text((600, 270), "1.5m", font=small_font, fill=(255, 100, 0))

draw.line([420, 370, 550, 370], fill=(255, 100, 0), width=2)
draw.text((460, 380), "1.3m", font=small_font, fill=(255, 100, 0))

# Door measurements
draw.line([750, 600, 750, 750], fill=(0, 200, 0), width=2)
draw.text((760, 670), "1.5m", font=small_font, fill=(0, 200, 0))

draw.line([650, 780, 750, 780], fill=(0, 200, 0), width=2)
draw.text((680, 790), "1.0m", font=small_font, fill=(0, 200, 0))

# ============================================================================
# ADD SCALE REFERENCE (Tape Measure)
# ============================================================================

# Draw a tape measure at the bottom (acts as scale reference)
tape_y = 850
draw.rectangle([50, tape_y - 20, 350, tape_y], fill=(255, 200, 0), outline=(200, 150, 0), width=2)
draw.text((140, tape_y - 15), "TAPE MEASURE (Reference: 1m = 60px)", font=small_font, fill=(0, 0, 0))

# Draw tick marks on tape
for i in range(0, 301, 30):  # Every 30 pixels = 0.5m
    draw.line([50 + i, tape_y - 5, 50 + i, tape_y], fill=(0, 0, 0), width=1)

draw.text((55, tape_y - 35), "0m", font=small_font, fill=(0, 0, 0))
draw.text((155, tape_y - 35), "1.67m", font=small_font, fill=(0, 0, 0))
draw.text((275, tape_y - 35), "3.33m", font=small_font, fill=(0, 0, 0))

# ============================================================================
# ADD TITLE AND INFO
# ============================================================================

draw.text((20, 20), "SITE PHOTO - CONSTRUCTION INSPECTION", font=title_font, fill=(0, 0, 0))
draw.text((20, 55), "Scale Reference: Tape measure at bottom (1m = 60 pixels)", font=small_font, fill=(100, 0, 0))

site_img.save(test_dir / "sample_site.jpg", quality=95)
logger.info(f"✅ Site photo created: {test_dir / 'sample_site.jpg'}")
logger.info(f"   Dimensions: 1200x900")
logger.info(f"   Contains: 3 walls, 2 windows, 1 door, measurements, scale reference")

# ============================================================================
# CREATE BLUEPRINT (Floor plan with measurements)
# ============================================================================

print("\n📋 Creating blueprint...")

blueprint_img = Image.new('RGB', (1200, 900), color=(220, 230, 245))  # Light blue background
draw = ImageDraw.Draw(blueprint_img)

# Draw title
draw.text((20, 20), "FLOOR PLAN BLUEPRINT", font=title_font, fill=(0, 0, 100))
draw.text((20, 55), "Scale: 1:100 (1cm = 1m)", font=small_font, fill=(0, 50, 100))

# Grid background (blueprint style)
for i in range(0, 1200, 50):
    draw.line([(i, 0), (i, 900)], fill=(200, 215, 235), width=1)
for j in range(0, 900, 50):
    draw.line([(0, j), (1200, j)], fill=(200, 215, 235), width=1)

# Draw walls (thicker lines for blueprint)
# Outer walls
draw.rectangle([100, 150, 1050, 750], outline=(0, 0, 0), width=4, fill=(250, 250, 250))

# Interior walls
draw.line([350, 150, 350, 750], fill=(0, 0, 0), width=3)  # Left interior wall
draw.line([700, 150, 700, 750], fill=(0, 0, 0), width=3)  # Right interior wall
draw.line([100, 450, 1050, 450], fill=(0, 0, 0), width=2)  # Horizontal divider

# Door opening
draw.rectangle([330, 700, 370, 750], fill=(255, 255, 255))
draw.line([330, 700, 370, 750], fill=(0, 0, 0), width=2)
draw.text((335, 760), "DOOR", font=small_font, fill=(0, 0, 0))

# Windows (shown as openings in walls)
draw.rectangle([120, 200, 120, 300], fill=(100, 150, 200), outline=(0, 0, 0), width=2)
draw.text((80, 245), "WD1", font=small_font, fill=(0, 0, 100))

draw.rectangle([1030, 300, 1030, 400], fill=(100, 150, 200), outline=(0, 0, 0), width=2)
draw.text((1040, 345), "WD2", font=small_font, fill=(0, 0, 100))

# Room labels
draw.text((200, 250), "ROOM 1", font=label_font, fill=(0, 0, 100))
draw.text((500, 250), "ROOM 2", font=label_font, fill=(0, 0, 100))
draw.text((800, 250), "ROOM 3", font=label_font, fill=(0, 0, 100))
draw.text((500, 600), "KITCHEN/HALL", font=label_font, fill=(0, 0, 100))

# ============================================================================
# ADD DIMENSION LINES AND MEASUREMENTS (Blueprint style)
# ============================================================================

# Top horizontal dimension
draw.line([100, 100, 1050, 100], fill=(200, 0, 0), width=2)
draw.line([100, 90, 100, 110], fill=(200, 0, 0), width=2)
draw.line([1050, 90, 1050, 110], fill=(200, 0, 0), width=2)
draw.text((520, 65), "5.5m", font=label_font, fill=(200, 0, 0))

# Left vertical dimension
draw.line([50, 150, 50, 750], fill=(200, 0, 0), width=2)
draw.line([40, 150, 60, 150], fill=(200, 0, 0), width=2)
draw.line([40, 750, 60, 750], fill=(200, 0, 0), width=2)
draw.text((10, 440), "6.0m", font=label_font, fill=(200, 0, 0))

# Interior divisions
draw.line([350, 130, 350, 160], fill=(50, 50, 150), width=2)
draw.text((355, 100), "2.0m", font=small_font, fill=(50, 50, 150))

draw.line([700, 130, 700, 160], fill=(50, 50, 150), width=2)
draw.text((705, 100), "1.75m", font=small_font, fill=(50, 50, 150))

# Vertical room division
draw.line([100, 450, 70, 450], fill=(50, 50, 150), width=2)
draw.text((15, 445), "3.0m", font=small_font, fill=(50, 50, 150))

# Window measurements
draw.text((85, 280), "1.5m", font=small_font, fill=(0, 0, 200))
draw.text((1000, 365), "1.3m", font=small_font, fill=(0, 0, 200))

# Door measurement
draw.text((340, 725), "1.0m", font=small_font, fill=(0, 0, 0))

# ============================================================================
# ADD LEGEND
# ============================================================================

legend_y = 800
draw.text((100, legend_y), "LEGEND:", font=small_font, fill=(0, 0, 0))
draw.line([250, legend_y + 3, 270, legend_y + 3], fill=(0, 0, 0), width=3)
draw.text((280, legend_y), "Walls", font=small_font, fill=(0, 0, 0))

draw.rectangle([450, legend_y - 3, 460, legend_y + 5], fill=(100, 150, 200), outline=(0, 0, 0), width=1)
draw.text((470, legend_y), "Windows/Doors", font=small_font, fill=(0, 0, 0))

draw.line([750, legend_y + 3, 770, legend_y + 3], fill=(200, 0, 0), width=2)
draw.text((780, legend_y), "Dimensions", font=small_font, fill=(200, 0, 0))

blueprint_img.save(test_dir / "sample_blueprint.jpg", quality=95)
logger.info(f"✅ Blueprint created: {test_dir / 'sample_blueprint.jpg'}")
logger.info(f"   Dimensions: 1200x900")
logger.info(f"   Contains: 3 rooms, 2 windows, 1 door, measurements, scale")

# ============================================================================
# SUMMARY
# ============================================================================

print("\n" + "="*70)
print("✅ SAMPLE PHOTOS CREATED SUCCESSFULLY")
print("="*70)
print()
print("📸 Sample Site Photo:")
print(f"   Location: {test_dir / 'sample_site.jpg'}")
print("   Contents:")
print("   • 3 walls with construction elements")
print("   • 2 windows (1.5m and 1.3m)")
print("   • 1 door (1.0m)")
print("   • Visible measurements (2.0m, 5.5m, 1.5m, etc.)")
print("   • Tape measure scale reference at bottom (1m = 60px)")
print()
print("📋 Sample Blueprint:")
print(f"   Location: {test_dir / 'sample_blueprint.jpg'}")
print("   Contents:")
print("   • Floor plan with 3 rooms")
print("   • 2 windows and 1 door")
print("   • Dimension annotations (5.5m, 6.0m, 1.5m, etc.)")
print("   • Blueprint-style grid background")
print("   • Legend and scale notation")
print()
print("🎯 How to Use:")
print("   1. Open web app: .\venv\Scripts\python run_app.py")
print("   2. Go to: http://localhost:5000")
print("   3. Upload:")
print(f"      • Site photo: {test_dir / 'sample_site.jpg'}")
print(f"      • Blueprint: {test_dir / 'sample_blueprint.jpg'}")
print("   4. Click 'Analyze'")
print("   5. Watch real-time progress")
print("   6. Download reports")
print()
print("="*70)
print()
