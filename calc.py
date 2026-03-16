import tkinter as tk
import math
import json
import os
from datetime import datetime, timedelta
from tkinter import messagebox

SETTINGS_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "settings.json"
)
HISTORY_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "history.json"
)

LARGE_FONT_STYLE = ("Arial", 40, "bold")
SMALL_FONT_STYLE = ("Arial", 16)
DIGITS_FONT_STYLE = ("Arial", 24, "bold")
DEFAULT_FONT_STYLE = ("Arial", 20)
ADV_FONT_STYLE = ("Arial", 14, "bold")
SETTINGS_FONT_STYLE = ("Arial", 14)
SETTINGS_TITLE_FONT = ("Arial", 18, "bold")

LIGHT = {
    "bg": "#FFFFFF",
    "display_bg": "#F5F5F5",
    "digit": "#FFFFFF",
    "operator": "#F8FAFF",
    "equals": "#CCEDFF",
    "special": "#F8FAFF",
    "advanced": "#E8F4FD",
    "text": "#25265E",
    "header_bg": "#25265E",
    "header_fg": "#FFFFFF",
    "settings_bg": "#F0F4FF",
    "row_bg": "#FFFFFF",
    "row_hover": "#B0D4F5",
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
    "header_bg": "#13132A",
    "header_fg": "#D0D0F0",
    "settings_bg": "#1A1A2E",
    "row_bg": "#2D2D42",
    "row_hover": "#3A5FA0",
}

DEFAULT_SETTINGS = {
    "theme": "Light",
    "advanced_mode": False,
    "angle_unit": "Degrees",
    "decimal_precision": 10,
    "history_retention_days": 30,
}

BASIC_HEIGHT = 667
ADVANCED_HEIGHT = 800
WIDTH = 375


