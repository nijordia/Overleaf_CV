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
        'company': '',
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

        if line.startswith('COMPANY:'):
            result['company'] = line.replace('COMPANY:', '').strip()
        elif line.startswith('ROLE:'):
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


def extract_company_from_email(text: str) -> str:
    """
    Extract company name from email domain or URL in text.

    Args:
        text: Text to search for email/URL

    Returns:
        Extracted company name or empty string
    """
    import re

    # Look for email addresses
    email_pattern = r'[\w\.-]+@([\w\.-]+\.\w+)'
    emails = re.findall(email_pattern, text.lower())

    if emails:
        # Get domain from first email
        domain = emails[0]
        # Remove common TLDs and get company name
        company = domain.split('.')[0]
        # Skip generic domains
        if company not in ['gmail', 'yahoo', 'hotmail', 'outlook', 'mail']:
            return company.capitalize()

    # Look for website URLs
    url_pattern = r'https?://(?:www\.)?([\w-]+)\.'
    urls = re.findall(url_pattern, text.lower())

    if urls:
        company = urls[0]
        if company not in ['gmail', 'yahoo', 'hotmail', 'outlook']:
            return company.capitalize()

    return ''


def detect_language(text: str) -> str:
    """
    Detect if text is in Spanish or English based on common words.

    Args:
        text: The text to analyze

    Returns:
        'es' for Spanish, 'en' for English
    """
    text_lower = text.lower()

    # Common Spanish words that are distinctive
    spanish_indicators = [
        'años', 'experiencia', 'trabajo', 'empresa', 'equipo', 'desarrollador',
        'ingeniero', 'conocimientos', 'habilidades', 'requisitos', 'buscamos',
        'para', 'con', 'del', 'las', 'los', 'una', 'y', 'en', 'de', 'la', 'el',
        'será', 'tendrá', 'debe', 'nuestro', 'nuestra', 'sobre', 'entre',
        'responsabilidades', 'ofrecemos', 'tecnologías', 'proyectos'
    ]

    # Common English words that are distinctive
    english_indicators = [
        'experience', 'work', 'team', 'developer', 'engineer', 'skills',
        'requirements', 'looking', 'for', 'with', 'the', 'and', 'in', 'of',
        'will', 'should', 'our', 'about', 'between', 'responsibilities',
        'offering', 'technologies', 'projects', 'years', 'company'
    ]

    # Count matches for each language
    spanish_count = sum(1 for word in spanish_indicators if f' {word} ' in f' {text_lower} ')
    english_count = sum(1 for word in english_indicators if f' {word} ' in f' {text_lower} ')

    # Determine language based on higher count
    if spanish_count > english_count:
        return 'es'
    else:
        return 'en'
