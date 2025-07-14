import psutil
import tkinter as tk
from tkinter import ttk
from datetime import datetime
import json
import os
import subprocess
import matplotlib.pyplot as plt
import csv
from tkinter import messagebox

INTERFACE_NAME = "Wi-Fi"  # Change if needed, e.g., "wlan0"
RECORD_FILE = "data_usage_record.json"
PROCESS_LOG_FILE = "app_usage_log.json"

def bytes_to_mb(bytes_val):
    return round(bytes_val / (1024 * 1024), 2)

def get_wifi_data():
    net_io = psutil.net_io_counters(pernic=True)
    if INTERFACE_NAME in net_io:
        data = net_io[INTERFACE_NAME]
        sent = bytes_to_mb(data.bytes_sent)
        recv = bytes_to_mb(data.bytes_recv)
        return sent, recv
    else:
        return 0.0, 0.0

def save_today_data(sent, recv):
    today = datetime.now().strftime("%Y-%m-%d")
    month = datetime.now().strftime("%Y-%m")
    record = {}

    if os.path.exists(RECORD_FILE):
        with open(RECORD_FILE, "r") as f:
            record = json.load(f)

    if month not in record:
        record[month] = {}
    record[month][today] = {
        "sent_MB": sent,
        "recv_MB": recv
    }

    with open(RECORD_FILE, "w") as f:
        json.dump(record, f, indent=4)

def get_active_internet_processes():
    try:
        output = subprocess.check_output("netstat -b -n -o", shell=True, text=True, stderr=subprocess.DEVNULL)
        lines = output.strip().split('\n')
        processes = set()

        for line in lines:
            if "TCP" in line or "UDP" in line:
                parts = line.split()
                if len(parts) >= 5:
                    pid = parts[4]
                    processes.add(pid)

        app_list = []
        for pid in processes:
            try:
                p = psutil.Process(int(pid))
                app_list.append(p.name())
            except:
                pass

        return list(set(app_list))[:10]  # Top 10 processes

    except Exception:
        return ["(Run as Administrator for full app list)"]

def log_apps(apps):
    today = datetime.now().strftime("%Y-%m-%d")
    record = {}

    if os.path.exists(PROCESS_LOG_FILE):
        with open(PROCESS_LOG_FILE, "r") as f:
            record = json.load(f)

    if today not in record:
        record[today] = []

    record[today].append({
        "time": datetime.now().strftime("%H:%M:%S"),
        "apps": apps
    })

    with open(PROCESS_LOG_FILE, "w") as f:
        json.dump(record, f, indent=4)

def update_data():
    sent, recv = get_wifi_data()
    total = round(sent + recv, 2)
    sent_label.config(text=f"Sent: {sent} MB")
    recv_label.config(text=f"Received: {recv} MB")
    total_label.config(text=f"Total Today: {total} MB")
    save_today_data(sent, recv)

    apps = get_active_internet_processes()
    app_text.set("\n".join(apps))
    log_apps(apps)

    root.after(10000, update_data)  # Refresh every 10 seconds

def show_graph():
    if not os.path.exists(RECORD_FILE):
        messagebox.showinfo("Info", "No usage data found yet.")
        return

    with open(RECORD_FILE, "r") as f:
        data = json.load(f)

    usage_by_day = {}
    for month in data:
        for day in data[month]:
            total = data[month][day]["sent_MB"] + data[month][day]["recv_MB"]
            usage_by_day[day] = round(total, 2)

    days = sorted(usage_by_day.keys())
    totals = [usage_by_day[d] for d in days]

    plt.figure(figsize=(10, 5))
    plt.plot(days, totals, marker='o', color='blue')
    plt.title("Daily Hotspot Usage (MB)")
    plt.xlabel("Date")
    plt.ylabel("Total MB")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.grid(True)
    plt.show()

def convert_to_csv():
    # Convert daily MB usage
    if os.path.exists(RECORD_FILE):
        with open(RECORD_FILE, "r") as f:
            data = json.load(f)

        with open("daily_usage.csv", "w", newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Date", "Sent_MB", "Received_MB", "Total_MB"])
            for month in data:
                for day in data[month]:
                    s = data[month][day]["sent_MB"]
                    r = data[month][day]["recv_MB"]
                    writer.writerow([day, s, r, s + r])

    # Convert app log
    if os.path.exists(PROCESS_LOG_FILE):
        with open(PROCESS_LOG_FILE, "r") as f:
            logs = json.load(f)

        with open("app_log.csv", "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Date", "Time", "App"])
            for day in logs:
                for entry in logs[day]:
                    time = entry["time"]
                    for app in entry["apps"]:
                        writer.writerow([day, time, app])

    messagebox.showinfo("Success", "Logs exported to daily_usage.csv and app_log.csv")

def show_app_table():
    win = tk.Toplevel(root)
    win.title("App Network Usage Log")
    win.geometry("400x400")

    tree = ttk.Treeview(win, columns=("Time", "App"), show="headings")
    tree.heading("Time", text="Time")
    tree.heading("App", text="App Name")
    tree.pack(fill="both", expand=True)

    if os.path.exists(PROCESS_LOG_FILE):
        with open(PROCESS_LOG_FILE, "r") as f:
            logs = json.load(f)

        today = datetime.now().strftime("%Y-%m-%d")
        if today in logs:
            for entry in logs[today]:
                t = entry["time"]
                for app in entry["apps"]:
                    tree.insert("", "end", values=(t, app))

# try:
#     import tkinter.messagebox
# except ImportError:
#     import tkMessageBox as tkinter.messagebox

# --- GUI Setup ---
root = tk.Tk()
root.title("Today's Hotspot Usage Tracker")
root.geometry("350x500")

sent_label = tk.Label(root, text="Sent: 0 MB", font=("Arial", 14))
recv_label = tk.Label(root, text="Received: 0 MB", font=("Arial", 14))
total_label = tk.Label(root, text="Total Today: 0 MB", font=("Arial", 16, "bold"))
app_title = tk.Label(root, text="Apps using Internet (topper):", font=("Arial", 12, "bold"))
app_text = tk.StringVar()
app_list = tk.Label(root, textvariable=app_text, font=("Arial", 11), justify="left")

sent_label.pack(pady=5)
recv_label.pack(pady=5)
total_label.pack(pady=10)
app_title.pack(pady=5)
app_list.pack(pady=5)

btn_graph = tk.Button(root, text="📊 Show Usage Graph", command=show_graph)
btn_graph.pack(pady=5)

btn_export = tk.Button(root, text="💾 Export Logs to CSV", command=convert_to_csv)
btn_export.pack(pady=5)

btn_table = tk.Button(root, text="📋 Show App Table (Today)", command=show_app_table)
btn_table.pack(pady=5)

update_data()
root.mainloop()
