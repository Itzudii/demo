"""
File Management System
Copyright (c) 2026 Uditya Patel
Licensed under the MIT License.
"""
from PyPDF2 import PdfReader 
import docx


def txt_reader(filepath:str):
    with open(filepath,'r',encoding='utf-8',errors="ignore") as file:
        return file.read()

def pdf_reader(filepath:str):
    reader = PdfReader(filepath)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def docx_reader(filepath:str):
    doc = docx.Document(filepath)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

def universal_reader(filepath:str):
    if filepath.endswith('.pdf'):
        return pdf_reader(filepath)
    elif filepath.endswith('.docx'):
        return docx_reader(filepath)
    else:
        return txt_reader(filepath)
