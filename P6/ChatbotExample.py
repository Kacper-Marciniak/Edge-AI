from datetime import datetime
from llama_cpp import Llama

MODEL_PATH = "./qwen_local/qwen2.5-0.5b-instruct-q4_k_m.gguf"

USER_NAME = "Jan Kowalski"
SYSTEM_PROMPT = f"""
You are a helpful assistant. You are designed to assist user with technical questions and provide accurate information.
Answer briefly and accurately.
Refer to yourself as \'Assistant\'.
User's name is {USER_NAME}. {USER_NAME} is a student at the Wrocław University of Science and Technology. {USER_NAME} is studying Mechatronics. {USER_NAME} is interested in robotics, AI, and embedded systems.
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


if __name__ == "__main__":

    print("Chat started.","Type 'exit' to quit.","Type 'clear' to clear conversation.\n", sep="\n")

    while True:

        user_input = input("You: ").strip()

        if user_input.lower() == "exit":
            break

        if user_input.lower() == "clear":
            messages = [messages[0]]
            print("Conversation cleared.\n")
            continue

        answer = model_inference(user_input)

        print(f"\nAssistant: {answer}\n")