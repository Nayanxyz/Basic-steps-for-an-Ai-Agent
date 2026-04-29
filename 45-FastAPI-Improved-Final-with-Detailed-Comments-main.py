# === KEY STEP 1: TOOLBOX IMPORTS ===
from ddgs import DDGS                                                                                                # Imports DuckDuckGo search tool for live news
from fastapi import FastAPI                                                                                          # Imports FastAPI framework to build the web server
from pydantic import BaseModel                                                                                       # Imports Pydantic to validate incoming JSON data
import uvicorn                                                                                                       # Imports Uvicorn server to run the FastAPI app
import os                                                                                                            # Imports OS module to read environment variables
import requests                                                                                                      # Imports Requests to make API calls to Groq
import chromadb                                                                                                      # Imports ChromaDB for local vector database (RAG)
import re                                                                                                            # Imports Regular Expressions for text filtering
from dotenv import load_dotenv                                                                                       # Imports dotenv to load secret keys from a .env file
from datetime import datetime                                                                                        # Imports datetime to get the current date and time

# === KEY STEP 2: ENVIRONMENT SETUP ===
load_dotenv()                                                                                                        # Loads the hidden passwords from the local .env file
API_KEY = os.getenv("GROQ_API_KEY")                                                                                  # Safely grabs the Groq API key from memory
CLOUD_URL = "https://api.groq.com/openai/v1/chat/completions"                                                        # Sets the exact URL for the Groq supercomputer

# === KEY STEP 3: SERVER & DATABASE INITIALIZATION ===
app = FastAPI(title="Enterprise Swarm API", version="1.0")                                                           # Initializes the FastAPI server application
active_sessions = {}                                                                                                 # Creates an empty dictionary to hold chat histories for different users

client = chromadb.Client()                                                                                           # Boots up the local ChromaDB database client
collection = client.get_or_create_collection(name="chroma_collection")                                               # Creates or opens a digital folder for company data

try:                                                                                                                 # Starts a safe execution block
    collection.add(documents=["The company wifi password is 'BlueMonkey42'."], ids=["doc1"])                         # Injects the company password into the database
except:                                                                                                              # Catches the error if the password is already in the database
    pass                                                                                                             # Ignores the error and keeps the server running smoothly

# === KEY STEP 4: DATA CONTRACTS (PYDANTIC) ===
class UserRequest(BaseModel):                                                                                        # Defines the strict input rules for the API
    user_id: str                                                                                                     # Demands that the incoming request must have a string ID
    prompt: str                                                                                                      # Demands that the incoming request must have a text prompt

class SwarmResponse(BaseModel):                                                                                      # Defines the strict output rules for the API
    manager_routing: str                                                                                             # Promises the output will contain the routing decision
    final_answer: str                                                                                                # Promises the output will contain the final AI text


# === KEY STEP 5: CORE AI WORKERS ===
def get_manager_decision(user_text):                                                                                 # Defines the Orchestrator function

    orchestrator_prompt = [                                                                                          # Creates the message list for the AI
        {"role": "system", "content": """You are the Orchestrator. Route the user's input.
You must output ONLY a comma-separated list of departments. DO NOT explain your reasoning.
ROUTING RULES:
1. Output 'WEB' for live events, weather, sports, recent news.
2. Output 'RAG' for internal company data, passwords.
3. Output 'CHAT' for small talk.
4. Output 'MATH' for calculation mathematics."""},                                                                   # The strict rules for the Manager
        {"role": "user", "content": user_text}                                                                       # Injects the user's actual question
    ]

    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}                             # Packages the security badge
    payload = {"model": "llama-3.1-8b-instant", "messages": orchestrator_prompt, "temperature": 0.0}                 # Packages the API request with 0 creativity
    response = requests.post(CLOUD_URL, headers=headers, json=payload)                                               # Sends the request to Groq over the internet
    return response.json()["choices"][0]["message"]["content"].strip().upper()                                       # Extracts and cleans the one-word answer


