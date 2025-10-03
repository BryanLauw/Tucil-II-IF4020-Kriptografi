def generate_random(key: str, max: int) -> int:
    """
    Menghasilkan bilangan bulat acak dengan rentang 0 s.d. max-1 berdasarkan key
    
    Args: 
        key (str): kunci untuk menghasilkan suatu bilangan acak
        max (int): nilai maksimal bilangan
        
    Output:
        Bilangan acak Z dengan 0 <= Z < max
    """
    out = 0
    for idx, char in enumerate(key):
        out += (idx + 1) * ord(char)
    
    return out % max