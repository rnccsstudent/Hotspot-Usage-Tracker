import psutil
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json
import os
import subprocess
import matplotlib.pyplot as plt
import csv
import winsound

start_time = datetime.now()
DAILY_REPORT_FILE = "daily_report.txt"
INTERFACE_NAME = "Wi-Fi"
RECORD_FILE = "data_usage_record.json"
PROCESS_LOG_FILE = "app_usage_log.json"
DAILY_LIMIT_MB = 500

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

        return list(set(app_list))[:10]

    except Exception:
        return ["(Run as Administrator for full app list)"]

def log_apps(apps):
    today = datetime.now().strftime("%Y-%m-%d")
    record = {}

    if os.path.exists(PROCESS_LOG_FILE):
        with open(PROCESS_LOG_FILE, "r") as f:
            record = json.load(f)

    if today not in record:
        record[today] = {}

    now_str = datetime.now().strftime("%H:%M:%S")

    for app in apps:
        if app not in record[today]:
            record[today][app] = {
                "hits": 1,
                "start": now_str,
                "end": now_str,
                "times": [now_str]
            }
        else:
            record[today][app]["hits"] += 1
            record[today][app]["end"] = now_str
            record[today][app]["times"].append(now_str)

    with open(PROCESS_LOG_FILE, "w") as f:
        json.dump(record, f, indent=4)

def update_data():
    sent, recv = get_wifi_data()
    total = round(sent + recv, 2)
    sent_label.config(text=f"Sent Data: {sent} MB")
    recv_label.config(text=f"Received Data: {recv} MB")
    total_label.config(text=f"Total Usage Data: {total} MB")

    if total > DAILY_LIMIT_MB:
        winsound.Beep(1000, 1000)
        messagebox.showwarning("Data Limit Exceeded", f"⚠️ You've used {total} MB today! Limit: {DAILY_LIMIT_MB} MB")

    save_today_data(sent, recv)

    apps = get_active_internet_processes()
    app_text.set("\n".join(apps))
    log_apps(apps)

    root.after(10000, update_data)

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

    if os.path.exists(PROCESS_LOG_FILE):
        with open(PROCESS_LOG_FILE, "r") as f:
            logs = json.load(f)

        with open("app_log.csv", "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Date", "Time", "App"])
            for day in logs:
                for app, details in logs[day].items():
                    for t in details["times"]:
                        writer.writerow([day, t, app])

        with open("app_summary.csv", "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Date", "App", "Hits", "Start", "End", "Duration (min)"])
            for day in logs:
                for app, details in logs[day].items():
                    try:
                        start = datetime.strptime(details["start"], "%H:%M:%S")
                        end = datetime.strptime(details["end"], "%H:%M:%S")
                        duration = round((end - start).total_seconds() / 60, 2)
                    except:
                        duration = ""
                    writer.writerow([day, app, details["hits"], details["start"], details["end"], duration])

    messagebox.showinfo("Success", "Logs exported to CSV successfully.")

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
            for app, details in logs[today].items():
                for t in details["times"]:
                    tree.insert("", "end", values=(t, app))

def show_app_summary():
    win = tk.Toplevel(root)
    win.title("📊 App Summary (Today)")
    win.geometry("600x400")

    tree = ttk.Treeview(win, columns=("App", "Hits", "Start", "End", "Duration"), show="headings")
    tree.heading("App", text="App Name")
    tree.heading("Hits", text="Hits")
    tree.heading("Start", text="Start Time")
    tree.heading("End", text="End Time")
    tree.heading("Duration", text="Duration (min)")
    tree.pack(fill="both", expand=True)

    today = datetime.now().strftime("%Y-%m-%d")

    if os.path.exists(PROCESS_LOG_FILE):
        with open(PROCESS_LOG_FILE, "r") as f:
            logs = json.load(f)

        if today in logs:
            for app, details in logs[today].items():
                try:
                    start = datetime.strptime(details["start"], "%H:%M:%S")
                    end = datetime.strptime(details["end"], "%H:%M:%S")
                    duration = round((end - start).total_seconds() / 60, 2)
                except:
                    duration = ""
                tree.insert("", "end", values=(app, details["hits"], details["start"], details["end"], duration))


