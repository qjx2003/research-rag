/************************************************************
 * viewer.js
 *
 * Loads "test.pdf" with PDF.js and highlights *all* occurrences
 * of the keyword "core tensor" across all pages. Fixes issues
 * with multi-span text, multiple matches, and text layer overlap.
 ************************************************************/

// Path (or URL) to your PDF file
const pdfUrl = 'test.pdf';

// The keyword to highlight (exact match by default)
const KEYWORD = 'core tensor';

// Begin loading the PDF
const loadingTask = pdfjsLib.getDocument(pdfUrl);

loadingTask.promise.then(pdf => {
  console.log('PDF loaded! Number of pages:', pdf.numPages);

  const container = document.getElementById('pdf-container');

  // Render each page sequentially
  for (let pageNum = 1; pageNum <= pdf.numPages; pageNum++) {
    pdf.getPage(pageNum).then(page => {
      // Decide how large to render
      const scale = 1.4;
      const viewport = page.getViewport({ scale });

      // Create a container for this page to keep the canvas
      // and text layer aligned relative to each other
      const pageContainer = document.createElement('div');
      pageContainer.style.position = 'relative';
      pageContainer.style.marginBottom = '10px';
      container.appendChild(pageContainer);

      // Create a <canvas> for this page
      const canvas = document.createElement('canvas');
      canvas.className = 'pdf-canvas';
      pageContainer.appendChild(canvas);

      // Prepare its drawing context
      const ctx = canvas.getContext('2d');
      canvas.height = viewport.height;
      canvas.width = viewport.width;

      // Create a text layer div above the canvas
      const textLayerDiv = document.createElement('div');
      textLayerDiv.className = 'textLayer';
      textLayerDiv.style.width = canvas.width + 'px';
      textLayerDiv.style.height = canvas.height + 'px';
      textLayerDiv.style.position = 'absolute';
      textLayerDiv.style.top = '0';
      textLayerDiv.style.left = '0';

      // --scale-factor is used in the CSS if desired
      textLayerDiv.style.setProperty('--scale-factor', scale);

      pageContainer.appendChild(textLayerDiv);

      // Render the PDF page into the canvas
      const renderTask = page.render({
        canvasContext: ctx,
        viewport: viewport
      });

      // After the page is rendered, get text content & build text layer
      renderTask.promise.then(() => {
        return page.getTextContent();
      }).then(textContent => {
        // Render text layer using PDF.js
        return pdfjsLib.renderTextLayer({
          textContentSource: textContent,
          container: textLayerDiv,
          viewport,
          textDivs: []
        }).promise;
      }).then(() => {
        // Now that the text layer is ready, highlight occurrences
        highlightAllOccurrences(textLayerDiv, KEYWORD);
      }).catch(err => {
        console.error('Error rendering page or highlighting:', err);
      });
    });
  }
}).catch(err => {
  console.error('Error loading PDF:', err);
});

/**
 * highlightAllOccurrences scans the text-layer's <span> elements
 * to find and highlight *all* matches of `keyword`.
 * It safely handles multi-span text and repeated matches.
 */
function highlightAllOccurrences(textLayerDiv, keyword) {
  // All text chunks are stored in span[role="presentation"]
  const textSpans = textLayerDiv.querySelectorAll("span[role='presentation']");

  // Combine text from all spans to find matches
  let combinedText = "";
  // We'll map each span to its [start, end] range within combinedText
  const spanInfo = [];

  textSpans.forEach(span => {
    const text = span.textContent || "";
    spanInfo.push({
      span: span,
      startIndex: combinedText.length,
      endIndex: combinedText.length + text.length,
      text: text
    });
    combinedText += text;
  });

  // Find *all* matches of the keyword in combinedText (case-sensitive or insensitive).
  // Here, we'll do case-sensitive. For case-insensitive, convert everything to .toLowerCase().
  const matches = [];
  let pos = 0;
  while (true) {
    pos = combinedText.indexOf(keyword, pos);
    if (pos === -1) break;
    matches.push({ start: pos, end: pos + keyword.length });
    pos += keyword.length; // Move past the current match
  }

  if (matches.length === 0) {
    console.log(`No matches for "${keyword}" on this page.`);
    return;
  }

  console.log(`Found ${matches.length} matches for "${keyword}" on this page.`);

  // Go through each match and highlight the overlapping portion in each span
  matches.forEach(match => {
    const { start: matchStart, end: matchEnd } = match;

    // For each span, check if it overlaps the match range
    spanInfo.forEach(info => {
      if (matchEnd <= info.startIndex || matchStart >= info.endIndex) {
        // No overlap with this span
        return;
      }
      // Overlap found. Compute local offsets inside this span
      const localStart = Math.max(0, matchStart - info.startIndex);
      const localEnd   = Math.min(info.text.length, matchEnd - info.startIndex);

      // Break the original text into before/highlight/after
      const originalText = info.text;
      const before  = escapeHtml(originalText.slice(0, localStart));
      const highlight = escapeHtml(originalText.slice(localStart, localEnd));
      const after   = escapeHtml(originalText.slice(localEnd));

      // Replace the span's HTML with the new structure
      info.span.innerHTML = before +
        `<span class="highlighted-text">${highlight}</span>` +
        after;

      // We keep info.text as the unmodified raw text 
      // so subsequent matches can still map to correct positions
      // (This is simpler, though if the same span has multiple hits 
      //  that overlap, it might require a bit more logic.)
    });
  });
}

/**
 * Escapes special HTML characters in `str`.
 */
function escapeHtml(str) {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}
