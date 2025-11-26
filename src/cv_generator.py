"""CV generator that updates LaTeX files based on job analysis."""
import re
import subprocess
from pathlib import Path
from typing import Dict, Optional
from .config_manager import ConfigManager


class CVGenerator:
    """Generates tailored CVs by modifying LaTeX files."""

    def __init__(self, config_manager: ConfigManager):
        self.config = config_manager
        self.file_targets = config_manager.get_file_targets()

    def update_header_title(self, role_title: str) -> bool:
        """Update job title in sections/header.tex and setup job title variable."""
        header_path = Path(self.file_targets['header_file'])
        macros_path = Path("setup/macros.tex")

        try:
            # Update header title (existing logic)
            with open(header_path, 'r', encoding='utf-8') as f:
                content = f.read()

            pattern = self.file_targets['header_title_pattern']
            replacement = f'\\1{role_title}\\3'

            if not re.search(pattern, content):
                print(f"Warning: Could not find header title pattern in {header_path}")
                return False

            content = re.sub(pattern, replacement, content)

            with open(header_path, 'w', encoding='utf-8') as f:
                f.write(content)

            # NEW: Update job title variable in macros.tex
            with open(macros_path, 'r', encoding='utf-8') as f:
                macros_content = f.read()

            # Pattern to match: \newcommand{\jobtitle}{Data Analyst}
            title_pattern = r'(\\newcommand\{\\jobtitle\}\{)([^}]+)(\})'
            title_replacement = f'\\1{role_title}\\3'

            if re.search(title_pattern, macros_content):
                macros_content = re.sub(title_pattern, title_replacement, macros_content)
                
                with open(macros_path, 'w', encoding='utf-8') as f:
                    f.write(macros_content)
                
                print(f"Updated job title variable: {role_title}")
            else:
                print("Warning: Could not find job title variable in macros.tex")

            return True
            
        except Exception as e:
            print(f"Error updating header title: {e}")
            return False
        
    def update_version_flags(self, version: str) -> bool:
        """
        Update CV version flags in main.tex.

        Args:
            version: The CV version to activate (FAANG, Startup, Climate, Gaming)

        Returns:
            True if successful, False otherwise
        """
        main_path = Path(self.file_targets['main_file'])

        try:
            with open(main_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # Find the flag lines (should be around lines 3-7)
            updated_lines = []
            flag_section = False

            for line in lines:
                # Detect flag section
                if '\\newif\\ifFAANG' in line:
                    flag_section = True
                elif flag_section and '\\input{setup/preamble.tex}' in line:
                    flag_section = False

                # Reset all flags to false in flag section
                if flag_section:
                    if '\\newif\\if' in line:
                        updated_lines.append(line)
                    elif 'true' in line.lower():
                        # This is a flag activation line - comment it out
                        continue
                else:
                    updated_lines.append(line)

            # Insert the selected version flag after the newif declarations
            insert_index = None
            for i, line in enumerate(updated_lines):
                if '\\newif\\ifGaming' in line:
                    insert_index = i + 1
                    break

            if insert_index is not None:
                updated_lines.insert(insert_index, f'\\{version}true\n')
            else:
                print("Warning: Could not find flag declaration section")
                return False

            with open(main_path, 'w', encoding='utf-8') as f:
                f.writelines(updated_lines)

            return True

        except FileNotFoundError:
            print(f"Error: Main file not found: {main_path}")
            return False
        except Exception as e:
            print(f"Error updating version flags: {e}")
            return False

    def generate_cv(self, analysis_result: Dict, output_name: Optional[str] = None) -> bool:
        """Generate complete CV by updating all files."""
        success = True

        # Update header title
        if not self.update_header_title(analysis_result['role']):
            print("Failed to update header title")
            success = False

        # Update ATS boost WITH keywords
        if not self.update_ats_boost(
            analysis_result['ats_text'], 
            analysis_result.get('keywords', [])  # Pass the extracted keywords
        ):
            print("Failed to update ATS boost text")
            success = False

        # Update version flags
        if not self.update_version_flags(analysis_result['version']):
            print("Failed to update version flags")
            success = False

        return success




    def compile_pdf(self, output_name: Optional[str] = None) -> bool:
        """
        Compile LaTeX to PDF using pdflatex.

        Args:
            output_name: Optional custom output filename

        Returns:
            True if compilation successful
        """
        try:
            # Check if pdflatex is available
            result = subprocess.run(
                ['pdflatex', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0:
                print("Error: pdflatex not found. Please ensure MiKTeX is installed.")
                return False

            # Compile LaTeX (run twice for references)
            for _ in range(2):
                result = subprocess.run(
                    ['pdflatex', '-interaction=nonstopmode', 'main.tex'],
                    capture_output=True,
                    text=True,
                    timeout=60
                )

                # Check if PDF was created (pdflatex may return non-zero even on success with warnings)
                if not Path('main.pdf').exists():
                    print("LaTeX compilation failed:")
                    print(result.stdout)
                    return False

            # Move PDF to output directory if custom name provided
            if output_name:
                output_dir = Path('output')
                output_dir.mkdir(exist_ok=True)

                source_pdf = Path('main.pdf')
                if source_pdf.exists():
                    target_pdf = output_dir / f"{output_name}.pdf"
                    source_pdf.rename(target_pdf)
                    print(f"PDF generated: {target_pdf}")

            return True

        except subprocess.TimeoutExpired:
            print("Error: LaTeX compilation timed out")
            return False
        except FileNotFoundError:
            print("Error: pdflatex not found. Please ensure MiKTeX is installed.")
            return False
        except Exception as e:
            print(f"Error compiling PDF: {e}")
            return False

    def cleanup_latex_artifacts(self):
        """Remove LaTeX auxiliary files."""
        artifacts = [
            '*.aux', '*.log', '*.out', '*.toc', '*.fdb_latexmk',
            '*.fls', '*.synctex.gz', '*.blg', '*.bbl'
        ]

        for pattern in artifacts:
            for file in Path('.').glob(pattern):
                try:
                    file.unlink()
                except Exception:
                    pass

          
    def update_ats_boost(self, ats_text: str, keywords: list = None) -> bool:
        """Update ATS boost text and keywords in sections/sidebar.tex."""
        sidebar_path = Path(self.file_targets['sidebar_file'])

        try:
            with open(sidebar_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 1. Update main ATS boost text (existing logic)
            pattern = r'(\\atsboost\{)(.*?)(\})'
            replacement = f'\\1{ats_text}\\3'

            if not re.search(pattern, content, re.DOTALL):
                print(f"Warning: Could not find \\atsboost pattern in {sidebar_path}")
                return False

            # Replace first atsboost (main text)
            content = re.sub(pattern, replacement, content, count=1, flags=re.DOTALL)

            # 2. NEW: Replace KEYWORDS_PLACEHOLDER with job-specific keywords
            if keywords and 'KEYWORDS_PLACEHOLDER' in content:
                # Format keywords as comma-separated string
                keyword_text = ', '.join(keywords[:15])  # Limit to 15 keywords
                content = content.replace('KEYWORDS_PLACEHOLDER', keyword_text)
                print(f"Updated keyword placeholder with {len(keywords)} keywords")

            # 3. Write updated content
            with open(sidebar_path, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"Successfully updated ATS boost text ({len(ats_text)} chars)")
            return True
            
        except Exception as e:
            print(f"Error updating ATS boost: {e}")
            return False