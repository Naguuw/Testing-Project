# Berkas uji: PDF valid, batas ukuran, berkas kosong, dan berkas terlarang.
from __future__ import annotations

from pathlib import Path

NAMA_BERKAS = {
    "pdf_valid": "materi_valid.pdf",
    "pdf_batas_bawah": "materi_batas_bawah.pdf",
    "pdf_batas_tepat": "materi_batas_tepat.pdf",
    "berkas_kosong": "berkas_0_byte.bin",
    "berkas_terlarang": "berkas_ilegal.exe",
    "duplikat_satu": "duplikat/satu/materi.pdf",
    "duplikat_dua": "duplikat/dua/materi.pdf",
}


def _bangun_pdf(padding: int) -> bytes:
    # Padding menambah ukuran berkas tanpa merusak struktur PDF.
    isi = b"BT /F1 16 Tf 72 780 Td (Bahan uji upload Sunan UMK) Tj ET\n"
    if padding > 1:
        isi += b"%" + b" " * (padding - 2) + b"\n"

    objek = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
        b"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(isi)).encode() + b" >>\nstream\n" + isi + b"endstream",
    ]

    keluaran = bytearray(b"%PDF-1.4\n")
    posisi = []
    for nomor, isi_objek in enumerate(objek, start=1):
        posisi.append(len(keluaran))
        keluaran += f"{nomor} 0 obj\n".encode() + isi_objek + b"\nendobj\n"

    mulai_xref = len(keluaran)
    keluaran += f"xref\n0 {len(objek) + 1}\n".encode()
    keluaran += b"0000000000 65535 f \n"
    for angka in posisi:
        keluaran += f"{angka:010d} 00000 n \n".encode()
    keluaran += b"trailer\n"
    keluaran += b"<< /Size " + str(len(objek) + 1).encode() + b" /Root 1 0 R >>\n"
    keluaran += b"startxref\n" + str(mulai_xref).encode() + b"\n%%EOF\n"
    return bytes(keluaran)


def pdf_seukuran(ukuran_byte: int) -> bytes:
    # Padding dihitung ulang sampai ukuran akhirnya pas.
    if ukuran_byte < 1400:
        raise ValueError("Ukuran PDF minimal 1400 byte")
    padding = ukuran_byte - 1400
    for _ in range(40):
        data = _bangun_pdf(padding)
        selisih = ukuran_byte - len(data)
        if selisih == 0:
            return data
        padding += selisih
        if padding < 1:
            raise ValueError(f"Ukuran {ukuran_byte} byte terlalu kecil untuk PDF")
    raise RuntimeError(f"Gagal menyusun PDF seukuran {ukuran_byte} byte")


def siapkan_berkas(folder: Path, batas_mb: int = 5) -> dict[str, Path]:
    folder.mkdir(parents=True, exist_ok=True)
    batas = batas_mb * 1024 * 1024
    target = {kunci: folder / nama for kunci, nama in NAMA_BERKAS.items()}

    if not target["pdf_valid"].exists():
        target["pdf_valid"].write_bytes(pdf_seukuran(1500))
    if not target["pdf_batas_bawah"].exists():
        target["pdf_batas_bawah"].write_bytes(pdf_seukuran(batas - 1))
    if not target["pdf_batas_tepat"].exists():
        target["pdf_batas_tepat"].write_bytes(pdf_seukuran(batas))
    if not target["berkas_kosong"].exists():
        target["berkas_kosong"].write_bytes(b"")
    if not target["berkas_terlarang"].exists():
        target["berkas_terlarang"].write_bytes(
            b"BERKAS TIRUAN untuk uji format terlarang. Tidak dapat dieksekusi.\n"
        )
    for kunci in ("duplikat_satu", "duplikat_dua"):
        berkas = target[kunci]
        berkas.parent.mkdir(parents=True, exist_ok=True)
        if not berkas.exists():
            berkas.write_bytes(pdf_seukuran(1500))

    return target
