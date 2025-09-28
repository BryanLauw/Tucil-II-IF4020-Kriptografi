import os
import hashlib
from typing import List

# ---------- Helpers ----------
def bits_from_lines(lines: List[str]) -> str:
    """Concatenate lines of bit-strings into a single bit string (str of '0'/'1')."""
    return ''.join(line.strip() for line in lines if line.strip())

def lines_from_bits(bits: str, chunk: int = 8) -> List[str]:
    """Split bit string into lines of `chunk` bits (last chunk may be shorter)."""
    return [bits[i:i+chunk] for i in range(0, len(bits), chunk)]

def int_to_bits(value: int, width: int) -> str:
    return format(value, f'0{width}b')

def bits_to_int(b: str) -> int:
    return int(b, 2) if b else 0

# ---------- Main functions ----------
def sisip(use_random_start: bool, n_lsb: int = 1):
    """
    Read cover.txt and sisip.txt and produce stega.txt.

    - use_random_start: if True, secret payload will be placed at a deterministic pseudo-random offset
                        (so it is not contiguous right after header).
    - n_lsb: number of LSBs to use for payload embedding (1..7). Metadata header is ALWAYS 1-LSB per byte.
    """
    assert 1 <= n_lsb <= 7, "n_lsb must be between 1 and 7"

    cover_file = "cover.txt"
    secret_file = "sisip.txt"
    output_file = "stega.txt"

    # --- Read cover ---
    with open(cover_file, "r") as f:
        lines = [ln.rstrip("\n") for ln in f.readlines()]
    cover_ext = lines[0].strip()
    cover_data_lines = lines[1:]
    # Validate each cover line is a bitstring (pad or error)
    cover_data = [line if len(line) >= 8 else line.zfill(8) for line in cover_data_lines]
    total_cover_bytes = len(cover_data)
    if total_cover_bytes == 0:
        raise ValueError("Cover contains no data bytes.")

    # --- Read secret ---
    with open(secret_file, "r") as f:
        s_lines = [ln.rstrip("\n") for ln in f.readlines()]
    secret_ext = s_lines[0].strip()  # e.g. ".pdf"
    secret_data_lines = s_lines[1:]
    secret_bits = bits_from_lines(secret_data_lines)
    content_size_bits = len(secret_bits)

    # --- Build header (we use 1 LSB per byte for header) ---
    # magic (16 bits) for validation
    magic = int_to_bits(0x5354, 16)  # 'ST'
    # store n_lsb as 8 bits
    n_lsb_bits = int_to_bits(n_lsb, 8)
    # ext_size as 8 bits
    ext_size = len(secret_ext)
    if ext_size > 255:
        raise ValueError("Extension string too long (max 255 chars).")
    ext_size_bits = int_to_bits(ext_size, 8)
    # options: 8 bits: bit0 = encryption (not implemented here), bit1 = random-start flag
    options = 0
    if use_random_start:
        options |= 0b00000010
    options_bits = int_to_bits(options, 8)
    # content size: 32 bits (number of bits in secret)
    content_size_bits_str = int_to_bits(content_size_bits, 32)
    # extension ascii bytes
    ext_type_bits = ''.join(int_to_bits(ord(c), 8) for c in secret_ext)

    header_bits = magic + n_lsb_bits + ext_size_bits + options_bits + content_size_bits_str + ext_type_bits
    header_len_bits = len(header_bits)  # number of bits in header
    header_bytes_needed = header_len_bits  # because metadata uses 1 LSB per byte

    if header_bytes_needed >= total_cover_bytes:
        raise ValueError("Cover too small to hold header.")

    # --- Compute available capacity for payload (in bits) ---
    available_bytes = total_cover_bytes - header_bytes_needed
    total_payload_capacity = available_bytes * n_lsb

    if content_size_bits > total_payload_capacity:
        raise ValueError(f"Not enough capacity: need {content_size_bits} bits but available {total_payload_capacity} bits (n_lsb={n_lsb}).")

    # --- Create mutable cover bytes lists ---
    cover_bytes = [list(b) for b in cover_data]  # list of list of char '0'/'1'

    # --- Embed header: write header_bits into first header_bytes_needed cover bytes using 1 LSB each ---
    for i in range(header_len_bits):
        bit = header_bits[i]
        byte_idx = i  # header occupies first N bytes
        # set least significant bit (rightmost)
        cover_bytes[byte_idx][-1] = bit

    # --- Determine payload start offset (in bits within available region) ---
    if use_random_start:
        # deterministic seed: SHA1 of extension + content_size
        seed_input = (secret_ext + str(content_size_bits)).encode("utf-8")
        digest = hashlib.sha1(seed_input).digest()
        seed_int = int.from_bytes(digest[:4], "big")
        start_offset_bit = seed_int % total_payload_capacity
    else:
        start_offset_bit = 0

    # --- Embed payload bits using n_lsb starting from header_bytes_needed ---
    for j in range(content_size_bits):
        global_payload_bit_index = (start_offset_bit + j) % total_payload_capacity
        # map to byte index and lsb pos within that byte
        payload_byte_offset = global_payload_bit_index // n_lsb  # 0..available_bytes-1
        lsb_pos = global_payload_bit_index % n_lsb  # 0..n_lsb-1
        target_byte_idx = header_bytes_needed + payload_byte_offset
        # set: we assign to position -(lsb_pos+1)
        cover_bytes[target_byte_idx][- (lsb_pos + 1)] = secret_bits[j]

    # --- Convert back to lines and write stega.txt ---
    stego_lines = [cover_ext] + [''.join(b) for b in cover_bytes]
    with open(output_file, "w") as f:
        f.write("\n".join(stego_lines))

    print(f"✅ stega.txt written. Embedded {content_size_bits} bits using n_lsb={n_lsb}. Header bytes used: {header_bytes_needed}.")