def get_search_query(user_text):                                                                                     # Defines the Micro-Agent function

    today = datetime.now().strftime("%B %d, %Y")                                                                     # Gets today's exact date as a string
    current_year = datetime.now().year                                                                               # Gets the current 4-digit year

    topic_prompt = [                                                                                                 # Creates the message list for the Micro-Agent
        {"role": "system", "content": f"""You are an SEO Search Expert. Today is {today}.
Your ONLY job is to extract the live news or web search topic from the user's prompt.
CRITICAL RULES:
1. IGNORE math equations.
2. IGNORE internal company questions (passwords, wifi, etc.).
3. If the user asks about current events, append the year '{current_year}' to the search string.
4. Output EXACTLY ONE string. Do not talk.

EXAMPLES:
User: "What is 5+5 and who won the Super Bowl?" -> "Super Bowl winner {current_year}"
User: "what is wifi password, Bengal election results, and 8/2?" -> "Bengal election results {current_year}"
User: "Hello, what is the weather in Tokyo?" -> "Tokyo weather {today}"
"""},                                                                                                                # Uses Few-Shot examples and temporal injection
        {"role": "user", "content": user_text}                                                                       # Injects the messy user prompt
    ]

    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}                             # Packages the security badge
    payload = {"model": "llama-3.1-8b-instant", "messages": topic_prompt, "temperature": 0.0}                               # Packages the request with 0 creativity
    response = requests.post(CLOUD_URL, headers=headers, json=payload)                                               # Sends the request to Groq
    return response.json()["choices"][0]["message"]["content"].strip()                                               # Extracts and cleans the search query


def send_to_cloud_ai(history_list):                                                                                  # Defines the main bridge function

    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}                             # Packages the security badge
    payload = {"model": "llama-3.1-8b-instant", "messages": history_list, "temperature": 0.7}                        # Packages the request with natural creativity (0.7)
    response = requests.post(CLOUD_URL, headers=headers, json=payload)                                               # Sends the request to Groq
    return response.json()["choices"][0]["message"]["content"]                                                       # Extracts the final AI English response


def compress_memory(history_list):                                                                                   # Defines the Background Janitor function

    compression_payload = [                                                                                          # Creates a special message list for summarizing
        {"role": "system", "content": "You are a backend memory manager. "
                                      "Generate a detailed 'Running Fact Sheet' from the log."},                     # Tells AI to summarize
        {"role": "user", "content": str(history_list)}                                                               # Converts the long history list into a text block
    ]
    return send_to_cloud_ai(compression_payload)                                                                     # Sends the summary request to Groq and returns the Fact Sheet


def calculate_math(expression):                                                                                      # Defines the Math worker function
    return eval(str(expression))                                                                                     # Uses Python's native calculator to solve the string equation


def perform_web_search(query):                                                                                       # Defines the live DuckDuckGo worker function

    print(f"\n[SERVER LOG] Searching the LIVE NEWS for: '{query}'")                                                  # Prints a debugging log to the terminal

    try:                                                                                                             # Starts a safe execution block
        with DDGS() as ddgs:                                                                                         # Opens a connection to DuckDuckGo
            results = list(ddgs.news(query, max_results=3))                                                          # Grabs the top 3 live news articles
        context = ""                                                                                                 # Creates a blank string to hold the news data

        for res in results:                                                                                          # Loops through each of the 3 articles
            context += (f"Source: {res['title']}\nDate Published: {res.get('date', 'Recent')}"
                        f"\nSnippet: {res['body']}\n\n")                                                             # Formats and stacks the news data
        return context                                                                                               # Returns the fully formatted news string

    except Exception as e:                                                                                           # Catches errors like rate limits or no internet
        print(f"[SERVER LOG] Web search failed: {e}")                                                                # Prints the error to the terminal
        return "No web data could be retrieved."                                                                     # Returns a safe fallback message


