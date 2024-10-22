import requests
import json
import os

# Configuration Constants
API_URL = 'https://88aa-120-151-185-163.ngrok-free.app/v1/chat/completions'
MODELS_URL = 'https://88aa-120-151-185-163.ngrok-free.app/v1/models/'
DEFAULT_SYSTEM_PROMPT = 'You are a helpful assistant.'

# Global State
streaming = False
system_prompt = DEFAULT_SYSTEM_PROMPT
current_model = None
available_models = []

# Model Name Mapping
model_name_mapping = {
    'llama-3.2-1b-instruct': 'Llama 3.2',
    'l3-evil-stheno-v3.2-8b': 'Evil Stheno',
}

# Utility Functions
def clear_terminal():
    """Clear the terminal for both Windows and Unix-based systems."""
    os.system('cls' if os.name == 'nt' else 'clear')

def display_help():
    """Display the list of available slash commands."""
    help_message = """
    Available Commands:
    /help       - View available commands
    /models     - List available models
    /usemodel   - Change the current model by number
    /system     - Set the system prompt
    /assistant  - Send an assistant message
    /stream     - Toggle streaming on and off
    /clear      - Clear the terminal
    /reset      - Clear both the terminal and conversation context
    /info       - View the current settings and statuses
    /exit       - Exit the chat
    """
    print(help_message)

def display_info():
    """Show the current settings and statuses."""
    info_message = f"""
    Current Settings:
    Streaming: {'On' if streaming else 'Off'}
    System Prompt: {system_prompt}
    Current Model: {current_model}
    """
    print(info_message)

# Model Communication Functions
def fetch_available_models():
    """Fetch the list of available models from the server."""
    global available_models
    try:
        response = requests.get(MODELS_URL)
        response.raise_for_status()
        available_models = response.json().get('data', [])
    except requests.RequestException as e:
        print(f"Error fetching models: {e}")

def list_available_models():
    """List the available models to the user."""
    if available_models:
        print("Available Models:")
        for idx, model in enumerate(available_models, start=1):
            print(f"{idx}. {model['id']}")
    else:
        print("No models available. Use /models to fetch them.")

def change_model_by_number(model_number):
    """Change the current model based on the user's selection number."""
    global current_model
    try:
        model_index = int(model_number) - 1
        if 0 <= model_index < len(available_models):
            current_model = available_models[model_index]['id']
        else:
            print(f"Error: Model number {model_number} is out of range.")
    except ValueError:
        print("Error: Please enter a valid number.")

def set_default_model():
    """Automatically set the first available model as the default."""
    if available_models:
        change_model_by_number(1)

def handle_streaming_response(response):
    """Handle the streaming response from the model."""
    print(f"{get_model_display_name(current_model)}: ", end='', flush=True)
    try:
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8').strip()
                if decoded_line.startswith('data: '):
                    chunk = decoded_line[6:].strip()
                    if chunk == "[DONE]":
                        break
                    try:
                        chunk_data = json.loads(chunk)
                        if 'choices' in chunk_data:
                            text_delta = chunk_data['choices'][0].get('delta', {}).get('content', '')
                            print(text_delta, end='', flush=True)
                    except json.JSONDecodeError:
                        print(f"\nError decoding JSON: {chunk}")
        print()  # Newline after streaming ends
    except Exception as e:
        print(f"Error while streaming: {e}")

def get_model_display_name(model_id):
    """Get the simplified display name for the model."""
    return model_name_mapping.get(model_id, model_id)  # Fallback to original name if not mapped

def send_message_to_model(messages):
    """Send the conversation messages to the model API."""
    headers = {'Content-Type': 'application/json'}
    data = {
        'model': current_model,
        'messages': messages,
        'stream': streaming
    }

    try:
        response = requests.post(API_URL, headers=headers, json=data, stream=streaming)
        response.raise_for_status()
        if streaming:
            handle_streaming_response(response)
            return None
        return response.json()
    except requests.RequestException as e:
        return {"error": str(e)}

# Command Handlers
def process_command(command, arg, conversation):
    """Process slash commands entered by the user."""
    global streaming, system_prompt
    command_handlers = {
        '/help': display_help,
        '/models': lambda: (fetch_available_models(), list_available_models()),
        '/usemodel': lambda: change_model_by_number(arg) if arg else print("Error: No model number specified."),
        '/system': lambda: set_system_prompt(arg, conversation),
        '/assistant': lambda: send_assistant_message(arg, conversation),
        '/stream': toggle_streaming,
        '/clear': clear_terminal,
        '/reset': reset_conversation,
        '/info': display_info,
    }

    handler = command_handlers.get(command)
    if handler:
        handler()
    else:
        print("Unknown command. Type '/help' to view commands.")

def set_system_prompt(arg, conversation):
    """Set the system prompt and update the conversation context."""
    global system_prompt
    if arg:
        system_prompt = arg
        conversation[0]['content'] = system_prompt
        print(f"System Prompt: {system_prompt}")
    else:
        print("Error: No message provided for /system command.")

def send_assistant_message(arg, conversation):
    """Send a message as the assistant."""
    if arg:
        assistant_message = f"{get_model_display_name(current_model)}: {arg}"
        print(assistant_message)  # Display the message as if sent by the model
        conversation.append({'role': 'assistant', 'content': arg})
    else:
        print("Error: No message provided for /assistant command.")

def toggle_streaming():
    """Toggle the streaming setting."""
    global streaming
    streaming = not streaming
    print(f"Streaming is now {'on' if streaming else 'off'}.")

def reset_conversation(conversation):
    """Clear both the terminal and conversation context."""
    clear_terminal()
    conversation.clear()
    conversation.append({'role': 'system', 'content': system_prompt})
    print("Context and terminal cleared.")

# Main Loop
def main():
    """Main program loop for the chat interface."""
    print("Interact with the model. Use '/help' for commands and 'exit' to stop.")

    conversation = [{'role': 'system', 'content': system_prompt}]
    
    # Fetch available models and set the default model
    fetch_available_models()
    set_default_model()

    while True:
        user_input = input("You: ")

        if user_input.lower() == 'exit':
            break

        if user_input.startswith('/'):
            command_parts = user_input.split(' ', 2)
            command = command_parts[0]
            command_arg = command_parts[1] if len(command_parts) > 1 else ""
            process_command(command, command_arg, conversation)
        else:
            conversation.append({'role': 'user', 'content': user_input})
            model_response = send_message_to_model(conversation)

            if not streaming:
                if 'error' in model_response:
                    print(f"Error: {model_response['error']}")
                else:
                    assistant_response = model_response.get('choices', [{}])[0].get('message', {}).get('content', 'No response')
                    model_message = f"{get_model_display_name(current_model)}: {assistant_response}"
                    print(model_message)
                    conversation.append({'role': 'assistant', 'content': assistant_response})

# Entry Point
if __name__ == "__main__":
    main()
