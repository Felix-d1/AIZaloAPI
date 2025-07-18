import random
import requests
from core.bot_sys import get_user_name_by_id
from zlapi.models import *

def handle_vdgai_command(message, message_object, thread_id, thread_type, author_id, client):    
    try:
        msg = f"[Ask by: {get_user_name_by_id(client, author_id)}]"
        listvd = "https://raw.githubusercontent.com/trannguyen-shiniuem/trannguyen-shiniuem/refs/heads/main/listvdtet.json"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }
        
        response = requests.get(listvd, headers=headers)
        response.raise_for_status()
        urls = response.json()
        video_url = random.choice(urls)

        image_list_url = "https://raw.githubusercontent.com/trannguyen-shiniuem/trannguyen-shiniuem/refs/heads/main/listvdtet.json"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }
        
        response = requests.get(image_list_url, headers=headers)
        response.raise_for_status()
        json_data = response.json()
        
        if isinstance(json_data, dict) and 'url' in json_data:
            image_url = json_data.get('url')
        elif isinstance(json_data, list):
            image_url = random.choice(json_data)
        else:
            raise Exception("Dữ liệu trả về không hợp lệ")

        thumbnail_url = image_url
        duration = '1000'

        client.sendRemoteVideo(
            video_url, 
            thumbnail_url,
            duration=duration,
            message=Message(text=msg),
            thread_id=thread_id,
            thread_type=thread_type,
            width=1080,
            height=1920
        )
        
    except requests.exceptions.RequestException as e:
        error_message = Message(text=f"Đã xảy ra lỗi khi gọi API: {str(e)}")
        client.sendMessage(error_message, thread_id, thread_type)
    except Exception as e:
        error_message = Message(text=f"Đã xảy ra lỗi: {str(e)}")
        client.sendMessage(error_message, thread_id, thread_type)