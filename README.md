# Quiz Tebak Lirik

Interactive quiz 4 grup, 5 lagu per grup. Untuk projector.

## Fitur
- Flow step-by-step: satu lagu tampil per halaman, tanpa spoiler
- Audio player + Play Bait (potong ke segment yang ditandai)
- Score per lagu: 2 (persis) / 1 (sebagian) / 0 (salah)
- Skor per grup + ranking akhir
- Admin UI (`admin.html`) untuk Mark Start/End timestamp bait

## Cara pakai

### 1. Upload MP3
Taruh file audio di folder `audio/` dengan nama:
```
audio/grup1-01-mungkin-nanti.mp3
audio/grup1-02-laskar-pelangi.mp3
audio/grup1-03-surat-cinta-untuk-starla.mp3
audio/grup1-04-to-the-bone.mp3
audio/grup1-05-tak-segampang-itu.mp3
audio/grup2-01-sempurna.mp3
audio/grup2-02-tentang-aku-kau-dan-dia.mp3
audio/grup2-03-asal-kau-bahagia.mp3
audio/grup2-04-gajah.mp3
audio/grup2-05-akad.mp3
audio/grup3-01-pupus.mp3
audio/grup3-02-menghapus-jejakmu.mp3
audio/grup3-03-kehadiranmu.mp3
audio/grup3-04-dia.mp3
audio/grup3-05-monokrom.mp3
audio/grup4-01-kenangan-terindah.mp3
audio/grup4-02-dan.mp3
audio/grup4-03-terima-kasih-cinta.mp3
audio/grup4-04-tetap-dalam-jiwa.mp3
audio/grup4-05-zona-nyaman.mp3
```

### 2. Set timestamp bait
Buka `admin.html`, play tiap lagu, klik **Mark Start** dan **Mark End** di bagian bait yang mau diputar.
Data disimpan di `localStorage` browser yang sama.

### 3. Quiz
Buka `index.html`. Klik **▶ Mulai Grup 1**.

## Deploy Vercel
1. Push repo ke GitHub
2. Import di Vercel → Framework: **Other**
3. Selesai

> ⚠ Audio harus diupload ke folder `audio/`. File MP3 tidak di-commit ke repo (ada di .gitignore).
> Timestamp tersimpan di browser (localStorage) — perlu di-export/import jika ganti device.
