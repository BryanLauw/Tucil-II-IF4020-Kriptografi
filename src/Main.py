from Sisip import *
from PlaySong import *
from FileProcessor import *
from Vigenere import *
import os

def sisip_pesan():
    print("\n=== Penyisipan Pesan Rahasia ke File Audio ===\n")
    print("Masukkan file beserta ekstensi!")
    cover_name = input("Masukkan nama file cover (mp3): ")
    cover_name = os.path.join("sound", cover_name)
    
    secret_name = input("Masukkan nama file pesan rahasia: ")
    secret_name = os.path.join("secret", secret_name)
    
    output_name = input("Masukkan path file output penyisipan pesan (mp3): ")
    output_name = os.path.join("output", output_name)
    
    key = input("Masukkan kunci enkripsi (tekan enter untuk tanpa kunci): ")
    n_lsb = int(input("Masukkan jumlah LSB yang digunakan (1-4): "))
    seed = input("Masukkan seed pembangkit acak (tekan enter untuk tanpa seed): ")
    
    try:
        read_input(cover_name, cover=True)
        read_input(secret_name, cover=False, key=key if key else None)
        sisip(False, n_lsb) # ubah setelah seed selesai
        write_stega(output_name)
        print(f"Pesan berhasil disisipkan ke dalam {output_name}")
        
        play_song(output_name)
    except Exception as e:
        print(f"Terjadi kesalahan: {e}")

def ekstrak_pesan():
    print("\n=== Ekstraksi Pesan Rahasia dari File Audio ===\n")
    stego_name = input("Masukkan nama file audio (mp3): ")
    stego_name = os.path.join("stego-audio", stego_name)
    
    output_name = input("Masukkan nama file output ekstraksi pesan: ")
    output_name = os.path.join("ekstraksi", output_name)
    
    key = input("Masukkan kunci dekripsi (tekan enter untuk tanpa kunci): ")
    
    try:
        read_input_stega(stego_name)
        ekstrak()
        read_write_secret(output_name, key if key else None)
        print(f"Pesan berhasil diekstrak ke dalam {output_name}")
        
    except Exception as e:
        print(f"Terjadi kesalahan: {e}")
        
def main():
    loop = True
    while loop: 
        fitur = input("Tentukan fitur yang ingin digunakan:\n1. Sisip Pesan\n2. Ekstrak Pesan\n3. Putar Lagu\nPilihan Anda: ")   
        if fitur == '1':
            loop = False
            sisip_pesan()
        elif fitur == '2':
            loop = False
            ekstrak_pesan()
        elif fitur == '3':
            loop = False
            nama_lagu = input("Masukkan nama file audio (mp3): ")
            nama_lagu = os.path.join("sound", nama_lagu)
            play_song(nama_lagu)
        else:
            print("\nPilihan tidak valid. Silakan coba lagi.")
    
main() 
