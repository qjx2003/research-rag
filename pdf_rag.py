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
        return 0
    
    def running(self):
        """
        Create a run and check output 
        Retrieve the contents of the file search results that were used by the model. 
        """
        return 0