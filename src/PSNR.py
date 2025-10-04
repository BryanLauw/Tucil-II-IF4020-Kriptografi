import math

def calculate_psnr_mp3(original_name: str, stego_name: str) -> float:
    """
    Menghitung PSNR antar dua file MP3 berdasarkan bit biner (tanpa dependency).
    File diambil dari folder 'sound/'.
    """
    # folder = "sound"
    # path_orig = os.path.join(folder, original_name)
    # path_stego = os.path.join(folder, stego_name)

    path_orig = original_name
    path_stego = stego_name
    # --- Baca file sebagai byte ---
    with open(path_orig, "rb") as f:
        data_orig = f.read()
    with open(path_stego, "rb") as f:
        data_stego = f.read()

    # --- Samakan panjang (truncate ke file yang lebih pendek) ---
    N = min(len(data_orig), len(data_stego))
    data_orig = data_orig[:N]
    data_stego = data_stego[:N]

    # --- Hitung Mean Squared Error (MSE) antar byte ---
    mse = sum((a - b) ** 2 for a, b in zip(data_orig, data_stego)) / N
    if mse == 0:
        print("✅ File identik, PSNR tak terhingga (∞)")
        return float('inf')

    # --- Hitung PSNR ---
    MAX = 255.0  # range maksimum 1 byte
    psnr = 10 * math.log10((MAX ** 2) / mse)

    print(f"✅ PSNR antara {original_name} dan {stego_name}: {psnr:.2f} dB")
    if psnr < 30:
        print("⚠️ Kualitas file berbeda signifikan (< 30 dB)")
    else:
        print("🎧 Kualitas masih baik (>= 30 dB)")

    return psnr