class SettingsScreen:
    def __init__(self, parent, settings, theme, on_save):
        self.settings = dict(settings)
        self.theme = theme
        self.on_save = on_save

        self.window = tk.Toplevel(parent)
        self.window.title("Settings")
        self.window.geometry("375x560")
        self.window.resizable(0, 0)
        self.window.configure(bg=theme["settings_bg"])
        self.window.grab_set()

        self._build_ui()

    def _build_ui(self):
        t = self.theme
        header = tk.Frame(self.window, bg=t["header_bg"], height=56)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Button(
            header, text="\u2190 Back",
            bg=t["header_bg"], fg=t["header_fg"],
            font=SETTINGS_FONT_STYLE, borderwidth=0, cursor="hand2",
            activebackground=t["header_bg"],
            activeforeground=t["equals"],
            command=self._go_back,
        ).pack(side=tk.LEFT, padx=16, pady=12)

        tk.Label(
            header, text="Settings",
            bg=t["header_bg"], fg=t["header_fg"],
            font=SETTINGS_TITLE_FONT,
        ).pack(side=tk.LEFT, expand=True)

        content = tk.Frame(
            self.window, bg=t["settings_bg"], padx=24, pady=16
        )
        content.pack(fill="both", expand=True)

        self._add_section_label(content, "Appearance")
        self._add_option_row(
            content, "Theme", ["Light", "Dark"],
            self.settings.get("theme", "Light"), "theme",
        )

        self._add_section_label(content, "Calculator")
        self._add_option_row(
            content, "Angle Unit", ["Degrees", "Radians"],
            self.settings.get("angle_unit", "Degrees"), "angle_unit",
        )
        self._add_spinbox_row(
            content, "Decimal Precision", 1, 15,
            self.settings.get("decimal_precision", 10),
            "decimal_precision",
        )
        self._add_check_row(
            content, "Advanced Mode (Log, Exp, Trig)",
            self.settings.get("advanced_mode", False),
            "advanced_mode",
        )

        self._add_section_label(content, "History")
        self._add_spinbox_row(
            content, "Retention (days)", 1, 365,
            self.settings.get("history_retention_days", 30),
            "history_retention_days",
        )

        tk.Button(
            self.window, text="Save",
            bg=t["equals"], fg=t["header_fg"],
            font=DEFAULT_FONT_STYLE, borderwidth=0,
            cursor="hand2", height=2,
            activebackground=t["row_hover"],
            command=self._save,
        ).pack(fill="x", padx=24, pady=16)

    def _add_section_label(self, parent, text):
        t = self.theme
        tk.Label(
            parent, text=text.upper(),
            bg=t["settings_bg"], fg=t["text"],
            font=("Arial", 11, "bold"), anchor="w",
        ).pack(fill="x", pady=(16, 4))
        tk.Frame(parent, bg=t["text"], height=1).pack(
            fill="x", pady=(0, 8)
        )

    def _add_option_row(self, parent, label, options, current, key):
        t = self.theme
        row = tk.Frame(parent, bg=t["row_bg"], pady=12, padx=12)
        row.pack(fill="x", pady=4)
        tk.Label(
            row, text=label,
            bg=t["row_bg"], fg=t["text"],
            font=SETTINGS_FONT_STYLE, anchor="w",
        ).pack(side=tk.LEFT, expand=True, fill="x")

        var = tk.StringVar(value=current)
        self.settings[key] = current
        menu = tk.OptionMenu(
            row, var, *options,
            command=lambda v, k=key: self.settings.update({k: v}),
        )
        menu.config(
            bg=t["display_bg"], fg=t["text"],
            font=SETTINGS_FONT_STYLE,
            borderwidth=0, highlightthickness=0,
        )
        menu["menu"].config(bg=t["display_bg"], fg=t["text"])
        menu.pack(side=tk.RIGHT)
        setattr(self, f"_var_{key}", var)

    def _add_spinbox_row(
        self, parent, label, from_, to, current, key
    ):
        t = self.theme
        row = tk.Frame(parent, bg=t["row_bg"], pady=12, padx=12)
        row.pack(fill="x", pady=4)
        tk.Label(
            row, text=label,
            bg=t["row_bg"], fg=t["text"],
            font=SETTINGS_FONT_STYLE, anchor="w",
        ).pack(side=tk.LEFT, expand=True, fill="x")

        var = tk.IntVar(value=current)
        self.settings[key] = current
        tk.Spinbox(
            row, from_=from_, to=to, textvariable=var, width=5,
            font=SETTINGS_FONT_STYLE,
            bg=t["display_bg"], fg=t["text"],
            buttonbackground=t["display_bg"], relief="flat",
            command=lambda k=key, sv=var: self.settings.update(
                {k: sv.get()}
            ),
        ).pack(side=tk.RIGHT)
        setattr(self, f"_var_{key}", var)

    def _add_check_row(self, parent, label, current, key):
        t = self.theme
        row = tk.Frame(parent, bg=t["row_bg"], pady=12, padx=12)
        row.pack(fill="x", pady=4)
        tk.Label(
            row, text=label,
            bg=t["row_bg"], fg=t["text"],
            font=SETTINGS_FONT_STYLE, anchor="w",
        ).pack(side=tk.LEFT, expand=True, fill="x")

        var = tk.BooleanVar(value=current)
        self.settings[key] = current
        tk.Checkbutton(
            row, variable=var,
            bg=t["row_bg"], selectcolor=t["digit"],
            activebackground=t["row_bg"],
            command=lambda k=key, sv=var: self.settings.update(
                {k: sv.get()}
            ),
        ).pack(side=tk.RIGHT)
        setattr(self, f"_var_{key}", var)

    def _save(self):
        for key in ("decimal_precision", "history_retention_days"):
            var = getattr(self, f"_var_{key}", None)
            if var:
                try:
                    self.settings[key] = int(var.get())
                except Exception:
                    pass
        for key in ("theme", "angle_unit"):
            var = getattr(self, f"_var_{key}", None)
            if var:
                self.settings[key] = var.get()
        var = getattr(self, "_var_advanced_mode", None)
        if var:
            self.settings["advanced_mode"] = bool(var.get())
        self.on_save(self.settings)
        messagebox.showinfo(
            "Settings", "Settings saved!", parent=self.window
        )
        self.window.destroy()

    def _go_back(self):
        self.window.destroy()


