from openai import OpenAI


class PDFRAG:
    def __init__(self, pdf_path):
        """
        Initialize OpenAI API, create a file search assistant,
        and set up the vector store.
        """
        self.pdf_path = pdf_path

        #Assumes OPENAI_API_KEY is set as an environment variable.
        self.client = OpenAI()

        #Vector Store
        self.vector_store = self.client.beta.vector_stores.create(name="PDF_Vector_Store")

        # Create an assistant with file search enabled
        self.assistant = self.client.beta.assistants.create(
            name="PDF RAG Assistant",
            model="gpt-4o-mini",
            tools=[{"type": "file_search"}], 
        )

        

    def upload_pdf(self):
        """
        Upload the PDF file to the vector store and associate it with the assistant.
        """

        # 改一下
        with open(self.pdf_path, "rb") as file_stream:
            file_batch = self.client.beta.vector_stores.file_batches.upload_and_poll(
                vector_store_id=self.vector_store.id, 
                files=[file_stream]
            )
        print(file_batch.status)
        print(file_batch.file_counts)

        #update the vectore store
        self.assistant = self.client.beta.assistants.update(
            assistant_id=self.assistant.id,
            tool_resources={"file_search": {"vector_store_ids": [self.vector_store.id]}},
        )


    def delete_vector_store(self):
        """
        Deletes the existing Vector Store.
        """
        if self.vector_store:
            self.client.beta.vector_stores.delete(self.vector_store.id)
            self.vector_store = None
    
    def running(self, query):
        """
        Create a run and check output 
        Retrieve the contents of the file search results that were used by the model. 
        """
        thread = self.client.beta.threads.create(
            messages=[
                {
                    "role": "user",
                    "content": query
                }
            ]
        )

        run = self.client.beta.threads.runs.create_and_poll(
            thread_id=thread.id, 
            assistant_id=self.assistant.id
        )
        
        messages = list(self.client.beta.threads.messages.list(thread_id=thread.id, run_id=run.id))
        
        message_content = messages[0].content[0].text
        annotations = message_content.annotations 

        citations = []
        for index, annotation in enumerate(annotations):
            message_content.value = message_content.value.replace(annotation.text, f"[{index}]")
            if file_citation := getattr(annotation, "file_citation", None):
                cited_file = self.client.files.retrieve(file_citation.file_id)
                #not sure if this one will work. 
                quote_text = file_citation.get("quote", "")
            
                citation_info = f"[{index}] {cited_file.filename}"
                citation_info += f"\nQuote: \"{quote_text}\""  
                citations.append(citation_info)
        
        print("Assistant Response:")
        print(message_content.value)

        print("\nCitations:")
        print("\n".join(citations))

        return citations
    
if __name__ == "__main__":
    pdf_path = "your_pdf_file.pdf"  
    rag = PDFRAG(pdf_path)

    print("Uploading PDF...")
    rag.upload_pdf()

    while True:
        query = input("\nEnter your query (or type 'q' to quit): ").strip()

        if query.lower() == "q":
            print("Exiting program.")
            break

        print("\nRunning query...")
        response = rag.running(query)
    
    rag.delete_vector_store()  