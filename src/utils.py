"""Utility functions for CV automation system."""
from pathlib import Path
from typing import Optional
import re


def sanitize_filename(text: str) -> str:
    """Convert text to valid filename."""
    # Remove special characters, replace spaces with underscores
    sanitized = re.sub(r'[^\w\s-]', '', text.lower())
    sanitized = re.sub(r'[-\s]+', '_', sanitized)
    return sanitized.strip('_')


def validate_job_posting(file_path: str) -> bool:
    """Validate job posting file exists and has content."""
    path = Path(file_path)
    if not path.exists():
        return False
    if path.stat().st_size == 0:
        return False
    return True


def read_file(file_path: str) -> str:
    """Read file contents with error handling."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        # Try with different encoding
        with open(file_path, 'r', encoding='latin-1') as f:
            return f.read()


def ensure_directory(dir_path: str) -> Path:
    """Ensure directory exists, create if necessary."""
    path = Path(dir_path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def parse_ai_response(response: str) -> dict:
    """Parse AI response into structured data."""
    result = {
        'role': '',
        'version': '',
        'confidence': 0.0,
        'keywords': [],
        'ats_text': ''
    }

    lines = response.strip().split('\n')
    current_section = None

    for line in lines:
        line = line.strip()

        if line.startswith('ROLE:'):
            result['role'] = line.replace('ROLE:', '').strip()
        elif line.startswith('VERSION:'):
            result['version'] = line.replace('VERSION:', '').strip()
        elif line.startswith('CONFIDENCE:'):
            try:
                result['confidence'] = float(line.replace('CONFIDENCE:', '').strip())
            except ValueError:
                result['confidence'] = 0.5
        elif line.startswith('KEYWORDS:'):
            keywords_str = line.replace('KEYWORDS:', '').strip()
            result['keywords'] = [k.strip() for k in keywords_str.split(',')]
        elif line.startswith('ATS_TEXT:'):
            current_section = 'ats_text'
            result['ats_text'] = line.replace('ATS_TEXT:', '').strip()
        elif current_section == 'ats_text' and line:
            result['ats_text'] += ' ' + line

    return result


def format_confidence(confidence: float) -> str:
    """Format confidence as percentage."""
    return f"{int(confidence * 100)}%"


def validate_version(version: str) -> bool:
    """Validate CV version name."""
    valid_versions = ['FAANG', 'Startup', 'Climate', 'Gaming']
    return version in valid_versions
