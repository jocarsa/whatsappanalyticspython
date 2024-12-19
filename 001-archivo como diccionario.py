import re
import json

def parse_whatsapp_chat(file_path):
    parsed_messages = []
    
    # Regular expression to match the WhatsApp chat format
    message_pattern = re.compile(r"\[(\d{2}/\d{2}/\d{2}), (\d{2}:\d{2}:\d{2})\] ([^:]+): (.+)")

    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            # Check if the line matches the expected pattern
            match = message_pattern.match(line)
            if match:
                date, time, name, message = match.groups()
                parsed_messages.append({
                    "date": date,
                    "hour": time,
                    "name": name,
                    "message": message
                })

    return parsed_messages

# Usage example:
if __name__ == "__main__":
    # Specify the path to your WhatsApp chat export text file
    chat_file = "_chat.txt"
    parsed_data = parse_whatsapp_chat(chat_file)

    # Print or save the parsed messages
    print(json.dumps(parsed_data, indent=4, ensure_ascii=False))
