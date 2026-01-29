from flask import Flask, request, jsonify
import requests
import os
import tempfile
from pathlib import Path
import csv
import io

# PDF extraction
try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# DOCX extraction
try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

# DOC extraction (old format)
try:
    import docx2python
    DOC_AVAILABLE = True
except ImportError:
    DOC_AVAILABLE = False

app = Flask(__name__)

def extract_pdf(file_path):
    """Extract text from PDF file"""
    if not PDF_AVAILABLE:
        return None, "PDF extraction library not available"
    
    try:
        text_content = []
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text_content.append(page.extract_text())
        return '\n'.join(text_content), None
    except Exception as e:
        return None, str(e)

def extract_docx(file_path):
    """Extract text from DOCX file"""
    if not DOCX_AVAILABLE:
        return None, "DOCX extraction library not available"
    
    try:
        doc = Document(file_path)
        text_content = []
        for paragraph in doc.paragraphs:
            text_content.append(paragraph.text)
        return '\n'.join(text_content), None
    except Exception as e:
        return None, str(e)

def extract_doc(file_path):
    """Extract text from DOC file (old format)"""
    if not DOC_AVAILABLE:
        return None, "DOC extraction library not available"
    
    try:
        doc_content = docx2python.docx2python(file_path)
        return doc_content.text, None
    except Exception as e:
        return None, str(e)

def extract_csv(file_path):
    """Extract content from CSV file"""
    try:
        content = []
        with open(file_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                content.append(','.join(row))
        return '\n'.join(content), None
    except Exception as e:
        return None, str(e)

def extract_txt(file_path):
    """Extract content from TXT file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read(), None
    except UnicodeDecodeError:
        # Try with different encoding
        try:
            with open(file_path, 'r', encoding='latin-1') as file:
                return file.read(), None
        except Exception as e:
            return None, str(e)
    except Exception as e:
        return None, str(e)

def download_file(url):
    """Download file from URL to temporary location"""
    try:
        response = requests.get(url, timeout=30, stream=True)
        response.raise_for_status()
        
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
        temp_file.write(response.content)
        temp_file.close()
        
        return temp_file.name, file_extension, None
    except Exception as e:
        return None, None, str(e)

@app.route('/extract', methods=['POST', 'GET'])
def extract():
    """Extract content from file URL"""
    try:
        # Get file URL from request
        if request.method == 'POST':
            data = request.get_json() or {}
            file_url = data.get('url') or request.form.get('url')
        else:
            file_url = request.args.get('url')
        
        if not file_url:
            return jsonify({
                'error': 'Missing file URL. Provide "url" parameter in query string (GET) or JSON body (POST)'
            }), 400
        
        # Download file
        file_path, file_extension, error = download_file(file_url)
        if error:
            return jsonify({'error': f'Failed to download file: {error}'}), 400
        
        try:
            # Determine file type and extract content
            content = None
            extract_error = None
            
            if file_extension == '.pdf':
                content, extract_error = extract_pdf(file_path)
            elif file_extension == '.docx':
                content, extract_error = extract_docx(file_path)
            elif file_extension == '.doc':
                content, extract_error = extract_doc(file_path)
            elif file_extension == '.csv':
                content, extract_error = extract_csv(file_path)
            elif file_extension == '.txt':
                content, extract_error = extract_txt(file_path)
            else:
                # Try to detect by content or file signature
                if not file_extension or file_extension == '.tmp':
                    # Try PDF first
                    try:
                        content, extract_error = extract_pdf(file_path)
                        if content:
                            file_extension = '.pdf'
                    except:
                        pass
                    
                    # Try DOCX
                    if not content:
                        try:
                            content, extract_error = extract_docx(file_path)
                            if content:
                                file_extension = '.docx'
                        except:
                            pass
                    
                    # Try DOC
                    if not content:
                        try:
                            content, extract_error = extract_doc(file_path)
                            if content:
                                file_extension = '.doc'
                        except:
                            pass
                    
                    # Try CSV
                    if not content:
                        try:
                            content, extract_error = extract_csv(file_path)
                            if content:
                                file_extension = '.csv'
                        except:
                            pass
                    
                    # Try TXT as last resort
                    if not content:
                        content, extract_error = extract_txt(file_path)
                        if content:
                            file_extension = '.txt'
            
            if extract_error:
                return jsonify({
                    'error': f'Failed to extract content: {extract_error}',
                    'file_type': file_extension
                }), 400
            
            if content is None:
                return jsonify({
                    'error': 'Unsupported file type or failed to extract content',
                    'file_type': file_extension,
                    'supported_types': ['.pdf', '.doc', '.docx', '.csv', '.txt']
                }), 400
            
            return jsonify({
                'success': True,
                'content': content,
                'file_type': file_extension,
                'content_length': len(content)
            }), 200
            
        finally:
            # Clean up temporary file
            if os.path.exists(file_path):
                os.unlink(file_path)
                
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'pdf_support': PDF_AVAILABLE,
        'docx_support': DOCX_AVAILABLE,
        'doc_support': DOC_AVAILABLE
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
        'supported_formats': ['.pdf', '.doc', '.docx', '.csv', '.txt']
    }), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
