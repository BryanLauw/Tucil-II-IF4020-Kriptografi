import pygame

def play_song(file_path: str):
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        print("Tekan Enter untuk menghentikan pemutaran lagu...")
        input()
        pygame.mixer.music.stop()
    except Exception as e:
        print(f"Terjadi kesalalahn: file tidak ditemukan")

# play_song("sound/test.mp3")