import re
import json
import matplotlib.pyplot as plt
from collections import Counter, defaultdict

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

def plot_messages_pie_chart(parsed_messages):
    # Count messages by each sender
    name_counts = Counter(message["name"] for message in parsed_messages)
    
    # Prepare data for the pie chart
    labels = name_counts.keys()
    sizes = name_counts.values()
    
    # Create the pie chart
    plt.figure(figsize=(8, 8))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, wedgeprops={'edgecolor': 'black'})
    plt.title("Number of Messages by Person in Conversation")
    plt.show()

def plot_messages_per_hour(parsed_messages):
    # Count messages per hour
    hour_counts = defaultdict(int)
    for message in parsed_messages:
        hour = int(message["hour"].split(":")[0])
        hour_counts[hour] += 1

    # Prepare data for the bar chart
    hours = list(range(24))
    counts = [hour_counts[hour] for hour in hours]

    # Create the bar chart
    plt.figure(figsize=(10, 6))
    plt.bar(hours, counts, edgecolor='black')
    plt.xticks(hours)
    plt.xlabel("Hour of the Day")
    plt.ylabel("Number of Messages")
    plt.title("Number of Messages per Hour")
    plt.show()

# Usage example:
if __name__ == "__main__":
    # Specify the path to your WhatsApp chat export text file
    chat_file = "whatsapp_chat.txt"
    parsed_data = parse_whatsapp_chat(chat_file)

    # Print or save the parsed messages
    print(json.dumps(parsed_data, indent=4, ensure_ascii=False))

    # Plot the pie chart
    plot_messages_pie_chart(parsed_data)

    # Plot messages per hour
    plot_messages_per_hour(parsed_data)
