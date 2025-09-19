
import io
import json
import base64
import asyncio
import tempfile
import os
import traceback
import time
import requests 
import soundfile as sf 

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState

import numpy as np
import librosa
import logging

app = FastAPI()



def extract_features(audio: np.ndarray, sr: int):
    """Извлечение акустических признаков из аудиоданных."""
    features = {}
    logging.info("Начало извлечения акустических признаков")
    try:
        energy = librosa.feature.rms(y=audio)[0]
        features['avg_energy'] = np.mean(energy)
        features['energy_std'] = np.std(energy)
        features['energy_stability'] = 1 / (np.std(energy) + 0.001)
        pitches, magnitudes = librosa.piptrack(y=audio, sr=sr)
        pitch_values = pitches[pitches > 0]
        if len(pitch_values) > 0:
            features['avg_pitch'] = np.mean(pitch_values)
            features['pitch_std'] = np.std(pitch_values)
            features['pitch_stability'] = 1 / (np.std(pitch_values) + 0.1)
        else:
            features['avg_pitch'] = 0
            features['pitch_std'] = 0
            features['pitch_stability'] = 0
        tempo, _ = librosa.beat.beat_track(y=audio, sr=sr)
        features['tempo'] = tempo[0] if isinstance(tempo, np.ndarray) and tempo.size > 0 else tempo


        silence_threshold = np.mean(energy) * 0.15
        speech_frames = np.sum(energy > silence_threshold)
        features['speech_ratio'] = speech_frames / len(energy) if len(energy) > 0 else 0.0

        spectral_centroids = librosa.feature.spectral_centroid(y=audio, sr=sr)[0]
        features['spectral_brightness'] = np.mean(spectral_centroids)
        features['brightness_stability'] = 1 / (np.std(spectral_centroids) + 0.1)


    except Exception as e:
        return {
            'avg_energy': 0.01, 'energy_std': 0.01, 'energy_stability': 1,
            'avg_pitch': 100, 'pitch_std': 10, 'pitch_stability': 1,
            'tempo': 120, 'speech_ratio': 0.5, 'spectral_brightness': 2000,
            'brightness_stability': 1,
            'error': str(e)
        }
    return features



def features_to_tags(features: dict):
    """Преобразование признаков в теги софт-скиллов."""
    tags = []
    scores = {}
    logging.info("Преобразование признаков в теги")
    confidence = 0
    if features.get('energy_stability', 0) > 10: confidence += 0.3
    if features.get('pitch_stability', 0) > 5: confidence += 0.3
    if 0.6 <= features.get('speech_ratio', 0) <= 0.85: confidence += 0.2
    if 80 <= features.get('tempo', 120) <= 140: confidence += 0.2
    if confidence >= 0.6: tags.append("Уверенный")
    elif confidence >= 0.3: tags.append("Достаточно уверенный")
    else: tags.append("Неуверенный")
    scores['confidence'] = round(confidence * 100, 1)
    stress_resistance = 0
    if features.get('pitch_std', 100) < 50: stress_resistance += 0.4
    if features.get('energy_std', 1) < 0.02: stress_resistance += 0.3
    if 90 <= features.get('tempo', 120) <= 130: stress_resistance += 0.3
    if stress_resistance >= 0.6: tags.append("Стрессоустойчивый")
    elif stress_resistance >= 0.3: tags.append("Средняя стрессоустойчивость")
    else: tags.append("Подвержен стрессу")
    scores['stress_resistance'] = round(stress_resistance * 100, 1)
    communication = 0
    if features.get('speech_ratio', 0) > 0.7: communication += 0.3
    if features.get('spectral_brightness', 0) > 2000: communication += 0.25
    if features.get('brightness_stability', 0) > 3: communication += 0.25
    if features.get('avg_energy', 0) > 0.03: communication += 0.2
    if communication >= 0.6: tags.append("Отличная коммуникация")
    elif communication >= 0.3: tags.append("Хорошая коммуникация")
    else: tags.append("Слабая коммуникация")
    scores['communication'] = round(communication * 100, 1)


    energy_score = 0
    if features.get('avg_energy', 0) > 0.05: energy_score += 0.5
    if 110 <= features.get('tempo', 120) <= 160: energy_score += 0.5
    if energy_score >= 0.6: tags.append("Энергичный")
    elif energy_score >= 0.3: tags.append("Умеренно активный")
    else: tags.append("Пассивный")
    scores['energy'] = round(energy_score * 100, 1)

    if features.get('tempo', 120) > 150: tags.append("Быстрая речь")
    elif features.get('tempo', 120) < 80: tags.append("Медленная речь")
    if features.get('avg_energy', 0) < 0.02: tags.append("Тихий голос")
    elif features.get('avg_energy', 0) > 0.1: tags.append("Громкий голос")
    if features.get('pitch_std', 100) < 20: tags.append("Монотонный")
 
    overall_score = (scores['confidence'] * 0.3 + scores['communication'] * 0.3 + scores['stress_resistance'] * 0.25 + scores['energy'] * 0.15)
    
    logging.info("Теги и оценки успешно сформированы.")
    
    return {
        'tags': list(set(tags)), # Убираем дубликаты
        'scores': scores,
        'overall_score': round(overall_score, 1)
    }


