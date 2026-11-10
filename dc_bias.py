"""DC bias analysis for an NPN common-emitter amplifier (voltage-divider bias).

This module is the pure engineering core of the Lab 02 web app: it knows
circuit physics and input validation, but nothing about Flask, HTTP or
HTML, so it can be unit-tested and reused without a web server.

Circuit topology (NPN, voltage-divider bias)::

    VCC --R1--+--R2-- GND      (base divider)
              B
    VCC --RC--C                  (collector)
              E
             RE-- GND           (emitter)

Model assumptions (forward-active approximation):
    * constant current gain beta and constant base-emitter voltage VBE
    * cutoff when VTH <= VBE (base not forward biased)
    * saturation when VCE < VCE_SAT_THRESHOLD (IC = beta * IB no longer holds)

Reference equations:
    VTH = VCC * R2 / (R1 + R2)
    RTH = R1 * R2 / (R1 + R2)
    IB  = (VTH - VBE) / (RTH + (beta + 1) * RE)
    IC  = beta * IB
    IE  = (beta + 1) * IB
    VE  = IE * RE
    VB  = VE + VBE
    VC  = VCC - IC * RC
    VCE = VC - VE
"""

from __future__ import annotations

import math
from dataclasses import dataclass

#: Typical VCE(sat) of a small-signal BJT [V]; below this the
#: forward-active relation IC = beta * IB is not valid.
VCE_SAT_THRESHOLD = 0.2
#: VCE below this (but above saturation) still deserves a design warning [V].
VCE_NEAR_SATURATION = 0.5

#: Form field order and human readable labels (used by UI + error messages).
FIELDS = ("vcc", "r1", "r2", "rc", "re", "beta", "vbe")
FIELD_LABELS = {
    "vcc": "VCC",
    "r1": "R1",
    "r2": "R2",
    "rc": "RC",
    "re": "RE",
    "beta": "β (beta)",
    "vbe": "VBE",
}
_MUST_BE_POSITIVE = frozenset({"vcc", "r1", "r2", "rc", "re", "beta"})
_MUST_BE_NON_NEGATIVE = frozenset({"vbe"})


class BiasInputError(ValueError):
    """Invalid component values: missing, non-numeric or out of range.

    ``messages`` always holds the individual per-field problems so the web
    UI can list every wrong field at once instead of only the first one.
    """

    def __init__(self, message: str, messages=None):
        super().__init__(message)
        self.messages = [str(m) for m in messages] if messages else [str(message)]


@dataclass(frozen=True)
class DcBiasResult:
    """DC operating point of the voltage-divider biased NPN stage (SI units).

    Voltages are in V, currents in A and resistances in ohm.
    ``region`` is one of ``"forward-active"``, ``"cutoff"`` or
    ``"saturation"``; ``warnings`` lists model limitations that the UI
    must show to the user.
    """

    # echo of the validated inputs
    vcc: float
    r1: float
    r2: float
    rc: float
    re: float
    beta: float
    vbe: float
    # Thevenin equivalent seen by the base
    vth: float
    rth: float
    # operating point
    ib: float
    ic: float
    ie: float
    vb: float
    ve: float
    vc: float
    vce: float
    # quality information
    region: str
    warnings: tuple

    @property
    def ic_ma(self) -> float:
        """Collector current in mA (display convenience)."""
        return self.ic * 1e3

    @property
    def ie_ma(self) -> float:
        """Emitter current in mA (display convenience)."""
        return self.ie * 1e3

    @property
    def ib_ua(self) -> float:
        """Base current in microamps (display convenience)."""
        return self.ib * 1e6

    @property
    def approximation_valid(self) -> bool:
        """True only in the forward-active region where the model applies."""
        return self.region == "forward-active"


def _validate_value(name: str, raw) -> float:
    """Turn one raw input (string or number) into a checked float.

    Raises :class:`BiasInputError` with a readable Thai message on any
    problem (missing value, non-numeric, non-finite, out of range).
    """
    label = FIELD_LABELS[name]
    if raw is None or (isinstance(raw, str) and not raw.strip()):
        raise BiasInputError(f"ต้องกรอกค่า {label} ให้ครบทุกช่องก่อนกดคำนวณ")
    try:
        value = float(raw)
    except (TypeError, ValueError):
        raise BiasInputError(
            f"{label} ต้องเป็นตัวเลข เช่น 12 หรือ 0.7 (ได้รับ '{raw}')"
        ) from None
    if not math.isfinite(value):
        raise BiasInputError(f"{label} ต้องเป็นตัวเลขจำกัด (ได้รับ '{raw}')")
    if name in _MUST_BE_POSITIVE and value <= 0:
        raise BiasInputError(f"{label} ต้องมากกว่า 0 (ได้รับ {value:g})")
    if name in _MUST_BE_NON_NEGATIVE and value < 0:
        raise BiasInputError(f"{label} ต้องไม่เป็นค่าลบ (ได้รับ {value:g})")
    return value


