import struct
import pathlib
from typing import List, Optional, Union

# binary string
def bstr(n: int) -> str: # n in range 0-255
    return ''.join([str(n >> x & 1) for x in (7,6,5,4,3,2,1,0)])

# read file into an array of binary formatted strings.
def read_binary(path: str) -> Union[List[str], str]:
    binlist = []
    extenstion = pathlib.Path(path).suffix
    
    with open(path, 'rb') as f:
        while True:
            byte = f.read(1)
            if not byte:
                break
            value = struct.unpack('B', byte)[0]
            binlist.append(bstr(value))
    return binlist, extenstion

# Contoh penggunaan
if __name__ == "__main__":
    filePath = input("Masukkan nama file: ")
    binList, extension = read_binary(filePath)
    print(binList)
    print(extension)