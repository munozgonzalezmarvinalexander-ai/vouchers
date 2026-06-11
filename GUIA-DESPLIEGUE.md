# Guía de despliegue — Sistema de Vouchers Contables

Esta guía te lleva, paso a paso, de las carpetas de código a un sistema en línea
que las 5 computadoras usan abriendo **una sola URL**, sin instalar nada en
ellas y compartiendo la misma base de datos. Todo con planes **gratuitos**.

Tiempo estimado la primera vez: 30–40 minutos.

---

## Panorama: las tres piezas

```
[5 computadoras]
   │  (solo abren el navegador en una URL)
   ▼
[Frontend en Vercel]  ──HTTPS──►  [Backend (API) en Render]  ──SQL──►  [Base de datos en Neon]
   la pantalla                       la lógica + PDF/Excel               donde viven los datos
```

- **Base de datos (Neon, PostgreSQL):** el lugar único y compartido donde se
  guardan los vouchers. Que sea uno solo es lo que permite que las 5 computadoras
  vean lo mismo.
- **Backend (Render, con Docker):** la API que ya construimos. Aquí corren las
  reglas (cuadre, numeración, estados) y se generan el PDF y el Excel.
- **Frontend (Vercel):** la interfaz. Es la URL que abren las computadoras.

Las computadoras **no instalan nada**: solo necesitan navegador e internet.

### Antes de empezar
- Una cuenta de **GitHub**.
- Este paquete de código (las carpetas `backend/` y `frontend/`).

---

## Paso 1 — Subir el código a GitHub

Desde la carpeta que contiene `backend/` y `frontend/`:

```bash
git init
git add .
git commit -m "Sistema de vouchers"
git branch -M main
git remote add origin https://github.com/TU-USUARIO/vouchers.git
git push -u origin main
```

(Primero crea el repositorio vacío en github.com → New repository, y usa esa URL.)

> Un solo repositorio con las dos carpetas dentro. Más adelante le dirás a Render
> que use `backend/` y a Vercel que use `frontend/`.

---

## Paso 2 — Crear la base de datos en Neon

1. Entra a **neon.tech** y crea una cuenta (gratis, **sin tarjeta**).
2. **New Project**. Ponle nombre (ej. `vouchers`) y elige una región cercana
   (por ejemplo *US East*).
3. Al crearlo, Neon te muestra la **Connection string**. Es algo así:

   ```
   postgresql://usuario:password@ep-xxxx-xxxx.us-east-2.aws.neon.tech/vouchers?sslmode=require
   ```

4. **Cópiala y guárdala.** Será tu `DATABASE_URL`.

> Neon en plan gratis “se duerme” cuando no hay uso; el primer pedido la despierta
> en menos de un segundo. Para 5 computadoras es más que suficiente.

---

## Paso 3 — Desplegar el backend en Render

1. Entra a **render.com** y crea cuenta (puedes usar tu GitHub).
2. **New + → Web Service** y conecta tu repositorio.
3. Configura:
   - **Root Directory:** `backend`
   - **Language / Runtime:** *Docker* (Render detecta el `Dockerfile` que ya viene incluido)
   - **Instance Type:** *Free*
4. En **Environment** agrega una variable:
   - `DATABASE_URL` = *(la cadena de Neon del paso 2)*

   (La variable `CORS_ORIGINS` la pondremos en el Paso 6, cuando ya tengamos la
   URL del frontend.)
5. **Create Web Service** y espera a que termine el build (instala las librerías
   del sistema para el PDF y las dependencias de Python).
6. Al terminar, copia la **URL del backend** (ej. `https://vouchers-api.onrender.com`)
   y ábrela en el navegador. Debe responder:

   ```json
   {"mensaje": "API de Vouchers en línea", "docs": "/docs"}
   ```

   Si agregas `/docs` a esa URL, verás la documentación interactiva de la API.

> Al arrancar, la app **crea las tablas solas** en Neon. Falta cargar el catálogo:
> eso es el siguiente paso.

---

## Paso 4 — Cargar el catálogo (una sola vez)

El catálogo de cuentas y los proyectos se cargan con `scripts/seed.py`
(es **idempotente**: puedes correrlo las veces que quieras sin duplicar nada).

**Opción A — desde Render (recomendada):**
1. En tu servicio de Render, abre la pestaña **Shell**.
2. Ejecuta:
   ```bash
   python scripts/seed.py
   ```
   Como `DATABASE_URL` ya está en el entorno, carga directo en Neon. Verás cuántas
   cuentas, proyectos y firmantes se sembraron.

