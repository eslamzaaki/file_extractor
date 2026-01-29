"""
Improved version of app.py with security enhancements and better practices
"""
from flask import Flask, request, jsonify
import requests
import os
import tempfile
from pathlib import Path
import csv
import logging
from urllib.parse import urlparse
from functools import lru_cache

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
@lru_cache()
def get_config():
    """Load configuration from environment variables"""
    return {
        'MAX_FILE_SIZE': int(os.environ.get('MAX_FILE_SIZE', 50 * 1024 * 1024)),  # 50MB default
        'REQUEST_TIMEOUT': int(os.environ.get('REQUEST_TIMEOUT', 30)),
        'ALLOWED_SCHEMES': ['http', 'https'],
        'BLOCKED_HOSTS': ['localhost', '127.0.0.1', '0.0.0.0', '::1', '169.254.169.254'],  # AWS metadata
    }

CONFIG = get_config()

# PDF extraction
try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    logger.warning("PyPDF2 not available. PDF extraction disabled.")

# DOCX extraction
try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    logger.warning("python-docx not available. DOCX extraction disabled.")

# DOC extraction (old format)
try:
    import docx2python
    DOC_AVAILABLE = True
except ImportError:
    DOC_AVAILABLE = False
    logger.warning("docx2python not available. DOC extraction disabled.")

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = CONFIG['MAX_FILE_SIZE'] * 2  # Allow larger responses

# Supported file types mapping
SUPPORTED_EXTENSIONS = ['.pdf', '.doc', '.docx', '.csv', '.txt']

