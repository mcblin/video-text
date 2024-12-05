import os
import moviepy.editor as mp
from pydub import AudioSegment
from vosk import Model, KaldiRecognizer
import wave

name_of_folder = input('название папки: ')
name_of_file = input('название файла: ')
files = f'{name_of_file}.txt'
video = name_of_file

eng = "vosk-model-en-us-0.42-gigaspeech"
rus = "vosk-model-ru-0.42"

ch_model = input('модель eng (1) или rus (2): ')

choosen_model = ''

if ch_model == '1':
    choosen_model = eng
else:
    choosen_model = rus

print(f'вы выбрали модель: {choosen_model}')


def video_to_audio(video_path, audio_path):
    """ Конвертируем видео в аудио """
    video = mp.VideoFileClip(video_path)
    video.audio.write_audiofile(audio_path)


def convert_audio_to_mono(audio_path, output_path):
    """ Конвертирует аудиофайл в формат моно, 16-bit, 16000 Hz """
    audio = AudioSegment.from_file(audio_path)
    # Преобразование в моно (если стерео)
    audio = audio.set_channels(1)

    # Преобразование в 16-bit (если другой битрейт)
    audio = audio.set_sample_width(2)

    # Преобразование в 16000 Hz (если другая частота)
    audio = audio.set_frame_rate(16000)

    # Сохранение в нужном формате
    audio.export(output_path, format="wav")


def recognize_speech(audio_path):
    """ Распознаем речь из аудиофайла с помощью vosk """
    model = Model(f"{choosen_model}")  # Укажи путь к папке с моделью vosk
    recognizer = KaldiRecognizer(model, 16000)

    # Открываем аудиофайл
    wf = wave.open(audio_path, "rb")
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() != 16000:
        raise ValueError("Аудиофайл должен быть моно, 16-bit, с частотой 16000 Hz")

    # Чтение данных и распознавание
    result_text = ""
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if recognizer.AcceptWaveform(data):
            result = recognizer.Result()
            result_text += result

    wf.close()
    return result_text


def main(video_path):
    raw_audio_path = "raw_audio.wav"
    converted_audio_path = "converted_audio.wav"

    # 1. Конвертируем видео в аудио
    video_to_audio(video_path, raw_audio_path)

    # 2. Преобразуем аудио в моно, 16-bit, 16000 Hz
    convert_audio_to_mono(raw_audio_path, converted_audio_path)

    # 3. Распознаем текст из аудио
    text = recognize_speech(converted_audio_path)

    # 4. Сохраняем текст в файл
    with open(files, "w", encoding="utf-8") as file:
        file.write(text)

    print(f"Текст успешно распознан и сохранен в {name_of_file}.txt")

    # Список ненужных символов
    unwanted_chars = ['{', '}', '"', '  "text" :', '  text : ']

    # Открываем файл для чтения
    with open(files, 'r', encoding='utf-8') as file:
        content = file.read()

    # Последовательно удаляем каждый ненужный символ
    for char in unwanted_chars:
        content = content.replace(char, '')

    # Открываем файл для записи и сохраняем изменения
    with open(files, 'w', encoding='utf-8') as file:
        file.write(content)

    os.remove('converted_audio.wav')
    os.remove('raw_audio.wav')

    print("Ненужные символы и файлы удалены.")


if __name__ == "__main__":
    video_path = f"{name_of_folder}/{video}.mp4"  # Укажи путь к своему видео
    main(video_path)
