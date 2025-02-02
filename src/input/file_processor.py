import os
from typing import Dict, List, Union
from docx import Document
from pypdf import PdfReader
import nbformat
import zipfile

class FileProcessor:
    """Handles the processing of different file formats for grading."""
    
    SUPPORTED_EXTENSIONS = {'.txt', '.pdf', '.docx', '.ipynb'}
    
    @staticmethod
    def extract_from_zip(zip_path: str) -> Dict[str, str]:
        """
        Extract content from a zip file containing assignments.
        
        Args:
            zip_path: Path to the zip file
            
        Returns:
            Dictionary mapping filenames to their content
        """
        contents = {}
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            for file_name in zip_ref.namelist():
                _, ext = os.path.splitext(file_name)
                if ext not in FileProcessor.SUPPORTED_EXTENSIONS:
                    continue
                    
                with zip_ref.open(file_name) as file:
                    if ext == '.pdf':
                        contents[file_name] = FileProcessor._process_pdf(file)
                    elif ext == '.docx':
                        contents[file_name] = FileProcessor._process_docx(file)
                    elif ext == '.ipynb':
                        contents[file_name] = FileProcessor._process_notebook(file)
                    else:  # .txt
                        contents[file_name] = file.read().decode('utf-8')
                        
        return contents
    
    @staticmethod
    def _process_pdf(file) -> str:
        """Extract text from PDF file."""
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    
    @staticmethod
    def _process_docx(file) -> str:
        """Extract text from DOCX file."""
        doc = Document(file)
        return "\n".join([paragraph.text for paragraph in doc.paragraphs])
    
    @staticmethod
    def _process_notebook(file) -> str:
        """Extract text and code from Jupyter notebook."""
        nb = nbformat.read(file, as_version=4)
        content = []
        
        for cell in nb.cells:
            if cell.cell_type == 'code':
                content.append(f"```python\n{cell.source}\n```")
            elif cell.cell_type == 'markdown':
                content.append(cell.source)
                
        return "\n\n".join(content) 