"""Configuration management for CV automation system."""
import yaml
from pathlib import Path
from typing import Dict, Any, List


class ConfigManager:
    """Manages configuration files for CV automation."""

    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.cv_config = self._load_yaml("cv_config.yaml")
        self.prompts = self._load_yaml("prompts.yaml")

    def _load_yaml(self, filename: str) -> Dict[str, Any]:
        """Load YAML configuration file."""
        config_path = self.config_dir / filename
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML file {config_path}: {e}")

    def get_version_keywords(self, version: str) -> List[str]:
        """Get keywords for a specific CV version."""
        return self.cv_config.get("version_keywords", {}).get(version, [])

    def get_all_versions(self) -> Dict[str, Dict[str, str]]:
        """Get all CV version definitions."""
        return self.cv_config.get("cv_versions", {})

    def get_file_targets(self) -> Dict[str, str]:
        """Get file paths and patterns for LaTeX updates."""
        return self.cv_config.get("file_targets", {})

    def get_ats_config(self) -> Dict[str, int]:
        """Get ATS configuration settings."""
        return self.cv_config.get("ats_config", {})

    def get_job_analysis_prompt(self) -> str:
        """Get the job analysis prompt template."""
        return self.prompts.get("job_analysis_prompt", "")

    def get_fallback_title(self, category: str = "default") -> str:
        """Get fallback job title."""
        return self.prompts.get("fallback_titles", {}).get(category, "Software Engineer")
