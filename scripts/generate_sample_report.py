import os
import sys
import pathlib
import logging

# Ensure project root is on sys.path so imports from project files work
PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from report_generator import create_and_save_reports

logger = logging.getLogger('sample_report')
logging.basicConfig(level=logging.INFO)

def make_sample_report():
    report = {
        'summary': {'total_matches': 3, 'unmatched_pdf': 1, 'unmatched_site': 0},
        'anomalies': {
            'summary': {'missing_count': 1, 'extra_count': 0, 'mismatch_count': 1}
        },
        'matches': [
            {'site': {'type': 'length', 'value_m': 10.5}, 'pdf': {'type': 'length', 'value_m': 10.2}, 'status': 'match', 'difference_percent': 2.9},
            {'site': {'type': 'width', 'value_m': 2.5}, 'pdf': {'type': 'width', 'value_m': 2.4}, 'status': 'match', 'difference_percent': 4.2},
            {'site': {'type': 'height', 'value_m': 3.0}, 'pdf': {'type': 'height', 'value_m': 3.7}, 'status': 'problem', 'difference_percent': 18.9}
        ]
    }
    return report

if __name__ == '__main__':
    out_dir = os.path.join(os.getcwd(), 'reports')
    os.makedirs(out_dir, exist_ok=True)
    report = make_sample_report()
    create_and_save_reports(report, out_dir, logger)
    print('Sample report generated in', out_dir)
