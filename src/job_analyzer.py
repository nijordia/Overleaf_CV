"""Job posting analyzer using OpenAI GPT-4o-mini."""
import os
from openai import OpenAI
from typing import Dict, List
from dotenv import load_dotenv
from .config_manager import ConfigManager
from .utils import parse_ai_response, validate_version, detect_language, extract_company_from_email
from .logger import get_logger

logger = get_logger(__name__)


class JobAnalyzer:
    """Analyzes job postings using GPT-4o-mini to extract keywords and recommend CV version."""

    def __init__(self, config_manager: ConfigManager):
        load_dotenv()
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.error("OPENAI_API_KEY not found in environment variables")
            raise ValueError("OPENAI_API_KEY not found in environment variables")

        logger.debug(f"Initializing JobAnalyzer with API key: {self.api_key[:20]}...")
        self.client = OpenAI(api_key=self.api_key, timeout=30.0)  # Add 30 second timeout
        self.config = config_manager
        self.model = "gpt-4o-mini"
        logger.info(f"JobAnalyzer initialized with model: {self.model}")

    def test_connection(self) -> bool:
        """Test OpenAI API connection."""
        logger.info("Testing OpenAI API connection...")
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Say 'API connection successful'"}],
                max_tokens=10,
                timeout=10.0
            )
            result = "successful" in response.choices[0].message.content.lower()
            if result:
                logger.info("API connection test: SUCCESS")
            else:
                logger.warning("API connection test: FAILED (unexpected response)")
            return result
        except Exception as e:
            logger.error(f"API connection test failed: {type(e).__name__}: {e}")
            return False

    def analyze_job_posting(self, job_text: str) -> Dict[str, any]:
        """
        Analyze job posting using GPT-4o-mini.

        Returns:
            Dict with keys: role, version, confidence, keywords, ats_text, language
        """
        logger.info("Starting job posting analysis...")
        logger.debug(f"Job text length: {len(job_text)} characters")

        # Detect language first
        detected_language = detect_language(job_text)
        logger.info(f"Detected language: {detected_language}")

        prompt_template = self.config.get_job_analysis_prompt()
        prompt = prompt_template.format(job_text=job_text)
        logger.debug(f"Generated prompt length: {len(prompt)} characters")

        try:
            logger.info("Calling OpenAI API...")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert ATS (Applicant Tracking System) analyzer and CV optimization specialist. Analyze job postings and extract key information for CV tailoring."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=500,
                temperature=0.3,
                timeout=30.0  # 30 second timeout
            )
            logger.info("Received response from OpenAI API")

            ai_response = response.choices[0].message.content
            logger.debug(f"AI response: {ai_response[:200]}...")

            result = parse_ai_response(ai_response)
            logger.info(f"Parsed result - Company: {result['company']}, Role: {result['role']}, Version: {result['version']}, Confidence: {result['confidence']}")

            # Add detected language to result
            result['language'] = detected_language

            # Validate and fallback
            if not result['company']:
                logger.warning("No company extracted, trying email/URL extraction")
                result['company'] = extract_company_from_email(job_text)
                if not result['company']:
                    logger.warning("No company found, using 'Unknown_Company'")
                    result['company'] = 'Unknown_Company'

            if not result['role']:
                logger.warning("No role extracted, using fallback title")
                result['role'] = self.config.get_fallback_title()

            if not validate_version(result['version']):
                logger.warning(f"Invalid version '{result['version']}', using fallback selection")
                result['version'] = self._fallback_version_selection(job_text)

            if result['confidence'] == 0.0:
                logger.warning("Zero confidence, setting to 0.5")
                result['confidence'] = 0.5

            logger.info(f"Analysis complete - Final: Company={result['company']}, Role={result['role']}, Version={result['version']}, Language={detected_language}")
            return result

        except Exception as e:
            logger.error(f"Error analyzing job posting with AI: {type(e).__name__}: {e}")
            logger.info("Falling back to keyword-based analysis")
            return self._fallback_analysis(job_text)

    def _fallback_version_selection(self, job_text: str) -> str:
        """Fallback keyword-based version selection if AI fails."""
        logger.debug("Running fallback version selection...")
        job_text_lower = job_text.lower()
        version_scores = {}

        # Score each version based on keyword matches
        for version, keywords in self.config.cv_config.get("version_keywords", {}).items():
            score = sum(1 for keyword in keywords if keyword.lower() in job_text_lower)
            version_scores[version] = score
            logger.debug(f"Version {version}: {score} keyword matches")

        # Return version with highest score, default to FAANG
        if version_scores:
            best_version = max(version_scores, key=version_scores.get)
            logger.info(f"Fallback selected version: {best_version} (score: {version_scores[best_version]})")
            return best_version

        logger.warning("No version scores, defaulting to FAANG")
        return "FAANG"

    def _fallback_analysis(self, job_text: str) -> Dict[str, any]:
        """Fallback analysis if API fails."""
        logger.info("Running fallback analysis (no API)")
        version = self._fallback_version_selection(job_text)

        # Detect language
        detected_language = detect_language(job_text)
        logger.info(f"Detected language (fallback): {detected_language}")

        # Try to extract company name
        company = extract_company_from_email(job_text)
        if not company:
            logger.warning("No company found in fallback, using 'Unknown_Company'")
            company = 'Unknown_Company'

        # Extract basic keywords
        keywords = self._extract_basic_keywords(job_text)
        logger.debug(f"Extracted {len(keywords)} keywords: {', '.join(keywords[:10])}...")

        result = {
            'company': company,
            'role': self.config.get_fallback_title(),
            'version': version,
            'confidence': 0.5,
            'keywords': keywords[:20],
            'ats_text': self._generate_basic_ats_text(keywords, version),
            'language': detected_language
        }

        logger.info(f"Fallback analysis complete - Company: {result['company']}, Role: {result['role']}, Version: {result['version']}, Language: {detected_language}")
        return result

    def _extract_basic_keywords(self, job_text: str) -> List[str]:
        """Extract basic keywords using simple text processing."""
        # Common technical keywords
        common_keywords = [
            'python', 'javascript', 'java', 'aws', 'docker', 'kubernetes',
            'sql', 'api', 'react', 'node', 'machine learning', 'data',
            'cloud', 'microservices', 'agile', 'ci/cd', 'git', 'rest',
            'backend', 'frontend', 'full-stack', 'database', 'linux'
        ]

        job_text_lower = job_text.lower()
        found_keywords = [kw for kw in common_keywords if kw in job_text_lower]
        return found_keywords

    def _generate_basic_ats_text(self, keywords: List[str], version: str) -> str:
        """Generate basic ATS text from keywords."""
        keywords_str = ', '.join(keywords[:15])

        templates = {
            'FAANG': f"Experienced software engineer with expertise in large-scale distributed systems. Skilled in {keywords_str}. Proven track record in delivering scalable solutions for high-traffic applications.",
            'Startup': f"Versatile full-stack developer with startup experience. Proficient in {keywords_str}. Adaptable team player comfortable with fast-paced environments and rapid iteration.",
            'Climate': f"Data engineer passionate about environmental impact. Expertise in {keywords_str}. Committed to leveraging technology for sustainability and climate solutions.",
            'Gaming': f"Creative developer with gaming industry experience. Technical skills in {keywords_str}. Passionate about creating engaging interactive experiences."
        }

        return templates.get(version, templates['FAANG'])

    def get_version_description(self, version: str) -> str:
        """Get human-readable description of CV version."""
        versions = self.config.get_all_versions()
        return versions.get(version, {}).get('description', 'Unknown version')