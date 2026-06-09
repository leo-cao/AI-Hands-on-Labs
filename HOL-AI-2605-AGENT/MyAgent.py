from ollama import chat
from ollama import ChatResponse

while True:
    user_input = input("YOU: ").strip()
    if user_input.lower() == 'exit' or user_input.lower() == 'quit':
        print("Exiting the chat. Goodbye!")
        break

    response: ChatResponse = chat(model='gemma4', messages=[
      {
        'role': 'user',
        'content': user_input,
      },
    ])

    print(f"AGENT: {response['message']['content']}")
