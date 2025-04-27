import os
import sys
import json
import psutil
import codecs
from llama_index.core import Document, VectorStoreIndex, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# Tắt cảnh báo và thiết lập môi trường
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

# Ép buộc mã hóa utf-8
sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())

# Kiểm tra bộ nhớ
memory = psutil.virtual_memory()
available_memory_mb = memory.available / (1024 * 1024)
if available_memory_mb < 1000:
    raise MemoryError(f"Bộ nhớ khả dụng quá thấp: {available_memory_mb:.2f}MB")
print(f"Bộ nhớ khả dụng: {available_memory_mb:.2f}MB")

# Cấu hình mô hình embedding
embed_model = HuggingFaceEmbedding(model_name="all-MiniLM-L6-v2")
Settings.embed_model = embed_model

# Tạo thư mục offload
offload_folder = "offload_weights"
if not os.path.exists(offload_folder):
    os.makedirs(offload_folder)

# Tải dữ liệu JSON
with open("data/weather_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

if not data:
    raise ValueError("Dữ liệu rỗng!")
print(f"Số bản ghi trong weather_data.json: {len(data)}")

# Chuyển dữ liệu thành Document
documents = []
for record in data:
    if not all(key in record for key in ["datetime", "temp", "humidity", "weather"]):
        raise KeyError("Dữ liệu JSON thiếu trường bắt buộc!")
    text = f"Thời gian: {record['datetime']}, Nhiệt độ: {record['temp']}°C, Độ ẩm: {record['humidity']}%, Thời tiết: {record['weather']}"
    documents.append(Document(text=text))

# Tạo chỉ mục
index = VectorStoreIndex.from_documents(documents, settings=Settings)

# Hàm phân tích câu hỏi và trả lời
def weather_agent(question):
    retriever = index.as_retriever(similarity_top_k=1)
    try:
        nodes = retriever.retrieve(question)
        if not nodes:
            return "Không tìm thấy thông tin thời tiết phù hợp."

        text = nodes[0].text
        # Trích xuất thông tin
        try:
            datetime = text.split("Thời gian: ")[1].split(",")[0]
            temp = text.split("Nhiệt độ: ")[1].split("°C")[0]
            humidity = text.split("Độ ẩm: ")[1].split("%")[0]
            weather = text.split("Thời tiết: ")[1]
        except IndexError:
            return "Lỗi: Không thể trích xuất thông tin từ dữ liệu!"

        # Phân tích câu hỏi
        question = question.lower()
        if "nhiệt độ" in question:
            return f"Nhiệt độ mới nhất là {temp}°C."
        elif "độ ẩm" in question:
            return f"Độ ẩm hiện tại là {humidity}%."
        elif "thời tiết" in question or "trời" in question:
            return f"Thời tiết hiện tại: Trời {weather.lower()} vào lúc {datetime}, nhiệt độ {temp}°C, độ ẩm {humidity}%."
        else:
            return f"Thông tin thời tiết mới nhất: Vào lúc {datetime}, nhiệt độ {temp}°C, độ ẩm {humidity}%, trời {weather.lower()}."

    except Exception as e:
        return f"Lỗi khi xử lý câu hỏi: {str(e)}"

# Hàm chính để chạy agent
def main():
    print("Chào bạn! Tôi là Weather Agent. Hỏi tôi về thời tiết nhé!")
    while True:
        question = input("Câu hỏi của bạn (hoặc 'thoát' để dừng): ")
        if question.lower() == "thoát":
            print("Tạm biệt!")
            break
        answer = weather_agent(question)
        print(f"Trả lời: {answer}")


# Chạy agent
if __name__ == "__main__":
    main()