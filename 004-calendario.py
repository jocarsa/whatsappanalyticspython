import re
import json
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from collections import Counter, defaultdict
from matplotlib.colors import LinearSegmentedColormap

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

def plot_messages_calendar_heatmap(parsed_messages):
    # Convert messages to a DataFrame
    df = pd.DataFrame(parsed_messages)
    df["date"] = pd.to_datetime(df["date"], format="%d/%m/%y")

    # Count messages per day
    daily_counts = df["date"].value_counts().sort_index()

    # Create a complete date range from first to last message
    full_date_range = pd.date_range(start=daily_counts.index.min(), end=daily_counts.index.max())
    daily_counts = daily_counts.reindex(full_date_range, fill_value=0)

    # Reshape data for heatmap (weeks vs days)
    num_weeks = (len(daily_counts) + 6) // 7  # Ensure enough rows for all days
    padded_counts = list(daily_counts.values) + [0] * (num_weeks * 7 - len(daily_counts))
    heatmap_data = np.array(padded_counts).reshape(num_weeks, 7)

    # Create the heatmap
    plt.figure(figsize=(12, 6))
    cmap = LinearSegmentedColormap.from_list("heatmap", ["#ffffff", "#ff9999", "#ff0000"])
    plt.imshow(heatmap_data, cmap=cmap, aspect="auto", origin="lower")
    plt.colorbar(label="Number of Messages")
    plt.title("Messages Per Day (Calendar Heatmap)")
    plt.xlabel("Day of Week")
    plt.ylabel("Week")
    plt.xticks(ticks=range(7), labels=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])
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

    # Plot calendar heatmap
    plot_messages_calendar_heatmap(parsed_data)
