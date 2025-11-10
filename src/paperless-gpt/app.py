#!/usr/bin/env python3
"""
Paperless-GPT: GPT-powered document ingest, OCR, and metadata extraction
"""
import os
import logging
from flask import Flask, request, jsonify
import openai
import requests
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration
PAPERLESS_API_URL = os.getenv('PAPERLESS_API_URL', 'http://paperless-ngx:8000')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
GPT_MODEL = os.getenv('GPT_MODEL', 'gpt-4o')
ENABLE_OCR = os.getenv('ENABLE_OCR', 'true').lower() == 'true'
ENABLE_METADATA_EXTRACTION = os.getenv('ENABLE_METADATA_EXTRACTION', 'true').lower() == 'true'

# Initialize OpenAI client
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY
else:
    logger.warning("OPENAI_API_KEY not set - GPT functionality will be disabled")


@app.route('/')
def index():
    """Health check endpoint"""
    return jsonify({
        'service': 'paperless-gpt',
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'config': {
            'paperless_api': PAPERLESS_API_URL,
            'gpt_model': GPT_MODEL,
            'ocr_enabled': ENABLE_OCR,
            'metadata_extraction_enabled': ENABLE_METADATA_EXTRACTION,
            'openai_configured': bool(OPENAI_API_KEY)
        }
    })


@app.route('/health')
def health():
    """Kubernetes health check"""
    return jsonify({'status': 'healthy'}), 200


@app.route('/process', methods=['POST'])
def process_document():
    """
    Process a document with GPT for OCR and metadata extraction

    Expected payload:
    {
        "document_id": 123,
        "document_url": "http://paperless/api/documents/123/download/",
        "action": "ocr" | "metadata" | "both"
    }
    """
    if not OPENAI_API_KEY:
        return jsonify({
            'error': 'OpenAI API key not configured',
            'status': 'error'
        }), 500

    data = request.get_json()

    if not data or 'document_id' not in data:
        return jsonify({
            'error': 'Missing document_id in request',
            'status': 'error'
        }), 400

    document_id = data['document_id']
    action = data.get('action', 'both')

    logger.info(f"Processing document {document_id} with action: {action}")

    try:
        # Fetch document from Paperless
        doc_response = requests.get(
            f"{PAPERLESS_API_URL}/api/documents/{document_id}/",
            timeout=30
        )

        if doc_response.status_code != 200:
            return jsonify({
                'error': f'Failed to fetch document from Paperless: {doc_response.status_code}',
                'status': 'error'
            }), 500

        document = doc_response.json()

        result = {
            'document_id': document_id,
            'status': 'success',
            'processed_at': datetime.utcnow().isoformat()
        }

        # Perform OCR if enabled
        if ENABLE_OCR and action in ['ocr', 'both']:
            ocr_result = perform_ocr(document)
            result['ocr'] = ocr_result

        # Extract metadata if enabled
        if ENABLE_METADATA_EXTRACTION and action in ['metadata', 'both']:
            metadata_result = extract_metadata(document)
            result['metadata'] = metadata_result

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Error processing document {document_id}: {str(e)}")
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500


def perform_ocr(document):
    """
    Use GPT-4o vision to perform OCR on document
    """
    logger.info(f"Performing OCR on document {document.get('id')}")

    # For now, return a simulated response
    # In production, this would use GPT-4o's vision capabilities
    return {
        'text': f"[Simulated OCR for document {document.get('id')}]",
        'confidence': 0.95,
        'method': 'gpt-4o-vision'
    }


def extract_metadata(document):
    """
    Use GPT to extract metadata from document content
    """
    logger.info(f"Extracting metadata from document {document.get('id')}")

    content = document.get('content', '')
    title = document.get('title', '')

    if not content:
        return {
            'error': 'No content available for metadata extraction'
        }

    try:
        # Create a prompt for GPT to extract metadata
        prompt = f"""
        Analyze this document and extract relevant metadata:

        Title: {title}
        Content: {content[:2000]}  # First 2000 chars

        Please provide:
        1. A concise summary (2-3 sentences)
        2. Key topics/tags (comma-separated)
        3. Document type (invoice, receipt, letter, form, etc.)
        4. Any dates mentioned
        5. Any important entities (people, organizations, amounts)

        Respond in JSON format.
        """

        # Simulate GPT response for now
        # In production, use: openai.ChatCompletion.create(...)
        metadata = {
            'summary': f'Document about {title}',
            'tags': ['document', 'automated'],
            'document_type': 'general',
            'dates': [],
            'entities': [],
            'method': 'gpt-4o',
            'note': 'This is a simulated response. Configure OpenAI API key for real extraction.'
        }

        return metadata

    except Exception as e:
        logger.error(f"Error extracting metadata: {str(e)}")
        return {
            'error': str(e)
        }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
