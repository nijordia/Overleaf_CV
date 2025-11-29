# AI-Powered CV Automation System

Automatically tailor your LaTeX CV to job postings using GPT-4o-mini. Takes a job posting, extracts keywords, recommends the best CV version, and generates a customized PDF in under 60 seconds.

## Features

- **AI-Powered Analysis**: Uses GPT-4o-mini to analyze job postings and extract keywords
- **Automatic Customization**: Updates 3 key CV elements:
  - Job title in header
  - ATS optimization text with relevant keywords
  - CV version selection (FAANG, Startup, Climate, Gaming)
- **Fast & Cost-Effective**: ~$0.002 per analysis, complete CV in <60 seconds
- **User Control**: Manual override with confidence scores
- **LaTeX Compilation**: Automatic PDF generation

## Quick Start

### 1. Installation

```bash
# Install Python dependencies
pip install -r requirements.txt

# Verify LaTeX is installed (MiKTeX)
pdflatex --version
```

### 2. Configure API Key

Create a `.env` file in the project root:

```
OPENAI_API_KEY=your-api-key-here
```

### 3. Setup

```bash
python main.py setup
```

This creates necessary directories and sample job postings.

### 4. Test API Connection

```bash
python main.py test-api
```

### 5. Generate Your First CV

```bash
python main.py generate --job tests/sample_jobs/faang_job.txt
```

## Usage

### Generate CV from Job Posting

```bash
# Interactive mode (user selects version)
python main.py generate --job job_posting.txt

# Auto mode (accepts AI recommendation)
python main.py generate --job job_posting.txt --auto

# Custom output filename
python main.py generate --job job_posting.txt --output senior_swe_aws
```

### Test with Sample Jobs

```bash
python main.py test
```

This runs analysis on all sample job postings in `tests/sample_jobs/`.

### System Information

```bash
python main.py info
```

Shows configuration, available CV versions, and keywords.

## Workflow

1. **User pastes job posting** into a text file
2. **Run generate command** with the file path
3. **AI analyzes posting** and extracts:
   - Role title (e.g., "Senior Software Engineer")
   - 15-20 ATS keywords
   - Recommended CV version
   - Confidence score
4. **User reviews recommendation** and selects version (or auto-accept)
5. **System updates LaTeX files**:
   - `sections/header.tex` - Job title
   - `sections/sidebar.tex` - ATS boost text
   - `main.tex` - Version flags
6. **Compiles PDF** automatically
7. **Output saved** to `output/` directory

## CV Versions

| Version | Description | Keywords |
|---------|-------------|----------|
| **FAANG** | Large tech companies | aws, google, meta, scale, microservices, distributed, cloud |
| **Startup** | Early-stage companies | startup, agile, fast-paced, mvp, small team, founder |
| **Climate** | Environmental/sustainability | climate, sustainability, carbon, renewable, esg, green |
| **Gaming** | Entertainment/interactive media | game, gaming, unity, entertainment, interactive, player |

## Project Structure

```
.
├── main.py                      # CLI interface
├── src/
│   ├── job_analyzer.py          # GPT-4o-mini integration
│   ├── cv_generator.py          # LaTeX file updates
│   ├── config_manager.py        # Configuration handling
│   └── utils.py                 # Helper functions
├── config/
│   ├── cv_config.yaml           # CV version definitions
│   └── prompts.yaml             # AI prompts
├── tests/
│   ├── test_api.py              # API tests
│   └── sample_jobs/             # Sample job postings
├── output/                      # Generated CVs
├── sections/                    # LaTeX CV sections
│   ├── header.tex               # Job title (updated)
│   ├── sidebar.tex              # ATS boost (updated)
│   └── ...
└── main.tex                     # Main LaTeX file (flags updated)
```

## How It Works

### 1. Job Analysis (job_analyzer.py)

- Sends job posting to GPT-4o-mini
- AI extracts role title, keywords, and recommends version
- Fallback to keyword-based analysis if API fails

### 2. CV Generation (cv_generator.py)

Updates three critical files:

**Header Title** (`sections/header.tex`):
```latex
{\large\bfseries Senior Software Engineer}\par  % Updated
```

**ATS Boost** (`sections/sidebar.tex`):
```latex
\atsboost{Expert in AWS, Python, distributed systems...}  % Updated
```

**Version Flags** (`main.tex`):
```latex
\newif\ifFAANG
\newif\ifStartup
\newif\ifClimate
\newif\ifGaming
\FAANGtrue  % Updated - only one true at a time
```

### 3. PDF Compilation

- Runs `pdflatex` twice for references
- Moves PDF to `output/` directory
- Cleans up auxiliary files

## Configuration

### cv_config.yaml

Define CV versions, file targets, and ATS settings:

```yaml
cv_versions:
  FAANG:
    description: "Large tech companies - AWS, scale, microservices focus"
    tex_flag: "FAANG"

file_targets:
  header_file: "sections/header.tex"
  sidebar_file: "sections/sidebar.tex"
  main_file: "main.tex"

ats_config:
  max_keywords: 20
  boost_text_length: 150
```

### prompts.yaml

Customize AI analysis prompt and fallback titles:

```yaml
job_analysis_prompt: |
  Analyze this job posting and provide:
  1. Extract the EXACT role title
  2. Identify 15-20 most important ATS keywords
  ...
```

## Error Handling

- **Missing API key**: Clear error with setup instructions
- **API failures**: Fallback to keyword-based analysis
- **LaTeX errors**: Detailed compilation output
- **Invalid job posting**: File validation before processing

## Cost & Performance

- **AI Cost**: ~$0.002 per analysis (GPT-4o-mini)
- **Speed**: <60 seconds from job posting to PDF
- **Accuracy**: >80% correct version selection
- **Reliability**: >95% successful compilations

## Troubleshooting

### API Connection Issues

```bash
# Check API key
cat .env

# Test connection
python main.py test-api
```

### LaTeX Compilation Errors

```bash
# Verify pdflatex is installed
pdflatex --version

# Check for syntax errors in LaTeX files
pdflatex -interaction=nonstopmode main.tex
```

### File Update Issues

The system expects specific patterns in LaTeX files:

- **header.tex line 11**: `{\large\bfseries JobTitle}\par`
- **sidebar.tex line 11**: `\atsboost{...}`
- **main.tex lines 3-7**: `\newif\if...` declarations

## Advanced Usage

### Custom Job Posting

Create a text file with the job posting:

```txt
Senior Data Engineer - Climate Tech

We're seeking a data engineer passionate about climate...
Requirements: Python, AWS, climate data processing...
```

Then run:

```bash
python main.py generate --job my_job.txt
```

### Batch Processing

Process multiple job postings:

```bash
for job in jobs/*.txt; do
    python main.py generate --job "$job" --auto
done
```

### API Testing

Run unit tests:

```bash
cd tests
python test_api.py
```

## Requirements

- Python 3.8+
- OpenAI API key
- MiKTeX LaTeX distribution
- Dependencies: openai, python-dotenv, pyyaml, typer, rich

## License

MIT License - See LICENSE file for details

## Contributing

Contributions welcome! Please open an issue or submit a pull request.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review error messages carefully
3. Run `python main.py info` to verify configuration
4. Check that all LaTeX files have correct patterns

## Future Enhancements

- [ ] Support for additional CV versions
- [ ] Multiple language support
- [ ] Cover letter generation
- [ ] Web interface
- [ ] Integration with job boards
- [ ] Version history tracking
