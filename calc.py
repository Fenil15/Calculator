import tkinter as tk
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


class Calculator:
    def __init__(self):
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

    def bind_keys(self):
        self.window.bind("<Return>", lambda event: self.evaluate())
        for key in self.digits:
            self.window.bind(
                str(key),
                lambda event, digit=key: self.add_to_expression(digit)
            )

        for key in self.operations:
            self.window.bind(
                key,
                lambda event, operator=key: self.append_operator(operator)
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
            padx=24, font=SMALL_FONT_STYLE
        )
        total_label.pack(expand=True, fill='both')

        label = tk.Label(
            self.display_frame, text=self.current_expression,
            anchor=tk.E, bg=LIGHT_GRAY, fg=LABEL_COLOR,
            padx=24, font=LARGE_FONT_STYLE
        )
        label.pack(expand=True, fill='both')

        return total_label, label

    def create_display_frame(self):
        # Top bar with settings button
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
            self.buttons_frame, text="C", bg=OFF_WHITE, fg=LABEL_COLOR,
            font=DEFAULT_FONT_STYLE, borderwidth=0, command=self.clear
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
        try:
            self.current_expression = str(eval(self.total_expression))
            self.total_expression = ""
        except Exception:
            self.current_expression = "Error"
        finally:
            self.update_label()

    def create_equals_button(self):
        button = tk.Button(
            self.buttons_frame, text="=", bg=LIGHT_BLUE, fg=LABEL_COLOR,
            font=DEFAULT_FONT_STYLE, borderwidth=0, command=self.evaluate
        )
        button.grid(row=4, column=3, columnspan=2, sticky=tk.NSEW)

    def create_buttons_frame(self):
        frame = tk.Frame(self.window)
        frame.pack(expand=True, fill="both")
        return frame

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
