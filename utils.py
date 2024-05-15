import requests
import aiohttp
import logging
import config
from openai import OpenAI
from pytube import YouTube
from moviepy.editor import *
from tqdm import tqdm
import os
from urllib.parse import urlencode, quote_plus

file_info = f"https://api.telegram.org/bot{config.BOT_TOKEN}/getFile?file_id="
file_url = f"https://api.telegram.org/file/bot{config.BOT_TOKEN}/"

# Example usage
async def generate_text(prompt): 
    try:
        client = OpenAI(api_key=config.DEEPSEEK_API_KEY, base_url=config.DEEPSEEK_API_ENDPOINT)
        
        response = client.chat.completions.create(
            model="deepseek-chat",
            max_tokens=50,
            messages=[
                #{"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": prompt},
            ]
        )
        return response.choices[0].message.content, response.usage.total_tokens
    except Exception as e:
        logging.error(e)


async def audio_from_Youtube(prompt, folder_name):
    
    # URL видео на YouTube
    youtube_video_url = prompt

    # Создаем объект YouTube
    yt = YouTube(youtube_video_url)
    video_title = yt.video_id
    # Получаем видео с наивысшей разрешением и скачиваем его с прогресс-баром
    video = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').asc().first()
    os.makedirs(folder_name, exist_ok=True)
    filename_video = os.path.join(folder_name, f"{video_title}.mp4")
    filename_audio = os.path.join(folder_name, f"{video_title}.mp3")

    video.download(filename=filename_video)

    # Извлекаем аудио из видео
    video_clip = VideoFileClip(filename_video)
    audio_clip = video_clip.audio

    # Сохраняем аудио в файл
    audio_clip.write_audiofile(filename_audio)

    video_clip.close()
    audio_clip.close()
    # Удаляем видеофайл, так как он нам больше не нужен
    os.remove(filename_video)
    return filename_audio, video_title

async def download_file(file_id, folder_name):

    resp = requests.get(file_info+file_id)
    audio_path = resp.json()["result"]["file_path"]
    audio_path = file_url+audio_path
    # Создаем директорию, если ее еще нет
    os.makedirs(folder_name, exist_ok=True)
    
    # Формируем путь для сохранения файла
    file_on_disk = os.path.join(folder_name, f"{file_id}.tmp")
    
    async with aiohttp.ClientSession() as session:
            async with session.get(audio_path) as resp:
                if resp.status == 200:
                    with open(file_on_disk, 'wb') as f:
                        while True:
                            chunk = await resp.content.read(1024)
                            if not chunk:
                                break
                            f.write(chunk)
                        return f

async def wolfram_solution(query):
    url = config.wolfram_query(query.replace('+','%2B'))
    resp = requests.get(url)
    all_data = resp.json()
    output_data = all_data['queryresult']['pods'][0]["subpods"][0]["plaintext"]
    return output_data

if __name__ == "__main__":
    print(wolfram_solution("integrate 4x+1"))