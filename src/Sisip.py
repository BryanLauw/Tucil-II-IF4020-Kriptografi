import os
import hashlib
from typing import List

# ---------- Helpers ----------
def bits_from_lines(lines: List[str]) -> str:
    return ''.join(line.strip() for line in lines if line.strip())

def lines_from_bits(bits: str, chunk: int = 8) -> List[str]:
    return [bits[i:i+chunk] for i in range(0, len(bits), chunk)]

def int_to_bits(value: int, width: int) -> str:
    return format(value, f'0{width}b')

def bits_to_int(b: str) -> int:
    return int(b, 2) if b else 0

# def find_audio_start(cover_bytes: list) -> int:
#     """
#     Find index where MP3 audio frames begin by scanning for sync word (11 ones).
#     The sync word can span across bytes, so we join all bits into one stream
#     and search globally. Return the byte index where the sync word starts.
#     If not found, return 0.
#     """
#     bitstream = "".join(cover_bytes)
#     sync_word = "1" * 11
#     pos = bitstream.find(sync_word)
#     print(bitstream[pos:pos+16])
#     if pos == -1:
#         return 0
#     return (pos // 8) + 1
def find_audio_start(cover_bytes: list) -> int:
    """
    Scan per byte for MP3 sync word (11 ones).
    Checks each byte and the next byte for the sync word starting at any bit position.
    Returns the byte index where the sync word starts, or 0 if not found.
    """
    sync_word = "1" * 11
    n = len(cover_bytes)
    for i in range(n - 1):
        # Combine current and next byte for overlap
        combined = cover_bytes[i] + cover_bytes[i + 1]
        # Check all possible bit positions in current byte
        for shift in range(8):
            candidate = combined[shift:shift + 11]
            if candidate == sync_word:
                print("audio_start:", i)
                return i + 4
    # Check last byte alone (if file is very short)
    if n > 0 and cover_bytes[-1].startswith(sync_word):
        return n - 1
    return 0


# ---------- Main functions ----------
def sisip(use_random_start: bool, n_lsb: int = 1):
    assert 1 <= n_lsb <= 4, "n_lsb must be between 1 and 4"

    cover_file = "cover.txt"
    secret_file = "sisip.txt"
    output_file = "stega.txt"

    # --- Read cover ---
    with open(cover_file, "r") as f:
        lines = [ln.rstrip("\n") for ln in f.readlines()]
    cover_ext = lines[0].strip()
    cover_data_lines = lines[1:]
    cover_data = [line if len(line) >= 8 else line.zfill(8) for line in cover_data_lines]
    total_cover_bytes = len(cover_data)
    if total_cover_bytes == 0:
        raise ValueError("Cover contains no data bytes.")

    # --- Find audio sample start ---
    audio_start_idx = find_audio_start(cover_data)
    print(audio_start_idx)
    cover_bytes = [list(b) for b in cover_data]
    usable_cover_bytes = cover_bytes[audio_start_idx:]
    total_usable_bytes = len(usable_cover_bytes)

    # --- Read secret ---
    with open(secret_file, "r") as f:
        s_lines = [ln.rstrip("\n") for ln in f.readlines()]
    secret_ext = s_lines[0].strip()
    secret_data_lines = s_lines[1:]
    secret_bits = bits_from_lines(secret_data_lines)
    content_size_bits = len(secret_bits)

    # --- Build header (always 1 LSB per byte) ---
    magic = int_to_bits(0x5354, 16)
    n_lsb_bits = int_to_bits(n_lsb, 8)
    ext_size = len(secret_ext)
    if ext_size > 255:
        raise ValueError("Extension string too long.")
    ext_size_bits = int_to_bits(ext_size, 8)
    options = 0
    if use_random_start:
        options |= 0b00000010
    options_bits = int_to_bits(options, 8)
    content_size_bits_str = int_to_bits(content_size_bits, 32)
    ext_type_bits = ''.join(int_to_bits(ord(c), 8) for c in secret_ext)

    header_bits = magic + n_lsb_bits + ext_size_bits + options_bits + content_size_bits_str + ext_type_bits
    header_len_bits = len(header_bits)
    header_bytes_needed = header_len_bits

    if header_bytes_needed >= total_usable_bytes:
        raise ValueError("Cover too small to hold header in audio region.")

    # --- Compute capacity ---
    available_bytes = total_usable_bytes - header_bytes_needed
    total_payload_capacity = available_bytes * n_lsb
    if content_size_bits > total_payload_capacity:
        raise ValueError("Not enough capacity in audio samples.")

    # --- Embed header ---
    for i in range(header_len_bits):
        bit = header_bits[i]
        usable_cover_bytes[i][-1] = bit

    # --- Payload start offset ---
    if use_random_start:
        seed_input = (secret_ext + str(content_size_bits)).encode("utf-8")
        digest = hashlib.sha1(seed_input).digest()
        seed_int = int.from_bytes(digest[:4], "big")
        start_offset_bit = seed_int % total_payload_capacity
    else:
        start_offset_bit = 0

    # --- Embed payload ---
    for j in range(content_size_bits):
        global_payload_bit_index = (start_offset_bit + j) % total_payload_capacity
        payload_byte_offset = global_payload_bit_index // n_lsb
        lsb_pos = global_payload_bit_index % n_lsb
        target_byte_idx = header_bytes_needed + payload_byte_offset
        usable_cover_bytes[target_byte_idx][- (lsb_pos + 1)] = secret_bits[j]

    # --- Write back ---
    modified_cover = cover_bytes[:audio_start_idx] + usable_cover_bytes
    stego_lines = [cover_ext] + [''.join(b) for b in modified_cover]
    with open(output_file, "w") as f:
        f.write("\n".join(stego_lines))

    print(f"✅ stega.txt written. Audio start at {audio_start_idx}. Embedded {content_size_bits} bits.")