class Calculator:
    def __init__(self):
        self.settings = self.load_settings()
        self.history = self.load_history()
        self.purge_old_history()

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
        self.operations = {
            "/": "\u00F7", "*": "\u00D7", "-": "-", "+": "+"
        }

        self.top_bar = None
        self.display_frame = None
        self.buttons_frame = None
        self.total_label = None
        self.label = None

        self._build_ui()
        self.bind_keys()

    # ── Settings persistence ──────────────────────────────────────────

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
        return DARK if self.settings.get("theme") == "Dark" else LIGHT

    # ── History persistence ───────────────────────────────────────────

    def load_history(self):
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE) as f:
                    return json.load(f)
            except Exception:
                pass
        return []

    def save_history(self):
        try:
            with open(HISTORY_FILE, "w") as f:
                json.dump(self.history, f, indent=2)
        except Exception:
            pass

    def purge_old_history(self):
        """Remove entries older than the configured retention period."""
        retention = self.settings.get("history_retention_days", 30)
        cutoff = datetime.now() - timedelta(days=retention)
        before = len(self.history)
        self.history = [
            e for e in self.history
            if datetime.fromisoformat(e["timestamp"]) > cutoff
        ]
        if len(self.history) < before:
            self.save_history()

    def add_to_history(self, expression, result):
        self.history.append({
            "expression": expression,
            "result": result,
            "timestamp": datetime.now().isoformat(),
        })
        self.save_history()

    # ── History window ────────────────────────────────────────────────

    def show_history(self):
        t = self.get_theme()
        win = tk.Toplevel(self.window)
        win.title("Calculation History")
        win.geometry("375x500")
        win.resizable(0, 0)
        win.configure(bg=t["bg"])

        header = tk.Frame(win, bg=t["display_bg"], pady=8)
        header.pack(fill="x")
        tk.Label(
            header, text="History",
            font=("Arial", 18, "bold"),
            bg=t["display_bg"], fg=t["text"],
        ).pack(side="left", padx=16)
        tk.Button(
            header, text="Clear All",
            font=("Arial", 12),
            bg=t["special"], fg=t["text"],
            borderwidth=0, padx=8, pady=4,
            command=lambda: self._clear_and_refresh(win),
        ).pack(side="right", padx=16)

        list_frame = tk.Frame(win, bg=t["digit"])
        list_frame.pack(expand=True, fill="both", padx=8, pady=4)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")

        listbox = tk.Listbox(
            list_frame, yscrollcommand=scrollbar.set,
            font=("Arial", 13),
            bg=t["digit"], fg=t["text"],
            selectbackground=t["equals"],
            borderwidth=0, activestyle="none",
        )
        listbox.pack(expand=True, fill="both")
        scrollbar.config(command=listbox.yview)

        if not self.history:
            listbox.insert(tk.END, "  No history yet.")
        else:
            for entry in reversed(self.history):
                ts = datetime.fromisoformat(
                    entry["timestamp"]
                ).strftime("%b %d, %H:%M")
                listbox.insert(
                    tk.END,
                    f"  {entry['expression']} = "
                    f"{entry['result']}   ({ts})",
                )

    def _clear_and_refresh(self, win):
        self.history = []
        self.save_history()
        win.destroy()
        self.show_history()

    # ── UI construction ───────────────────────────────────────────────

    def _build_ui(self):
        """(Re)build the entire UI to reflect current settings."""
        t = self.get_theme()
        height = (
            ADVANCED_HEIGHT
            if self.settings["advanced_mode"]
            else BASIC_HEIGHT
        )
        self.window.geometry(f"{WIDTH}x{height}")
        self.window.configure(bg=t["bg"])

        for attr in ("top_bar", "display_frame", "buttons_frame"):
            frame = getattr(self, attr)
            if frame:
                frame.destroy()

        self.top_bar = self._create_top_bar()
        self.display_frame = self._create_display_frame()
        self.total_label, self.label = self._create_display_labels()
        self.buttons_frame = self._create_buttons_frame()
        self._populate_buttons()

    def _create_top_bar(self):
        t = self.get_theme()
        bar = tk.Frame(self.window, bg=t["header_bg"], height=40)
        bar.pack(fill="x")
        bar.pack_propagate(False)

        tk.Button(
            bar, text="H  History",
            bg=t["header_bg"], fg=t["header_fg"],
            font=("Arial", 12), borderwidth=0, cursor="hand2",
            activebackground=t["header_bg"],
            activeforeground=t["equals"],
            command=self.show_history,
        ).pack(side=tk.LEFT, padx=12, pady=6)

        tk.Button(
            bar, text="\u2699  Settings",
            bg=t["header_bg"], fg=t["header_fg"],
            font=("Arial", 12), borderwidth=0, cursor="hand2",
            activebackground=t["header_bg"],
            activeforeground=t["equals"],
            command=self.open_settings,
        ).pack(side=tk.RIGHT, padx=12, pady=6)

        return bar

    def _create_display_frame(self):
        t = self.get_theme()
        frame = tk.Frame(self.window, height=221, bg=t["display_bg"])
        frame.pack(expand=True, fill="both")
        return frame

    def _create_display_labels(self):
        t = self.get_theme()
        total_label = tk.Label(
            self.display_frame,
            text=self.total_expression,
            anchor=tk.E,
            bg=t["display_bg"], fg=t["text"],
            padx=24, font=SMALL_FONT_STYLE,
        )
        total_label.pack(expand=True, fill="both")

        label = tk.Label(
            self.display_frame,
            text=self.current_expression,
            anchor=tk.E,
            bg=t["display_bg"], fg=t["text"],
            padx=24, font=LARGE_FONT_STYLE,
        )
        label.pack(expand=True, fill="both")

        return total_label, label

    def _create_buttons_frame(self):
        t = self.get_theme()
        frame = tk.Frame(self.window, bg=t["bg"])
        frame.pack(expand=True, fill="both")
        return frame

    def _populate_buttons(self):
        adv = self.settings["advanced_mode"]
        offset = 2 if adv else 0

        for r in range(5 + offset):
            self.buttons_frame.rowconfigure(r, weight=1)
        for c in range(1, 5):
            self.buttons_frame.columnconfigure(c, weight=1)

        if adv:
            self._create_advanced_buttons()
        self._create_special_buttons(offset)
        self._create_operator_buttons(offset)
        self._create_digit_buttons(offset)

    def _create_advanced_buttons(self):
        t = self.get_theme()
        buttons = [
            ("sin",     self.calc_sin,     0, 1),
            ("cos",     self.calc_cos,     0, 2),
            ("tan",     self.calc_tan,     0, 3),
            ("log",     self.calc_log,     0, 4),
            ("ln",      self.calc_ln,      1, 1),
            ("e\u02e3", self.calc_exp,     1, 2),
            ("\u03c0",  self.insert_pi,    1, 3),
            ("x^y",     self.insert_power, 1, 4),
        ]
        for text, cmd, r, c in buttons:
            tk.Button(
                self.buttons_frame, text=text,
                bg=t["advanced"], fg=t["text"],
                font=ADV_FONT_STYLE, borderwidth=0, command=cmd,
            ).grid(row=r, column=c, sticky=tk.NSEW)

    def _create_special_buttons(self, offset=0):
        t = self.get_theme()
        specials = [
            ("C",       self.clear,    offset,     1, False),
            ("x\u00b2", self.square,   offset,     2, False),
            ("\u221ax", self.sqrt,     offset,     3, False),
            ("=",       self.evaluate, offset + 4, 3, True),
        ]
        for text, cmd, r, c, is_eq in specials:
            btn = tk.Button(
                self.buttons_frame, text=text,
                bg=t["equals"] if is_eq else t["special"],
                fg=t["text"],
                font=DEFAULT_FONT_STYLE, borderwidth=0, command=cmd,
            )
            if is_eq:
                btn.grid(row=r, column=c, columnspan=2, sticky=tk.NSEW)
            else:
                btn.grid(row=r, column=c, sticky=tk.NSEW)

    def _create_operator_buttons(self, offset=0):
        t = self.get_theme()
        for i, (op, symbol) in enumerate(self.operations.items()):
            tk.Button(
                self.buttons_frame, text=symbol,
                bg=t["operator"], fg=t["text"],
                font=DEFAULT_FONT_STYLE, borderwidth=0,
                command=lambda x=op: self.append_operator(x),
            ).grid(row=i + offset, column=4, sticky=tk.NSEW)

    def _create_digit_buttons(self, offset=0):
        t = self.get_theme()
        for digit, (r, c) in self.digits.items():
            tk.Button(
                self.buttons_frame, text=str(digit),
                bg=t["digit"], fg=t["text"],
                font=DIGITS_FONT_STYLE, borderwidth=0,
                command=lambda x=digit: self.add_to_expression(x),
            ).grid(row=r + offset, column=c, sticky=tk.NSEW)

    # ── Settings window ───────────────────────────────────────────────

    def open_settings(self):
        SettingsScreen(
            self.window, self.settings,
            self.get_theme(), self._apply_settings,
        )

    def _apply_settings(self, new_settings):
        self.settings = new_settings
        self.save_settings()
        self.purge_old_history()
        self._build_ui()
        self.bind_keys()

    # ── Key bindings ──────────────────────────────────────────────────

    def bind_keys(self):
        self.window.bind("<Return>", lambda event: self.evaluate())
        for key in self.digits:
            self.window.bind(
                str(key),
                lambda event, d=key: self.add_to_expression(d),
            )
        for key in self.operations:
            self.window.bind(
                key,
                lambda event, op=key: self.append_operator(op),
            )

    # ── Basic calculator operations ───────────────────────────────────

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
            self.current_expression = str(
                eval(f"{self.current_expression}**2")
            )
        except Exception:
            self.current_expression = "Error"
        self.update_label()

    def sqrt(self):
        try:
            self.current_expression = str(
                eval(f"{self.current_expression}**0.5")
            )
        except Exception:
            self.current_expression = "Error"
        self.update_label()

    def evaluate(self):
        self.total_expression += self.current_expression
        self.update_total_label()
        expr = self.total_expression
        try:
            precision = self.settings.get("decimal_precision", 10)
            result = str(round(eval(expr), precision))
            self.current_expression = result
            self.add_to_history(expr, result)
            self.total_expression = ""
        except Exception:
            self.current_expression = "Error"
        finally:
            self.update_label()

    # ── Advanced math operations ──────────────────────────────────────

    def _apply_math(self, fn):
        """Apply a single-arg math function to current expression."""
        try:
            precision = self.settings.get("decimal_precision", 10)
            result = fn(float(self.current_expression))
            self.current_expression = str(round(result, precision))
        except Exception:
            self.current_expression = "Error"
        self.update_label()

    def _to_rad(self, x):
        if self.settings.get("angle_unit") == "Radians":
            return x
        return math.radians(x)

    def calc_sin(self):
        self._apply_math(lambda x: math.sin(self._to_rad(x)))

    def calc_cos(self):
        self._apply_math(lambda x: math.cos(self._to_rad(x)))

    def calc_tan(self):
        self._apply_math(lambda x: math.tan(self._to_rad(x)))

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
        """Commit current expression and start an exponent (x^y)."""
        self.total_expression += self.current_expression + "**"
        self.current_expression = ""
        self.update_total_label()
        self.update_label()

    # ── Display helpers ───────────────────────────────────────────────

    def update_total_label(self):
        expression = self.total_expression
        for op, symbol in self.operations.items():
            expression = expression.replace(op, f" {symbol} ")
        self.total_label.config(text=expression)

    def update_label(self):
        self.label.config(text=self.current_expression[:11])

    def run(self):
        self.window.mainloop()


if __name__ == "__main__":
    calc = Calculator()
    calc.run()
