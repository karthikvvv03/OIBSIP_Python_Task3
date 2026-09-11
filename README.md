# 🔐 PASSWORD GENERATOR — Random Password Generator

A polished desktop password generator built entirely with Python. This project implements the advanced internship requirements with a security-first approach and a portfolio-ready Tkinter interface.

## ✨ Features

- Password length control from **8–64 characters**
- Uppercase, lowercase, numbers and symbols
- Enforces **at least two character categories**
- Uses Python's **`secrets`** module for cryptographically secure randomness
- Guarantees at least **one character from every selected category**
- Secure Fisher–Yates shuffle using `secrets.randbelow`
- **Weak / Medium / Strong** strength indicator
- Optional exclusion of ambiguous characters: `0 O l I 1`
- Automatic clipboard copy after generation
- Manual **Copy** button
- Session history containing only the **latest 5 passwords**
- History is stored in memory and **never written to disk**
- Matplotlib strength snapshot
- Responsive-feeling desktop layout with a dark modern UI
- Input validation and user-friendly error messages
- Unit tests for core password-generation logic

## 🛠 Tech Stack

- Python 3.10+
- Tkinter
- `secrets`
- `pyperclip`
- `matplotlib`
- `unittest`

> `tkinter` normally ships with Python on Windows and macOS. On some Linux distributions you may need the OS package `python3-tk`.

## 🚀 Run locally

### 1. Clone the repository

```bash
git clone https://github.com/YOUR-USERNAME/random-password-generator.git
cd random-password-generator
```

### 2. Create a virtual environment

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Run

```bash
python -m app.password_generator
```
### Screenshots

Place screenshots of the working application in the `screenshots/` folder.

![PASSWORD GENERATOR](screenshots/main_window.png)

## 🔐 Security notes

This application does not use Python's `random` module for password generation. The `secrets` module is designed for security-sensitive random values.

Passwords are never persisted to a database or file. The history is kept in RAM for the current session only and limited to five entries.

## 📁 Project structure

```text
random-password-generator/
├── app/
│   ├── __init__.py
│   └── password_generator.py
├── tests/
│   └── test_password_generator.py
├── .gitignore
├── LICENSE
├── README.md
└── requirements.txt
```

## 💼 Internship talking points

### Problem
Users often create predictable passwords or reuse weak ones.

### Solution
A desktop utility that securely generates random passwords according to user-selected complexity rules.

### Why `secrets`?
`secrets` uses randomness appropriate for security-sensitive applications, unlike general-purpose pseudo-random generation with `random`.

### Why session-only history?
Password history can be sensitive. Keeping only five generated values in memory avoids unnecessary persistence.

## 📌 Future enhancements

- Strength estimation using entropy in bits
- Theme switcher
- Export-free QR display for one-time transfer
- Accessibility improvements
- Packaging with PyInstaller for a standalone executable

## 📄 License

MIT License
