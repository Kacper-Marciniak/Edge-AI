import json
from llama_cpp import Llama
from SqlDatabase import analyze_logs, init_sql_database, load_events_from_json

MODEL_PATH = "./qwen_local/qwen2.5-0.5b-instruct-q4_k_m.gguf"

# Ładowanie lokalnego modelu Qwen

print("Loading local model...")
model = Llama(
    model_path=MODEL_PATH,
    n_ctx=8192,
    n_threads=4,    
    temperature=0,
    verbose=False,
)
print("Model ready.")

SYSTEM_PROMPT = """
You are a local system auditor.
You are generating a technical report for a user.
The report must include:
- system status
- total number of events
- number of INFO/WARNING/ERROR events
- recent critical events
- brief conclusions
Do not make up any data.
Use only the information provided.

Format:

STATUS:
...

STATISTICS:
...

CRITICAL EVENTS:
...

CONCLUSIONS:
...
"""

# Agent LLM - generacja raportu dla użytkownika na podstawie analizy logów

def generate_report(report: dict):

    context = json.dumps(
        report,
        ensure_ascii=False,
        indent=2
    )

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": f"""
Results of log analysis:

{context}

Generate report.
"""
        }
    ]

    response = model.create_chat_completion(
        messages=messages,
        max_tokens=2048,
        temperature=0
    )
    
    answer = response["choices"][0]["message"]["content"]

    return answer

### MAIN

if __name__ == "__main__":

    init_sql_database() # Inicjalizacja bazy danych SQLite
    load_events_from_json() # Wczytanie eventów z pliku JSON do bazy danych SQLite
    print("Analyzing logs...")

    report = analyze_logs() # Surowy raport z bazy danych
    final_report = generate_report(report) # Raport wygenerowany przez model LLM

    print("\n====================")
    print("SYSTEM REPORT")
    print("====================\n")

    print(final_report)