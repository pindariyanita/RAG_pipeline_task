RAG Pipeline Assignment

This project implements a **Retrieval-Augmented Generation (RAG)** system using a Django backend and a lightweight open-source LLM (`flan-t5-base`) to answer user queries based on a large PDF document.

Here are the steps for setting project in local.

1) Clone project by running,
   (`git clone https://github.com/pindariyanita/RAG_pipeline_task.git`)
2) (`cd .\RAG_pipeline_task\`)
3) For installing all the dependencies, please run 
    (`pip install -r requirements.txt`)
4) For Migrations, please run
   (`python manage.py migrate`)
5) For starting Django project, please run
   (`python manage.py runserver`)
6) For testing, please run the below command in new terminal while keeping above step command run in existing terminal
    (`python test_api.py`)
   
   OR you can paste below API endpoint into POSTMAN

   API:- http://127.0.0.1:8000/api/query/
   Method:- POST
   Body (Select Raw):-
   {
     "query": "What includes in Original Medicare?"
   }

   OR by using curl, Please use Invoke-WebRequest for Windows Powershell.
   (`(Invoke-WebRequest -UseBasicParsing -Uri "http://127.0.0.1:8000/api/query/" -Method Post -ContentType "application/json" -Body '{ "query": "What includes in Original Medicare?" }').Content | ConvertFrom-Json | ConvertTo-Json`)

Here we can replace query with our prompt.

**API Endpoint**

http://127.0.0.1:8000/api/query


**Features**

Dynamic Chunking: Automatically adjusts chunk size based on content and token length.

PDF Retrieval: Retrieves relevant chunks from a large PDF.

LLM Integration: Uses flan-t5-base for text generation.

Structured JSON Output:

   answer: Generated answer to the query
   
   source_page: Page number in the PDF
   
   confidence_score: Similarity score with the retrieved chunk
   
   chunk_size: Number of characters in the final chunk
