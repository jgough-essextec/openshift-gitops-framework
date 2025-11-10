#!/usr/bin/env python3
"""
Glue Worker: Flask webhook orchestrator for Paperless document pipeline
Routes documents through GPT processing and AI reindexing
"""
import os
import logging
from flask import Flask, request, jsonify
import requests
from datetime import datetime
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration
PAPERLESS_API_URL = os.getenv('PAPERLESS_API_URL', 'http://paperless-ngx:8000')
PAPERLESS_GPT_URL = os.getenv('PAPERLESS_GPT_URL', 'http://paperless-gpt:8080')
PAPERLESS_AI_URL = os.getenv('PAPERLESS_AI_URL', 'http://paperless-ai:8000')
FLASK_ENV = os.getenv('FLASK_ENV', 'production')
ENABLE_GPT_ROUTING = os.getenv('ENABLE_GPT_ROUTING', 'true').lower() == 'true'
ENABLE_AI_REINDEX = os.getenv('ENABLE_AI_REINDEX', 'true').lower() == 'true'


@app.route('/')
def index():
    """Health check endpoint"""
    return jsonify({
        'service': 'glue-worker',
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'config': {
            'paperless_api': PAPERLESS_API_URL,
            'paperless_gpt': PAPERLESS_GPT_URL,
            'paperless_ai': PAPERLESS_AI_URL,
            'gpt_routing_enabled': ENABLE_GPT_ROUTING,
            'ai_reindex_enabled': ENABLE_AI_REINDEX
        }
    })


@app.route('/health')
def health():
    """Kubernetes health check"""
    return jsonify({'status': 'healthy'}), 200


@app.route('/webhook/document', methods=['POST'])
def webhook_document():
    """
    Webhook endpoint for new document events from Paperless

    Expected payload from Paperless webhook:
    {
        "event": "document_added" | "document_updated",
        "document_id": 123,
        "document": { ... document object ... }
    }
    """
    data = request.get_json()

    if not data or 'document_id' not in data:
        return jsonify({
            'error': 'Missing document_id in webhook payload',
            'status': 'error'
        }), 400

    event = data.get('event', 'unknown')
    document_id = data['document_id']

    logger.info(f"Received webhook event '{event}' for document {document_id}")

    try:
        # Route document through processing pipeline
        result = process_pipeline(document_id, event)

        return jsonify({
            'status': 'success',
            'document_id': document_id,
            'event': event,
            'pipeline_result': result,
            'processed_at': datetime.utcnow().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Error processing webhook for document {document_id}: {str(e)}")
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500


@app.route('/process/<int:document_id>', methods=['POST'])
def process_document(document_id: int):
    """
    Manually trigger processing for a specific document
    """
    logger.info(f"Manual processing triggered for document {document_id}")

    try:
        result = process_pipeline(document_id, 'manual')

        return jsonify({
            'status': 'success',
            'document_id': document_id,
            'pipeline_result': result,
            'processed_at': datetime.utcnow().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Error processing document {document_id}: {str(e)}")
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500


def process_pipeline(document_id: int, event: str) -> Dict[str, Any]:
    """
    Route document through the processing pipeline:
    1. GPT processing (if enabled)
    2. AI reindexing (if enabled)
    """
    pipeline_result = {
        'document_id': document_id,
        'event': event,
        'steps': []
    }

    # Step 1: Send to GPT for OCR and metadata extraction
    if ENABLE_GPT_ROUTING:
        logger.info(f"Routing document {document_id} to paperless-gpt")
        gpt_result = route_to_gpt(document_id)
        pipeline_result['steps'].append({
            'service': 'paperless-gpt',
            'result': gpt_result
        })

    # Step 2: Send to AI for embeddings and classification
    if ENABLE_AI_REINDEX:
        logger.info(f"Routing document {document_id} to paperless-ai for reindexing")
        ai_result = route_to_ai(document_id)
        pipeline_result['steps'].append({
            'service': 'paperless-ai',
            'result': ai_result
        })

    return pipeline_result


def route_to_gpt(document_id: int) -> Dict[str, Any]:
    """
    Send document to paperless-gpt for processing
    """
    try:
        response = requests.post(
            f"{PAPERLESS_GPT_URL}/process",
            json={
                'document_id': document_id,
                'action': 'both'
            },
            timeout=60
        )

        if response.status_code == 200:
            return {
                'status': 'success',
                'data': response.json()
            }
        else:
            logger.warning(f"GPT processing returned status {response.status_code}")
            return {
                'status': 'error',
                'code': response.status_code,
                'message': response.text
            }

    except requests.exceptions.RequestException as e:
        logger.error(f"Error connecting to paperless-gpt: {str(e)}")
        return {
            'status': 'error',
            'message': str(e)
        }


def route_to_ai(document_id: int) -> Dict[str, Any]:
    """
    Send document to paperless-ai for embeddings and classification
    """
    try:
        # Paperless-AI uses the same API structure as paperless-ngx
        # We can trigger reindexing via its API
        response = requests.post(
            f"{PAPERLESS_AI_URL}/api/index/",
            json={
                'document_ids': [document_id]
            },
            timeout=60
        )

        if response.status_code in [200, 201, 204]:
            return {
                'status': 'success',
                'message': f'Document {document_id} queued for AI reindexing'
            }
        else:
            logger.warning(f"AI reindexing returned status {response.status_code}")
            return {
                'status': 'error',
                'code': response.status_code,
                'message': response.text
            }

    except requests.exceptions.RequestException as e:
        logger.error(f"Error connecting to paperless-ai: {str(e)}")
        return {
            'status': 'error',
            'message': str(e)
        }


@app.route('/stats')
def stats():
    """
    Get processing statistics
    """
    # In production, this would query a database or cache
    return jsonify({
        'service': 'glue-worker',
        'uptime': 'simulated',
        'documents_processed': 0,
        'pipeline_enabled': {
            'gpt': ENABLE_GPT_ROUTING,
            'ai': ENABLE_AI_REINDEX
        }
    })


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=(FLASK_ENV == 'development'))
