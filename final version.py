#for document processing
from openai import OpenAI
#The file path management for PDFs
import os
# PyMuPDF for PDF highlighting
import fitz  
#saving highlight results
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
#String matching of similar text
from rapidfuzz import fuzz

class PDFRAG:
    def __init__(self, pdf_path):
        """
        Initialize the OpenAI API, create a file search assistant, and set up vector storage.
        """
        self.key = os.getenv("OPENAI_API_KEY")

        self.pdf_path = pdf_path

        # Assume that OPENAI_API_KEY has been set as an environment variable.
        self.client = OpenAI(api_key=self.key)

        description = """"""
        instructions  = """"""
        # Create an assistant that enables file search
        self.assistant = self.client.beta.assistants.create(
            name="PDF RAG Assistant",
            description=description,
            instructions=instructions,
            model="gpt-4o-mini",
            tools=[{"type": "file_search"}], 
        )

        #Vector Store
        self.vector_store = self.client.beta.vector_stores.create(name="PDF_Vector_Store")
        print("Initialization is done")

        

    def upload_pdf(self):
        """
        Upload the PDF file to the vector storage and associate it with the assistant.
        """
        print("Uploading PDF...")
        file_streams = [open(path, "rb") for path in self.pdf_path]
        file_batch = self.client.beta.vector_stores.file_batches.upload_and_poll(
            vector_store_id=self.vector_store.id, 
            files=file_streams
        )
        print(file_batch.status)
        print(file_batch.file_counts)

        #update the vectore store
        #a weird update step in here, but this is the workflow provided by OpenAI
        self.assistant = self.client.beta.assistants.update(
            assistant_id=self.assistant.id,
            tool_resources={"file_search": {"vector_store_ids": [self.vector_store.id]}},
        )
        print("Assistant Updated with vector store!")

        
    def delete_vector_store(self):
        """
        Deletes the existing Vector Store.
        """
        if self.vector_store:
            self.client.beta.vector_stores.delete(self.vector_store.id)
            self.vector_store = None
    

    def running(self):
        """
        Create a run, process user queries, and highlight the best matching paragraph.
        """
        thread = self.client.beta.threads.create()
        print(f"Your thread id is: {thread.id}\n\n")

        while True:
            query = input("What's your question? (or type 'q' to quit)\n")

            if query.lower() == "q":
                print("Exiting program.")
                break

            self.client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=query
            )

            print("\nRunning query...")
            run = self.client.beta.threads.runs.create_and_poll(
                thread_id=thread.id,
                assistant_id=self.assistant.id
            )

            # Retrieve the full text returned by the Assistant
            messages = list(self.client.beta.threads.messages.list(thread_id=thread.id, run_id=run.id))
            
            if not messages or not messages[0].content:
                print("No response received from Assistant.")
                continue

            # Extract full response text
            extracted_text = ""
            for msg in messages:
                for content in msg.content:
                    if hasattr(content, 'text'):
                        extracted_text += content.text.value + "\n"

            # Display full response
            print(f"Hey We get best matching paragraph found:\n{extracted_text.strip()}")

            # Highlight the best paragraph
            paragraphs = self.extract_text_from_pdf(self.pdf_path[0])
            best_paragraph = self.find_best_paragraph(extracted_text, paragraphs)

            if best_paragraph:
                print(f"Best matching paragraph found:\n{best_paragraph}")

                # Highlight the best paragraph
                highlight_data = self.highlight_text_in_pdf(self.pdf_path[0], best_paragraph)
                if highlight_data:
                    print("Highlighted PDF saved successfully.")
                    with open("highlight_data.json", "w", encoding="utf-8") as json_file:
                        json.dump(highlight_data, json_file, indent=4)
                else:
                    print("No highlights were found in the document.")
            else:
                print("No matching paragraph found.")

    def extract_text_from_pdf(self, pdf_path):
        """
        Extract text from PDF in paragraph-level blocks instead of lines.
        """
        doc = fitz.open(pdf_path)
        paragraphs = []
    
        for page in doc:
            blocks = page.get_text("blocks")  # Extract blocks of text
            for block in blocks:
                text = block[4].strip()
                if len(text) > 30:  # Filter out very short lines
                    paragraphs.append(text)
    
        doc.close()
        return paragraphs

    def find_best_paragraph(self, query, paragraphs):
        """
        Finds the paragraph with the highest similarity score using TF-IDF + Cosine Similarity.
        """
        vectorizer = TfidfVectorizer()
        #Compute TF-IDF vectors
        vectors = vectorizer.fit_transform([query] + paragraphs)  
        query_vector = vectors[0]  
        paragraph_vectors = vectors[1:]  
        # Compute cosine similarity 
        scores = cosine_similarity(query_vector, paragraph_vectors).flatten() 
        if len(scores) == 0 or max(scores) <0.3:
            return None  
        # Get the index of the most similar paragraph
        best_index = np.argmax(scores)  
        return paragraphs[best_index]
    
  def highlight_text_in_pdf(self, pdf_path, text_chunk):
      """
      Efficiently finds and highlights a single best-matching paragraph in the PDF.
      """
      doc = fitz.open(pdf_path)
      best_page = None
      best_score = 0
      best_rect = None
      
      # First pass: Find the best matching paragraph across all pages
      for page_num, page in enumerate(doc):
          # Extract text blocks
          blocks = page.get_text("blocks")
          
          # Process blocks to form complete paragraphs
          paragraphs = []
          for block in blocks:
              text = block[4].strip()
              if len(text) > 30:  # Filter out very short blocks
                  # Calculate similarity score
                  score = fuzz.ratio(text_chunk, text)
                  if score > best_score:
                      best_score = score
                      best_page = page_num
                      best_rect = fitz.Rect(block[:4])
      
      # Second pass: Apply highlight only to the best match
      if best_page is not None and best_score > 60:  # Adjust threshold as needed
          page = doc[best_page]
          page.add_highlight_annot(best_rect)
          
          # Save the highlighted PDF
          highlighted_pdf_path = "highlighted_output.pdf"
          doc.save(highlighted_pdf_path)
          doc.close()
          print(f"Highlighted PDF saved as '{highlighted_pdf_path}'")
          return {"highlighted_pdf": highlighted_pdf_path, "similarity_score": best_score}
      else:
          doc.close()
          print("No matching paragraph found for highlighting.")
          return None
    
if __name__ == "__main__":
    
    pdf_path = [os.path.join(os.getcwd(),"final report.pdf")] 
    print(pdf_path[0])
    rag = PDFRAG(pdf_path)
    rag.upload_pdf()
    response = rag.running()
    rag.delete_vector_store() 
