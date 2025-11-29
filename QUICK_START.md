# Quick Start Guide

## Installation (One-Time Setup)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Add your API key to .env
# Edit .env and add: OPENAI_API_KEY=your-key-here

# 3. Run setup
python main.py setup

# 4. Test API connection
python main.py test-api
```

## Daily Usage

### Generate CV from Job Posting

```bash
# Interactive (choose version yourself)
python main.py generate --job job_posting.txt

# Auto mode (AI chooses version)
python main.py generate --job job_posting.txt --auto
```

### Test with Sample Jobs

```bash
python main.py test
```

## Commands Reference

| Command | Description | Example |
|---------|-------------|---------|
| `setup` | Create directories and samples | `python main.py setup` |
| `test-api` | Test OpenAI connection | `python main.py test-api` |
| `generate` | Generate CV from job posting | `python main.py generate --job job.txt` |
| `test` | Run test suite | `python main.py test` |
| `info` | Show system information | `python main.py info` |

## Workflow in 3 Steps

1. **Copy job posting** to a text file (e.g., `aws_job.txt`)
2. **Run**: `python main.py generate --job aws_job.txt`
3. **Get CV**: Check `output/` folder for your tailored PDF

## CV Versions

- **FAANG**: Large tech (AWS, Google, Meta)
- **Startup**: Early-stage companies
- **Climate**: Environmental/sustainability roles
- **Gaming**: Game development roles

## What Gets Updated

1. **Job Title** in [sections/header.tex](sections/header.tex#L11)
2. **ATS Boost Text** in [sections/sidebar.tex](sections/sidebar.tex#L11)
3. **Version Flags** in [main.tex](main.tex#L7)

## Output

Generated CVs are saved in: `output/[job_title]_[version].pdf`

## Need Help?

- Full documentation: [README.md](README.md)
- Detailed guide: [USAGE_GUIDE.md](USAGE_GUIDE.md)
- Check API key: Make sure `.env` has valid `OPENAI_API_KEY`
- Test system: `python main.py info`

## Cost

~$0.002 per CV generation (very cheap!)

## Tips

- Review AI confidence score (>70% is good)
- Use `--auto` for quick processing
- Test with samples first: `python main.py test`
