from datetime import datetime
from llama_cpp import Llama

MODEL_PATH = "./qwen_local/qwen2.5-0.5b-instruct-q4_k_m.gguf"

USER_NAME = "Jan Kowalski"
SYSTEM_PROMPT = f"""
You are a helpful assistant. You are designed to assist user with technical questions and provide accurate information.
Answer briefly and accurately.
Refer to yourself as \'Assistant\'.
You have access to the sensors of the Raspberry Pi Sense HAT, which can provide information about temperature, pressure, and humidity.
"""

MAX_HISTORY = 10

print("Loading local model...")
model = Llama(
    model_path=MODEL_PATH,
    n_ctx=8192,
    n_threads=4,
    verbose=False,
)
print("Model ready.")

messages = [
    {
        "role": "system",
        "content": SYSTEM_PROMPT
    }
]

def model_inference(user_prompt: str) -> str:

    global messages

    messages.append(
        {
            "role": "user",
            "content": user_prompt
        }
    )

    if len(messages) > MAX_HISTORY * 2 + 1:
        messages = [messages[0]] + messages[-MAX_HISTORY * 2:]

    print(datetime.now().strftime("[%Y-%m-%d %H:%M:%S]"),"Generating response for user prompt:", user_prompt)

    response = model.create_chat_completion(
        messages=messages,
        max_tokens=512,
        temperature=0
    )

    answer = response["choices"][0]["message"]["content"]

    messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )

    print(datetime.now().strftime("[%Y-%m-%d %H:%M:%S]"),"Finished inference.")

    return answer

from sense_hat import SenseHat
from queue import Queue
from threading import Thread
import sqlite3
import time

def init_db():
    db = sqlite3.connect("example.db")
    db.execute(f"CREATE TABLE IF NOT EXISTS logs(id INTEGER PRIMARY KEY,pressure REAL, temperature REAL, humidity REAL)")
    db.commit()
    db.close()

def add_record(record: dict):
    db = sqlite3.connect("example.db")
    db.execute(
        f"INSERT OR IGNORE INTO logs (pressure, temperature, humidity) VALUES (?, ?, ?)",
        (record["pressure"],record["temperature"],record["humidity"])
    )
    db.commit()
    db.close()

def get_last_record():
    db = sqlite3.connect("example.db")
    cursor = db.cursor()
    cursor.execute(
        """
        SELECT pressure, temperature, humidity
        FROM logs
        ORDER BY id DESC
        LIMIT 1
        """
    )
    data = cursor.fetchall()
    if data: return f"Pressure: {data[0][0]:.1f}, Temperature: {data[0][1]:.1f}, Humidity: {data[0][2]:.1f}"
    else: return None

def run_chatbot(queue_answer: Queue):
    global messages
    
    print("Chat started.","Type 'exit' to quit.","Type 'clear' to clear conversation.\n", sep="\n")

    while True:

        user_input = input("You: ").strip()

        if user_input.lower() == "exit":
            queue_answer.put("exit")
            break

        if user_input.lower() == "clear":
            messages = [messages[0]]
            print("Conversation cleared.\n")
            continue

        sensor_data = get_last_record()
        user_input += f"\nCurrent sensor data: {sensor_data}"
        answer = model_inference(user_input)

        queue_answer.put(answer)

        print(f"\nAssistant: {answer}\n")

def display_message_in_loop(hat: SenseHat, queue: Queue):
    hat.clear()

    while True:

        message = queue.get()
        if message == "exit":
            break
        else:
            hat.show_message(message, text_colour=[255, 0, 0], back_colour=[0, 0, 0], scroll_speed=0.025)
            queue.task_done()

def get_data_from_sensors(hat: SenseHat):
    init_db()
    while True:

        sensor_data = {
            "temperature": hat.get_temperature(),
            "pressure": hat.get_pressure(),
            "humidity": hat.get_humidity()
        }
        add_record(sensor_data)

        time.sleep(5)

if __name__ == "__main__":
    hat = SenseHat()
    queue_display = Queue()

    thread_chatbot = Thread(target=run_chatbot, args=(queue_display,))
    thread_display = Thread(target=display_message_in_loop, args=(hat, queue_display,))
    thread_sensors = Thread(target=get_data_from_sensors, args=(hat,))

    thread_chatbot.start()
    thread_display.start()
    thread_sensors.start()

    thread_chatbot.join()
    thread_display.join()
    thread_sensors.join()