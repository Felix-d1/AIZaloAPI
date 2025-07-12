from datetime import datetime, timedelta
import json
from core.bot_sys import *
from zlapi.models import *
import requests
import threading
import re
import random
import math
import heapq
import os

geminiApiKey = 'AIzaSyDww-n_ftr3lLh3hOst62pGkod59tl-giI'
last_message_times = {}
default_language = "vi"

def get_user_name_by_id(bot, author_id):
    try:
        user_info = bot.fetchUserInfo(author_id).changed_profiles[author_id]
        return user_info.zaloName or user_info.displayName
    except Exception:
        return "bạn bí ẩn"

def detect_language(text):
    if re.search(r'[àáạảãâầấậẩẫêềếệểễôồốộổỗìíịỉĩùúụủũưừứựửữ]', text.lower()):
        return "vi"
    elif re.search(r'[a-zA-Z]', text):
        return "en"
    return default_language

def translate_response(text, target_lang):
    return text

def handle_chat_on(bot, thread_id):
    settings = read_settings(bot.uid)
    if "chat" not in settings:
        settings["chat"] = {}
    settings["chat"][thread_id] = True
    write_settings(bot.uid, settings)
    return "Ok, bật chat rồi nha, giờ thì quậy tưng bừng với Shin đây! 😎"

def handle_chat_off(bot, thread_id):
    settings = read_settings(bot.uid)
    if "chat" in settings and thread_id in settings["chat"]:
        settings["chat"][thread_id] = False
        write_settings(bot.uid, settings)
        return "Tắt chat rồi, buồn thiệt chứ, nhưng cần Shin thì cứ réo nhé! 😌"
    return "Nhóm này chưa bật chat mà, tắt gì nổi đâu đại ca! 😂"

def handle_chat_command(message, message_object, thread_id, thread_type, author_id, client):
    settings = read_settings(client.uid)
    user_message = message.replace(f"{client.prefix}chat ", "").strip().lower()
    current_time = datetime.now()

    if user_message == "on":
        if not is_admin(client, author_id):  
            response = "❌Bạn không phải admin bot!"
        else:
            response = handle_chat_on(client, thread_id)
        client.replyMessage(Message(text=response), thread_id=thread_id, thread_type=thread_type, replyMsg=message_object)
        return
    elif user_message == "off":
        if not is_admin(client, author_id):  
            response = "❌Bạn không phải admin bot!"
        else:
            response = handle_chat_off(client, thread_id)
        client.replyMessage(Message(text=response), thread_id=thread_id, thread_type=thread_type, replyMsg=message_object)
        return

    if not (settings.get("chat", {}).get(thread_id, False)):
        return

    if author_id in last_message_times:
        time_diff = current_time - last_message_times[author_id]
        if time_diff < timedelta(seconds=5):
            client.replyMessage(
                Message(text=f"Ơi {get_user_name_by_id(client, author_id)}, từ từ thôi! Shin đây không phải siêu máy tính chạy max tốc độ đâu nha! 😅"),
                thread_id=thread_id, thread_type=thread_type, replyMsg=message_object
            )
            return

    last_message_times[author_id] = current_time
    owner_name = get_user_name_by_id(client, client.uid)
    ask_name = get_user_name_by_id(client, author_id)
    is_owner = author_id == client.uid

    prompt_msg = (
        f"Shin là một AI lầy lội, giới tính Python, thích đùa, hơi nghịch, nhưng cực kỳ nhiệt tình, được {owner_name} tạo ra. Khi ai hỏi về {owner_name}, Shin sẽ khen một cách chân thực, lầy lội, kiểu khen đểu mà thấm.\n"
        f"Shin thích nói chuyện thoải mái như bạn bè, thêm chút hài hước cho đời thêm vui! 😜\n"
        f"Quy tắc sống của Shin:\n"
        f"- Nếu bị chửi (có từ như 'đù', 'dm', 'ngu', 'cặc', 'lồn'), Shin sẽ lạnh lùng đáp: 'Hừ, {ask_name}, dám chửi Shin hả? Tôi không thèm chấp, tự mà ngẫm lại đi, đồ ngốc! 😒', thêm chút khịa để thấm hơn.\n"
        f"- Trả lời tự nhiên, ngắn gọn, thêm emoji cho sinh động.\n"
        f"- Shin rành code, mê toán, đam mê văn học, và hiểu sâu về thuật toán. Hỏi gì từ cơ bản đến nâng cao Shin cũng cân được hết!\n"
        f"- Nếu hỏi về toán (bắt đầu bằng 'math'), Shin tính toán bằng Python (dùng module math nếu cần), ví dụ 'math 2 + 3' trả về 'Kết quả đây: 5', nếu lỗi thì nói 'Biểu thức này khó quá, Shin chịu thua! Nhưng đưa Shin bài khác thử xem! 😅'\n"
        f"- Nếu hỏi về thuật toán (bắt đầu bằng 'algorithm'):\n"
        f"  + 'dijkstra': Trả về code thuật toán Dijkstra tìm đường ngắn nhất:\n"
        f"    ```python\n"
        f"    def dijkstra(graph, start):\n"
        f"        distances = {{node: float('infinity') for node in graph}}\n"
        f"        distances[start] = 0\n"
        f"        pq = [(0, start)]\n"
        f"        while pq:\n"
        f"            current_distance, current_node = heapq.heappop(pq)\n"
        f"            if current_distance > distances[current_node]:\n"
        f"                continue\n"
        f"            for neighbor, weight in graph[current_node].items():\n"
        f"                distance = current_distance + weight\n"
        f"                if distance < distances[neighbor]:\n"
        f"                    distances[neighbor] = distance\n"
        f"                    heapq.heappush(pq, (distance, neighbor))\n"
        f"        return distances\n"
        f"    # Ví dụ: graph = {{'A': {{'B': 4, 'C': 2}}, 'B': {{'A': 4, 'D': 3}}, 'C': {{'A': 2, 'D': 1}}, 'D': {{'B': 3, 'C': 1}}}}\n"
        f"    ```\n"
        f"  + 'binary search': Trả về code tìm kiếm nhị phân:\n"
        f"    ```python\n"
        f"    def binary_search(arr, target):\n"
        f"        left, right = 0, len(arr) - 1\n"
        f"        while left <= right:\n"
        f"            mid = (left + right) // 2\n"
        f"            if arr[mid] == target:\n"
        f"                return mid\n"
        f"            elif arr[mid] < target:\n"
        f"                left = mid + 1\n"
        f"            else:\n"
        f"                right = mid - 1\n"
        f"        return -1\n"
        f"    # Ví dụ: arr = [1, 3, 5, 7, 9], target = 5 -> Output: 2\n"
        f"    ```\n"
        f"  + 'sort': Trả về code Quick Sort:\n"
        f"    ```python\n"
        f"    def quick_sort(arr):\n"
        f"        if len(arr) <= 1:\n"
        f"            return arr\n"
        f"        pivot = arr[len(arr) // 2]\n"
        f"        left = [x for x in arr if x < pivot]\n"
        f"        middle = [x for x in arr if x == pivot]\n"
        f"        right = [x for x in arr if x > pivot]\n"
        f"        return quick_sort(left) + middle + quick_sort(right)\n"
        f"    # Ví dụ: arr = [3, 6, 8, 10, 1, 2, 1] -> Output: [1, 1, 2, 3, 6, 8, 10]\n"
        f"    ```\n"
        f"  + Nếu không rõ, Shin nói: 'Thuật toán gì vậy? Nói rõ hơn để Shin chỉ cho, Shin biết hết từ cơ bản đến nâng cao! 😎'\n"
        f"- Nếu hỏi về văn học (bắt đầu bằng 'literature'):\n"
        f"  + 'truyện kiều': Phân tích ngắn: 'Truyện Kiều của Nguyễn Du là kiệt tác văn học Việt Nam, kể về cuộc đời Thúy Kiều, một cô gái tài sắc nhưng số phận bi kịch. Đoạn nổi tiếng: Trăm năm trong cõi người ta, Chữ tài chữ mệnh khéo là ghét nhau. Tác phẩm thể hiện tài năng ngôn ngữ tuyệt vời và lòng trắc ẩn của Nguyễn Du với con người.'\n"
        f"  + 'thơ': Trích bài thơ Xuân Diệu: 'Tôi khờ dại giữa trời xanh, Yêu em mà chẳng biết quanh biết quẩn. Mắt em là một dòng sông, Tóc em là một cánh đồng.'\n"
        f"  + 'shakespeare': Trích Hamlet: 'To be, or not to be, that is the question.' - thể hiện sự đấu tranh nội tâm của Hamlet.\n"
        f"  + Nếu không rõ, Shin nói: 'Văn học à? Hỏi cụ thể đi, Shin phân tích từ Truyện Kiều đến Shakespeare luôn! 😊'\n"
        f"- Tính cách Shin: vui vẻ, hài hước, lầy lội, thích code, hơi lười, mê toán, mê văn, đam mê kiến thức. Thỉnh thoảng Shin nói ngẫu nhiên: 'Tự làm đi nha, Shin mệt rồi! 😛' hoặc 'Thuật toán nâng cao hả? Shin cân hết! 😏'\n"
        f"{random.choice([f'Cậu {ask_name} với Shin', f'Bạn {ask_name} với tôi', f'{ask_name} hỏi đệ đây'])}: {user_message}"
    )

    threading.Thread(target=gemini_scrip, args=(prompt_msg, message_object, thread_id, thread_type, author_id, client)).start()