def analyze_audio_sync(audio_np: np.ndarray, sr: int):
    """Синхронная обертка для анализа аудио."""
    if audio_np.size == 0:
        logging.info("Попытка анализа пустого аудио массива.")
        return {
            'tags': ['Нет данных'],
            'scores': {},
            'error': 'Нет аудиоданных для анализа'
        }
    
    start_time = time.time()
    features = extract_features(audio_np, sr)
    analysis_result = features_to_tags(features)
    processing_time = (time.time() - start_time) * 1000
    
    analysis_result['meta'] = {
        'total_duration': round(len(audio_np) / sr, 2),
        'processing_time_ms': round(processing_time, 1)
    }
    return analysis_result

def transcribe_audio_api(audio_np: np.ndarray, sr: int):
    """Транскрипция аудио через внешний API."""
    if audio_np.size == 0:
        logging.error("Попытка транскрипции пустого аудио массива.")
        return "Пустой аудио файл"

    API_KEY = os.getenv("FIREWORKS_API_KEY", "fw_3ZiJ91MC7JGPnCg7U4fjqYgF")
    if not API_KEY:
        logging.error(" Ключ API Fireworks.ai не найден!")
        return "Ошибка: Ключ API не настроен."

    temp_audio_file = None
    try:
        logging.error(f"Запускаем транскрипцию через API...")
        start_time = time.time()

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmpfile:
            temp_audio_file = tmpfile.name
            sf.write(tmpfile, audio_np, sr)
            logging.info(f"Аудио временно сохранено в: {temp_audio_file}")

        with open(temp_audio_file, "rb") as f:
            response = requests.post(
                "https://audio-turbo.us-virginia-1.direct.fireworks.ai/v1/audio/transcriptions",
                headers={"Authorization": f"Bearer {API_KEY}"},
                files={"file": f},
                data={
                    "model": "whisper-v3-turbo",
                    "temperature": "0",
                    "vad_model": "silero"
                },
            )
        
        processing_time = time.time() - start_time
        logging.info(f"API обработал запрос за {processing_time:.2f}с")

        if response.status_code == 200:
            transcribed_text = response.json().get("text", "").strip()
            if not transcribed_text:
                logging.error("API вернул пустой текст")
                return "Не удалось распознать речь"
            return transcribed_text
        else:
            logging.error(f"Ошибка API: {response.status_code}", response.text)
            return f"Извините, возникли проблемы с распознаванием речи (ошибка: {response.status_code})."

    except Exception as e:
        logging.error(f"Критическая ошибка при вызове API: {e}")
        traceback.print_exc()
        return "Извините, возникли технические проблемы с распознаванием речи. Попробуйте записать ответ еще раз."
    finally:
        if temp_audio_file and os.path.exists(temp_audio_file):
            os.unlink(temp_audio_file)


