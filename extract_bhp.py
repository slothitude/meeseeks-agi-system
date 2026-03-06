#!/usr/bin/env python3
"""Extract Black Hat Python chapters and identify key techniques."""

from pypdf import PdfReader
import re

def extract_pdf_text(pdf_path, max_pages=50):
    """Extract text from PDF."""
    reader = PdfReader(pdf_path)
    print(f"Total pages: {len(reader.pages)}")
    
    text = ""
    for i, page in enumerate(reader.pages[:max_pages]):
        text += f"\n--- PAGE {i+1} ---\n"
        text += page.extract_text() or ""
    
    return text

def find_chapters(text):
    """Find chapter markers in the text."""
    # Common chapter patterns
    patterns = [
        r'Chapter\s+\d+',
        r'CHAPTER\s+\d+',
        r'^\d+\.\s+[A-Z]',
    ]
    
    chapters = []
    for pattern in patterns:
        matches = re.finditer(pattern, text, re.MULTILINE | re.IGNORECASE)
        for match in matches:
            chapters.append((match.start(), match.group()))
    
    chapters.sort(key=lambda x: x[0])
    return chapters

def main():
    pdf_path = "AGI-STUDY/black_hat_python.pdf"
    
    # Extract first 50 pages to get chapters 1-3
    print("Extracting text from PDF...")
    text = extract_pdf_text(pdf_path, max_pages=60)
    
    # Save raw extraction
    with open("research/bhp_raw_extract.txt", "w", encoding="utf-8") as f:
        f.write(text)
    print(f"Saved raw extract ({len(text)} chars)")
    
    # Find chapters
    chapters = find_chapters(text)
    print(f"\nFound {len(chapters)} chapter markers:")
    for pos, title in chapters[:10]:
        print(f"  Position {pos}: {title}")
    
    # Extract table of contents if visible
    toc_match = re.search(r'Contents|CONTENTS|Table of Contents', text)
    if toc_match:
        # Get surrounding context
        start = max(0, toc_match.start() - 100)
        end = min(len(text), toc_match.start() + 2000)
        print(f"\nTable of Contents region:\n{text[start:end]}")

if __name__ == "__main__":
    main()
