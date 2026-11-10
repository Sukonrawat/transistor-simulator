# BJT DC Bias Web App — ENG29 2121 · Lab 02

เว็บแอปพลิเคชัน **Flask (Python)** สำหรับคำนวณ **จุดทำงาน DC (DC Operating Point)** ของวงจรขยาย **NPN Common Emitter แบบ Voltage-Divider Bias**

ผู้ใช้กรอก `VCC, R1, R2, RC, RE, β, VBE` ผ่านหน้าเว็บ → Flask รับ HTTP POST → `dc_bias.py` คำนวณด้วย Python → ส่ง `VB, VE, VC, VCE, IC` (พร้อม `IB, IE`) กลับมาแสดงใน Browser พร้อมหน่วย, การตรวจสอบข้อมูล และคำเตือนเมื่ออยู่นอก Active Region

> หมายเหตุ: ต้องรันผ่าน **Python Web Server** เท่านั้น (ตามขั้นตอนด้านล่าง) — การ double-click เปิดไฟล์ `templates/index.html` ตรง ๆ ด้วย `file://` **ไม่ใช่** วิธีใช้งาน เพราะจะไม่มีส่วนคำนวณของ Backend ทำงาน

## 1 · การติดตั้งและรัน (Installation)

ต้องมี **Python 3.10+** (`python --version` ตรวจได้)

**Windows (PowerShell)**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m flask --app app run --debug
```

**Linux / macOS**

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m flask --app app run --debug
```

จากนั้นเปิด Browser ไปที่ **<http://127.0.0.1:5000/>** — จะเห็นฟอร์มกรอกค่าที่ prefill ด้วยชุดข้อมูลอ้างอิงจากใบ Lab อยู่แล้ว กด **คำนวณ DC Bias (Calculate)** เพื่อดูผล

> Flask Debug Server ใช้เฉพาะการพัฒนาบนเครื่องตัวเอง ห้ามเปิดเผยให้เครือข่ายสาธารณะ

## 2 · การรัน Automated Tests

ใช้ Terminal อื่น (จาก environment เดียวกันที่ activate `.venv` แล้ว):

```bash
python -m unittest discover -s tests -v
```

ผลที่คาดหวัง: **18 tests OK** — 9 unit tests วิศวกรรม (`tests/test_dc_bias.py`) + 9 HTTP tests ผ่าน Flask test client (`tests/test_web.py`)

## 3 · โครงสร้างโปรเจกต์

```
transistor-simulator/
├── app.py                  # Flask application & HTTP routes (GET /, POST /calculate)
├── dc_bias.py              # independent engineering calculations (ไม่รู้จัก HTTP/HTML)
├── templates/
│   └── index.html          # input form + DC results (Jinja)
├── static/
│   └── style.css           # responsive layout and presentation
├── tests/
│   ├── test_dc_bias.py     # unit tests for engineering logic
│   └── test_web.py         # Flask HTTP route tests (test client)
├── requirements.txt        # Flask and necessary dependencies
├── README.md               # install/run instructions (ไฟล์นี้)
├── AGENTS.md               # AI coding conventions
└── docs/
    ├── design-note.md      # สิ่งที่ตัดสินใจออกแบบและเหตุผล
    ├── validation.md       # การคำนวณอิสระและการตรวจรับ
    ├── reflection.md       # สะท้อนคิดหลังจบ Lab
    └── screenshots/         # ภาพหน้าจอหลักฐานการทำงาน
```

**ความรับผิดชอบแยกส่วน (Separation of concerns)**

| ไฟล์ | หน้าที่ | ต้องไม่ทำ |
|---|---|---|
| `app.py` | รับ HTTP request, เรียก `dc_bias`, เรียก template | ฝังสมการฟิสิกส์ |
| `dc_bias.py` | คำนวณวงจร + ตรวจความถูกต้องอินพุต | รู้จัก Flask/HTML/HTTP |
| `templates/index.html` | แสดงฟอร์ม/ผลลัพธ์ (Jinja) | เขียนสมการหรือตัวเลขค้าง |
| `static/style.css` | จัดหน้าตาเว็บ | อะไรที่เกี่ยวกับตัวเลข |

## 4 · แบบจำลองและสมการที่ใช้

วงจร: `R1` ต่อ VCC–Base, `R2` ต่อ Base–GND, `RC` ต่อ VCC–Collector, `RE` ต่อ Emitter–GND