# === KEY STEP 6: THE API ENDPOINT (FRONT DOOR) ===
@app.post("/chat", response_model=SwarmResponse)                                                                # Opens the /chat URL and enforces the output contract
async def chat_with_swarm(request: UserRequest):                                                                     # Creates the async function that accepts the user's ticket

    print(f"\n--- NEW REQUEST FROM [{request.user_id}] ---")                                                         # Prints a log indicating a new user request arrived

    # === KEY STEP 7: MEMORY MANAGEMENT ===
    if request.user_id not in active_sessions:                                                                       # Checks if the user is completely new
        active_sessions[request.user_id] = [                                                                         # Creates a brand new chat history list for them
            {"role": "system", "content": "You are the Senior Synthesis AI. "
                                          "Answer clearly using the provided system data."}                          # Inserts the base personality
        ]

    user_history = active_sessions[request.user_id]                                                                  # Pulls the specific user's folder from the cabinet
    user_history.append({"role": "user", "content": request.prompt})                                                 # Appends their new question to the bottom of the list

    if len(user_history) > 6:                                                                                        # Checks if the file is getting too heavy (over 6 messages)

        print(f"[SERVER LOG] Compressing memory for {request.user_id}...")                                           # Prints a log indicating compression is starting
        compressed_text = compress_memory(user_history[:-1])                                                         # Sends everything except the newest message to the Janitor

        active_sessions[request.user_id] = [                                                                         # Rebuilds the user's history list
            user_history[0],                                                                                         # Keeps the system prompt
            {"role": "system", "content": f"Fact Sheet:\n{compressed_text}"},                                        # Inserts the new Fact Sheet
            user_history[-1]                                                                                         # Keeps the newest question
        ]

        user_history = active_sessions[request.user_id]                                                              # Refreshes the local variable with the newly compressed list


    # === KEY STEP 8: PIPELINE ROUTING ===
    decision = get_manager_decision(request.prompt)                                                                  # Asks the Manager which departments to open

    print(f"[SERVER LOG] Manager routed to: {decision}")                                                             # Prints the Manager's decision to the terminal

    temp_memory = user_history.copy()                                                                                # Creates a temporary clone of the memory so we don't pollute the UI
    collected_context = ""                                                                                           # Creates a blank clipboard to hold backend data

    if "RAG" in decision:                                                                                            # Checks if RAG was chosen
        results = collection.query(query_texts=[request.prompt], n_results=1)                                        # Searches ChromaDB for the closest match
        collected_context += f"<internal_company_data>\n{results['documents'][0][0]}\n</internal_company_data>\n\n"   # Wraps data in XML and staples it to clipboard

    if "WEB" in decision:                                                                                            # Checks if WEB was chosen
        optimized_query = get_search_query(request.prompt)                                                           # Asks the Micro-Agent to clean the search topic
        if optimized_query != "NONE":                                                                                # Ensures the topic isn't empty
            live_data = perform_web_search(optimized_query)                                                          # Scrapes DuckDuckGo for live news
            collected_context += f"<live_web_data query='{optimized_query}'>\n{live_data}\n</live_web_data>\n\n"     # Wraps data in XML and staples it to clipboard

    if "MATH" in decision:                                                                                           # Checks if MATH was chosen
        math_expression = re.sub(r'[^0-9\+\-\*\/\(\)\.]', '', request.prompt)                            # Uses Regex Bouncer to delete all letters
        print(f"[SERVER LOG] MATH Department extracted equation: '{math_expression}'")                               # Prints the cleaned equation

        try:                                                                                                         # Starts a safe execution block
            answer = calculate_math(math_expression)                                                                 # Uses Python to solve the math
            print(f"[SERVER LOG] MATH Department calculated: {answer}")                                              # Prints the final answer
            collected_context += (f"<math_calculation>"
                                  f"\nThe exact mathematical answer to the user's equation is: {answer}"
                                  f"\n</math_calculation>\n\n")                                                      # Wraps answer in XML and staples it

        except Exception as e:                                                                                       # Catches division by zero or invalid math
            print(f"[SERVER LOG] MATH failed: {e}")                                                                  # Prints the error to the terminal


    # === KEY STEP 9: FINAL SYNTHESIS (BUG FIXED HERE) ===
    if collected_context != "":                                                                                      # Checks if ANY data was collected on the clipboard (Fixed Indentation!)

        final_prompt = f"""You are a helpful Enterprise AI. Read the XML data provided below. 
You MUST address every single piece of data provided in the XML tags. 
Checklist:
- Did you answer the company data question?
- Did you answer the live web question?
- Did you explicitly state the math calculation result?
Do not mention the XML tags or this checklist to the user. Just provide the answers.

SYSTEM DATA:
{collected_context}

USER PROMPT: {request.prompt}"""                                                                                     # Builds a massive instruction packet with the XML and Checklist

        temp_memory[-1] = {"role": "user", "content": final_prompt}                                                  # Swaps the user's basic question with this massive packet in the cloned memory

    ai_words = send_to_cloud_ai(temp_memory)                                                                         # Sends the cloned memory to Groq for the final answer

