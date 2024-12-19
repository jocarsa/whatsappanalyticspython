import re
import json
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from collections import Counter, defaultdict
from matplotlib.colors import LinearSegmentedColormap
from flask import Flask, request, render_template, redirect, url_for, session
import os
import uuid

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Replace with a secure secret key
UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "static/charts"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

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

def plot_messages_pie_chart(parsed_messages, output_file):
    # Count messages by each sender
    name_counts = Counter(message["name"] for message in parsed_messages)
    
    # Prepare data for the pie chart
    labels = name_counts.keys()
    sizes = name_counts.values()
    
    # Create the pie chart
    plt.figure(figsize=(8, 8))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, wedgeprops={'edgecolor': 'black'})
    plt.title("Number of Messages by Person in Conversation")
    plt.savefig(output_file)
    plt.close()

def plot_messages_per_hour(parsed_messages, output_file):
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
    plt.savefig(output_file)
    plt.close()

def plot_messages_calendar_heatmap(parsed_messages, output_file):
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
    plt.savefig(output_file)
    plt.close()

def plot_messages_per_weekday(parsed_messages, output_file):
    # Convert messages to a DataFrame
    df = pd.DataFrame(parsed_messages)
    df["date"] = pd.to_datetime(df["date"], format="%d/%m/%y")

    # Count messages per weekday
    weekday_counts = df["date"].dt.day_name().value_counts()
    weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    counts = [weekday_counts.get(day, 0) for day in weekday_order]

    # Create the bar chart
    plt.figure(figsize=(10, 6))
    plt.bar(weekday_order, counts, edgecolor='black')
    plt.xlabel("Weekday")
    plt.ylabel("Number of Messages")
    plt.title("Number of Messages per Weekday")
    plt.xticks(rotation=45)
    plt.savefig(output_file)
    plt.close()

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())

    user_output_folder = os.path.join(OUTPUT_FOLDER, session['session_id'])
    os.makedirs(user_output_folder, exist_ok=True)

    if request.method == 'POST':
        file = request.files['file']
        if file:
            file_path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(file_path)

            parsed_data = parse_whatsapp_chat(file_path)

            # Generate all charts
            plot_messages_pie_chart(parsed_data, os.path.join(user_output_folder, "messages_by_person.png"))
            plot_messages_per_hour(parsed_data, os.path.join(user_output_folder, "messages_per_hour.png"))
            plot_messages_calendar_heatmap(parsed_data, os.path.join(user_output_folder, "messages_calendar_heatmap.png"))
            plot_messages_per_weekday(parsed_data, os.path.join(user_output_folder, "messages_per_weekday.png"))

            return redirect(url_for('display_charts'))

    return render_template('upload.html')

@app.route('/charts')
def display_charts():
    user_output_folder = os.path.join(OUTPUT_FOLDER, session['session_id'])
    images = [
        f"charts/{session['session_id']}/messages_by_person.png",
        f"charts/{session['session_id']}/messages_per_hour.png",
        f"charts/{session['session_id']}/messages_calendar_heatmap.png",
        f"charts/{session['session_id']}/messages_per_weekday.png"
    ]
    return render_template('charts.html', images=images)

if __name__ == "__main__":
    app.run(debug=True)
