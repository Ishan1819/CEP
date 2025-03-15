# import chromadb
# from chromadb.utils import embedding_functions
# import google.generativeai as genai

# # 1. Load the text file
# def load_text(file_path):
#     with open(file_path, "r", encoding="utf-8") as file:
#         return file.read()

# # 2. Split text into chunks
# def split_text(text, chunk_size=500):
#     return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

# # 3. Create embeddings
# embedding_model = embedding_functions.DefaultEmbeddingFunction()
# chroma_client = chromadb.PersistentClient(path="./chroma_db")

# collection = chroma_client.get_or_create_collection(name="chatbot_knowledge")

# def store_embeddings(text_chunks):
#     for idx, chunk in enumerate(text_chunks):
#         embedding = embedding_model([chunk])[0]
#         collection.add(ids=[str(idx)], embeddings=[embedding], documents=[chunk])

# # 4. Retrieve relevant chunks
# def retrieve_relevant_chunks(query):
#     query_embedding = embedding_model([query])[0]
#     try:
#         # Get the count of items in the collection to avoid requesting too many
#         collection_count = collection.count()
#         n_results = min(3, collection_count)
        
#         results = collection.query(query_embeddings=[query_embedding], n_results=n_results)
#         if results["documents"]:
#             return " ".join(results["documents"][0])
#         return ""
#     except Exception as e:
#         print(f"Error retrieving chunks: {e}")
#         return ""

# # 5. Use Gemini for final response
# genai.configure(api_key="AIzaSyDyIOLNBCqpT-pyHXcFZZg8SZsFtPnlwoE")  # Replace with your actual API key

# def chatbot_response(user_query):
#     context = retrieve_relevant_chunks(user_query)
    
#     # Use Gemini 1.5 Flash specifically
#     model = genai.GenerativeModel('gemini-1.5-flash')
    
#     # Generate response
#     prompt = f"Based on the following information, answer the question: {context}\n\nUser: {user_query}"
#     try:
#         response = model.generate_content(prompt)
#         return response.text
#     except Exception as e:
#         return f"Error generating response: {e}"

# # Run chatbot
# text_data = load_text("F:/Ishan_Data/cep.txt")
# text_chunks = split_text(text_data)
# store_embeddings(text_chunks)

# user_question = "What is mentioned about AI in the text?"
# print(chatbot_response(user_question))

import chromadb
from chromadb.utils import embedding_functions
import google.generativeai as genai
import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
import re

# Download NLTK resources (run once)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

# Configure Gemini API
genai.configure(api_key="AIzaSyDyIOLNBCqpT-pyHXcFZZg8SZsFtPnlwoE")  # Replace with your actual API key

# 1. Load the text file
def load_text(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()

# 2. Preprocess text with tokenization and lemmatization
def preprocess_text(text):
    # Convert to lowercase
    text = text.lower()
    
    # Remove special characters but keep some punctuation for sentence boundaries
    text = re.sub(r'[^\w\s\.\,\:\;\-]', '', text)
    
    # Tokenize
    tokens = word_tokenize(text)
    
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if word not in stop_words]
    
    # Lemmatization
    lemmatizer = WordNetLemmatizer()
    lemmatized_tokens = [lemmatizer.lemmatize(word) for word in tokens]
    
    return ' '.join(lemmatized_tokens)

# 3. Split text into chunks - keep chunks more meaningful
def split_text(text, chunk_size=200):
    # Split by paragraphs or sentences first
    paragraphs = text.split('\n')
    chunks = []
    current_chunk = ""
    
    for para in paragraphs:
        if len(current_chunk) + len(para) <= chunk_size:
            current_chunk += para + " "
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = para + " "
    
    if current_chunk:
        chunks.append(current_chunk.strip())
        
    return chunks

# 4. Create embeddings
embedding_model = embedding_functions.DefaultEmbeddingFunction()
chroma_client = chromadb.PersistentClient(path="./chroma_db")

# Remove existing collection if it exists and create a new one
try:
    chroma_client.delete_collection(name="chatbot_knowledge")
except:
    pass
collection = chroma_client.create_collection(name="chatbot_knowledge")

def store_embeddings(chunks):
    # Store the original text directly
    for idx, chunk in enumerate(chunks):
        processed_chunk = preprocess_text(chunk)
        embedding = embedding_model([processed_chunk])[0]
        collection.add(ids=[str(idx)], embeddings=[embedding], documents=[chunk])

# 5. Retrieve relevant chunks
def retrieve_relevant_chunks(query):
    # Preprocess the query the same way as the documents
    processed_query = preprocess_text(query)
    query_embedding = embedding_model([processed_query])[0]
    
    try:
        # Get the count of items in the collection
        collection_count = collection.count()
        if collection_count == 0:
            return "No data available in the collection."
        
        n_results = min(3, collection_count)
        results = collection.query(query_embeddings=[query_embedding], n_results=n_results)
        
        if not results["documents"] or not results["documents"][0]:
            return ""
        
        # Return all retrieved documents
        return " ".join(results["documents"][0])
        
    except Exception as e:
        print(f"Error retrieving chunks: {e}")
        return ""

# 6. Use Gemini to filter for relevance
def filter_relevant_content(retrieved_text, user_query):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
        TASK: Extract ONLY the information from the provided text that directly answers the user's question.
        
        USER QUESTION: {user_query}
        
        TEXT FROM DOCUMENT: {retrieved_text}
        
        INSTRUCTIONS:
        1. Extract ONLY information that directly answers the user's question.
        2. Do NOT add any information beyond what's in the document.
        3. Return the exact text from the document that answers the question.
        4. If no relevant information exists in the document, respond with ONLY: "No information"
        5. Do not summarize or paraphrase - return the exact text from the document.
        6. Do not include any explanations or additional commentary.
        """
        
        response = model.generate_content(prompt)
        filtered_content = response.text.strip()
        
        # If the response is empty or indicates no information
        if not filtered_content or filtered_content.lower() in ["no information", "no relevant information", "none"]:
            return "No information"
            
        return filtered_content
        
    except Exception as e:
        print(f"Error with Gemini API: {e}")
        # Fallback to basic filtering if Gemini fails
        return retrieved_text

# 7. Main chatbot response function
def chatbot_response(user_query):
    # First retrieve potentially relevant chunks from the text file
    retrieved_context = retrieve_relevant_chunks(user_query)
    
    if not retrieved_context:
        return "No information found in the text file."
    
    # Use Gemini to filter for truly relevant content
    relevant_content = filter_relevant_content(retrieved_context, user_query)
    
    return relevant_content

# Run chatbot
file_path = "F:/Ishan_Data/cep.txt"
text_data = load_text(file_path)
chunks = split_text(text_data)
store_embeddings(chunks)

user_question = "How can I become a civil engineer?"
print(chatbot_response(user_question))