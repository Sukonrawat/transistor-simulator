# AGENTS.md — AI Coding Conventions

ข้อตกลงสำหรับ AI agent (เช่น OpenCode + Superpowers) ที่ทำงานใน repository นี้
ทุกการแก้ไขโค้ดต้องยึดกฎเหล่านี้เพื่อให้โครงสร้าง สไตล์ และคุณภาพคงเดิม

## ภาษาและการสื่อสาร

- ข้อความใน UI (`templates/index.html`) และ error message ที่ผู้ใช้เห็น: **ภาษาไทย**
- ชื่อตัวแปร/ฟังก์ชัน/คอมเมนต์โค้ด/docstring: **ภาษาอังกฤษ**
- docstring อธิบายสมการ/สมมติฐานได้ แต่ห้ามใส่ตัวเลขผลลัพธ์ที่ "ควรจะได้" โดยไม่มีที่มา

## สถาปัตยกรรม (บังคับใช้)

1. `dc_bias.py` = pure engineering module — **ห้าม import flask / รู้จัก HTTP, request, HTML**
   - รับค่าเป็นตัวเลขหรือ string ที่แปลงเป็น float ได้
   - โยน `BiasInputError` เมื่ออินพุตไม่ถูกต้อง (รวมทุก field ที่ผิดใน `messages`)
2. `app.py` = thin routing layer — **ห้ามใส่สมการฟิสิกส์** เรียก `dc_bias.*` เท่านั้น
3. `templates/index.html` — **ห้ามฝังสมการ/ตัวเลขผลลัพธ์** ทุกค่าต้องมาจากตัวแปร Jinja ที่ backend ส่งมา
4. `static/style.css` — จัดแต่งหน้าตาเท่านั้น ห้ามมีเนื้อหาเชิงข้อมูล
5. เพิ่ม endpoint ใหม่ → ต้องเพิ่ม test ใน `tests/test_web.py` ด้วยเสมอ

## การเขียนโค้ด Python

- Python 3.10+, type hints ใน public functions, docstring ครบทุก module/function สาธารณะ
- หน่วยภายใน: SI ทั้งหมด (โวลต์, โอห์ม, แอมแปร์) — แปลงเป็น mA/µA เฉพาะชั้นแสดงผล (`ic_ma`, `ib_ua`)
- ค่าคงที่ที่เป็นเกณฑ์วิศวกรรม (เช่น `VCE_SAT_THRESHOLD`) ต้องตั้งชื่อเป็น module constant พร้อมคอมเมนต์ที่มา
- ห้าม hardcode ผลลัพธ์ใน HTML, ใน template หรือใน route เด็ดขาด (เกณฑ์ A2)

## การทดสอบ

- รัน `python -m unittest discover -s tests -v` ก่อนทุก commit — **ต้องผ่าน 100%**
- ค่า expected ของ test วิศวกรรมต้องมาจาก **การคำนวณอิสระ** (มือ/เครื่องคิดเลข) ไม่ใช่ copy จาก output โค้ด — อ้างอิงขั้นตอนได้ที่ `docs/validation.md`
- test ใหม่ที่เกี่ยวกับพฤติกรรม browser → ใช้ Flask test client ไม่ต้องเปิด server จริง
- ชื่อ test ใช้รูป `test_<เกณฑ์หรือพฤติกรรม>_<สิ่งที่ตรวจ>` เช่น `test_a4_negative_resistor_shows_clear_error`

## ความปลอดภัยและสิ่งที่ห้าม commit

- ห้าม commit: `.venv/`, `__pycache__/`, `.env`, API keys, credentials (ดู `.gitignore`)
- ก่อน commit ตรวจ `git status` และ `git diff --staged` ทุกครั้ง
- Debug server (`flask run --debug`) ใช้เฉพาะ localhost — ห้ามเปิดเผยสาธารณะ

## ขอบเขตของ Lab (ห้าม scope creep)

- Lab นี้ทำ **DC Bias แบบ Voltage-Divider** เท่านั้น
- ห้ามเพิ่ม AC/transient/Bode/SPICE/FET/UI ตกแต่งหนักโดยไม่ได้รับอนุมัติ — ถ้าเสนอ feature ที่เกิน ให้ตัดออกตามหลักการของ Superpowers workflow (Brainstorm → Design Approval → Plan → Execute → Test)
- การเปลี่ยนสมการหรือเกณฑ์ region ต้องอัปเดต `docs/validation.md` และ test ให้สอดคล้องกันใน commit เดียวกัน

## รูปแบบ commit

ข้อความ commit ภาษาอังกฤษ สั้น ขึ้นต้นด้วย area เช่น `dc_bias:`, `web:`, `tests:`, `docs:` — ยกตัวอย่าง:
`dc_bias: warn when VCE approaches saturation edge`
