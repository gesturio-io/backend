# Gesturio.io

Backend for **Gesturio.io**, built using Django REST Framework.

---

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/gesturio-io/backend.git
cd backend
```

### 2. Set Up Virtual Environment

Install `virtualenv` if not already installed:

```bash
pip install virtualenv
```

Create and activate a virtual environment:

- **Windows**
  ```bash
  virtualenv venv
  .\venv\Scripts\activate
  ```

- **Linux / macOS**
  ```bash
  virtualenv venv
  source venv/bin/activate
  ```

### 3. Install Python Dependencies

```bash
cd gesturio
pip install -r requirements.txt
```

### 4. Configure Redis Server

Download Redis from [this link (v5.0.14.1 for Windows)](https://github.com/tporadowski/redis/releases/download/v5.0.14.1/Redis-x64-5.0.14.1.msi)
Make sure to add it to PATH
Start Redis on port `6380` using:

```bash
redis-server --port 6380
```

---

## 🛠 Running the Development Server

Run database migrations:

```bash
python manage.py migrate
```

Start the server **strictly on `127.0.0.1:8000`** (not `localhost`, which may cause Cookie issues):

```bash
python manage.py runserver 127.0.0.1:8000
```

> **Note:** Using `127.0.0.1:8000` is essential for correct functioning and proper client-server communication.

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please [open an issue](https://github.com/gesturio-io/backend/issues) first to discuss your proposal.

Make sure to update and run tests as appropriate.

---

## 📄 License

This project is licensed under the [MIT License](https://choosealicense.com/licenses/mit/).
