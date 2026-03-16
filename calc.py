import tkinter as tk
import json
import os
from datetime import datetime, timedelta
from tkinter import messagebox

LARGE_FONT_STYLE = ("Arial", 40, "bold")
SMALL_FONT_STYLE = ("Arial", 16)
DIGITS_FONT_STYLE = ("Arial", 24, "bold")
DEFAULT_FONT_STYLE = ("Arial", 20)
SETTINGS_FONT_STYLE = ("Arial", 14)
SETTINGS_TITLE_FONT = ("Arial", 18, "bold")

OFF_WHITE = "#F8FAFF"
WHITE = "#FFFFFF"
LIGHT_BLUE = "#CCEDFF"
LIGHT_GRAY = "#F5F5F5"
LABEL_COLOR = "#25265E"
SETTINGS_BG = "#F0F4FF"
BUTTON_HOVER = "#B0D4F5"

DEFAULT_SETTINGS = {
    "theme": "Light",
    "decimal_precision": 10,
    "angle_unit": "Degrees",
}


class SettingsScreen:
    def __init__(self, parent, settings, on_save):
        self.parent = parent
        self.settings = dict(settings)
        self.on_save = on_save

        self.window = tk.Toplevel(parent)
        self.window.title("Settings")
        self.window.geometry("375x667")
        self.window.resizable(0, 0)
        self.window.configure(bg=SETTINGS_BG)
        self.window.grab_set()

        self._build_ui()

    def _build_ui(self):
        # Header bar
        header = tk.Frame(self.window, bg=LABEL_COLOR, height=56)
        header.pack(fill="x")
        header.pack_propagate(False)

        back_btn = tk.Button(
            header, text="\u2190 Back", bg=LABEL_COLOR, fg=WHITE,
            font=SETTINGS_FONT_STYLE, borderwidth=0, cursor="hand2",
            activebackground=LABEL_COLOR, activeforeground=LIGHT_BLUE,
            command=self._go_back
        )
        back_btn.pack(side=tk.LEFT, padx=16, pady=12)

        title_lbl = tk.Label(
            header, text="Settings", bg=LABEL_COLOR, fg=WHITE,
            font=SETTINGS_TITLE_FONT
        )
        title_lbl.pack(side=tk.LEFT, expand=True)

        # Settings content
        content = tk.Frame(self.window, bg=SETTINGS_BG, padx=24, pady=24)
        content.pack(fill="both", expand=True)

        # Theme
        self._add_section_label(content, "Appearance")
        self._add_option_row(
            content, "Theme",
            ["Light", "Dark"],
            self.settings.get("theme", "Light"),
            "theme"
        )

        # Decimal precision
        self._add_section_label(content, "Calculation")
        self._add_spinbox_row(
            content, "Decimal Precision",
            1, 15,
            self.settings.get("decimal_precision", 10),
            "decimal_precision"
        )

        # Angle unit
        self._add_option_row(
            content, "Angle Unit",
            ["Degrees", "Radians"],
            self.settings.get("angle_unit", "Degrees"),
            "angle_unit"
        )

        # Save button
        save_btn = tk.Button(
            self.window, text="Save", bg=LIGHT_BLUE, fg=LABEL_COLOR,
            font=DEFAULT_FONT_STYLE, borderwidth=0, cursor="hand2",
            activebackground=BUTTON_HOVER, height=2,
            command=self._save
        )
        save_btn.pack(fill="x", padx=24, pady=16)

    def _add_section_label(self, parent, text):
        lbl = tk.Label(
            parent, text=text.upper(), bg=SETTINGS_BG,
            fg=LABEL_COLOR, font=("Arial", 11, "bold"),
            anchor="w"
        )
        lbl.pack(fill="x", pady=(16, 4))

        sep = tk.Frame(parent, bg=LABEL_COLOR, height=1)
        sep.pack(fill="x", pady=(0, 8))

    def _add_option_row(self, parent, label, options, current, key):
        row = tk.Frame(parent, bg=WHITE, pady=12, padx=12)
        row.pack(fill="x", pady=4)

        tk.Label(
            row, text=label, bg=WHITE, fg=LABEL_COLOR,
            font=SETTINGS_FONT_STYLE, anchor="w"
        ).pack(side=tk.LEFT, expand=True, fill="x")

        var = tk.StringVar(value=current)
        self.settings[key] = current

        option_menu = tk.OptionMenu(
            row, var, *options,
            command=lambda v, k=key, sv=var: self._on_option_change(k, sv)
        )
        option_menu.config(
            bg=LIGHT_GRAY, fg=LABEL_COLOR, font=SETTINGS_FONT_STYLE,
            borderwidth=0, highlightthickness=0
        )
        option_menu["menu"].config(bg=LIGHT_GRAY, fg=LABEL_COLOR)
        option_menu.pack(side=tk.RIGHT)

        setattr(self, f"_var_{key}", var)

    def _add_spinbox_row(self, parent, label, from_, to, current, key):
        row = tk.Frame(parent, bg=WHITE, pady=12, padx=12)
        row.pack(fill="x", pady=4)

        tk.Label(
            row, text=label, bg=WHITE, fg=LABEL_COLOR,
            font=SETTINGS_FONT_STYLE, anchor="w"
        ).pack(side=tk.LEFT, expand=True, fill="x")

        var = tk.IntVar(value=current)
        self.settings[key] = current

        spinbox = tk.Spinbox(
            row, from_=from_, to=to, textvariable=var, width=4,
            font=SETTINGS_FONT_STYLE, bg=LIGHT_GRAY, fg=LABEL_COLOR,
            buttonbackground=LIGHT_GRAY, relief="flat",
            command=lambda k=key, sv=var: self._on_spinbox_change(k, sv)
        )
        spinbox.pack(side=tk.RIGHT)

        setattr(self, f"_var_{key}", var)

    def _on_option_change(self, key, var):
        self.settings[key] = var.get()

    def _on_spinbox_change(self, key, var):
        self.settings[key] = var.get()

    def _save(self):
        # Sync spinbox value (Spinbox command fires before value updates)
        for key in ("decimal_precision",):
            var = getattr(self, f"_var_{key}", None)
            if var:
                try:
                    self.settings[key] = int(var.get())
                except (ValueError, tk.TclError):
                    pass

        for key in ("theme", "angle_unit"):
            var = getattr(self, f"_var_{key}", None)
            if var:
                self.settings[key] = var.get()

        self.on_save(self.settings)
        messagebox.showinfo("Settings", "Settings saved!", parent=self.window)
        self.window.destroy()

    def _go_back(self):
        self.window.destroy()

HISTORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "history.json")
SETTINGS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.json")
DEFAULT_SETTINGS = {"history_retention_days": 30}


class Calculator:
    def __init__(self):
        self.settings = self.load_settings()
        self.history = self.load_history()
        self.purge_old_history()

        self.window = tk.Tk()
        self.window.geometry("375x667")
        self.window.resizable(0, 0)
        self.window.title("Calculator")

        self.settings = dict(DEFAULT_SETTINGS)

        self.total_expression = ""
        self.current_expression = ""
        self.display_frame = self.create_display_frame()

        self.total_label, self.label = self.create_display_labels()

        self.digits = {
            7: (1, 1), 8: (1, 2), 9: (1, 3),
            4: (2, 1), 5: (2, 2), 6: (2, 3),
            1: (3, 1), 2: (3, 2), 3: (3, 3),
            0: (4, 2), '.': (4, 1)
        }
        self.operations = {"/": "\u00F7", "*": "\u00D7", "-": "-", "+": "+"}
        self.buttons_frame = self.create_buttons_frame()

        self.buttons_frame.rowconfigure(0, weight=1)
        for x in range(1, 5):
            self.buttons_frame.rowconfigure(x, weight=1)
            self.buttons_frame.columnconfigure(x, weight=1)

        self.create_digit_buttons()
        self.create_operator_buttons()
        self.create_special_buttons()
        self.bind_keys()

    # ── Settings ──────────────────────────────────────────────────────────────

    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r") as f:
                    return {**DEFAULT_SETTINGS, **json.load(f)}
            except Exception:
                pass
        return DEFAULT_SETTINGS.copy()

    def save_settings(self):
        with open(SETTINGS_FILE, "w") as f:
            json.dump(self.settings, f, indent=2)

    # ── History persistence ───────────────────────────────────────────────────

    def load_history(self):
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, "r") as f:
                    return json.load(f)
            except Exception:
                pass
        return []

    def save_history(self):
        with open(HISTORY_FILE, "w") as f:
            json.dump(self.history, f, indent=2)

    def purge_old_history(self):
        """Remove entries older than the configured retention period."""
        retention_days = self.settings.get("history_retention_days", 30)
        cutoff = datetime.now() - timedelta(days=retention_days)
        original_count = len(self.history)
        self.history = [
            e for e in self.history
            if datetime.fromisoformat(e["timestamp"]) > cutoff
        ]
        if len(self.history) < original_count:
            self.save_history()

    def add_to_history(self, expression, result):
        entry = {
            "expression": expression,
            "result": result,
            "timestamp": datetime.now().isoformat(),
        }
        self.history.append(entry)
        self.save_history()

    # ── History window ────────────────────────────────────────────────────────

    def show_history(self):
        history_win = tk.Toplevel(self.window)
        history_win.title("Calculation History")
        history_win.geometry("375x500")
        history_win.resizable(0, 0)

        # Header row
        header = tk.Frame(history_win, bg=LIGHT_GRAY, pady=8)
        header.pack(fill="x")
        tk.Label(
            header, text="History", font=("Arial", 18, "bold"),
            bg=LIGHT_GRAY, fg=LABEL_COLOR
        ).pack(side="left", padx=16)
        tk.Button(
            header, text="Clear All", font=("Arial", 12),
            bg=OFF_WHITE, fg=LABEL_COLOR, borderwidth=0, padx=8, pady=4,
            command=lambda: self._clear_and_refresh(history_win),
        ).pack(side="right", padx=16)

        # Scrollable entry list
        list_frame = tk.Frame(history_win, bg=WHITE)
        list_frame.pack(expand=True, fill="both", padx=8, pady=4)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")

        listbox = tk.Listbox(
            list_frame, yscrollcommand=scrollbar.set,
            font=("Arial", 13), bg=WHITE, fg=LABEL_COLOR,
            selectbackground=LIGHT_BLUE, borderwidth=0,
            activestyle="none",
        )
        listbox.pack(expand=True, fill="both")
        scrollbar.config(command=listbox.yview)

        if not self.history:
            listbox.insert(tk.END, "  No history yet.")
        else:
            for entry in reversed(self.history):
                ts = datetime.fromisoformat(entry["timestamp"]).strftime("%b %d, %H:%M")
                listbox.insert(
                    tk.END,
                    f"  {entry['expression']} = {entry['result']}   ({ts})"
                )

    def _clear_and_refresh(self, history_win):
        self.history = []
        self.save_history()
        history_win.destroy()
        self.show_history()

    # ── Settings window ───────────────────────────────────────────────────────

    def show_settings(self):
        settings_win = tk.Toplevel(self.window)
        settings_win.title("Settings")
        settings_win.geometry("375x220")
        settings_win.resizable(0, 0)

        tk.Label(
            settings_win, text="Settings",
            font=("Arial", 18, "bold"), fg=LABEL_COLOR, bg=LIGHT_GRAY
        ).pack(fill="x", ipady=12)

        form = tk.Frame(settings_win, padx=24, pady=16)
        form.pack(fill="x")

        tk.Label(
            form, text="History retention (days):", font=("Arial", 14)
        ).grid(row=0, column=0, sticky="w", pady=8)

        days_var = tk.StringVar(
            value=str(self.settings.get("history_retention_days", 30))
        )
        days_entry = tk.Entry(form, textvariable=days_var, font=("Arial", 14), width=6)
        days_entry.grid(row=0, column=1, padx=12)

        error_label = tk.Label(form, text="", font=("Arial", 11), fg="red")
        error_label.grid(row=1, column=0, columnspan=2, sticky="w")

        def apply_settings():
            try:
                days = int(days_var.get())
                if days <= 0:
                    raise ValueError
                self.settings["history_retention_days"] = days
                self.save_settings()
                self.purge_old_history()
                settings_win.destroy()
            except ValueError:
                error_label.config(text="Please enter a positive whole number.")

        tk.Button(
            settings_win, text="Apply", font=("Arial", 14),
            bg=LIGHT_BLUE, fg=LABEL_COLOR, borderwidth=0,
            padx=24, pady=8, command=apply_settings,
        ).pack(pady=4)

    # ── UI creation ───────────────────────────────────────────────────────────

    def bind_keys(self):
        self.window.bind("<Return>", lambda event: self.evaluate())
        for key in self.digits:
            self.window.bind(
                str(key), lambda event, digit=key: self.add_to_expression(digit)
            )
        for key in self.operations:
            self.window.bind(
                key, lambda event, operator=key: self.append_operator(operator)
            )

    def create_special_buttons(self):
        self.create_clear_button()
        self.create_equals_button()
        self.create_square_button()
        self.create_sqrt_button()

    def create_display_labels(self):
        total_label = tk.Label(
            self.display_frame, text=self.total_expression,
            anchor=tk.E, bg=LIGHT_GRAY, fg=LABEL_COLOR,
            padx=24, font=SMALL_FONT_STYLE,
        )
        total_label.pack(expand=True, fill="both")

        label = tk.Label(
            self.display_frame, text=self.current_expression,
            anchor=tk.E, bg=LIGHT_GRAY, fg=LABEL_COLOR,
            padx=24, font=LARGE_FONT_STYLE,
        )
        label.pack(expand=True, fill="both")

        return total_label, label

    def create_display_frame(self):
        # Top bar with history and settings buttons
        top_bar = tk.Frame(self.window, bg=LABEL_COLOR, height=40)
        top_bar.pack(fill="x")
        top_bar.pack_propagate(False)

        settings_btn = tk.Button(
            top_bar, text="\u2699 Settings", bg=LABEL_COLOR, fg=WHITE,
            font=("Arial", 12), borderwidth=0, cursor="hand2",
            activebackground=LABEL_COLOR, activeforeground=LIGHT_BLUE,
            command=self.open_settings
        )
        settings_btn.pack(side=tk.RIGHT, padx=12, pady=6)

        history_btn = tk.Button(
            top_bar, text="\U0001F55D History", bg=LABEL_COLOR, fg=WHITE,
            font=("Arial", 12), borderwidth=0, cursor="hand2",
            activebackground=LABEL_COLOR, activeforeground=LIGHT_BLUE,
            command=self.show_history
        )
        history_btn.pack(side=tk.RIGHT, padx=4, pady=6)

        frame = tk.Frame(self.window, height=221, bg=LIGHT_GRAY)
        frame.pack(expand=True, fill="both")
        return frame

    def open_settings(self):
        SettingsScreen(self.window, self.settings, self._apply_settings)

    def _apply_settings(self, new_settings):
        self.settings = new_settings

    def add_to_expression(self, value):
        self.current_expression += str(value)
        self.update_label()

    def create_digit_buttons(self):
        for digit, grid_value in self.digits.items():
            button = tk.Button(
                self.buttons_frame, text=str(digit), bg=WHITE,
                fg=LABEL_COLOR, font=DIGITS_FONT_STYLE, borderwidth=0,
                command=lambda x=digit: self.add_to_expression(x)
            )
            button.grid(
                row=grid_value[0], column=grid_value[1], sticky=tk.NSEW
            )

    def append_operator(self, operator):
        self.current_expression += operator
        self.total_expression += self.current_expression
        self.current_expression = ""
        self.update_total_label()
        self.update_label()

    def create_operator_buttons(self):
        i = 0
        for operator, symbol in self.operations.items():
            button = tk.Button(
                self.buttons_frame, text=symbol, bg=OFF_WHITE,
                fg=LABEL_COLOR, font=DEFAULT_FONT_STYLE, borderwidth=0,
                command=lambda x=operator: self.append_operator(x)
            )
            button.grid(row=i, column=4, sticky=tk.NSEW)
            i += 1

    def clear(self):
        self.current_expression = ""
        self.total_expression = ""
        self.update_label()
        self.update_total_label()

    def create_clear_button(self):
        button = tk.Button(
            self.buttons_frame, text="C",
            bg=OFF_WHITE, fg=LABEL_COLOR, font=DEFAULT_FONT_STYLE,
            borderwidth=0, command=self.clear,
        )
        button.grid(row=0, column=1, sticky=tk.NSEW)

    def create_history_button(self):
        button = tk.Button(
            self.buttons_frame, text="H",
            bg=OFF_WHITE, fg=LABEL_COLOR, font=DEFAULT_FONT_STYLE,
            borderwidth=0, command=self.show_history,
        )
        button.grid(row=0, column=0, sticky=tk.NSEW)

    def create_settings_button(self):
        button = tk.Button(
            self.buttons_frame, text="\u2699",
            bg=OFF_WHITE, fg=LABEL_COLOR, font=DEFAULT_FONT_STYLE,
            borderwidth=0, command=self.show_settings,
        )
        button.grid(row=0, column=1, sticky=tk.NSEW)

    def square(self):
        self.current_expression = str(eval(f"{self.current_expression}**2"))
        self.update_label()

    def create_square_button(self):
        button = tk.Button(
            self.buttons_frame, text="x\u00b2", bg=OFF_WHITE, fg=LABEL_COLOR,
            font=DEFAULT_FONT_STYLE, borderwidth=0, command=self.square
        )
        button.grid(row=0, column=2, sticky=tk.NSEW)


    def sqrt(self):
        self.current_expression = str(eval(f"{self.current_expression}**0.5"))
        self.update_label()

    def create_sqrt_button(self):
        button = tk.Button(
            self.buttons_frame, text="\u221ax", bg=OFF_WHITE, fg=LABEL_COLOR,
            font=DEFAULT_FONT_STYLE, borderwidth=0, command=self.sqrt
        )
        button.grid(row=0, column=3, sticky=tk.NSEW)

    def evaluate(self):
        self.total_expression += self.current_expression
        self.update_total_label()
        expression_to_save = self.total_expression
        try:
            result = str(eval(self.total_expression))
            self.current_expression = result
            self.add_to_history(expression_to_save, result)
            self.total_expression = ""
        except Exception:
            self.current_expression = "Error"
        finally:
            self.update_label()

    def create_equals_button(self):
        button = tk.Button(
            self.buttons_frame, text="=",
            bg=LIGHT_BLUE, fg=LABEL_COLOR, font=DEFAULT_FONT_STYLE,
            borderwidth=0, command=self.evaluate,
        )
        button.grid(row=4, column=3, columnspan=2, sticky=tk.NSEW)

    def create_buttons_frame(self):
        frame = tk.Frame(self.window)
        frame.pack(expand=True, fill="both")
        return frame

    def update_total_label(self):
        expression = self.total_expression
        for operator, symbol in self.operations.items():
            expression = expression.replace(operator, f" {symbol} ")
        self.total_label.config(text=expression)

    def update_label(self):
        self.label.config(text=self.current_expression[:11])

    def run(self):
        self.window.mainloop()


if __name__ == "__main__":
    calc = Calculator()
    calc.run()