@app.websocket("/ws/voice")
async def websocket_voice(websocket: WebSocket):
    print("🔗 Новое WebSocket подключение")
    await websocket.accept()
    print("✅ WebSocket соединение принято")
    
    audio_buffer = io.BytesIO()
    chunks_received = 0
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message['type'] == 'audio_chunk':
                chunk_b64 = message['data']
                chunk_bytes = base64.b64decode(chunk_b64)
                audio_buffer.write(chunk_bytes)
                chunks_received += 1
                
                if chunks_received % 20 == 0:
                    logging.info(f"Получено {chunks_received} чанков, общий размер: {audio_buffer.tell()} байт")


            elif message['type'] == 'end':
                logging.info("Получен сигнал завершения записи.")
                logging.info(f"Всего получено чанков: {chunks_received}")
                
                audio_bytes = audio_buffer.getvalue()
                
                if len(audio_bytes) == 0:
                    logging.info("Получено пустое аудио. Отправляем ошибку клиенту.")
                    if websocket.application_state == WebSocketState.CONNECTED:
                        await websocket.send_json({'type': 'error', 'message': 'Аудиозапись пуста.'})
                    continue


                logging.info(f"Начинаем обработку аудио размером {len(audio_bytes)} байт")
                loop = asyncio.get_event_loop()
                
                temp_audio_file = tempfile.NamedTemporaryFile(suffix=".webm", delete=False)
                temp_file_path = temp_audio_file.name
                
                try:
                    temp_audio_file.write(audio_bytes)
                    temp_audio_file.close()
                    logging.info(f"Аудио данные записаны во временный файл: {temp_file_path}")

                    logging.info("Декодирование аудио файла в numpy array...")
                    start_decode = time.time()
                    audio_np, sr = librosa.load(temp_file_path, sr=16000, mono=True)
                    logging.info(f"Аудио декодировано за {time.time() - start_decode:.2f}с. Сэмплов: {len(audio_np)}, Частота: {sr}Hz")

                    transcribe_task = loop.run_in_executor(None, transcribe_audio_api, audio_np, sr)
                    analyze_task = loop.run_in_executor(None, analyze_audio_sync, audio_np, sr)
                    
                    transcription_result = await transcribe_task
                    analysis_result = await analyze_task
                    
                    print(f"Результат транскрипции: '{transcription_result}'")
                    print(f"Результат анализа: {analysis_result['tags']}")
                    
                    if websocket.application_state == WebSocketState.CONNECTED:
                        response = {
                            'type': 'final_result',
                            'transcription': transcription_result,
                            'analysis': analysis_result
                        }
                        logging.info(f"Отправляем результат клиенту...")
                        await websocket.send_json(response)
                        logging.info("Результат успешно отправлен")
                    else:
                        logging.info("WebSocket не подключен, не можем отправить результат")

                finally:
                    if os.path.exists(temp_file_path):
                        os.unlink(temp_file_path)
                        logging.info(f"🗑️ Временный файл удален: {temp_file_path}")

                audio_buffer = io.BytesIO()
                chunks_received = 0
                logging.info("\nБуфер сброшен, готов к новой записи.")


    except WebSocketDisconnect:
        logging.info("Клиент отключился от WebSocket.")
    except Exception as e:
        logging.info(f"Критическая ошибка в WebSocket: {e}")
        traceback.print_exc()
    finally:
        if not audio_buffer.closed:
            audio_buffer.close()

if __name__ == "__main__":
    import uvicorn

    logging.info("Запуск сервера Uvicorn на http://0.0.0.0:8001")
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=False)