**สมมติฐาน:** Forward-Active Approximation — β คงที่และ VBE คงที่ตามค่าที่กรอก (ไม่ใช่ SPICE)

```
VTH = VCC × R2 / (R1+R2)
RTH = R1·R2 / (R1+R2)
IB  = (VTH−VBE) / (RTH+(β+1)·RE)
IC  = β·IB          IE = (β+1)·IB
VE  = IE·RE         VB = VE+VBE
VC  = VCC−IC·RC     VCE = VC−VE
```

**การตรวจภูมิภาคทำงาน:** Cutoff เมื่อ `VTH ≤ VBE` · Saturation เมื่อ `VCE < 0.2 V` (ค่าประมาณ VCE(sat)) — ทั้งสองกรณีแสดง **Warning** ชัดเจนและไม่อ้างว่าเป็นผลที่เชื่อถือได้ ส่วน `VCE < 0.5 V` แจ้งเตือนว่าใกล้ขอบ saturation

**หน่วยอินพุต:** VCC, VBE เป็น **โวลต์ (V)** · R1, R2, RC, RE เป็น **โอห์ม (Ω)** เช่น 2.2 kΩ = `2200` · β ไม่มีหน่วย

**ชุดข้อมูลอ้างอิงจากใบ Lab:** `VCC=12 V, R1=100 kΩ, R2=22 kΩ, RC=2.2 kΩ, RE=1 kΩ, β=100, VBE=0.70 V` → `IB = 1.2298581×10⁻⁵ A` (คำนวณอิสระ — ดู `docs/validation.md`)

## 5 · เกณฑ์ตรวจรับ (Acceptance Tests A1–A7)

| # | รายการ | สถานะ | หลักฐาน |
|---|---|---|---|
| A1 | `GET /` แสดงฟอร์ม, HTTP 200 | ✅ | `tests/test_web.py::test_a1_get_index_shows_the_input_form` + `docs/screenshots/01_input_form.png` |
| A2 | `POST /calculate` คำนวณด้วย Backend จริง | ✅ | `test_a2_post_calculate_returns_backend_results`, `test_a2_results_change_with_the_input` + `02_reference_results.png` |
| A3 | ผลตรงกับการคำนวณอิสระ | ✅ | `tests/test_dc_bias.py::ReferenceCircuitTest` (ค่า expected คำนวณมือก่อนรันโค้ด) + `docs/validation.md` |
| A4 | อินพุตไม่ถูกต้องแสดง Error, หน้าไม่ล้ม | ✅ | `test_a4_negative_resistor_shows_clear_error`, `test_a4_non_numeric_and_missing_shows_clear_error` + `04_validation_error.png` |
| A5 | นอก Active Region แสดง Warning | ✅ | `test_a5_cutoff_case_shows_warning`, `test_a5_saturation_case_shows_warning` + `03_cutoff_warning.png`, `05_saturation_warning.png` |
| A6 | ≥3 engineering tests + ≥1 Flask test client test | ✅ | 18 tests รวม (9 engineering + 9 HTTP) |
| A7 | Clone แล้วรันตาม README ได้ | ✅ | ทำตามข้อ 1–2 ของไฟล์นี้ |

## 6 · เดโมสั้น ๆ (Minimum Demo)

1. เปิด <http://127.0.0.1:5000/> → เห็นฟอร์ม
2. กดคำนวณด้วยค่าอ้างอิง → เห็นตาราง `VB=1.942 V, VE=1.242 V, VC=9.294 V, VCE=8.052 V, IC=1.230 mA` พร้อม badge **Forward-Active**
3. เปลี่ยน RC เป็น `-5` → เห็นข้อความ error ภาษาไทยระบุช่องที่ผิด (HTTP 400, หน้าไม่ล้ม)
4. กรอก `VCC=5, R1=10000, R2=100` (VTH ≤ VBE) → badge **Cutoff** + Warning
5. รัน `python -m unittest discover -s tests -v` → 18 OK
6. `git log` → แสดง commit history

## 7 · ขอบเขตของ Lab นี้

ทำเฉพาะ **DC Bias ของ Voltage-Divider Bias** — ยังไม่มี Fixed/Emitter bias อื่น, AC small-signal, Bode plot, transient, signal generator, SPICE solver หรือ FET (จะเพิ่มใน Lab ถัดไปตาม Roadmap ของรายวิชา)

---

ENG29 2121 · COMPUTER PROGRAMMING FOR ELECTRICAL ENGINEERS · 2/2569 · Lab 02
