# Manajemen Servis Bengkel Motor

REST API untuk manajemen servis bengkel motor. Dibuat dengan FastAPI dan Pydantic v2, dengan struktur modular, API key sederhana, serta unit test dan tes API menggunakan pytest.

## Persyaratan
Python 3.9 atau lebih baru (sudah diuji di Python 3.9).

## Entitas
Pelanggan, Kendaraan, Mekanik, Sparepart, dan Servis (order).

## Alur status servis
```text
antri -> dikerjakan -> selesai -> dibayar
```
Status hanya boleh maju satu langkah. Melompat atau mundur ditolak dengan `409 INVALID_STATUS_TRANSITION`.

## Aturan bisnis
1. **Total biaya = jasa + sparepart.** `total_cost = labor_cost + jumlah(harga_satuan x qty)`. Dihitung ulang setiap kali sparepart ditambahkan.
2. **Stok sparepart berkurang otomatis** saat sparepart ditambahkan ke servis. Jika stok tidak cukup, request ditolak (`409 INSUFFICIENT_STOCK`) dan stok tidak berubah. Harga satuan dikunci saat sparepart ditambahkan.
3. **Satu mekanik tidak boleh memegang lebih dari N servis aktif.** Servis aktif adalah servis berstatus `antri` atau `dikerjakan`. Default N = 3 dan bisa diubah lewat environment variable `BENGKEL_MAX_ACTIVE_SERVICES`. Jika sudah penuh, servis baru ditolak (`409 MECHANIC_AT_CAPACITY`). Setelah servis `selesai`, kapasitas mekanik kembali.
4. Sparepart hanya bisa ditambahkan saat servis `antri` atau `dikerjakan`.
5. Plat nomor kendaraan dinormalkan (huruf besar, spasi dirapikan) dan harus unik.

## Menjalankan di macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
uvicorn main:app --reload
```

Buka `http://127.0.0.1:8000/docs` untuk mencoba API melalui Swagger UI.

## API key
Untuk endpoint `/api/v1/...`, kirim header:

```text
X-API-Key: bengkel-dev-key
```

Key ini hanya contoh untuk tugas. Bisa diganti lewat environment variable `BENGKEL_API_KEY`.

> Penyimpanan menggunakan memori (in-memory), sehingga data kosong kembali saat server dimulai ulang.

## Endpoint

| Method | Endpoint | Fungsi |
|---|---|---|
| GET | `/` | Informasi layanan, tanpa API key |
| POST | `/api/v1/customers` | Tambah pelanggan |
| GET | `/api/v1/customers` | Daftar pelanggan |
| GET | `/api/v1/customers/{id}` | Detail pelanggan |
| POST | `/api/v1/vehicles` | Tambah kendaraan milik pelanggan |
| GET | `/api/v1/vehicles` | Daftar kendaraan; mendukung `?customer_id=1` |
| GET | `/api/v1/vehicles/{id}` | Detail kendaraan |
| POST | `/api/v1/mechanics` | Tambah mekanik |
| GET | `/api/v1/mechanics` | Daftar mekanik beserta jumlah servis aktif |
| GET | `/api/v1/mechanics/{id}` | Detail mekanik |
| POST | `/api/v1/spareparts` | Tambah sparepart |
| GET | `/api/v1/spareparts` | Daftar sparepart |
| GET | `/api/v1/spareparts/{id}` | Detail sparepart |
| POST | `/api/v1/spareparts/{id}/restock` | Tambah stok |
| POST | `/api/v1/services` | Buat servis (status awal `antri`) |
| GET | `/api/v1/services` | Daftar servis; mendukung `?status=` dan `?mechanic_id=` |
| GET | `/api/v1/services/{id}` | Detail servis beserta total biaya |
| POST | `/api/v1/services/{id}/parts` | Tambah sparepart ke servis (stok berkurang) |
| PATCH | `/api/v1/services/{id}/status` | Maju ke status berikutnya |

## Contoh alur

Contoh berikut untuk macOS/Linux (bash/zsh), dijalankan setelah server menyala.

```bash
KEY="X-API-Key: bengkel-dev-key"
JSON="Content-Type: application/json"

curl -X POST http://127.0.0.1:8000/api/v1/customers -H "$JSON" -H "$KEY" \
  -d '{"name":"Andi Saputra","phone":"081234567890"}'

curl -X POST http://127.0.0.1:8000/api/v1/vehicles -H "$JSON" -H "$KEY" \
  -d '{"customer_id":1,"plate_number":"DD 1234 AB","brand":"Honda","model":"Beat","year":2020}'

curl -X POST http://127.0.0.1:8000/api/v1/mechanics -H "$JSON" -H "$KEY" \
  -d '{"name":"Budi","specialty":"Mesin"}'

curl -X POST http://127.0.0.1:8000/api/v1/spareparts -H "$JSON" -H "$KEY" \
  -d '{"name":"Oli Mesin 1L","price":50000,"stock":10}'

curl -X POST http://127.0.0.1:8000/api/v1/services -H "$JSON" -H "$KEY" \
  -d '{"vehicle_id":1,"mechanic_id":1,"complaint":"Mesin brebet saat digas","labor_cost":100000}'

curl -X POST http://127.0.0.1:8000/api/v1/services/1/parts -H "$JSON" -H "$KEY" \
  -d '{"sparepart_id":1,"quantity":2}'

curl -X PATCH http://127.0.0.1:8000/api/v1/services/1/status -H "$JSON" -H "$KEY" \
  -d '{"status":"dikerjakan"}'
```

## Menjalankan tes

```bash
pytest -v
```

- `tests/unit/` berisi unit test untuk aturan bisnis murni (billing, workflow, inventory, mechanic_load) tanpa HTTP.
- `tests/test_api.py` berisi tes endpoint lewat FastAPI `TestClient`.
- Data penyimpanan di-reset sebelum setiap tes agar hasil tes tidak saling memengaruhi.

## Struktur folder

```text
ManajemenServisBengkelMotor/
├── main.py
├── requirements.txt
├── pytest.ini
├── README.md
├── app/
│   ├── core/            # config, enum status, error domain
│   ├── dependencies/    # autentikasi API key
│   ├── repositories/    # penyimpanan in-memory
│   ├── schemas/         # contract data (Pydantic)
│   ├── services/        # aturan bisnis (billing, workflow, inventory, mechanic_load, orders)
│   └── routers/         # endpoint HTTP
└── tests/
    ├── conftest.py
    ├── test_api.py
    └── unit/
```
