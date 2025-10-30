"""
PDF 처리 유틸리티
"""
import base64
from pathlib import Path
from typing import Optional
import fitz  # PyMuPDF

def load_pdf_as_base64(pdf_path: Path) -> Optional[str]:
    """PDF를 base64로 인코딩"""
    try:
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()
            base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
            return base64_pdf
    except Exception as e:
        print(f"PDF 로드 실패: {e}")
        return None