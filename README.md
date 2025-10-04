# Tucil-II-IF4020-Kriptografi

## Steganografi Audio MP3 dengan Multiple-LSB

### 📖 Deskripsi
Proyek ini merupakan implementasi **Tugas Kecil II IF4020 Kriptografi (2025/2026-1)** dengan topik **Steganografi pada berkas audio menggunakan metode Multiple-LSB**.

Program ini dapat:
- Menyisipkan berkas rahasia (secret file) ke dalam audio MP3 (cover audio) dengan memodifikasi bit LSB.
- Mengekstrak kembali berkas rahasia dari audio stego.
- Melakukan enkripsi pada berkas yang disisipkan dan dekripsi ketika mengambil berkas.
- Memulai penyisipan dengan **seed** untuk random start.
- (Bonus) Mengukur kualitas audio hasil stego dengan pendekatan **PSNR (Peak Signal-to-Noise Ratio)** untuk menilai perbedaan kualitas audio sebelum dan sesudah penyisipan.

---

### 📂 Aturan Penempatan Berkas Sesuai Folder
- **`sound/`** : berkas audio cover (input) dan audio hasil sisip (stego).
- **`secret/`** : berkas rahasia yang ingin disembunyikan.
- **`output/`** : berkas audio hasil proses penyisipan.
- **`ekstraksi/`** : berkas rahasia hasil ekstraksi.

---

### ⚙️ Requirement
Seluruh requirement Python dapat diunduh menggunakan file `requirements.txt`.  
Install dengan perintah berikut:
```bash
pip install -r requirements.txt
```

---

### 🛠️ Tech Stack & Dependency
- **Python 3.10+**
- **Standard Library**: `os`, `math`, dll.
- **Tidak menggunakan library eksternal khusus audio** (proses MP3 dilakukan secara biner).
- Semua dependensi tambahan (**pygame**) sudah tercantum di `requirements.txt`.

---

### 🚀 Cara Menjalankan Program
1. Pastikan semua berkas sudah ditempatkan sesuai struktur folder di atas.
2. Jalankan program utama dari folder `src/` dengan perintah:
   ```bash
   python Main.py
   ```
   atau tekan tombol **Play** di VS Code pada file `Main.py`.

---

### 📝 Catatan
- Pastikan nama dan lokasi berkas sesuai dengan spesifikasi folder agar program berjalan dengan baik.
- Untuk proses penyisipan dan ekstraksi, ikuti instruksi yang muncul di terminal atau VS Code.

---