# Study Buddy Project

Flask application that extracts skills from a resume, generates a quiz using the Mistral LLM, and matches a study buddy.

## Setup

### 1. Clone and install dependencies

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Environment variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

Edit `.env`:

```env
MISTRAL_API_KEY=your_real_key_here
MISTRAL_MODEL=mistral-small  # optional
FLASK_SECRET_KEY=some_random_string
```

Alternatively you can export variables directly in your shell:

```bash
export MISTRAL_API_KEY=your_real_key_here
export FLASK_SECRET_KEY=$(openssl rand -hex 16)
```

The app loads `.env` automatically via `python-dotenv` (see `app.py`). If `MISTRAL_API_KEY` is missing, quiz generation will raise an error.

### 3. Run the app

```bash
python app.py
```

Visit: <http://127.0.0.1:5000>

## Mistral Integration

- Logic in `studybuddy/mistral_api.py`.
- Uses official SDK if installed; falls back to raw HTTP.
- Ensures clean JSON quiz payload.

## Project Structure (simplified)

```text
app.py
studybuddy/
  mistral_api.py
  skill_extractor.py
  quiz_generator.py
  matching.py
templates/
static/
```

## Notes

- Only resumes with `@cmrit.ac.in` email domain accepted.
- Top 3 extracted skills used for quiz generation.

## Troubleshooting

| Issue | Fix |
|-------|-----|
| MISTRAL_API_KEY not set | Create `.env` or export variable |
| 401 from API | Verify key validity and model name |
| Empty quiz | Check skills extraction and API response |

## License

Internal / Educational use only.
