# Quiz Tebak Lirik

Interactive quiz 4 grup, 5 lagu per grup. Untuk projector.

## Fitur
- Flow step-by-step: satu lagu tampil per halaman, tanpa spoiler
- Audio player + Play Bait (potong ke segment yang ditandai)
- Score per lagu: 2 (persis) / 1 (sebagian) / 0 (salah)
- Skor per grup + ranking akhir
- Admin UI (`admin.html`) untuk Mark Start/End timestamp bait
- Audio via CDN: `https://cdn.andotherstori.my.id/quiz-tebak-lirik/audio/`

## Local VPS server
Service aktif via systemd user:

```bash
systemctl --user status quiz-tebak-lirik.service
systemctl --user restart quiz-tebak-lirik.service
```

URL VPS:

```text
http://43.134.72.148:8777/
```

## Upload MP3 ke CDN
Upload MP3 ke R2/CDN path. Taruh file di `audio/`, lalu jalankan:

```bash
BUCKET=cdn ./upload-audio.sh
```

Script pakai `npx wrangler r2 object put`, paralel default 4 upload.

Expected path:

```text
quiz-tebak-lirik/audio/grup1-01-mungkin-nanti.mp3
quiz-tebak-lirik/audio/grup1-02-laskar-pelangi.mp3
quiz-tebak-lirik/audio/grup1-03-surat-cinta-untuk-starla.mp3
quiz-tebak-lirik/audio/grup1-04-to-the-bone.mp3
quiz-tebak-lirik/audio/grup1-05-tak-segampang-itu.mp3
quiz-tebak-lirik/audio/grup2-01-sempurna.mp3
quiz-tebak-lirik/audio/grup2-02-tentang-aku-kau-dan-dia.mp3
quiz-tebak-lirik/audio/grup2-03-asal-kau-bahagia.mp3
quiz-tebak-lirik/audio/grup2-04-gajah.mp3
quiz-tebak-lirik/audio/grup2-05-akad.mp3
quiz-tebak-lirik/audio/grup3-01-pupus.mp3
quiz-tebak-lirik/audio/grup3-02-menghapus-jejakmu.mp3
quiz-tebak-lirik/audio/grup3-03-kehadiranmu.mp3
quiz-tebak-lirik/audio/grup3-04-dia.mp3
quiz-tebak-lirik/audio/grup3-05-monokrom.mp3
quiz-tebak-lirik/audio/grup4-01-kenangan-terindah.mp3
quiz-tebak-lirik/audio/grup4-02-dan.mp3
quiz-tebak-lirik/audio/grup4-03-terima-kasih-cinta.mp3
quiz-tebak-lirik/audio/grup4-04-tetap-dalam-jiwa.mp3
quiz-tebak-lirik/audio/grup4-05-zona-nyaman.mp3
```

Final URLs must resolve like:

```text
https://cdn.andotherstori.my.id/quiz-tebak-lirik/audio/grup1-01-mungkin-nanti.mp3
```

## Set timestamp bait
Buka `admin.html`, play tiap lagu, klik **Mark Start** dan **Mark End** di bagian bait yang mau diputar.
Data disimpan di `localStorage` browser yang sama.

Gunakan **Export JSON** untuk backup, **Import JSON** kalau pindah device/browser.

## Quiz
Buka `index.html`. Klik **Mulai Grup 1**.

## Deploy Vercel
1. Import repo di Vercel
2. Framework: **Other**
3. Deploy

Tidak perlu build command.