**Opción B — desde tu computadora:**
1. En `backend/`, crea un archivo `.env` con `DATABASE_URL=` *(la de Neon)*.
2. ```bash
   pip install -r requirements.txt
   python scripts/seed.py
   ```

---

## Paso 5 — Desplegar el frontend en Vercel

1. Entra a **vercel.com** y crea cuenta con GitHub.
2. **Add New → Project** e importa el mismo repositorio.
3. Configura:
   - **Root Directory:** `frontend`
   - **Framework Preset:** *Vite* (lo detecta solo)
   - **Build Command / Output:** déjalos por defecto (`npm run build` → `dist`)
4. En **Environment Variables** agrega:
   - `VITE_API_URL` = *(la URL del backend de Render, sin barra al final)*

     Ej. `https://vouchers-api.onrender.com`
5. **Deploy.** Al terminar, copia la **URL del frontend**
   (ej. `https://vouchers.vercel.app`). **Esta es la URL que abrirán las 5
   computadoras.**

---

## Paso 6 — Conectar el frontend con el backend (CORS)

Por seguridad, el backend solo acepta peticiones de los dominios que autorices.

1. Vuelve a **Render → tu servicio → Environment**.
2. Agrega la variable:
   - `CORS_ORIGINS` = *(la URL de Vercel)* — ej. `https://vouchers.vercel.app`
3. Guarda. Render redepliega solo en un minuto.

Listo: el frontend ya puede comunicarse con la API.

---

## Paso 7 — Usar el sistema en las 5 computadoras

En cada computadora, abre el navegador en la **URL de Vercel**. Nada más.

- Todas ven y editan **los mismos datos** (la misma base en Neon).
- Pueden crear vouchers, numerarlos, revisarlos/autorizarlos, **imprimir**,
  descargar PDF/Excel y ver reportes.
- Tip: guarda la URL como marcador o acceso directo en el escritorio.

---

## Notas útiles

- **Imprimir sin descargar:** el botón *Imprimir* abre el voucher y manda al
  diálogo de impresión; no genera ningún archivo.
- **PDF:** funciona en el servidor gracias al `Dockerfile` (no instalas nada en
  Windows). El *Imprimir* y el *Excel* no dependen de eso.
- **Primer acceso lento:** tanto Neon como el plan gratis de Render “se duermen”
  tras un rato sin uso; el primer acceso del día puede tardar algunos segundos en
  despertar. Después va normal. Si quieres que el backend esté siempre despierto,
  es el único punto que podría justificar un plan de pago modesto (o un “ping”
  automático cada pocos minutos).
- **Respaldo:** puedes exportar el libro de vouchers a Excel cuando quieras
  (Reportes → *Descargar libro*).
- **Sin inicio de sesión:** por decisión, no hay login; cualquiera con la URL
  puede entrar. La auditoría registra las acciones como “sistema”. Si en el
  futuro hace falta, se agrega esa etapa.

---

## Si algo falla (errores comunes)

- **El frontend dice “Failed to fetch” o error de CORS:** revisa que
  `CORS_ORIGINS` en Render sea **exactamente** la URL de Vercel (sin barra al
  final) y que el backend haya redeployado.
- **Al pedir PDF responde 503:** el backend no se desplegó con Docker. Asegúrate
  de que el *Runtime* en Render sea **Docker** (no el Python por defecto).
- **No aparecen cuentas/proyectos:** falta correr el seed (Paso 4).
- **`VITE_API_URL` no toma efecto:** Vite la incrusta al construir; si la cambias,
  vuelve a hacer *Redeploy* en Vercel.

---

## Resumen de variables de entorno

| Dónde            | Variable        | Valor                                            |
|------------------|-----------------|--------------------------------------------------|
| Backend (Render) | `DATABASE_URL`  | Cadena de conexión de Neon                       |
| Backend (Render) | `CORS_ORIGINS`  | URL del frontend (Vercel)                         |
| Frontend (Vercel)| `VITE_API_URL`  | URL del backend (Render), sin barra al final      |

---

## Correr todo localmente (opcional, para probar antes de subir)

**Backend** (sin `DATABASE_URL` usa SQLite, cero configuración):
```bash
cd backend
pip install -r requirements.txt
python scripts/seed.py
uvicorn app.main:app --reload
# API en http://localhost:8000  ·  documentación en http://localhost:8000/docs
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
# Pantalla en http://localhost:5173
```
