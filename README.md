# DRF Authentication Lab — 4 ta autentifikatsiya usuli

**Maqsad:** bir loyiha ichida `BasicAuthentication`, `SessionAuthentication`, `TokenAuthentication` va `JWTAuthentication` ni amaliy farqlash. Qo'shimcha: registratsiya, JWT bilan himoyalangan shaxsiy `Note` CRUD va avtomatik testlar.

> Bu lokal o'quv loyihasi. Production uchun standart `SECRET_KEY`, `DEBUG`, HTTP va login cheklovlarini alohida sozlash kerak.

## 1. O'rnatish (Windows PowerShell)

```powershell
cd drf_auth_lab
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py makemigrations notes
python manage.py migrate
python manage.py test
python manage.py runserver
```

PowerShell skriptni bloklasa `\.venv\Scripts\python.exe manage.py ...` ko'rinishida virtual muhit Pythoni bilan buyruqlarni bajaring.

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py makemigrations notes
python manage.py migrate
python manage.py test
python manage.py runserver
```

Brauzer: `http://127.0.0.1:8000/api/` — endpointlar ro'yxati.

## 2. Bitta test foydalanuvchi yarating

`POST http://127.0.0.1:8000/api/register/` JSON:

```json
{
  "username": "student",
  "email": "student@example.com",
  "password": "ExamplePassword123!",
  "password_confirm": "ExamplePassword123!"
}
```

Natija: `201 Created`. Parol bazada hash holida saqlanadi. Misoldagi parol faqat lokal dars uchun.

## 3. To'rt usulni sinab ko'rish

### A) Basic Authentication

`GET /api/basic/me/` — Postman: Authorization → **Basic Auth**; Username `student`, Password `ExamplePassword123!`. Har so'rovda login/parol jo'natiladi (base64 shifrlash emas). Faqat HTTPS ostida ishlatish kerak.

### B) Session Authentication

Brauzerda `http://127.0.0.1:8000/accounts/login/` ni oching, login qiling. Keyin `http://127.0.0.1:8000/api/session/me/` ni oching. Django `sessionid` cookie yordamida sizni taniydi. `POST/PATCH/DELETE` uchun CSRF himoyasi majburiy; HTML login formasida `{% csrf_token %}` bor.

### C) Token Authentication (DRF)

`POST /api/token/login/`:

```json
{"username":"student","password":"ExamplePassword123!"}
```

Natijada `token` qaytadi. `GET /api/token/me/` ga header qo'shing:

```http
Authorization: Token <token>
```

`POST /api/token/logout/` — shu header bilan: token bazadan o'chadi. DRF built-in token standart holatda muddatsiz va bitta user uchun bitta token; real mahsulotda tokenlarni boshqarish kuchliroq bo'lishi kerak.

### D) JWT Authentication (SimpleJWT)

`POST /api/jwt/login/`:

```json
{"username":"student","password":"ExamplePassword123!"}
```

Javobda `access` (15 daqiqa) va `refresh` (1 kun) keladi.

`GET /api/jwt/me/` header:

```http
Authorization: Bearer <access>
```

`POST /api/jwt/refresh/`:

```json
{"refresh":"<refresh>"}
```

`POST /api/jwt/logout/`:

```json
{"refresh":"<refresh>"}
```

`logout` refresh tokenni blacklistga qo'shadi. **Avval chiqarilgan access token 15 daqiqalik muddat tugaguncha ishlashi mumkin.** JWT tokenni tekshirish uchun `POST /api/jwt/verify/` va `{"token":"<access>"}` ishlating.

## 4. JWT bilan haqiqiy CRUD: Notes

`Authorization: Bearer <access>` bilan:

| Method | Manzil | Vazifa |
|---|---|---|
| GET | `/api/notes/` | Faqat o'zingizning yozuvlaringiz |
| POST | `/api/notes/` | `{"title":"Dars","body":"DRF JWT"}` |
| GET | `/api/notes/1/` | Bir yozuvni olish |
| PATCH | `/api/notes/1/` | `{"title":"Yangi nom"}` |
| DELETE | `/api/notes/1/` | O'chirish |

Boshqa foydalanuvchining Note'ini ochib bo'lmaydi: queryset `owner=request.user` orqali cheklanadi.

## 5. Autentifikatsiya va permission farqi

- **Authentication** — siz kimsiz? `request.user` ni aniqlaydi.
- **Permission** — sizga kirishga ruxsat bormi? `IsAuthenticated` tekshiradi.
- Har endpoint uchun `authentication_classes` alohida berilgan. Bu metodlar bir-biri bilan aralashmaydi.

## 6. Tushunish uchun asosiy fayllar

```text
drf_auth_lab/
├── manage.py
├── requirements.txt
├── config/
│   ├── settings.py          # Global DRF / JWT sozlamalari
│   └── urls.py              # Barcha URL lar
├── accounts/
│   ├── serializers.py       # Ro'yxatdan o'tish / user
│   ├── views.py             # Basic, Session, Token, JWT
│   ├── urls.py
│   ├── tests.py             # Auth testlari
│   └── templates/registration/login.html
└── notes/
    ├── models.py            # Note model
    ├── serializers.py
    ├── views.py             # JWT + owner filtering
    └── urls.py
```

## 7. Amaliy mashqlar

1. `GET /api/basic/me/` ni parolsiz yuboring va status kodini yozing.
2. Session login qilib, boshqa brauzerda `GET /api/session/me/` ni oching.
3. Token logoutdan keyin eski token bilan murojaat qiling.
4. JWT access muddatini 1 daqiqa qilib ko'ring va refresh bilan yangilang.
5. 2 ta foydalanuvchi yarating; birining Note yozuvini boshqasi o'qiy olmasligini tekshiring.
6. `IsAuthenticated` o'rniga `IsAdminUser` qo'yib, `403 Forbidden` holatini ko'ring.

## Muhim cheklovlar

- Dars namunasida login endpointlarini kuchli brute-force himoyasisiz qoldirmaslik uchun productionda IP/user asosidagi limit va monitoring joriy qiling; DRF ichki throttling haqiqiy himoyaning o'rnini bosmaydi.
- HTTPS, muhit o'zgaruvchilaridagi maxfiy kalit, secure cookie va to'g'ri CORS/CSRF siyosati real serverda zarur.
- Logout qilish access JWTni darhol bekor qilmaydi; yuqoridagi muddat tugashi kerak.

Rasmiy manbalar:
- https://www.django-rest-framework.org/api-guide/authentication/
- https://django-rest-framework-simplejwt.readthedocs.io/en/stable/getting_started.html