def ekstrak():
    """
    Read stega.txt produced by sisip() and write extracted.txt which has:
    - line 1: secret extension (e.g. .pdf)
    - following lines: bit lines representing secret content (8 bits per line except possibly last)
    """
    stego_file = "stega.txt"
    output_file = "extracted.txt"

    with open(stego_file, "r") as f:
        lines = [ln.rstrip("\n") for ln in f.readlines()]
    if not lines:
        raise ValueError("stega.txt empty.")
    stego_ext = lines[0].strip()
    stego_data_lines = lines[1:]
    cover_bytes = [line if len(line) >= 8 else line.zfill(8) for line in stego_data_lines]
    total_cover_bytes = len(cover_bytes)
    if total_cover_bytes == 0:
        raise ValueError("No cover bytes found in stega.txt")

    # --- Read first fixed header fields using 1 LSB per byte ---
    # Need to read at least:
    # magic (16) + n_lsb (8) + ext_size (8) + options (8) + content_size (32) = 72 bits
    min_header_bits = 16 + 8 + 8 + 8 + 32
    if total_cover_bytes < min_header_bits:
        raise ValueError("stego file too small to contain header")

    # Read first min_header_bits bits (1 LSB each)
    header_bits_partial = ''.join(cover_bytes[i][-1] for i in range(min_header_bits))
    # parse
    magic = bits_to_int(header_bits_partial[0:16])
    if magic != 0x5354:
        raise ValueError("Magic header mismatch. This file may not contain hidden data (magic mismatch).")
    n_lsb = bits_to_int(header_bits_partial[16:24])
    ext_size = bits_to_int(header_bits_partial[24:32])
    options = bits_to_int(header_bits_partial[32:40])
    content_size = bits_to_int(header_bits_partial[40:72])

    # Now we need to read extension string bits (ext_size*8 bits) from next cover bytes (still 1 LSB per byte)
    ext_bits_start = min_header_bits
    ext_bits_len = ext_size * 8
    ext_bits = ''.join(cover_bytes[ext_bits_start + i][-1] for i in range(ext_bits_len)) if ext_bits_len > 0 else ""
    ext_chars = ''.join(chr(bits_to_int(ext_bits[i:i+8])) for i in range(0, len(ext_bits), 8))

    # Compute how many header bytes we consumed:
    header_bytes_consumed = min_header_bits + ext_bits_len  # because 1 bit per byte

    # available region
    available_bytes = total_cover_bytes - header_bytes_consumed
    total_payload_capacity = available_bytes * n_lsb
    if content_size > total_payload_capacity:
        raise ValueError(f"Content size ({content_size}) exceeds available capacity ({total_payload_capacity}).")

    # Determine start offset (bit index within available region)
    use_random_start = bool(options & 0b00000010)
    if use_random_start:
        seed_input = (ext_chars + str(content_size)).encode("utf-8")
        digest = hashlib.sha1(seed_input).digest()
        seed_int = int.from_bytes(digest[:4], "big")
        start_offset_bit = seed_int % total_payload_capacity
    else:
        start_offset_bit = 0

    # Extract content bits
    extracted_bits = []
    for j in range(content_size):
        global_payload_bit_index = (start_offset_bit + j) % total_payload_capacity
        payload_byte_offset = global_payload_bit_index // n_lsb
        lsb_pos = global_payload_bit_index % n_lsb
        source_byte_idx = header_bytes_consumed + payload_byte_offset
        extracted_bits.append(cover_bytes[source_byte_idx][- (lsb_pos + 1)])

    secret_bits = ''.join(extracted_bits)

    # Write extracted.txt: first line extension, then bit lines (8 bits per line)
    bit_lines = lines_from_bits(secret_bits, 8)
    with open(output_file, "w") as f:
        f.write(ext_chars + "\n")
        for bl in bit_lines:
            f.write(bl + "\n")

    print(f"✅ Extracted {len(secret_bits)} bits to {output_file}. Extension: '{ext_chars}'. n_lsb used: {n_lsb}.")


# ---------------- Example usage ----------------
if __name__ == "__main__":
    # Example: insert using random start with 2 LSBs
    # sisip(use_random_start=False, n_lsb=2)

    # Or extract
    ekstrak()

    # For demonstration here we will not auto-run either function.
    print("Load this module and call sisip(...) to embed or ekstrak() to extract.")
