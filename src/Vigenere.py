def encrypt_vigenere(plain: int, key: int) -> int:
    """
    Mengenkripsi satu byte plain dengan satu byte key
    
    Args: 
        plain (int): satu byte plaintext pada posisi ke-i
        key (int): satu byte kunci pada posisi ke-(i % len(key asli)
        
    Output:
        satu byte ciphertext
    """
    return (plain + key) % 256
    
def decrypt_vigenere(cipher: int, key: int) -> int:
    """
    Mendekripsi satu byte cipher dengan satu byte key
    
    Args: 
        cipher (int): satu byte ciphertext pada posisi ke-i
        key (int): satu byte kunci pada posisi ke-(i % len(key asli)
        
    Output:
        satu byte plaintext
    """
    return (cipher - key) % 256