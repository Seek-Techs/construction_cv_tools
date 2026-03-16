# Testing Guide: Real Construction Photo Analysis

## Quick Start (3 steps)

### Step 1: Start the Web App
```bash
cd c:\Users\Admin\Documents\Python project\2026\construction_cv_tool
.\venv\Scripts\python scripts\run_web_app.py
```

### Step 2: Open Browser
Navigate to: **http://localhost:5000**

### Step 3: Upload Photos
- Upload a **site photo** (construction site image)
- Upload a **blueprint** (floor plan, reference photo, or PDF)
- Click "Analyze"
- Watch real-time progress
- Download PDF/CSV reports

---

## Testing Scenarios

### Scenario 1: Sample Construction Photos (Included)
**What You'll See:**
- Automatic scale detection from reference objects
- Measurement extraction from photos
- Element matching between site and blueprint
- Professional PDF and CSV reports

**How to Test:**
```bash
# Photos are generated automatically in test_data/
# sample_site.jpg
# sample_blueprint.jpg

# Upload via web interface or use test script:
.\venv\Scripts\python scripts\test_with_real_photos.py
```

### Scenario 2: Real Construction Photos
**What to Upload:**
1. **Site Photo**: Photo of construction work with measurements visible
   - Can include tape measure, ruler, or brick for scale
   - Should show construction elements clearly
   - JPG/PNG format

2. **Blueprint**: Reference floor plan or blueprint
   - Original blueprint, floor plan, or design drawing
   - Should show same area as site photo
   - PDF, JPG, or PNG format

**Expected Results:**
- Phase 1: Auto-detect scale from reference objects
- Phase 2: Extract all visible measurements (meters, feet, cm, etc.)
- Phase 3: Match site measurements to blueprint elements
- Phase 4: Generate professional reports
- Phase 5: Real-time progress tracking in web UI

### Scenario 3: Testing Without OCR (Tesseract)
If Tesseract is not installed, the system still works:
- ✅ Scale detection (works)
- ⚠️ Measurement extraction (falls back to default values)
- ✅ Element matching (works)
- ✅ Report generation (works)
- ✅ Web interface (works)

**To Install Tesseract:**
1. Download: https://github.com/UB-Mannheim/tesseract/wiki
2. Run installer
3. Restart terminal/VS Code

---

## Web Interface Guide

### Upload Section
```
📸 UPLOAD CONSTRUCTION PHOTOS
┌─────────────────────────────────────────┐
│ 📄 Select Site Photo (JPG, PNG)         │
│ 📄 Select Blueprint (JPG, PNG, PDF)     │
│                                         │
│  [ANALYZE]                              │
└─────────────────────────────────────────┘
```

### Real-Time Monitoring
```
🔄 ACTIVE TASKS
┌─────────────────────────────────────────┐
│ Task ID: abc123de-f456-7890             │
│ Status:  ⏳ PROCESSING                  │
│ Progress: ▓▓▓▓░░░░░░ 40%                │
│                                         │
│ Phase 1: ✅ Scale Detection             │
│ Phase 2: ⏳ Measurement Extraction      │
│ Phase 3: ⏳ Element Matching             │
│ Phase 4: ⏳ Report Generation           │
│                                         │
│ Time: 2.3s                              │
└─────────────────────────────────────────┘
```

### Reports Section
```
📊 AVAILABLE REPORTS
┌─────────────────────────────────────────┐
│ analysis_report_20260215_123456.pdf ⬇️  │
│ analysis_report_20260215_123456.csv ⬇️  │
│ analysis_report_20260215_120000.pdf ⬇️  │
│ analysis_report_20260215_120000.csv ⬇️  │
└─────────────────────────────────────────┘
```

---

## API Endpoints (For Developers)

### Upload Analysis
```bash
curl -F "sitePhoto=@site.jpg" \
     -F "pdfPhoto=@blueprint.pdf" \
     http://localhost:5000/upload
```

**Response:**
```json
{
  "task_id": "abc123de-f456-7890",
  "status": "queued",
  "message": "Analysis queued"
}
```

### Check Task Status
```bash
curl http://localhost:5000/tasks/abc123de-f456-7890
```

**Response:**
```json
{
  "task_id": "abc123de-f456-7890",
  "job_type": "analyze_photos",
  "status": "completed",
  "progress": 100,
  "result": {
    "pdf_report": "analysis_report_20260215_123456.pdf",
    "csv_report": "analysis_report_20260215_123456.csv"
  }
}
```

### List All Tasks
```bash
curl http://localhost:5000/tasks
```

### Download Report
```bash
curl -O http://localhost:5000/reports/analysis_report_20260215_123456.pdf
```

### Health Check
```bash
curl http://localhost:5000/health
```

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'tesseract'"
**Solution:**
- Install Tesseract (see above)
- Or just proceed - system works without it (measurements use defaults)

### Issue: "Port 5000 already in use"
**Solution:**
```bash
# Find and kill process using port 5000
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### Issue: "No measurements extracted"
**Possible Causes:**
- Tesseract not installed (see above)
- Photo quality too low
- Text too small in photo

**Solution:**
- Use higher resolution photos
- Ensure text is clearly visible
- System works with or without extracted measurements

### Issue: "Connection refused" when opening browser
**Solution:**
- Wait 2-3 seconds for Flask to start
- Manually open http://localhost:5000
- Check console for error messages

---

## Performance Expectations

| Operation | Expected Time |
|-----------|---|
| Scale Detection | < 1 second |
| Measurement Extraction | 2-5 seconds |
| Element Matching | < 100ms |
| Report Generation | < 500ms |
| **Total End-to-End** | **5-10 seconds** |

---

## Sample Test Data

The system automatically creates test images in `test_data/`:
- `sample_site.jpg` - Mock construction site photo
- `sample_blueprint.jpg` - Mock floor plan

You can:
1. Use these for testing
2. Replace with real construction photos
3. Upload via web interface

---

## What Gets Generated

After analysis, you'll find in `reports/`:
- **PDF Reports** with:
  - Formatted analysis summary
  - Match tables
  - Anomaly detection results
  - Professional formatting

- **CSV Reports** with:
  - Site measurements
  - Blueprint measurements
  - Match status (matched/missing/extra)
  - Confidence scores
  - Exportable to Excel/Sheets

---

## Next Steps

After testing:

1. **Review Reports**
   - Check PDF for visual summary
   - Check CSV for detailed data
   - Verify matches are accurate

2. **Test with More Photos**
   - Try different construction scenarios
   - Test with various photo qualities
   - Verify element matching accuracy

3. **Deploy to Production**
   - See Phase 7 documentation
   - Set up Docker container
   - Configure for production server

4. **Integrate with Workflow**
   - Use API endpoints in your tools
   - Automate report generation
   - Build contractor interface

---

## Support

For issues or questions:
1. Check test results in `test_results/test_results.json`
2. Review logs in console output
3. See `PHASES_1-5_COMPLETE.md` for architecture
4. Check individual phase summaries (PHASE_1-5_SUMMARY.md)

Good luck! 🚀
