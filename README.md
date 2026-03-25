# Club ID Invest

**Plataforma de Inversión Colectiva (Fideicomisos) con Co-Inversión Automática del Club**

## 📋 Descripción

Club ID Invest es una plataforma Fintech que permite la inversión colectiva en proyectos inmobiliarios a través de fideicomisos. El sistema cuenta con 3 niveles de inversores y reglas automáticas de co-inversión del Club.

## 🎯 Reglas de Negocio Críticas

### Niveles de Inversores

| Categoría | % Mínimo Recaudado | Meses Mínimos | Aporte del Club |
|-----------|-------------------|---------------|-----------------|
| Cebollitas | >55% | 3 | 45% |
| 1ra Div | >65% | 6 | 35% |
| Senior | >75% | 9 | 25% |

### Gestión de Inactividad

- **60 días (2 meses)**: Marca como 'inactive', genera deuda de $50
- **180 días (6 meses)**: Marca como 'churned'

### Restricciones

- Máximo 5 inversiones activas por usuario
- Máximo 50 inversores por proyecto

## 🏗️ Arquitectura Técnica

### Stack Tecnológico

- **Frontend**: Next.js 14 (TypeScript), Tailwind CSS, Shadcn/UI, Framer Motion
- **Backend**: Python FastAPI (Tipado fuerte, Pydantic)
- **Base de Datos**: PostgreSQL (Transaccional)
- **ORM**: SQLAlchemy 2.0 + Alembic (Migraciones)
- **Task Queue**: Redis + Celery (Cron jobs)
- **Auth**: JWT + Role Based Access Control (RBAC)
- **Docs**: Swagger/OpenAPI automático

### ☁️ GitHub Codespaces

El proyecto está configurado para desarrollarse en **GitHub Codespaces** con:

- Entorno preconfigurado (Python 3.11, Node.js 20, PostgreSQL 15, Redis 7)
- Docker Compose para todos los servicios
- Extensiones de VS Code instaladas automáticamente
- Variables de entorno configuradas