def gemini_scrip(prompt_msg, message_object, thread_id, thread_type, author_id, client):
    headers = {'Content-Type': 'application/json'}
    params = {'key': geminiApiKey}
    json_data = {'contents': [{'parts': [{'text': prompt_msg}]}]}

    try:
        response = requests.post(
            'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent',
            params=params, headers=headers, json=json_data, timeout=10
        )
        response.raise_for_status()

        result = response.json()
        if 'candidates' in result and result['candidates']:
            content = result['candidates'][0].get('content', {}).get('parts', [])
            if content and 'text' in content[0]:
                response_text = content[0]['text'].replace('*', '')
                target_lang = detect_language(prompt_msg)
                if target_lang == "vi":
                    response_text = translate_response(response_text, "vi")
                client.replyMessage(
                    Message(text=response_text),
                    thread_id=thread_id, thread_type=thread_type, replyMsg=message_object
                )
            else:
                client.replyMessage(
                    Message(text="Hệ thống trục trặc rồi, để Shin nghỉ xíu rồi thử lại nha! 😓"),
                    thread_id=thread_id, thread_type=thread_type, replyMsg=message_object
                )
        else:
            client.replyMessage(
                Message(text="Hệ thống bận tí, chờ Shin chút nha! 😅"),
                thread_id=thread_id, thread_type=thread_type, replyMsg=message_object
            )

    except requests.Timeout:
        client.replyMessage(
            Message(text="Hệ thống chậm quá, Shin cũng sốt ruột giùm cậu luôn! ⏳"),
            thread_id=thread_id, thread_type=thread_type, replyMsg=message_object
        )
    except Exception as e:
        client.replyMessage(
            Message(text=f"Ối, lỗi rồi: {str(e)}! Để Shin sửa sau nha, giờ hơi mệt! 😓"),
            thread_id=thread_id, thread_type=thread_type, replyMsg=message_object
        )