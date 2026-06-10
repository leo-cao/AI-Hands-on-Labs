# VxRail AIOPS Agent with Memory
# By Leo Cao, June 10, 2026
# Version: 0.1

from ollama import Client
from ollama import ChatResponse

client = Client()

# History Memeroy
messages=[
      {
        'role': 'system',
        'content': 'You are a VxRail AIOPS Agent. You will assist users with VxRail related questions and issues. Provide accurate and helpful information based on the user\'s input.',
      },
]


while True:
    user_input = input("USER: ").strip()
    if user_input.lower() == 'exit' or user_input.lower() == 'quit':
        print("Exiting the chat. Goodbye!")
        break

    # Append user input to the message history    
    messages.append({
        'role': 'user',
        'content': user_input,
      })

    response = client.chat( 
        model='gemma4', 
        messages=messages, # Pass the entire message history to the model
        stream=False,
        options={'temperature': 0.5}
        )
    assistant_message = response.message
    messages.append(assistant_message) # Append assistant response to the message history

    print(f"VxRail AIOPS AGENT: {assistant_message['content']}\n")
