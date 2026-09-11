import string
import tkinter as tk
from dataclasses import dataclass
from tkinter import messagebox, ttk
from secrets import choice, randbelow

import pyperclip

try:
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
except ImportError:
    FigureCanvasTkAgg = None
    Figure = None


APP_BG = "#0b1120"
CARD_BG = "#111827"
CARD_ALT = "#0f172a"
BORDER = "#1f2937"
TEXT = "#f8fafc"
MUTED = "#94a3b8"
ACCENT = "#38bdf8"
ACCENT_DARK = "#082f49"
SUCCESS = "#4ade80"
WARNING = "#fbbf24"
DANGER = "#f87171"


@dataclass(frozen=True)
class PasswordSettings:
    length: int
    include_upper: bool
    include_lower: bool
    include_numbers: bool
    include_symbols: bool
    exclude_ambiguous: bool


def sanitize_charset(charset: str, exclude_ambiguous: bool) -> str:
    if not exclude_ambiguous:
        return charset
    ambiguous = set("0OlI1l")
    return "".join(ch for ch in charset if ch not in ambiguous)


def generate_password(settings: PasswordSettings) -> str:
    selected = []

    if settings.include_upper:
        selected.append(sanitize_charset(string.ascii_uppercase, settings.exclude_ambiguous))
    if settings.include_lower:
        selected.append(sanitize_charset(string.ascii_lowercase, settings.exclude_ambiguous))
    if settings.include_numbers:
        selected.append(sanitize_charset(string.digits, settings.exclude_ambiguous))
    if settings.include_symbols:
        selected.append(sanitize_charset(string.punctuation, settings.exclude_ambiguous))

    if settings.length < 8:
        raise ValueError("Password length must be at least 8.")
    if len(selected) < 2:
        raise ValueError("Select at least two character types.")
    if any(not charset for charset in selected):
        raise ValueError("Ambiguous-character filtering removed a selected character set.")

    # Guarantee one character from every selected category.
    password_chars = [choice(charset) for charset in selected]

    pool = "".join(selected)
    password_chars.extend(choice(pool) for _ in range(settings.length - len(password_chars)))

    # Fisher-Yates shuffle using cryptographically secure randbelow.
    for index in range(len(password_chars) - 1, 0, -1):
        swap_index = randbelow(index + 1)
        password_chars[index], password_chars[swap_index] = (
            password_chars[swap_index],
            password_chars[index],
        )

    return "".join(password_chars)


def calculate_strength(password: str, category_count: int) -> tuple[str, int]:
    score = 0
    length = len(password)

    if length >= 8:
        score += 20
    if length >= 12:
        score += 15
    if length >= 16:
        score += 15
    if length >= 24:
        score += 10

    score += min(category_count, 4) * 10

    if any(char.isupper() for char in password):
        score += 5
    if any(char.islower() for char in password):
        score += 5
    if any(char.isdigit() for char in password):
        score += 5
    if any(char in string.punctuation for char in password):
        score += 10

    score = min(score, 100)

    if score < 45:
        return "Weak", score
    if score < 75:
        return "Medium", score
    return "Strong", score


class PasswordGeneratorApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.history: list[str] = []
        self.last_strength_score = 0

        self.length_var = tk.IntVar(value=18)
        self.upper_var = tk.BooleanVar(value=True)
        self.lower_var = tk.BooleanVar(value=True)
        self.number_var = tk.BooleanVar(value=True)
        self.symbol_var = tk.BooleanVar(value=True)
        self.ambiguous_var = tk.BooleanVar(value=True)

        self.password_var = tk.StringVar(value="Generate a secure password")
        self.strength_var = tk.StringVar(value="Not generated")
        self.status_var = tk.StringVar(value="Select your preferences, then generate a password.")

        self._setup_window()
        self._setup_styles()
        self._build_ui()
        self._refresh_summary()

    def _setup_window(self) -> None:
        self.root.title("Password Generator")
        self.root.geometry("1120x760")
        self.root.minsize(960, 680)
        self.root.configure(bg=APP_BG)

    def _setup_styles(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Horizontal.TProgressbar",
            troughcolor="#1e293b",
            background=ACCENT,
            bordercolor="#1e293b",
            lightcolor=ACCENT,
            darkcolor=ACCENT,
        )

    def _build_ui(self) -> None:
        self._build_header()

        body = tk.Frame(self.root, bg=APP_BG)
        body.pack(fill="both", expand=True, padx=32, pady=(0, 28))
        body.columnconfigure(0, weight=3)
        body.columnconfigure(1, weight=2)
        body.rowconfigure(0, weight=1)

        self._build_generator_card(body).grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self._build_history_card(body).grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        footer = tk.Label(
            self.root,
            text="Built with Python • secrets • Tkinter • pyperclip • matplotlib",
            bg=APP_BG,
            fg="#475569",
            font=("Segoe UI", 9),
        )
        footer.pack(pady=(0, 12))

    def _build_header(self) -> None:
        header = tk.Frame(self.root, bg=APP_BG)
        header.pack(fill="x", padx=32, pady=(28, 16))

        tk.Label(
            header,
            text="PASSWORD GENERATOR",
            bg=APP_BG,
            fg=ACCENT,
            font=("Segoe UI", 11, "bold"),
        ).pack(anchor="w")

        tk.Label(
            header,
            text="Generate passwords that are hard to guess.",
            bg=APP_BG,
            fg=TEXT,
            font=("Segoe UI", 26, "bold"),
        ).pack(anchor="w", pady=(4, 1))

        tk.Label(
            header,
            text="Secure by default. Clean by design. Nothing is written to disk.",
            bg=APP_BG,
            fg=MUTED,
            font=("Segoe UI", 10),
        ).pack(anchor="w")

    def _card(self, parent: tk.Widget) -> tk.Frame:
        return tk.Frame(parent, bg=CARD_BG, highlightbackground=BORDER, highlightthickness=1)

    def _section_title(self, parent: tk.Widget, title: str, subtitle: str | None = None) -> None:
        tk.Label(
            parent,
            text=title,
            bg=CARD_BG,
            fg=TEXT,
            font=("Segoe UI", 12, "bold"),
        ).pack(anchor="w", padx=24, pady=(22, 2))
        if subtitle:
            tk.Label(
                parent,
                text=subtitle,
                bg=CARD_BG,
                fg=MUTED,
                font=("Segoe UI", 9),
            ).pack(anchor="w", padx=24, pady=(0, 12))

    def _build_generator_card(self, body: tk.Frame) -> tk.Frame:
        card = self._card(body)

        self._section_title(card, "PASSWORD BUILDER", "Tune the password to your needs.")

        row = tk.Frame(card, bg=CARD_BG)
        row.pack(fill="x", padx=24, pady=(2, 0))

        tk.Label(row, text="Length", bg=CARD_BG, fg=MUTED, font=("Segoe UI", 10, "bold")).pack(side="left")
        self.length_value = tk.Label(row, textvariable=self.length_var, bg=CARD_BG, fg=ACCENT, font=("Segoe UI", 11, "bold"))
        self.length_value.pack(side="right")

        scale = tk.Scale(
            card,
            from_=8,
            to=64,
            orient="horizontal",
            resolution=1,
            variable=self.length_var,
            showvalue=False,
            bg=CARD_BG,
            fg=ACCENT,
            troughcolor="#243244",
            activebackground=ACCENT,
            highlightthickness=0,
            bd=0,
            command=lambda _: self._refresh_summary(),
        )
        scale.pack(fill="x", padx=18, pady=(2, 16))

        tk.Label(
            card,
            text="Character types  •  select at least two",
            bg=CARD_BG,
            fg=MUTED,
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w", padx=24, pady=(0, 8))

        options = tk.Frame(card, bg=CARD_BG)
        options.pack(fill="x", padx=18)

        self._make_checkbox(options, "Uppercase  A–Z", self.upper_var).grid(row=0, column=0, sticky="w", padx=6, pady=5)
        self._make_checkbox(options, "Lowercase  a–z", self.lower_var).grid(row=0, column=1, sticky="w", padx=6, pady=5)
        self._make_checkbox(options, "Numbers  0–9", self.number_var).grid(row=1, column=0, sticky="w", padx=6, pady=5)
        self._make_checkbox(options, "Symbols  !@#$", self.symbol_var).grid(row=1, column=1, sticky="w", padx=6, pady=5)

        self.type_summary = tk.Label(
            card,
            text="4 types selected",
            bg=CARD_BG,
            fg=SUCCESS,
            font=("Segoe UI", 9, "bold"),
        )
        self.type_summary.pack(anchor="w", padx=24, pady=(2, 6))

        self._make_checkbox(
            card,
            "Exclude ambiguous characters  •  0 O l I 1",
            self.ambiguous_var,
        ).pack(anchor="w", padx=18, pady=(3, 16))

        tk.Label(
            card,
            text="GENERATED PASSWORD",
            bg=CARD_BG,
            fg="#64748b",
            font=("Segoe UI", 9, "bold"),
        ).pack(anchor="w", padx=24)

        output = tk.Frame(card, bg=CARD_ALT, highlightbackground="#263448", highlightthickness=1)
        output.pack(fill="x", padx=24, pady=(7, 10))

        self.password_entry = tk.Entry(
            output,
            textvariable=self.password_var,
            bg=CARD_ALT,
            fg=TEXT,
            insertbackground=TEXT,
            font=("Consolas", 16, "bold"),
            justify="center",
            relief="flat",
            bd=0,
        )
        self.password_entry.pack(fill="x", padx=14, pady=14)

        actions = tk.Frame(card, bg=CARD_BG)
        actions.pack(fill="x", padx=24, pady=(0, 12))

        tk.Button(
            actions,
            text="GENERATE PASSWORD",
            command=self.generate,
            bg=ACCENT,
            fg=ACCENT_DARK,
            activebackground="#7dd3fc",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            bd=0,
            padx=16,
            pady=11,
            cursor="hand2",
        ).pack(side="left", fill="x", expand=True)

        tk.Button(
            actions,
            text="COPY",
            command=self.copy_current,
            bg="#1e293b",
            fg="#e2e8f0",
            activebackground="#334155",
            activeforeground=TEXT,
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            bd=0,
            padx=18,
            pady=11,
            cursor="hand2",
        ).pack(side="left", padx=(10, 0))

        strength_header = tk.Frame(card, bg=CARD_BG)
        strength_header.pack(fill="x", padx=24)
        tk.Label(strength_header, text="Strength", bg=CARD_BG, fg=MUTED, font=("Segoe UI", 9)).pack(side="left")
        self.strength_label = tk.Label(strength_header, textvariable=self.strength_var, bg=CARD_BG, fg=MUTED, font=("Segoe UI", 9, "bold"))
        self.strength_label.pack(side="right")

        self.progress = ttk.Progressbar(card, orient="horizontal", mode="determinate", maximum=100)
        self.progress.pack(fill="x", padx=24, pady=(7, 8))

        tk.Label(
            card,
            textvariable=self.status_var,
            bg=CARD_BG,
            fg="#64748b",
            font=("Segoe UI", 9),
            wraplength=650,
            justify="left",
        ).pack(anchor="w", padx=24, pady=(0, 20))

        return card

    def _make_checkbox(self, parent: tk.Widget, text: str, variable: tk.BooleanVar) -> tk.Checkbutton:
        return tk.Checkbutton(
            parent,
            text=text,
            variable=variable,
            command=self._refresh_summary,
            bg=CARD_BG,
            fg="#cbd5e1",
            selectcolor="#1e293b",
            activebackground=CARD_BG,
            activeforeground=TEXT,
            font=("Segoe UI", 9),
        )

    def _build_history_card(self, body: tk.Frame) -> tk.Frame:
        card = self._card(body)
        self._section_title(card, "SESSION HISTORY", "The last five passwords stay in memory only.")

        self.history_frame = tk.Frame(card, bg=CARD_BG)
        self.history_frame.pack(fill="both", expand=True, padx=18, pady=(0, 10))

        for _ in range(5):
            self._history_placeholder()

        if Figure and FigureCanvasTkAgg:
            tk.Label(
                card,
                text="STRENGTH SNAPSHOT",
                bg=CARD_BG,
                fg="#64748b",
                font=("Segoe UI", 9, "bold"),
            ).pack(anchor="w", padx=24, pady=(10, 4))

            self.figure = Figure(figsize=(4.0, 1.35), dpi=85, facecolor=CARD_BG)
            self.ax = self.figure.add_subplot(111)
            self.canvas = FigureCanvasTkAgg(self.figure, master=card)
            self.canvas.get_tk_widget().pack(fill="x", padx=20, pady=(0, 16))
            self._draw_strength_chart(None, 0)

        return card

    def _history_placeholder(self) -> None:
        row = tk.Frame(self.history_frame, bg=CARD_ALT)
        row.pack(fill="x", pady=4)
        tk.Label(row, text="No password yet", bg=CARD_ALT, fg="#475569", font=("Consolas", 10)).pack(anchor="w", padx=12, pady=10)

    def _refresh_summary(self) -> None:
        selected = sum(v.get() for v in (self.upper_var, self.lower_var, self.number_var, self.symbol_var))
        self.type_summary.config(
            text=f"{selected} type{'s' if selected != 1 else ''} selected",
            fg=SUCCESS if selected >= 2 else DANGER,
        )
        if selected < 2:
            self.status_var.set("Select at least two character types before generating.")

    def _settings(self) -> PasswordSettings:
        return PasswordSettings(
            length=int(self.length_var.get()),
            include_upper=self.upper_var.get(),
            include_lower=self.lower_var.get(),
            include_numbers=self.number_var.get(),
            include_symbols=self.symbol_var.get(),
            exclude_ambiguous=self.ambiguous_var.get(),
        )

    def generate(self) -> None:
        try:
            settings = self._settings()
            password = generate_password(settings)
        except ValueError as exc:
            messagebox.showerror("Check your settings", str(exc))
            return

        category_count = sum(
            [settings.include_upper, settings.include_lower, settings.include_numbers, settings.include_symbols]
        )
        strength, score = calculate_strength(password, category_count)

        self.password_var.set(password)
        self.last_strength_score = score
        self._update_strength(strength, score)
        self._remember(password)
        self._copy(password)
        self.status_var.set("Generated securely with Python's secrets module and copied to your clipboard.")

    def _update_strength(self, strength: str, score: int) -> None:
        self.strength_var.set(strength)
        self.progress["value"] = score

        color = DANGER if strength == "Weak" else WARNING if strength == "Medium" else SUCCESS
        self.strength_label.config(fg=color)
        self._draw_strength_chart(strength, score)

    def _draw_strength_chart(self, strength: str | None, score: int) -> None:
        if not (hasattr(self, "ax") and hasattr(self, "canvas")):
            return

        self.ax.clear()
        self.ax.set_facecolor(CARD_BG)
        self.ax.set_xlim(0, 100)
        self.ax.set_ylim(0, 1)
        self.ax.set_xticks([])
        self.ax.set_yticks([])

        bar_color = "#334155" if strength is None else (
            DANGER if strength == "Weak" else WARNING if strength == "Medium" else SUCCESS
        )
        self.ax.barh([0.5], [score], height=0.28, color=bar_color)
        self.ax.barh([0.5], [100], height=0.28, color="#1e293b", zorder=0)
        self.ax.barh([0.5], [score], height=0.28, color=bar_color, zorder=1)
        self.ax.text(
            50 if not strength else min(score + 4, 92),
            0.5,
            "Generate a password" if strength is None else f"{score}/100",
            va="center",
            ha="center" if strength is None else "left",
            color=TEXT,
            fontsize=9,
            fontweight="bold",
        )
        for spine in self.ax.spines.values():
            spine.set_visible(False)
        self.figure.tight_layout(pad=0.3)
        self.canvas.draw()

    def _remember(self, password: str) -> None:
        self.history.insert(0, password)
        self.history = self.history[:5]

        for child in self.history_frame.winfo_children():
            child.destroy()

        for item in self.history:
            row = tk.Frame(self.history_frame, bg=CARD_ALT)
            row.pack(fill="x", pady=4)

            masked = "•" * min(len(item), 18)
            tk.Label(
                row, text=masked, bg=CARD_ALT, fg="#cbd5e1",
                font=("Consolas", 10)
            ).pack(side="left", padx=(12, 4), pady=9)

            tk.Label(
                row, text=f"{len(item)} chars", bg=CARD_ALT, fg="#64748b",
                font=("Segoe UI", 8)
            ).pack(side="left")

            tk.Button(
                row,
                text="COPY",
                command=lambda p=item: self._copy(p),
                bg="#1e293b",
                fg="#94a3b8",
                activebackground="#334155",
                relief="flat",
                bd=0,
                cursor="hand2",
                font=("Segoe UI", 8, "bold"),
            ).pack(side="right", padx=6, pady=5)

    def _copy(self, password: str) -> None:
        try:
            pyperclip.copy(password)
        except Exception:
            self.root.clipboard_clear()
            self.root.clipboard_append(password)
            self.root.update()

    def copy_current(self) -> None:
        current = self.password_var.get()
        if not current or current == "Generate a secure password":
            messagebox.showwarning("Nothing to copy", "Generate a password first.")
            return
        self._copy(current)
        self.status_var.set("Password copied to clipboard.")


def main() -> None:
    root = tk.Tk()
    app = PasswordGeneratorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
