# OSINT SEARCH – Aplicație de Investigație pe Bază de Date Publice

##  Descriere
**OSINT SEARCH** este o aplicație informatică dezvoltată în Python pentru colectarea automată a informațiilor publice despre o persoană (e-mail, username, număr de telefon, imagini), cu scopul generării unui raport vizual de tip OSINT. Este adresată în special angajatorilor sau investigatorilor care doresc validarea identității online a unei persoane.

##  Funcționalități
- Verificarea prezenței unei adrese de e-mail pe site-uri ca Amazon, Instagram, etc.
- Căutarea unui username pe platforme sociale și generarea linkurilor către profilurile găsite.
- Obținerea informațiilor despre un număr de telefon (operator, regiune, validitate).
- Încărcarea de fotografii, cu metadate (descriere, sursă), pentru completarea investigației.
- Crearea și salvarea de rapoarte OSINT vizuale cu drag & drop.
- Interfață grafică modernă (CustomTkinter).
- Vizualizare și editare a bazei de date (PostgreSQL) pentru administrator.

## ⚙ Tehnologii utilizate
- **Python 3.10+**
- **Tkinter / CustomTkinter** – interfață grafică
- **httpx**, **BeautifulSoup**, **Selenium** – web scraping
- **PostgreSQL** – salvarea rezultatelor

##  Instalare

### 1. Creează un mediu virtual (opțional, recomandat)
```bash
python -m venv venv
source venv/bin/activate      # Linux/macOS
venv\Scripts\activate         # Windows
```

### 2. Instalează toate pachetele necesare
Trebuie să instalezi toate bibliotecile externe din fișierul `requirements.txt` folosind comanda:
```bash
pip install -r requirements.txt
```

> Această comandă va instala automat toate dependențele necesare pentru rularea aplicației (Tkinter, httpx, BeautifulSoup, Selenium, CustomTkinter, etc.).

### 3. Asigură-te că ai PostgreSQL instalat și configurat

Creează o bază de date numită `osintSearchDB` și setează utilizatorul `postgres` cu parola `admin`, sau modifică datele din codul aplicației pentru a corespunde propriului tău setup.

Exemplu de conexiune din cod:
```python
def get_connection(self):
    return psycopg2.connect(
        host="localhost",
        database="osintSearchDB",
        user="postgres",
        password="admin",
        port="5432"
    )
```

Dacă folosești alte credențiale, actualizează-le în fișierele sursă corespunzătoare (`databaseinterface.py` sau unde este definită conexiunea).

## Rulare aplicație
După instalarea dependențelor și configurarea bazei de date:
```bash
python main.py
```


## Note legale
Această aplicație respectă politicile GDPR și accesează doar date publice, vizibile legal pe internet. Nu este recomandată utilizarea sa în scopuri ilegale.
