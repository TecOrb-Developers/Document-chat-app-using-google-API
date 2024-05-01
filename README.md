Document chat app using google API:
What is end Goal:
We have created a chatbot, for companies where they can add their company's pdf document, After our model completes fine-tuning, visitors on that website can chat with the AI trained bot.

Process we have used:
1. We have made a system to upload PDF Upload(Company can use any type of PDFs/Documents like FAQ, knowledge documentations, Old chats with live agents, et)
2. Then have system extracts text from the uploaded PDF documents.
3. Then the extracted text is divided into smaller chunks.
4. After creation of chunk from pdf document we have used the embedding model “embedding-001” from Google GenerativeAI Embeddings class use for vector creation.
5. After creating vector we have stored in FAISS(facebook AI similarity search). FAISS is a library use for efficient similarity search and clustering of dense vectors.
6. Then we have used “gemini-pro” model which from chatgooglegenerativeAI class from the langchain google genAI module. We set gemini-pro model with temperature 0.3 for text generation.
7. Our system maintains a chat history, recording both user queries and system responses in text file.


Dependencies we have used:
•	Python 3.x
•	PyPDF2
•	Streamlit
•	dotenv
•	langchain
•	google.generativeai

** Change ISO pdf (Use any other PDF)
** Don't share any credentials/oath on git commit.
