# Design Note — Lab 02 · BJT DC Bias Web App

บันทึกการออกแบบ (ผลของขั้น Brainstorm + Design Approval ก่อนลงมือเขียนโค้ด)
พร้อมเหตุผลของทางเลือกสำคัญทั้งหมด

## 1 · เป้าหมายและขอบเขต

**เป้าหมาย:** Web Application ที่เปิดผ่าน browser (`http://127.0.0.1:5000/`) รับค่า `VCC, R1, R2, RC, RE, β, VBE` แล้วให้ **Python backend** คำนวณ DC Operating Point (`VB, VE, VC, VCE, IC` + `IB, IE`) แสดงพร้อมหน่วย, มี input validation, มี region warning, มี automated tests และ push ขึ้น GitHub ภายในคาบ

**นอกขอบเขต (ตัดทิ้งตั้งแต่ Brainstorm):** Fixed bias / Emitter bias อื่น (Lab 3), SPICE/ngspice (Lab 4), AC/Bode (Lab 5), Transient (Lab 6), วาดวงจรแบบ interactive (Lab 7), FET (Lab 9–10) — ตัดตามหลัก "ทุกสัปดาห์จบด้วยระบบที่ใช้ได้บางส่วน"

## 2 · ทางเลือกทางเทคนิคและเหตุผล

| หัวข้อ | ทางเลือกที่ตัดสินใจ | เหตุผล | ทางเลือกที่ไม่เอา |
|---|---|---|---|
| Web framework | **Flask** | ตามแนะนำใน Lab, เรียนรู้ pattern GET/POST/template ได้ตรงประเด็น, ติดตั้งเบา | Django (หนักเกินจำเป็น), ฝัง JavaScript คำนวณใน browser (ไม่ตอบโจทย์ "Python Backend คำนวณ") |
| สถาปัตยกรรม | **3 ชั้นแยกไฟล์**: `app.py` (routing) → `dc_bias.py` (pure math) → `templates/index.html` (แสดงผล) | ตรงตามโครงสร้างที่ Lab กำหนด; `dc_bias.py` ไม่รู้จัก HTTP จึง test ได้โดยไม่ต้องเปิด server; แก้สมการที่เดียวไม่กระทบ HTML | ไฟล์เดียวทุกอย่าง, ฝังสมการใน template |
| การส่งฟอร์ม | **POST เต็มหน้า** (มาตรฐาน HTML form ธรรมดา) | เรียบง่าย ทดสอบง่าย ไม่ต้องพึ่ง JS — สอดคล้องจุดประสงค์การเรียน HTTP request/response | AJAX/fetch + JSON API (เพิ่มความซับซ้อนโดยไม่จำเป็นในคาบนี้) |
| ชนิด input ใน HTML | `<input type="text" inputmode="decimal">` + validate ฝั่ง server | ยอมรับทั้ง `0.7` `1e3` `2200`; อยากให้ **server เป็นคนตรวจความถูกต้องเสมอ** (เกณฑ์ A4) ไม่พึ่ง client-side อย่างเดียว | `type="number"` (browser กลืน error บางแบบเอง ทำให้ไม่เห็น validation ฝั่ง server) |
| หน่วยอินพุต | VCC/VBE เป็น V, R เป็น Ω, β ไม่มีหน่วย | ตรงตาราง "ข้อมูลเข้า" ใน Lab; แสดง hint หน่วยใต้ฟอร์ม + แปลง kΩ ให้ดูในส่วน "ดูวิธีคำนวณ" | รับหลายหน่วยพร้อมกัน (เพิ่ม parsing ซับซ้อน) |
| Region detection | `VTH ≤ VBE` → cutoff; `VCE < 0.2 V` → saturation; `VCE < 0.5 V` → warning | ตามเงื่อนไขที่ Lab ระบุ ("กรณี VTH ≤ VBE หรือ VCE ต่ำใกล้ saturation ต้องแจ้งข้อจำกัด") | ทำ nonlinear solver จริง (เกินขอบเขต Lab) |
| การแสดงผล | ตาราง HTML + badge region + collapsible แสดงสมการ/สมมติฐาน | โปร่งใสต่อการตรวจสอบย้อนกลับ (แสดง VTH, RTH, ทุก step ได้) | กราฟ/plot (ยังไม่จำเป็นต่อ DC bias) |

## 3 · พฤติกรรมเชิงวิศวกรรมที่ออกแบบไว้

1. **Validation รวมทุก field:** ถ้าผู้ใช้กรอกผิดหลายช่อง แจ้งครบทั้งหมดในครั้งเดียว (ไม่ใช่ทีละช่อง) — ลดความหงุดหงิดตอนแก้
2. **Cutoff แสดงผลทางฟิสิกส์จริง:** เมื่อ `VTH ≤ VBE` ให้ `IB=IC=IE=0`, `VB=VTH`, `VC=VCC`, `VCE=VCC` พร้อม warning ว่าแบบจำลองใช้ไม่ได้ — ไม่ใช่โยนค่าไร้ความหมายใส่สูตร
3. **Saturation:** ยังคำนวณจากสูตร active แต่**ติด warning ชัดเจน**ว่า `IC = β·IB` ใช้ไม่ได้แล้วและค่าจริงจะต่ำกว่านี้ (ตรงตามหลัก "ไม่รายงานว่า approximation ใช้ได้")
4. **ฟอร์มจำค่าที่ผู้ใช้กรอก** หลัง submit ทั้งกรณีสำเร็จและผิดพลาด — ผู้ใช้แก้เฉพาะช่องที่ error ระบุ
5. **Default คือชุดข้อมูลอ้างอิงของ Lab** เพื่อให้เทียบกับ validation doc ได้ทันที

## 4 · ความเสี่ยงและการบริหาร (จาก Brainstorm)

| ความเสี่ยง | การรับมือ |
|---|---|
| เวลา Lab จำกัด (180 นาทีรวม setup) | ตัด scope ตั้งแต่ design: 1 วงจร, 1 หน้าเว็บ, ไม่มี JS logic |
| ค่าที่ได้ "ดูเหมือนถูก" แต่ผิด | เขียน expected values จากการคำนวณมือ**ก่อน**รันโค้ด (ดู `docs/validation.md`) |
| Agent เสนอ feature เกิน Lab | ยึด AGENTS.md "ห้าม scope creep" เป็นเงื่อนไขเขียนโค้ด |
| สับสนหน่วย kΩ/Ω | กำหนด Ω เป็นหน่วยเดียว + แสดงค่า kΩ ข้างผลลัพธ์ในส่วน method |

## 5 · สิ่งที่ตั้งใจทิ้งไว้ให้ Lab ถัดไป

- `dc_bias.py` ถูกออกแบบให้เพิ่ม topology อื่น (fixed bias, emitter bias) ได้โดยเพิ่มฟังก์ชันใหม่โดยไม่ทำลายของเดิม — Lab 3 จะได้ต่อยอดที่นี่
- ผลลัพธ์ใน `DcBiasResult` เป็น dataclass ที่ขยายเป็น JSON API ได้ง่ายเมื่อถึงคาบที่ต้องใช้ frontend แบบ interactive
