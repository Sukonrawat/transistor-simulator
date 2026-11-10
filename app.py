"""Flask front end for the ENG29 2121 Lab 02 BJT DC bias web app.

Responsibilities (kept intentionally thin):
    * serve the input form                       (GET /)
    * accept the submitted component values      (POST /calculate, also POST /)
    * delegate ALL circuit math to dc_bias.py
    * render results / validation errors through templates/index.html

Run (development server only, never expose to a public network):
    python -m flask --app app run --debug
    # then open http://127.0.0.1:5000/
"""

from __future__ import annotations

from flask import Flask, render_template, request

import dc_bias

app = Flask(__name__)

# Reference circuit from the lab handout (resistances in ohm);
# also used to prefill the form on a fresh GET /.
DEFAULT_VALUES = {
    "vcc": 12.0,
    "r1": 100_000.0,
    "r2": 22_000.0,
    "rc": 2_200.0,
    "re": 1_000.0,
    "beta": 100.0,
    "vbe": 0.70,
}


def _format_number(value) -> str:
    """Render a float for the form: integers without ``.0``, rest compact."""
    value = float(value)
    if value.is_integer():
        return str(int(value))
    return f"{value:g}"


def _form_values(source=None) -> dict:
    """Values used to (re)fill the form: submitted input or the defaults."""
    values = {}
    for name, default in DEFAULT_VALUES.items():
        submitted = source.get(name) if source is not None else None
        if submitted is not None and str(submitted).strip() != "":
            values[name] = submitted
        else:
            values[name] = _format_number(default)
    return values


@app.get("/")
def index():
    """A1: show the input form prefilled with the reference values."""
    return render_template(
        "index.html", form_values=_form_values(), result=None, error_messages=None
    )


@app.post("/")
def index_post():
    """Convenience alias so POST / behaves exactly like POST /calculate."""
    return calculate()


@app.post("/calculate")
def calculate():
    """A2-A5: validate input, compute DC bias, render results or errors."""
    try:
        values = dc_bias.parse_bias_form(request.form)
    except dc_bias.BiasInputError as exc:
        # A4: clear per-field error listing; the page still renders (no crash).
        return render_template(
            "index.html",
            form_values=_form_values(request.form),
            result=None,
            error_messages=exc.messages,
        ), 400
    result = dc_bias.calculate_dc_bias(**values)
    return render_template(
        "index.html",
        form_values={name: _format_number(value) for name, value in values.items()},
        result=result,
        error_messages=None,
    )


if __name__ == "__main__":
    # Development server only — never expose this to a public network.
    app.run(host="127.0.0.1", port=5000, debug=True)
