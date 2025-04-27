import requests
import json
from datetime import datetime
import os
from apscheduler.schedulers.blocking import BlockingScheduler

# Load API key và city từ config
API_KEY = "310521b4a80bb1973b4f3cfba5bd3cf9"
CITY = "Ho Chi Minh"
API_URL = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric&lang=vi"

# --- Hàm thu thập dữ liệu ---
def collect_weather_data():
    response = requests.get(API_URL)
    if response.status_code == 200:
        data = response.json()
        weather_info = {
            "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "temp": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "weather": data["weather"][0]["main"]
        }
        print("API Success:", weather_info)
        save_data(weather_info)
    else:
        print(f"API Error: {response.status_code} - {response.text}")

# --- Hàm lưu dữ liệu vào JSON ---
def save_data(info):
    os.makedirs("data", exist_ok=True)  # Tạo thư mục nếu chưa có
    file_path = "data/weather_data.json"
    
    existing_data = []
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            try:
                existing_data = json.load(file)
            except json.JSONDecodeError:
                # File tồn tại nhưng bị trống hoặc lỗi JSON -> coi như không có dữ liệu
                existing_data = []

    existing_data.append(info)

    with open(file_path, "w") as file:
        json.dump(existing_data, file, indent=4)

# --- Scheduler ---
if __name__ == "__main__":
    scheduler = BlockingScheduler()
    scheduler.add_job(collect_weather_data, 'interval', seconds=10)
    print("Weather Collector Agent started. Collecting every 10 seconds...")
    scheduler.start()
