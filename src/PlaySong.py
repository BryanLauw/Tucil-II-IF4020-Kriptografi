import pygame

def play_song(file_path: str):
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        print("Press Enter to stop playback...")
        input()
        pygame.mixer.music.stop()
    except Exception as e:
        print(f"Error playing sound: {e}")

# play_song("sound/test.mp3")