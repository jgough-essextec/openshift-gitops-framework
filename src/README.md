# Paperless Services

This directory contains the source code for custom Paperless-NGX integration services.

## Services

### paperless-gpt

GPT-powered document ingest, OCR, and metadata extraction service.

**Features:**

- GPT-4o vision-based OCR
- Automatic metadata extraction
- Document classification
- Integration with Paperless-NGX API

**Environment Variables:**

- `PAPERLESS_API_URL`: Paperless-NGX API endpoint
- `OPENAI_API_KEY`: OpenAI API key for GPT access
- `GPT_MODEL`: GPT model to use (default: gpt-4o)
- `ENABLE_OCR`: Enable OCR processing (default: true)
- `ENABLE_METADATA_EXTRACTION`: Enable metadata extraction (default: true)
- `PORT`: HTTP port (default: 8080)

### glue-worker

Flask webhook orchestrator for routing documents through the processing pipeline.

**Features:**

- Webhook receiver for Paperless-NGX document events
- Routes documents through GPT and AI services
- Pipeline orchestration and error handling

**Environment Variables:**

- `PAPERLESS_API_URL`: Paperless-NGX API endpoint
- `PAPERLESS_GPT_URL`: Paperless-GPT service URL
- `PAPERLESS_AI_URL`: Paperless-AI service URL
- `FLASK_ENV`: Flask environment (default: production)
- `ENABLE_GPT_ROUTING`: Enable GPT processing (default: true)
- `ENABLE_AI_REINDEX`: Enable AI reindexing (default: true)
- `PORT`: HTTP port (default: 5000)

## Building

### Local Build

```bash
# Build paperless-gpt
cd src/paperless-gpt
docker build -t ghcr.io/rbales79/paperless-gpt:latest .

# Build glue-worker
cd src/glue-worker
docker build -t ghcr.io/rbales79/paperless-glue-worker:latest .
```

### GitHub Actions

Images are automatically built and pushed to GitHub Container Registry on:

- Push to main branch
- Manual workflow dispatch

## API Endpoints

### paperless-gpt

- `GET /` - Health check and configuration
- `GET /health` - Kubernetes health probe
- `POST /process` - Process document with GPT
  ```json
  {
    "document_id": 123,
    "action": "ocr" | "metadata" | "both"
  }
  ```

### glue-worker

- `GET /` - Health check and configuration
- `GET /health` - Kubernetes health probe
- `POST /webhook/document` - Webhook for Paperless document events
- `POST /process/<document_id>` - Manual processing trigger
- `GET /stats` - Processing statistics

## Deployment

These services are deployed via Helm charts in the `charts/paperless/` directory:

- `charts/paperless/paperless-gpt/`
- `charts/paperless/glue-worker/`

See the Helm chart values for configuration options.
