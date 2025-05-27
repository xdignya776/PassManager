# Flask Password Manager

A simple multi-user password manager with:

- User registration (up to 10 users)
- Secure password hashing
- Login/logout with session management
- Each user has their own password vault
- SQLLite3 database for persistent storage
- Native desktop window via [pywebview](https://pywebview.flowrl.com/)
- Ready for packaging as a standalone app with PyInstaller

---

## Features

- Register and log in with a username and password
- Each user can store, view, and delete their own passwords
- All passwords are stored securely in a local SQLite database
- The app opens in a native window (not a browser tab)
- Easy to run on Windows, macOS, or Linux

---

## Installation

1. **Clone or download this repository.**

2. **Install dependencies:**
    ```sh
    pip install flask werkzeug pywebview
    ```

3. **(Optional) Set a strong secret key for Flask sessions:**
    ```sh
    # On Windows (PowerShell)
    $env:FLASK_KEY = "your-very-secret-key"
    # On Linux/macOS
    export FLASK_KEY="your-very-secret-key"
    ```

---

## Usage

Run the app with:

```sh
python app.py
```

- The app will open in a native window at `http://127.0.0.1:9090/`.
- Register a new user, then log in.
- Add, view, and delete passwords in your personal vault.

---

## Packaging as a Standalone App

You can use [PyInstaller](https://pyinstaller.org/) to create a single-file executable:

```sh
pip install pyinstaller
pyinstaller --onefile --noconsole app.py
```

- The resulting executable will open the password manager in a native window.

---

## Security Notes

- Passwords are hashed before storage, but vault entries are stored in plaintext in the database.
---

## License

MIT License

---

## Credits

- [Flask](https://flask.palletsprojects.com/)
- [Werkzeug](https://werkzeug.palletsprojects.com/)
