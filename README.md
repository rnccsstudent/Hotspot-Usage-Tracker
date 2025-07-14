# 📶 Hotspot Usage Tracker – Python GUI App

A simple yet powerful Python GUI app that helps you track **daily internet usage**, especially from **Wi-Fi/hotspot**, and shows which apps are using your internet in real time.

## 🔗 Screenshots

➡️ [View Live]()

---

## 🚀 Features

- 📊 Track **today's total Wi-Fi/hotspot data** usage (Sent / Received / Total in MB)
- 🧠 Shows **top 10 apps** currently using internet
- 🕓 Logs app usage every 10 seconds with timestamps
- 📈 View **graph of daily internet usage**
- 📋 View app activity logs in a GUI table
- 💾 Export all usage logs to **CSV** (for Excel or analysis)
- 🗃️ Stores daily usage history in JSON

---

## 🛠️ How to Run

### 1. ✅ Prerequisites

Make sure you have:

- Python 3.10 or higher installed
- Admin access (for per-app network info on Windows)

### 2. ✅ Install dependencies

Open terminal or CMD and run:

    pip install psutil matplotlib

### 3. 🚀 Run Locally

On Windows, run this file as Administrator:
   
    python app.py

You’ll see a live GUI with usage info and buttons for:

- Viewing graphs

- Viewing logs

- Exporting to CSV

---
### 📂 Files Generated

- `data_usage_record.json` – stores daily total data usage

- `app_usage_log.json` – logs apps that used internet with timestamps

- `daily_usage.csv` – exported CSV of daily usage

- `app_log.csv` – exported app activity log

---

⚠️ Important Notes

- Must run as Administrator to access full per-process network data.

- Only tracks data from the Wi-Fi/hotspot interface (default is "Wi-Fi").

- Can be customized for "Ethernet" or other interfaces.

---

### Windows Default Open Resource Monitor

Press Win + R to open Run

Type:

    resmon
Press Enter

Go to the Network tab

### 📊 What You'll See
🔸 Processes with Network Activity:

   Shows which .exe or process is using network
   Sortable by Send (B/sec) or Receive (B/sec)

🔸 Network Activity:

   Shows total amount of data used by each app, live

🔸 TCP Connections:

   Shows which app is connected to which remote IP
   
---
🧠 Future Ideas

- 🔔 Notify user when data crosses a daily limit

- 📊 Show top data-consuming apps

- ☁️ Sync logs to cloud

### 📜 License

    This project is open source and available under the MIT License.

---

### 👨‍💻 Author

- Made with ❤️ by Pranab Mahata
- [GitHub](https://github.com/rnccsstudent)

---

### 💬 Feedback

      If you find a bug or want to suggest a feature, feel free to open an issue or a pull request.

---
