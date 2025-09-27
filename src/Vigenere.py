def encrypt_vigenere(plain: int, key: int) -> int:
    return (plain + key) % 256
    
def decrypt_vigenere(cipher: int, key: int) -> int:
    return (cipher - key) % 256