def validate_url(url):
    """
    Validate URL to prevent SSRF attacks
    
    Args:
        url: URL string to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not url or not isinstance(url, str):
        return False, "URL must be a non-empty string"
    
    if len(url) > 2048:
        return False, "URL too long (max 2048 characters)"
    
    try:
        parsed = urlparse(url)
        
        # Only allow http/https
        if parsed.scheme not in CONFIG['ALLOWED_SCHEMES']:
            return False, f"Only {', '.join(CONFIG['ALLOWED_SCHEMES'])} URLs are allowed"
        
        # Block internal/private IPs
        host = parsed.hostname
        if not host:
            return False, "Invalid URL: missing hostname"
        
        # Check for blocked hosts
        if host.lower() in CONFIG['BLOCKED_HOSTS']:
            return False, "Internal URLs are not allowed"
        
        # Block private IP ranges (basic check)
        host_lower = host.lower()
        if (host_lower.startswith('10.') or 
            host_lower.startswith('192.168.') or 
            host_lower.startswith('172.16.') or
            host_lower.startswith('172.17.') or
            host_lower.startswith('172.18.') or
            host_lower.startswith('172.19.') or
            host_lower.startswith('172.20.') or
            host_lower.startswith('172.21.') or
            host_lower.startswith('172.22.') or
            host_lower.startswith('172.23.') or
            host_lower.startswith('172.24.') or
            host_lower.startswith('172.25.') or
            host_lower.startswith('172.26.') or
            host_lower.startswith('172.27.') or
            host_lower.startswith('172.28.') or
            host_lower.startswith('172.29.') or
            host_lower.startswith('172.30.') or
            host_lower.startswith('172.31.')):
            return False, "Private IP addresses are not allowed"
        
        return True, None
    except Exception as e:
        logger.error(f"URL validation error: {str(e)}")
        return False, f"Invalid URL format: {str(e)}"

def extract_pdf(file_path):
    """Extract text from PDF file"""
    if not PDF_AVAILABLE:
        return None, "PDF extraction library not available"
    
    try:
        text_content = []
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text = page.extract_text()
                if text:
                    text_content.append(text)
        return '\n'.join(text_content), None
    except Exception as e:
        logger.error(f"PDF extraction error: {str(e)}")
        return None, str(e)

def extract_docx(file_path):
    """Extract text from DOCX file"""
    if not DOCX_AVAILABLE:
        return None, "DOCX extraction library not available"
    
    try:
        doc = Document(file_path)
        text_content = []
        for paragraph in doc.paragraphs:
            if paragraph.text:
                text_content.append(paragraph.text)
        return '\n'.join(text_content), None
    except Exception as e:
        logger.error(f"DOCX extraction error: {str(e)}")
        return None, str(e)

def extract_doc(file_path):
    """Extract text from DOC file (old format)"""
    if not DOC_AVAILABLE:
        return None, "DOC extraction library not available"
    
    try:
        doc_content = docx2python.docx2python(file_path)
        return doc_content.text, None
    except Exception as e:
        logger.error(f"DOC extraction error: {str(e)}")
        return None, str(e)

def extract_csv(file_path):
    """Extract content from CSV file with better error handling"""
    encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
    
    for encoding in encodings:
        try:
            content = []
            with open(file_path, 'r', encoding=encoding) as file:
                csv_reader = csv.reader(file)
                for row in csv_reader:
                    if row:  # Skip empty rows
                        content.append(','.join(str(cell) for cell in row))
            return '\n'.join(content), None
        except (UnicodeDecodeError, csv.Error) as e:
            logger.debug(f"CSV extraction with {encoding} failed: {str(e)}")
            continue
        except Exception as e:
            logger.error(f"CSV extraction error: {str(e)}")
            return None, str(e)
    
    return None, "Could not parse CSV file with any supported encoding"

def extract_txt(file_path):
    """Extract content from TXT file"""
    encodings = ['utf-8', 'latin-1', 'cp1252']
    
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as file:
                return file.read(), None
        except UnicodeDecodeError:
            continue
        except Exception as e:
            logger.error(f"TXT extraction error: {str(e)}")
            return None, str(e)
    
    return None, "Could not read text file with any supported encoding"

def download_file(url):
    """
    Download file from URL to temporary location with size limits
    
    Args:
        url: URL to download from
        
    Returns:
        tuple: (file_path, file_extension, error_message)
    """
    try:
        response = requests.get(
            url, 
            timeout=CONFIG['REQUEST_TIMEOUT'], 
            stream=True,
            allow_redirects=True
        )
        response.raise_for_status()
        
        # Check content length header
        content_length = response.headers.get('Content-Length')
        if content_length:
            try:
                size = int(content_length)
                if size > CONFIG['MAX_FILE_SIZE']:
                    return None, None, f"File too large. Maximum size: {CONFIG['MAX_FILE_SIZE'] / (1024*1024):.1f}MB"
            except ValueError:
                pass  # Invalid content-length, continue
        
        # Get file extension from URL or Content-Type
        content_type = response.headers.get('Content-Type', '')
        file_extension = None
        
        # Try to get extension from URL
        url_path = Path(url.split('?')[0])  # Remove query parameters
        if url_path.suffix:
            file_extension = url_path.suffix.lower()
        
        # If no extension from URL, try Content-Type
        if not file_extension:
            if 'pdf' in content_type.lower():
                file_extension = '.pdf'
            elif 'word' in content_type.lower() or 'document' in content_type.lower():
                file_extension = '.docx' if 'openxml' in content_type.lower() else '.doc'
            elif 'csv' in content_type.lower() or 'text/csv' in content_type.lower():
                file_extension = '.csv'
            elif 'text/plain' in content_type.lower():
                file_extension = '.txt'
        
        # Create temporary file
        suffix = file_extension or '.tmp'
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        
        # Stream download with size check
        downloaded = 0
        try:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    downloaded += len(chunk)
                    if downloaded > CONFIG['MAX_FILE_SIZE']:
                        temp_file.close()
                        os.unlink(temp_file.name)
                        return None, None, f"File too large. Maximum size: {CONFIG['MAX_FILE_SIZE'] / (1024*1024):.1f}MB"
                    temp_file.write(chunk)
        finally:
            temp_file.close()
        
        logger.info(f"Downloaded file: {downloaded} bytes, extension: {file_extension}")
        return temp_file.name, file_extension, None
        
    except requests.Timeout:
        return None, None, f"Request timeout (>{CONFIG['REQUEST_TIMEOUT']}s)"
    except requests.RequestException as e:
        logger.error(f"Download error: {str(e)}")
        return None, None, f"Failed to download file: {str(e)}"
    except Exception as e:
        logger.error(f"Unexpected download error: {str(e)}")
        return None, None, f"Unexpected error: {str(e)}"

# Extraction function mapping
EXTRACTION_FUNCTIONS = {
    '.pdf': extract_pdf,
    '.docx': extract_docx,
    '.doc': extract_doc,
    '.csv': extract_csv,
    '.txt': extract_txt
}

def try_extract_with_fallback(file_path, file_extension=None):
    """
    Try extraction with multiple methods if file extension is unknown
    
    Args:
        file_path: Path to the file
        file_extension: Known extension or None
        
    Returns:
        tuple: (content, detected_extension, error_message)
    """
    # If we have a known extension, try it first
    if file_extension and file_extension in EXTRACTION_FUNCTIONS:
        extract_func = EXTRACTION_FUNCTIONS[file_extension]
        try:
            content, error = extract_func(file_path)
            if content and not error:
                return content, file_extension, None
        except Exception as e:
            logger.debug(f"Extraction with {file_extension} failed: {str(e)}")
    
    # Try all supported formats
    for ext, extract_func in EXTRACTION_FUNCTIONS.items():
        if file_extension and ext == file_extension:
            continue  # Already tried
        try:
            content, error = extract_func(file_path)
            if content and not error:
                logger.info(f"Detected file type as {ext} via content analysis")
                return content, ext, None
        except Exception as e:
            logger.debug(f"Extraction with {ext} failed: {str(e)}")
            continue
    
    return None, file_extension, "Could not extract content with any supported method"

@app.route('/extract', methods=['POST', 'GET'])
def extract():
    """Extract content from file URL"""
    file_path = None
    try:
        # Get file URL from request
        if request.method == 'POST':
            data = request.get_json() or {}
            file_url = data.get('url') or request.form.get('url')
        else:
            file_url = request.args.get('url')
        
        if not file_url:
            logger.warning("Extraction request without URL")
            return jsonify({
                'error': 'Missing file URL. Provide "url" parameter in query string (GET) or JSON body (POST)'
            }), 400
        
        # Validate URL
        is_valid, error_msg = validate_url(file_url)
        if not is_valid:
            logger.warning(f"Invalid URL rejected: {file_url[:100]}")
            return jsonify({'error': f'Invalid URL: {error_msg}'}), 400
        
        logger.info(f"Extraction request for URL: {file_url[:100]}...")
        
        # Download file
        file_path, file_extension, error = download_file(file_url)
        if error:
            logger.error(f"Download failed: {error}")
            return jsonify({'error': error}), 400
        
        # Extract content
        content, detected_ext, extract_error = try_extract_with_fallback(file_path, file_extension)
        
        if extract_error:
            logger.error(f"Extraction failed: {extract_error}")
            return jsonify({
                'error': f'Failed to extract content: {extract_error}',
                'file_type': detected_ext or file_extension
            }), 400
        
        if content is None:
            logger.warning(f"Could not extract content from file: {file_extension}")
            return jsonify({
                'error': 'Unsupported file type or failed to extract content',
                'file_type': detected_ext or file_extension,
                'supported_types': SUPPORTED_EXTENSIONS
            }), 400
        
        logger.info(f"Successfully extracted {detected_ext or file_extension} file, length: {len(content)}")
        return jsonify({
            'success': True,
            'content': content,
            'file_type': detected_ext or file_extension,
            'content_length': len(content)
        }), 200
            
    except Exception as e:
        logger.error(f"Unexpected error in extract endpoint: {str(e)}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500
    finally:
        # Clean up temporary file
        if file_path and os.path.exists(file_path):
            try:
                os.unlink(file_path)
            except Exception as e:
                logger.warning(f"Failed to delete temp file {file_path}: {str(e)}")

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'pdf_support': PDF_AVAILABLE,
        'docx_support': DOCX_AVAILABLE,
        'doc_support': DOC_AVAILABLE,
        'max_file_size_mb': CONFIG['MAX_FILE_SIZE'] / (1024 * 1024)
    }), 200

@app.route('/', methods=['GET'])
def index():
    """Root endpoint with API information"""
    return jsonify({
        'message': 'File Extractor API',
        'endpoints': {
            '/extract': 'Extract content from file URL (GET or POST with url parameter)',
            '/health': 'Health check endpoint'
        },
        'supported_formats': SUPPORTED_EXTENSIONS,
        'max_file_size_mb': CONFIG['MAX_FILE_SIZE'] / (1024 * 1024)
    }), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
