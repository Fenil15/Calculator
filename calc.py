import tkinter as tk
import math
import json
import os

SETTINGS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.json")

LARGE_FONT_STYLE = ("Arial", 40, "bold")
SMALL_FONT_STYLE = ("Arial", 16)
DIGITS_FONT_STYLE = ("Arial", 24, "bold")
DEFAULT_FONT_STYLE = ("Arial", 20)
ADV_FONT_STYLE = ("Arial", 14, "bold")

LIGHT = {
    "bg": "#FFFFFF",
    "display_bg": "#F5F5F5",
    "digit": "#FFFFFF",
    "operator": "#F8FAFF",
    "equals": "#CCEDFF",
    "special": "#F8FAFF",
    "advanced": "#E8F4FD",
    "text": "#25265E",
}

DARK = {
    "bg": "#1E1E2E",
    "display_bg": "#13132A",
    "digit": "#2D2D42",
    "operator": "#242438",
    "equals": "#3A6FAA",
    "special": "#242438",
    "advanced": "#1E3050",
    "text": "#D0D0F0",
}

DEFAULT_SETTINGS = {"dark_mode": False, "advanced_mode": False}

BASIC_HEIGHT = 667
ADVANCED_HEIGHT = 800
WIDTH = 375


class Calculator:
    def __init__(self):
        self.settings = self.load_settings()

        self.window = tk.Tk()
        self.window.resizable(0, 0)
        self.window.title("Calculator")

        self.total_expression = ""
        self.current_expression = ""

        self.digits = {
            7: (1, 1), 8: (1, 2), 9: (1, 3),
            4: (2, 1), 5: (2, 2), 6: (2, 3),
            1: (3, 1), 2: (3, 2), 3: (3, 3),
            0: (4, 2), '.': (4, 1),
        }
        self.operations = {"/": "\u00F7", "*": "\u00D7", "-": "-", "+": "+"}

        self.display_frame = None
        self.buttons_frame = None
        self.total_label = None
        self.label = None

        self._build_ui()
        self.bind_keys()

    # ── Settings persistence ──────────────────────────────────────────────────

    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE) as f:
                    data = json.load(f)
                s = DEFAULT_SETTINGS.copy()
                s.update(data)
                return s
            except Exception:
                pass
        return DEFAULT_SETTINGS.copy()

    def save_settings(self):
        try:
            with open(SETTINGS_FILE, "w") as f:
                json.dump(self.settings, f, indent=2)
        except Exception:
            pass

    def get_theme(self):
        return DARK if self.settings["dark_mode"] else LIGHT

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self):
        """(Re)build the entire UI to reflect current settings."""
        theme = self.get_theme()
        height = ADVANCED_HEIGHT if self.settings["advanced_mode"] else BASIC_HEIGHT
        self.window.geometry(f"{WIDTH}x{height}")
        self.window.configure(bg=theme["bg"])

        if self.display_frame:
            self.display_frame.destroy()
        if self.buttons_frame:
            self.buttons_frame.destroy()

        self.display_frame = self._create_display_frame()
        self.total_label, self.label = self._create_display_labels()
        self.buttons_frame = self._create_buttons_frame()
        self._populate_buttons()

    def _create_display_frame(self):
        theme = self.get_theme()
        frame = tk.Frame(self.window, height=221, bg=theme["display_bg"])
        frame.pack(expand=True, fill="both")

        settings_btn = tk.Button(
            frame, text="\u2699", bg=theme["display_bg"], fg=theme["text"],
            font=("Arial", 16), borderwidth=0, relief="flat",
            command=self.open_settings,
        )
        settings_btn.place(relx=1.0, rely=0.0, anchor="ne", x=-8, y=8)

        return frame

    def _create_display_labels(self):
        theme = self.get_theme()
        total_label = tk.Label(
            self.display_frame, text=self.total_expression, anchor=tk.E,
            bg=theme["display_bg"], fg=theme["text"], padx=24, font=SMALL_FONT_STYLE,
        )
        total_label.pack(expand=True, fill="both")

        label = tk.Label(
            self.display_frame, text=self.current_expression, anchor=tk.E,
            bg=theme["display_bg"], fg=theme["text"], padx=24, font=LARGE_FONT_STYLE,
        )
        label.pack(expand=True, fill="both")

        return total_label, label

    def _create_buttons_frame(self):
        theme = self.get_theme()
        frame = tk.Frame(self.window, bg=theme["bg"])
        frame.pack(expand=True, fill="both")
        return frame

    def _populate_buttons(self):
        adv = self.settings["advanced_mode"]
        offset = 2 if adv else 0  # advanced functions occupy rows 0 and 1

        total_rows = 5 + offset
        for r in range(total_rows):
            self.buttons_frame.rowconfigure(r, weight=1)
        for c in range(1, 5):
            self.buttons_frame.columnconfigure(c, weight=1)

        if adv:
            self._create_advanced_buttons()

        self._create_special_buttons(offset)
        self._create_operator_buttons(offset)
        self._create_digit_buttons(offset)

    def _create_advanced_buttons(self):
        theme = self.get_theme()
        buttons = [
            ("sin",       self.calc_sin,      0, 1),
            ("cos",       self.calc_cos,      0, 2),
            ("tan",       self.calc_tan,      0, 3),
            ("log",       self.calc_log,      0, 4),
            ("ln",        self.calc_ln,       1, 1),
            ("e\u02e3",   self.calc_exp,      1, 2),
            ("\u03c0",    self.insert_pi,     1, 3),
            ("x^y",       self.insert_power,  1, 4),
        ]
        for text, cmd, r, c in buttons:
            btn = tk.Button(
                self.buttons_frame, text=text, bg=theme["advanced"],
                fg=theme["text"], font=ADV_FONT_STYLE, borderwidth=0, command=cmd,
            )
            btn.grid(row=r, column=c, sticky=tk.NSEW)

    def _create_special_buttons(self, offset=0):
        theme = self.get_theme()
        specials = [
            ("C",         self.clear,    offset,     1, False),
            ("x\u00b2",  self.square,   offset,     2, False),
            ("\u221ax",   self.sqrt,     offset,     3, False),
            ("=",         self.evaluate, offset + 4, 3, True),
        ]
        for text, cmd, r, c, is_equals in specials:
            btn = tk.Button(
                self.buttons_frame, text=text,
                bg=theme["equals"] if is_equals else theme["special"],
                fg=theme["text"], font=DEFAULT_FONT_STYLE, borderwidth=0, command=cmd,
            )
            if is_equals:
                btn.grid(row=r, column=c, columnspan=2, sticky=tk.NSEW)
            else:
                btn.grid(row=r, column=c, sticky=tk.NSEW)

    def _create_operator_buttons(self, offset=0):
        theme = self.get_theme()
        for i, (operator, symbol) in enumerate(self.operations.items()):
            btn = tk.Button(
                self.buttons_frame, text=symbol, bg=theme["operator"],
                fg=theme["text"], font=DEFAULT_FONT_STYLE, borderwidth=0,
                command=lambda x=operator: self.append_operator(x),
            )
            btn.grid(row=i + offset, column=4, sticky=tk.NSEW)

    def _create_digit_buttons(self, offset=0):
        theme = self.get_theme()
        for digit, (r, c) in self.digits.items():
            btn = tk.Button(
                self.buttons_frame, text=str(digit), bg=theme["digit"],
                fg=theme["text"], font=DIGITS_FONT_STYLE, borderwidth=0,
                command=lambda x=digit: self.add_to_expression(x),
            )
            btn.grid(row=r + offset, column=c, sticky=tk.NSEW)

    # ── Settings window ───────────────────────────────────────────────────────

    def open_settings(self):
        theme = self.get_theme()
        win = tk.Toplevel(self.window)
        win.title("Settings")
        win.geometry("300x220")
        win.resizable(0, 0)
        win.configure(bg=theme["display_bg"])
        win.grab_set()

        dark_var = tk.BooleanVar(value=self.settings["dark_mode"])
        adv_var = tk.BooleanVar(value=self.settings["advanced_mode"])

        tk.Label(
            win, text="Settings", bg=theme["display_bg"], fg=theme["text"],
            font=("Arial", 18, "bold"),
        ).pack(pady=(16, 12))

        chk_kw = dict(
            bg=theme["display_bg"], fg=theme["text"],
            selectcolor=theme["digit"], font=("Arial", 13),
            activebackground=theme["display_bg"], activeforeground=theme["text"],
        )
        tk.Checkbutton(win, text="Dark Mode", variable=dark_var, **chk_kw).pack(anchor="w", padx=30)
        tk.Checkbutton(
            win, text="Advanced Mode  (Log, Exp, Trig)", variable=adv_var, **chk_kw
        ).pack(anchor="w", padx=30)

        def apply_settings():
            self.settings["dark_mode"] = dark_var.get()
            self.settings["advanced_mode"] = adv_var.get()
            self.save_settings()
            win.destroy()
            self._build_ui()
            self.bind_keys()

        btn_frame = tk.Frame(win, bg=theme["display_bg"])
        btn_frame.pack(pady=20)

        tk.Button(
            btn_frame, text="Apply", command=apply_settings,
            bg=theme["equals"], fg=theme["text"],
            font=("Arial", 12), padx=16, pady=6, borderwidth=0,
        ).pack(side=tk.LEFT, padx=8)

        tk.Button(
            btn_frame, text="Cancel", command=win.destroy,
            bg=theme["special"], fg=theme["text"],
            font=("Arial", 12), padx=16, pady=6, borderwidth=0,
        ).pack(side=tk.LEFT, padx=8)

    # ── Key bindings ──────────────────────────────────────────────────────────

    def bind_keys(self):
        self.window.bind("<Return>", lambda event: self.evaluate())
        for key in self.digits:
            self.window.bind(str(key), lambda event, d=key: self.add_to_expression(d))
        for key in self.operations:
            self.window.bind(key, lambda event, op=key: self.append_operator(op))

    # ── Basic calculator operations ───────────────────────────────────────────

    def add_to_expression(self, value):
        self.current_expression += str(value)
        self.update_label()

    def append_operator(self, operator):
        self.current_expression += operator
        self.total_expression += self.current_expression
        self.current_expression = ""
        self.update_total_label()
        self.update_label()

    def clear(self):
        self.current_expression = ""
        self.total_expression = ""
        self.update_label()
        self.update_total_label()

    def square(self):
        try:
            self.current_expression = str(eval(f"{self.current_expression}**2"))
        except Exception:
            self.current_expression = "Error"
        self.update_label()

    def sqrt(self):
        try:
            self.current_expression = str(eval(f"{self.current_expression}**0.5"))
        except Exception:
            self.current_expression = "Error"
        self.update_label()

    def evaluate(self):
        self.total_expression += self.current_expression
        self.update_total_label()
        try:
            self.current_expression = str(eval(self.total_expression))
            self.total_expression = ""
        except Exception:
            self.current_expression = "Error"
        finally:
            self.update_label()

    # ── Advanced math operations ──────────────────────────────────────────────

    def _apply_math(self, fn):
        """Apply a single-argument math function to the current expression."""
        try:
            result = fn(float(self.current_expression))
            self.current_expression = str(result)
        except Exception:
            self.current_expression = "Error"
        self.update_label()

    def calc_sin(self):
        self._apply_math(lambda x: math.sin(math.radians(x)))

    def calc_cos(self):
        self._apply_math(lambda x: math.cos(math.radians(x)))

    def calc_tan(self):
        self._apply_math(lambda x: math.tan(math.radians(x)))

    def calc_log(self):
        self._apply_math(math.log10)

    def calc_ln(self):
        self._apply_math(math.log)

    def calc_exp(self):
        self._apply_math(math.exp)

    def insert_pi(self):
        self.current_expression += str(math.pi)
        self.update_label()

    def insert_power(self):
        """Commit current expression and begin an exponent (x^y)."""
        self.total_expression += self.current_expression + "**"
        self.current_expression = ""
        self.update_total_label()
        self.update_label()

    # ── Display helpers ───────────────────────────────────────────────────────

    def update_total_label(self):
        expression = self.total_expression
        for operator, symbol in self.operations.items():
            expression = expression.replace(operator, f' {symbol} ')
        self.total_label.config(text=expression)

    def update_label(self):
        self.label.config(text=self.current_expression[:11])

    def run(self):
        self.window.mainloop()


if __name__ == "__main__":
    calc = Calculator()
    calc.run()
