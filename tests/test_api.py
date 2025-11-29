"""Tests for OpenAI API integration."""
import unittest
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config_manager import ConfigManager
from src.job_analyzer import JobAnalyzer


class TestAPIConnection(unittest.TestCase):
    """Test OpenAI API connectivity and basic functionality."""

    def setUp(self):
        """Set up test fixtures."""
        try:
            self.config = ConfigManager()
            self.analyzer = JobAnalyzer(self.config)
        except Exception as e:
            self.skipTest(f"Could not initialize system: {e}")

    def test_api_connection(self):
        """Test basic API connection."""
        result = self.analyzer.test_connection()
        self.assertTrue(result, "API connection should succeed")

    def test_job_analysis(self):
        """Test job posting analysis."""
        sample_job = """
        Senior Python Developer - AWS Infrastructure

        We are looking for a Python developer with AWS experience.
        Requirements: Python, AWS, Docker, microservices.
        """

        result = self.analyzer.analyze_job_posting(sample_job)

        self.assertIn('role', result)
        self.assertIn('version', result)
        self.assertIn('confidence', result)
        self.assertIn('keywords', result)
        self.assertIn('ats_text', result)

        self.assertIsInstance(result['keywords'], list)
        self.assertGreater(len(result['keywords']), 0)
        self.assertGreater(result['confidence'], 0.0)
        self.assertLessEqual(result['confidence'], 1.0)


if __name__ == '__main__':
    unittest.main()