def ekstrak():
    stego_file = "stega.txt"
    output_file = "extracted.txt"

    with open(stego_file, "r") as f:
        lines = [ln.rstrip("\n") for ln in f.readlines()]
    stego_ext = lines[0].strip()
    stego_data_lines = lines[1:]
    cover_bytes = [line if len(line) >= 8 else line.zfill(8) for line in stego_data_lines]

    audio_start_idx = find_audio_start(cover_bytes)
    print(audio_start_idx)
    usable_cover_bytes = [list(b) for b in cover_bytes[audio_start_idx:]]  # FIX
    total_usable_bytes = len(usable_cover_bytes)

    # --- Read header sequentially (1 bit per byte) ---
    fixed_header_len = 16 + 8 + 8 + 8 + 32  # = 72 bits
    fixed_header_bits = ''.join(usable_cover_bytes[i][-1] for i in range(fixed_header_len))

    magic = bits_to_int(fixed_header_bits[0:16])
    if magic != 0x5354:
        raise ValueError(f"Magic mismatch. Expected 0x5354, got {hex(magic)}")

    n_lsb = bits_to_int(fixed_header_bits[16:24])
    ext_size = bits_to_int(fixed_header_bits[24:32])
    options = bits_to_int(fixed_header_bits[32:40])
    content_size = bits_to_int(fixed_header_bits[40:72])

    # extension string
    ext_bits_len = ext_size * 8
    ext_bits = ''.join(usable_cover_bytes[fixed_header_len + i][-1] for i in range(ext_bits_len))
    ext_chars = ''.join(chr(bits_to_int(ext_bits[i:i+8])) for i in range(0, len(ext_bits), 8))

    header_bits_total = fixed_header_len + ext_bits_len
    available_bytes = total_usable_bytes - header_bits_total
    total_payload_capacity = available_bytes * n_lsb

    # payload offset
    use_random_start = bool(options & 0b00000010)
    if use_random_start:
        seed_input = (ext_chars + str(content_size)).encode("utf-8")
        digest = hashlib.sha1(seed_input).digest()
        seed_int = int.from_bytes(digest[:4], "big")
        start_offset_bit = seed_int % total_payload_capacity
    else:
        start_offset_bit = 0

    # extract payload
    extracted_bits = []
    for j in range(content_size):
        global_payload_bit_index = (start_offset_bit + j) % total_payload_capacity
        payload_byte_offset = global_payload_bit_index // n_lsb
        lsb_pos = global_payload_bit_index % n_lsb
        source_byte_idx = header_bits_total + payload_byte_offset
        extracted_bits.append(usable_cover_bytes[source_byte_idx][- (lsb_pos + 1)])

    secret_bits = ''.join(extracted_bits)

    # write out
    bit_lines = lines_from_bits(secret_bits, 8)
    with open(output_file, "w") as f:
        f.write(ext_chars + "\n")
        for bl in bit_lines:
            f.write(bl + "\n")

    print(f"✅ Extracted {len(secret_bits)} bits. Extension: {ext_chars}. Audio start at {audio_start_idx}.")


if __name__ == "__main__":
    print("start sisip")
    sisip(use_random_start=False, n_lsb=4)
    print("beres sisip, mulai ekstrak")
    ekstrak()
    print("beres ekstrak")
