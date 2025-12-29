# PDF to MCQ Web App

A web application that converts PDFs into MCQs using AI. Because a lot of the times you don't get practice exams.

## Features

- User authentication via Supabase Auth
- PDF upload and management
- AI-powered MCQ generation (using OpenAI models)
- Interactive quiz taking
- Results with explanations

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file with the following variables:
```
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4o-mini
APP_SECRET_KEY=your_secret_key
BASE_URL=http://localhost:8000
```

3. Set up Supabase:
   - Create a project on Supabase
   - Go to the SQL Editor and run the contents of `schema.sql` to create tables
   - Go to Storage and create a bucket named `pdfs` with public access disabled

4. Run the application:
```bash
uvicorn app.main:app --reload
```

5. Access the app at `http://localhost:8000`

## Docker Deployment

1. Build the Docker image:
```bash
docker build -t pdf-to-mcq .
```

2. Run the container:
```bash
docker run -p 8000:8000 --env-file .env pdf-to-mcq
```

Or use Docker Compose (recommended):

```bash
docker-compose up -d
```

To stop:
```bash
docker-compose down
```

## Project Structure

```
app/
  main.py           - FastAPI application entry point
  config.py         - Configuration settings
  deps.py           - FastAPI dependencies
  
  auth/             - Authentication module
    router.py       - Auth routes
    service.py      - Auth service
  
  pdfs/             - PDF management module
    router.py       - PDF routes
    service.py      - PDF service
    storage.py      - Storage utilities
  
  mcq/              - MCQ generation module
    router.py       - MCQ routes
    service.py      - MCQ service
    pipeline/       - (To be implemented)
  
  quiz/             - Quiz module
    router.py       - Quiz routes
    service.py      - Quiz service
  
  templates/        - Jinja2 HTML templates
  static/           - CSS and JavaScript files
```