def show_total_runtime():
    end_time = datetime.now()
    duration = end_time - start_time

    win = tk.Toplevel(root)
    win.title("⏱️ Total Time on Hotspot Usage Tracker")
    win.geometry("400x200")

    tk.Label(win, text=f"Opening Time: {start_time.strftime('%H:%M:%S')}", font=("Arial", 12)).pack(pady=10)
    tk.Label(win, text=f"Closing Time: {end_time.strftime('%H:%M:%S')}", font=("Arial", 12)).pack(pady=10)
    tk.Label(win, text=f"Total Duration: {str(duration).split('.')[0]}", font=("Arial", 14, "bold")).pack(pady=10)

def save_daily_summary_to_txt():
    end_time = datetime.now()
    duration = end_time - start_time
    today = datetime.now().strftime("%Y-%m-%d")
    opening = start_time.strftime("%H:%M:%S")
    closing = end_time.strftime("%H:%M:%S")
    total_mb = 0.0
    app_list = []

    # Load today's usage from JSON if exists
    if os.path.exists(RECORD_FILE):
        with open(RECORD_FILE, "r") as f:
            record = json.load(f)
        month = datetime.now().strftime("%Y-%m")
        if month in record and today in record[month]:
            total_mb = round(record[month][today]["sent_MB"] + record[month][today]["recv_MB"], 2)

    # Load today's apps
    if os.path.exists(PROCESS_LOG_FILE):
        with open(PROCESS_LOG_FILE, "r") as f:
            logs = json.load(f)
        if today in logs:
            app_list = list(logs[today].keys())

    # Format the report
    report = f"Date: {today}\n"
    report += f"Opening Time: {opening}\n"
    report += f"Closing Time: {closing}\n"
    report += f"Total Duration: {str(duration).split('.')[0]}\n"
    report += f"Total Data Usage: {total_mb} MB\n"
    report += f"Apps Used:\n"
    for app in app_list:
        report += f"- {app}\n"
    report += "-" * 40 + "\n"

    # Append to .txt file
    # Append to .txt file
    filename = f"{today}.txt"
    with open(filename, "a") as f:
        f.write(report)

    messagebox.showinfo("Saved ✅", f"Daily summary saved to {filename}")

def merge_txt_reports():
    output_file = "all_reports.txt"
    txt_files = [f for f in os.listdir() if f.endswith(".txt") and f != output_file]

    if not txt_files:
        messagebox.showinfo("Info", "No daily .txt files found to merge.")
        return

    txt_files.sort()

    with open(output_file, "w") as outfile:
        for file in txt_files:
            with open(file, "r") as infile:
                outfile.write(infile.read())
                outfile.write("\n")  # spacing between reports

    messagebox.showinfo("✅ Done", f"Merged {len(txt_files)} files into '{output_file}'")

def on_close():
    save_daily_summary_to_txt()
    root.destroy()


# -------------------- GUI SETUP --------------------
root = tk.Tk()
root.title("📶 Today's Hotspot Usage Tracker")
root.geometry("400x580")

sent_label = tk.Label(root, text="Sent Data: 0 MB", font=("Arial", 14))
recv_label = tk.Label(root, text="Received Data: 0 MB", font=("Arial", 14))
total_label = tk.Label(root, text="Total Usage Data: 0 MB", font=("Arial", 16, "bold"))
app_title = tk.Label(root, text="Apps using Internet (Topper):", font=("Arial", 12, "bold"))
app_text = tk.StringVar()
app_list = tk.Label(root, textvariable=app_text, font=("Arial", 11), justify="left")

sent_label.pack(pady=5)
recv_label.pack(pady=5)
total_label.pack(pady=10)
app_title.pack(pady=5)
app_list.pack(pady=5)

tk.Button(root, text="⏱️ Calculate Total Usage Time", command=show_total_runtime).pack(pady=5)
tk.Button(root, text="📝 Save Daily Summary to TXT", command=save_daily_summary_to_txt).pack(pady=5)
tk.Button(root, text="📁 Merge All Daily TXT Reports", command=merge_txt_reports).pack(pady=5)
tk.Button(root, text="📊 Show Usage Graph", command=show_graph).pack(pady=5)
tk.Button(root, text="📋 Show App Log (Today)", command=show_app_table).pack(pady=5)
tk.Button(root, text="📊 App Usage Summary (Today)", command=show_app_summary).pack(pady=5)
tk.Button(root, text="💾 Export Logs to CSV", command=convert_to_csv).pack(pady=5)


update_data()
root.protocol("WM_DELETE_WINDOW", on_close)  #Auto save on close .txt file
root.mainloop()