def parse_bias_form(form) -> dict:
    """Validate a mapping (e.g. ``flask.request.form``) of raw strings.

    Collects every field problem into a single :class:`BiasInputError`
    (``exc.messages`` lists them all) so the UI can show them at once.
    Returns ``{field: float}`` on success.
    """
    errors = []
    values = {}
    for name in FIELDS:
        try:
            values[name] = _validate_value(name, form.get(name))
        except BiasInputError as exc:
            errors.extend(exc.messages)
    if errors:
        raise BiasInputError("ข้อมูลที่กรอกไม่ถูกต้อง", messages=errors)
    return values


def calculate_dc_bias(vcc, r1, r2, rc, re, beta, vbe) -> DcBiasResult:
    """Compute the DC operating point of the voltage-divider biased NPN stage.

    Accepts numbers or numeric strings for every component value and
    raises :class:`BiasInputError` for invalid inputs. See the module
    docstring for the equations and assumptions.
    """
    inputs = {
        "vcc": _validate_value("vcc", vcc),
        "r1": _validate_value("r1", r1),
        "r2": _validate_value("r2", r2),
        "rc": _validate_value("rc", rc),
        "re": _validate_value("re", re),
        "beta": _validate_value("beta", beta),
        "vbe": _validate_value("vbe", vbe),
    }
    vcc = inputs["vcc"]
    r1 = inputs["r1"]
    r2 = inputs["r2"]
    rc = inputs["rc"]
    re = inputs["re"]
    beta = inputs["beta"]
    vbe = inputs["vbe"]

    vth = vcc * r2 / (r1 + r2)
    rth = r1 * r2 / (r1 + r2)
    warnings = []

    if vth <= vbe:
        # The divider cannot forward-bias the base-emitter junction, so the
        # transistor is cut off: IB = IC = IE = 0 and no current flows. With
        # zero base current VB equals VTH (no drop across RTH) and the whole
        # supply appears across collector-emitter.
        ib = ic = ie = ve = 0.0
        vb = vth
        vc = vcc
        vce = vcc
        region = "cutoff"
        warnings.append(
            "Cutoff: VTH ≤ VBE แรงดันไบอัสที่ฐานต่ำกว่า VBE ทรานซิสเตอร์จึงไม่นำกระแส "
            "(IB ≈ IC ≈ 0) แบบจำลอง Forward-Active ใช้ไม่ได้ในภูมิภาคนี้"
        )
    else:
        ib = (vth - vbe) / (rth + (beta + 1.0) * re)
        ic = beta * ib
        ie = (beta + 1.0) * ib
        ve = ie * re
        vb = ve + vbe
        vc = vcc - ic * rc
        vce = vc - ve
        if vce < VCE_SAT_THRESHOLD:
            region = "saturation"
            warnings.append(
                f"Saturation: VCE = {vce:.3f} V ต่ำกว่า VCE(sat) ≈ {VCE_SAT_THRESHOLD:.1f} V "
                "ทรานซิสเตอร์อิ่มตัว สมการ IC = β×IB ใช้ไม่ได้ ค่าที่แสดงเป็นเพียงการประมาณ "
                "จุดทำงานจริงจะมี IC ต่ำกว่าค่านี้"
            )
        else:
            region = "forward-active"
            if vce < VCE_NEAR_SATURATION:
                warnings.append(
                    f"VCE = {vce:.3f} V ต่ำใกล้ขอบ Saturation (< {VCE_NEAR_SATURATION:.1f} V) "
                    "ควรตรวจสอบการออกแบบไบอัสอีกครั้ง เพราะค่าจริงอาจตกไปอยู่ในภาวะอิ่มตัว"
                )

    return DcBiasResult(
        vcc=vcc, r1=r1, r2=r2, rc=rc, re=re, beta=beta, vbe=vbe,
        vth=vth, rth=rth, ib=ib, ic=ic, ie=ie,
        vb=vb, ve=ve, vc=vc, vce=vce,
        region=region, warnings=tuple(warnings),
    )
