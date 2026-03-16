#!/usr/bin/env python
"""
Run SiteComparator.match_and_analyze on existing test_data images
"""
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils import load_config, setup_logging
from site_comparator import SiteComparator

logger = setup_logging('INFO')
config = load_config()

comparator = SiteComparator(config, logger)

test_dir = project_root / 'test_data'
site = test_dir / 'sample_site.jpg'
blueprint = test_dir / 'sample_blueprint.jpg'

if not site.exists() or not blueprint.exists():
    logger.error(f"Test data files not found: {site}, {blueprint}")
    sys.exit(2)

logger.info(f"Running match_and_analyze on: {site} and {blueprint}")
report = comparator.match_and_analyze(str(site), str(blueprint))

import json
logger.info('Match report (JSON):')
logger.info(json.dumps(report, indent=2, default=str))

print('DONE')
