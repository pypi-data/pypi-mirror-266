from prompt_toolkit import print_formatted_text, HTML
from prompt_toolkit.styles import Style
from prompt_toolkit import prompt
from prompt_toolkit.history import InMemoryHistory
import requests
import json
import argparse


style = Style.from_dict({
    "welcome": "bold underline",
    "question": "fg:#00FF00",
    "generated_text": "fg:#FF0000",
    "error": "fg:#FF0000",
    "prompt": "fg:#FFA500",
    "prompt_text": "fg:#FFFFFF",
})

def generate_text(question, url):
    payload = {
        "text": question
    }

    headers = {
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload), stream=True)

        if response.status_code == 200:
            print_formatted_text(HTML("<ansired>B-chat:</ansired>"), style=style)
          
           
            # Print response character by character
            for chunk in response.iter_content(chunk_size=1):
                print_formatted_text(chunk.decode(), end='', style=style)
                
            print()
        else:
            print_formatted_text(HTML("<ansired>Error:</ansired>"), HTML(f"<ansigreen>{response.text}</ansigreen>"), style=style)
    except requests.exceptions.ConnectionError:
        print_formatted_text(HTML("<ansired>Connection issue! Please try again.</ansired>"))
        pass

    # # Execute the curl command to get the answer
    # process = subprocess.Popen(['curl', '-X', 'POST', 'http://10.101.15.172:8002/llm-process', '-H', 'Content-Type: application/json', '-d', f'{{"text": "{question}"}}', '--no-buffer'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    # # Initialize variables to track the first word arrival time and full response
    # first_word_received = False
    # first_word_time = None
    # full_response = ""

    # while True:
    #     # Read a single character from the stream
    #     char = process.stdout.read(1)
    #     if not char:
    #         break
    #     # Check if it's a word character and update first word arrival time
    #     if char.isalnum() and not first_word_received:
    #         first_word_received = True
    #         first_word_time = datetime.now()
    #     # Append character to full response
    #     full_response += char
    #     # Print the character
    #     print(char, end='', flush=True)


# def generate_text(question, url):
#     payload = {
#         "text": question
#     }
 
#     headers = {
#         "Content-Type": "application/json"
#     }

#     response = requests.post(url, headers=headers, data=json.dumps(payload))

#     if response.status_code == 200:
#         print_formatted_text(HTML("<ansired>B-chat:</ansired>"), style=style)
#         for char in response.text:
#             print_formatted_text(char, end='', style=style)
#             sleep(0.05)
#     else:
#         print_formatted_text(HTML("<ansired>Error:</ansired>"), HTML(f"<ansigreen>{response.text}</ansigreen>"), style=style)


def main():
    print_formatted_text(HTML("<ansibrightblue>Welcome to Text Generation Interface!</ansibrightblue>"), style=style)
    print_formatted_text(HTML("<ansiblue>Enter your question or type 'quit' to exit.</ansiblue>"), style=style)

    parser = argparse.ArgumentParser(description='Text Generation Interface')
    parser.add_argument('--url', type=str,
                        help='URL for text generation service', required=True)

    args = parser.parse_args()
    
    print_formatted_text(HTML(f"<ansicyan>Connected to {args.url}</ansicyan>"), style=style)

    history = InMemoryHistory()

    while True:
        try:
            question = prompt("\nPrompt: ", style=style, history=history)

            if question.lower() == 'quit' or question.lower() == 'exit':
                print_formatted_text(HTML(f"<ansibrightgreen>Goodbye!</ansibrightgreen>"), style=style)
                break

            generate_text(question, args.url)
        except KeyboardInterrupt:
            print_formatted_text(HTML(f"<ansibrightgreen>Goodbye!</ansibrightgreen>"), style=style)
            break

if __name__ == "__main__":
    main()
