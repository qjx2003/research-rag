import fitz

def highlight_annotations_in_pdf(input_pdf_path, annotations, output_pdf_path):
    """
    Highlight all annotations in a PDF based on absolute (whole-document)
    character offsets.
    
    :param input_pdf_path: Path to the original PDF file.
    :param annotations: A list of dicts (or objects) each containing at least
                        'start_index' and 'end_index'.
    :param output_pdf_path: Path to write the highlighted PDF.
    """
    
    doc = fitz.open(input_pdf_path)
    
    # We'll accumulate text length page by page to map absolute offsets
    # (relative to the entire document text) to specific pages
    cumulative_offset = 0
    
    for page_index, page in enumerate(doc):
        # Extract all text from this page
        page_text = page.get_text()
        page_length = len(page_text)
        
        # For each annotation, check if it falls within this page’s text
        for ann in annotations:
            start_abs = ann["start_index"]  # absolute start index in the entire PDF
            end_abs   = ann["end_index"]    # absolute end index in the entire PDF
            
            # Determine if the annotation’s range intersects this page’s range
            # Page's text covers [cumulative_offset, cumulative_offset + page_length)
            page_start = cumulative_offset
            page_end   = cumulative_offset + page_length
            
            # If the annotation falls (even partially) on this page:
            if (start_abs < page_end) and (end_abs > page_start):
                # Convert absolute offsets to local offsets
                local_start = max(0, start_abs - page_start)
                local_end   = min(page_length, end_abs - page_start)
                
                # The exact substring on this page we want to highlight
                substring_to_highlight = page_text[local_start:local_end]
                
                # Use `page.search_for` to find bounding boxes for this text
                # If the same substring appears multiple times on the page,
                # you may get multiple bounding rectangles. Typically we expect
                # a unique match, but be aware of potential duplicates.
                highlight_areas = page.search_for(substring_to_highlight)
                
                for rect in highlight_areas:
                    # Create a highlight annotation in each bounding rectangle
                    highlight = page.add_highlight_annot(rect)
                    # Optionally, you can set any annotation info, like colors or comments:
                    # highlight.set_colors({"stroke": (1, 1, 0), "fill": (1, 1, 0)})
                    # highlight.update()
                    
        # After checking all annotations, move the offset for the next page
        cumulative_offset += page_length

    # Save the modified PDF
    doc.save(output_pdf_path)


if __name__ == "__main__":
    # Example usage:
    
    # A list of annotations with absolute character offsets in the entire PDF’s text
    annotations = [
        {
            "start_index": 1715,
            "end_index": 1727,
            "text": "【4:1†source】"
        },
        {
            "start_index": 1727,
            "end_index": 1739,
            "text": "【4:5†source】"
        },
        {
            "start_index": 1998,
            "end_index": 2010,
            "text": "【4:1†source】"
        },
        {
            "start_index": 2010,
            "end_index": 2022,
            "text": "【4:2†source】"
        }
    ]
    
    input_pdf_path = "test.pdf"
    output_pdf_path = "output1.pdf"
    
    highlight_annotations_in_pdf(input_pdf_path, annotations, output_pdf_path)
    print(f"Highlighted PDF saved to: {output_pdf_path}")
