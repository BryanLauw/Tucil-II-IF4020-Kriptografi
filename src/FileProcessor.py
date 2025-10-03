import struct
import pathlib
from Vigenere import *

def bstr(n: int) -> str:
    """
    Konversi integer (0 - 255) menjadi 8-bit.
    """
    return ''.join([str(n >> x & 1) for x in (7,6,5,4,3,2,1,0)])

def read_input(path: str, cover: bool, key: str | None = None):
    """
    Membaca file dan menyimpan dalam representasi bit-bit di file txt
    
    Args:
        path (str): Path file yang dibaca (wajib mp3 untuk cover True)
        cover (bool): True jika file adalah cover, False jika file rahasia
        key (str | None): Kunci untuk enkripsi vigenere (opsional)
    Output:
        cover = True -> cover.txt
        cover = False -> sisip.txt
    """
    if cover and not path.endswith('.mp3'):
        raise Exception("File harus berekstensi mp3!")
    
    key_idx = 0
    if not cover and key:
        key = key.encode("utf-8")
        key_len = len(key)
    
    with open(path, 'rb') as f, open('cover.txt' if cover else 'sisip.txt', 'w') as temp:
        temp.write(pathlib.Path(path).suffix + '\n')
        
        while True:
            byte = f.read(1)
            if not byte:
                break
            
            value = struct.unpack('B', byte)[0]
            # Enkripsi file rahasia jika ada key
            if not cover and key:
                current_key = key[key_idx % key_len]
                value = encrypt_vigenere(value, current_key)
                key_idx += 1
            
            temp.write(bstr(value) + '\n')

def read_input_stega(path: str):
    """
    Membaca file dan menyimpan dalam representasi bit-bit di file txt
    
    Args:
        path (str): Path file yang dibaca (wajib mp3 untuk cover True)
    Output:
        stega.txt
    """
    if not path.endswith('.mp3'):
        raise Exception("File harus berekstensi mp3!")
    
    with open(path, 'rb') as f, open('stega.txt', 'w') as temp:
        temp.write(pathlib.Path(path).suffix + '\n')
        
        while True:
            byte = f.read(1)
            if not byte:
                break
            
            value = struct.unpack('B', byte)[0]
            
            temp.write(bstr(value) + '\n')

def write_stega(fileName: str):
    """
    Membuat file .mp3 hasil steganografi yang bit-bitnya diambil dari file stega.txt
    
    Args:
        fileName (str): File output steganografi (wajib mp3)
    Output:
        stego-file disimpan di fileName
    """
    if (not fileName.endswith('.mp3')):
        raise Exception("File harus berekstensi mp3!")
    
    # with open('cover.txt', 'r') as f, open(fileName, 'wb') as out:
    with open('stega.txt', 'r') as f, open(fileName, 'wb') as out:
        f.readline() # skipping extension tergantung di stego.txt nanti ada ekstensi/tidak
        
        while True:
            byteString = f.readline().strip()
            if not byteString: break
            
            byteResult = bytes([int(byteString, 2)])
            out.write(byteResult)

def read_write_secret(fileName: str, key: str | None = None):
    """
    Rekronsturksi file rahasia dari extracted.txt
    
    Args:
        fileName (str): File output
        key (str | None): Kunci untuk dekripsi vigenere (opsional)
        
    Output:
        file rahasia disimpan di fileName
    """
    key_idx = 0
    if key:
        key = key.encode("utf=8")
        key_len = len(key)
    fileName = fileName.split('.')[0]
        
    with open('extracted.txt', 'r') as f:
        ext = f.readline().strip() # Read and add extension
        fileName += ext
        
        with open(fileName, 'wb') as out:    
            while True:
                byteString = f.readline().strip()
                if not byteString: break
                
                value = int(byteString, 2)
                if key:
                    current_key = key[key_idx % key_len]
                    value = decrypt_vigenere(value, current_key)
                    key_idx += 1

                byteResult = bytes([value])
                out.write(byteResult)


# Contoh penggunaan
# if __name__ == "__main__":
    # secretFile = input("Masukkan nama file yang disembunyikan: ")
    # secretKey = input("Masukkan kunci: ")
    
    # read_input(secretFile, False, secretKey)
    
    # output1 = input("Masukkan nama file tanpa dekripsi (ekstensi sama dengan file awal): ")
    # read_write_secret(output1)
    
    # output2 = input("Masukkan nama file tanpa dekripsi (ekstensi sama dengan file awal): ")
    # write_stega(output2)
    
    # output2 = input("Masukkan nama file dengan dekripsi (ekstensi sama dengan file awal): ")
    # read_write_secret(output2, secretKey)