[![Abrir en GitHub Codespaces](https://img.shields.io/badge/Abrir%20en-Codespaces-blue?logo=github)](https://codespaces.new/lautxon/club-id-invest)

## 📁 Estructura del Proyecto

```
club id invest/
├── app/                        # Backend FastAPI
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── core/
│   │   ├── config.py           # Business rules & constants
│   │   ├── database.py         # SQLAlchemy connection
│   │   └── security.py         # JWT & password hashing (Phase 3)
│   ├── models/                 # SQLAlchemy models (Phase 1)
│   │   ├── users.py
│   │   ├── legal_entities.py
│   │   ├── memberships.py
│   │   ├── projects.py
│   │   ├── investments.py
│   │   ├── contracts.py
│   │   └── audit_logs.py
│   ├── schemas/                # Pydantic schemas (Phase 2)
│   │   └── __init__.py
│   ├── services/               # Business logic (Phase 2 + 3)
│   │   ├── investment_service.py
│   │   ├── membership_service.py
│   │   ├── contract_service.py
│   │   └── auth_service.py     # Authentication (Phase 3)
│   ├── tasks/                  # Celery tasks (Phase 2)
│   │   ├── celery_app.py
│   │   └── scheduled_tasks.py
│   └── api/                    # REST endpoints (Phase 2 + 3)
│       ├── auth.py             # Authentication (Phase 3)
│       ├── users.py            # User management (Phase 3)
│       ├── investments.py
│       ├── projects.py
│       ├── contracts.py
│       └── dashboard.py
├── frontend/                   # Next.js Frontend (Phase 3)
│   ├── src/
│   │   ├── app/
│   │   │   ├── dashboard/
│   │   │   ├── login/
│   │   │   ├── register/
│   │   │   ├── page.tsx
│   │   │   ├── layout.tsx
│   │   │   └── providers.tsx
│   │   ├── components/
│   │   │   ├── DashboardMember.tsx
│   │   │   ├── ProjectCard.tsx
│   │   │   ├── AlertSystem.tsx
│   │   │   └── ui.tsx
│   │   └── lib/
│   │       ├── api.ts
│   │       ├── auth-store.ts
│   │       └── utils.ts
│   ├── package.json
│   └── README.md
├── tests/
│   └── test_business_rules.py
├── docs/
│   └── ERD.md
├── requirements.txt
├── .env.example
└── README.md
```

## 🚀 Instalación

### ☁️ GitHub Codespaces (Recomendado)

La forma más rápida de empezar es usando **GitHub Codespaces**:

1. **Abrir el repositorio en Codespaces**
   - Hacé clic en el botón "Code" en GitHub
   - Seleccioná "Create codespace on main"
   - O usá este link: https://codespaces.new/lautxon/club-id-invest

2. **Esperar la configuración automática**
   - El Codespace instalará Python, Node.js, PostgreSQL y Redis
   - Las extensiones de VS Code se instalarán automáticamente
   - Los scripts de post-creación configurarán el entorno

3. **Iniciar los servicios con Docker Compose**
```bash
docker-compose up -d
```

4. **Acceder a las aplicaciones**
   - **Frontend**: http://localhost:3000
   - **Backend API**: http://localhost:8000
   - **Swagger Docs**: http://localhost:8000/api/docs
   - **PostgreSQL**: localhost:5432
   - **Redis**: localhost:6379

5. **Comandos útiles**
```bash
# Ver logs de todos los servicios
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs -f backend

# Detener todos los servicios
docker-compose down

# Reiniciar un servicio
docker-compose restart backend

# Ejecutar tests
docker-compose exec backend pytest tests/ -v

# Acceder a la terminal del backend
docker-compose exec backend bash

# Acceder a la terminal del frontend
docker-compose exec frontend sh
```

**Ventajas de Codespaces:**
- ✅ Sin instalación local de PostgreSQL/Redis
- ✅ Entorno idéntico para todo el equipo
- ✅ Configuración versionada en el repo
- ✅ Ideal para la Fase 4 (Tests E2E + Deploy)

---

### Backend (Instalación Local)

#### Prerrequisitos

- Python 3.11+
- PostgreSQL 15+
- Redis 7+

#### Pasos de Instalación

1. **Clonar el repositorio**
```bash
git clone https://github.com/lautxon/club-id-invest.git
cd club-id-invest
```

2. **Crear entorno virtual**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**
```bash
cp .env.example .env
# Editar .env con tus credenciales
```

5. **Inicializar base de datos**
```bash
# Para desarrollo (usar Alembic en producción)
python -c "from app.core.database import init_db; init_db()"
```

6. **Ejecutar tests**
```bash
pytest tests/ -v
```

7. **Iniciar servidor de desarrollo**
```bash
uvicorn app.main:app --reload
```

8. **Acceder a la documentación API**
```
http://localhost:8000/api/docs
```

### Frontend

1. **Navegar al directorio frontend**
```bash
cd frontend
```

2. **Instalar dependencias**
```bash
npm install
```

3. **Configurar variables de entorno**
```bash
# Crear .env.local
echo "API_URL=http://localhost:8000/api" > .env.local
```

4. **Iniciar servidor de desarrollo**
```bash
npm run dev
```

5. **Acceder a la aplicación**
```
http://localhost:3000
```

## 📊 Modelos de Datos

### Tablas Principales

1. **users** - Autenticación y perfiles de usuario
2. **legal_entities** - Entidades legales y representantes
3. **memberships** - Categorías de inversor y lifecycle
4. **projects** - Proyectos de inversión (fideicomisos)
5. **investments** - Inversiones individuales
6. **investment_transactions** - Movimientos financieros
7. **contracts** - Contratos legales
8. **audit_logs** - Trail de auditoría (7 años)

Ver [ERD.md](docs/ERD.md) para el diagrama completo de entidad-relación.

## 🔌 API Endpoints

### Authentication (Phase 3)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/register` | POST | Registrar nuevo usuario |
| `/api/auth/login` | POST | Login y obtener tokens JWT |
| `/api/auth/logout` | POST | Logout (invalidar sesión) |
| `/api/auth/refresh` | POST | Refresh access token |
| `/api/auth/me` | GET | Obtener usuario actual |
| `/api/auth/change-password` | POST | Cambiar contraseña |

### Users (Phase 3 - Admin)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/users/` | GET | Listar usuarios (admin) |
| `/api/users/{id}` | GET | Obtener usuario (admin) |
| `/api/users/{id}/activate` | PATCH | Activar usuario (admin) |
| `/api/users/{id}/deactivate` | PATCH | Desactivar usuario (admin) |
| `/api/users/{id}/role` | PATCH | Cambiar rol (admin) |

### Investments
- `POST /api/investments/validate` - Validar inversión antes de crear
- `POST /api/investments/` - Crear nueva inversión
- `GET /api/investments/{id}` - Obtener detalles de inversión
- `GET /api/investments/` - Listar inversiones con filtros
- `POST /api/investments/{id}/confirm` - Confirmar pago manualmente

### Projects
- `GET /api/projects/` - Listar proyectos con filtros
- `GET /api/projects/{id}` - Obtener detalles de proyecto
- `GET /api/projects/{id}/investors` - Obtener lista de inversores (anónima)

### Contracts
- `POST /api/contracts/` - Generar nuevo contrato
- `POST /api/contracts/{id}/generate-pdf` - Generar PDF
- `POST /api/contracts/{id}/send-signature` - Enviar para firma
- `POST /api/contracts/{id}/sign` - Firmar electrónicamente
- `GET /api/contracts/{id}` - Obtener contrato
- `GET /api/contracts/` - Listar contratos

### Dashboard
- `GET /api/dashboard/` - Dashboard completo del usuario
- `GET /api/dashboard/alerts` - Obtener alertas pendientes
- `GET /api/dashboard/projects` - Progreso de proyectos activos

## 🧪 Testing

Los tests unitarios cubren las reglas de co-inversión automática:

```bash
# Ejecutar todos los tests
pytest tests/ -v

# Ejecutar tests específicos
pytest tests/test_business_rules.py -v

# Con coverage
pytest tests/ --cov=app
```

### Casos Borde Testeados

- 54% vs 55% (límite Cebollitas)
- 89 días vs 90 días (3 meses)
- 179 días vs 180 días (6 meses)
- 269 días vs 270 días (9 meses)

## 🔄 Celery Tasks (Background Jobs)

### Tareas Programadas

| Tarea | Frecuencia | Descripción |
|-------|------------|-------------|
| `run_auto_investment_check` | Diaria | Verifica y dispara co-inversión del Club |
| `run_membership_lifecycle_check` | Diaria | Gestiona inactividad y penalizaciones |
| `send_contract_reminders` | 6 horas | Envía recordatorios de contratos pendientes |
| `update_funding_progress` | Horaria | Actualiza progreso de financiación |

### Ejecutar Celery

```bash
# Worker
celery -A app.tasks.celery_app worker --loglevel=info

# Beat (scheduler)
celery -A app.tasks.celery_app beat --loglevel=info
```

## 🔐 Seguridad

- JWT con RBAC (4 roles: investor, project_manager, admin, super_admin)
- Encriptación de contraseñas con bcrypt
- Audit logging de todas las operaciones críticas
- Retención de logs: 7 años (2555 días)
- Validación estricta con Pydantic
- Refresh tokens con expiración de 7 días
- Access tokens con expiración de 30 minutos

## 🖥️ Frontend (Phase 3)

### Componentes Principales

- **DashboardMember**: Dashboard principal con estadísticas de portfolio
- **ProjectCard**: Card de proyecto con barra de progreso y regla de co-inversión
- **AlertSystem**: Sistema de alertas con notificaciones en tiempo real
- **UI Primitives**: Componentes reutilizables (Button, Card, Input, Badge, etc.)

### Características

- Autenticación JWT con refresh automático
- React Query para data fetching y caching
- Zustand para estado global
- Framer Motion para animaciones
- Tailwind CSS para styling
- Diseño responsive mobile-first

## 📝 Fases de Desarrollo

- [x] **Fase 1**: Modelado de datos (SQLAlchemy)
- [x] **Fase 2**: Lógica de negocio + API REST + Celery
- [x] **Fase 3**: Autenticación JWT + Frontend Next.js
- [ ] **Fase 4**: Tests E2E + Deploy a producción

## 🔧 Comandos Útiles

### Backend

```bash
# Iniciar API en desarrollo
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Iniciar Celery worker
celery -A app.tasks.celery_app worker --loglevel=info --pool=solo

# Iniciar Celery beat (scheduler)
celery -A app.tasks.celery_app beat --loglevel=info

# Ver tareas de Celery
celery -A app.tasks.celery_app inspect active

# Migraciones de base de datos (Alembic)
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

### Frontend

```bash
cd frontend

# Desarrollo
npm run dev

# Build de producción
npm run build

# Start production server
npm start

# Linting
npm run lint
```

## 📄 Licencia

Propiedad privada - Club ID Invest

## 👥 Equipo

Desarrollado por el equipo de Club ID Invest

---

**Nota**: Para producción, usar migraciones de Alembic en lugar de `init_db()` y configurar adecuadamente las variables de entorno en `.env`.
