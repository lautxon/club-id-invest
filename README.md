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

- **Frontend**: Next.js 14 (TypeScript), Tailwind CSS, Shadcn/UI
- **Backend**: Python FastAPI (Tipado fuerte, Pydantic)
- **Base de Datos**: PostgreSQL (Transaccional)
- **ORM**: SQLAlchemy 2.0 + Alembic (Migraciones)
- **Task Queue**: Redis + Celery (Cron jobs)
- **Auth**: JWT + Role Based Access Control (RBAC)
- **Docs**: Swagger/OpenAPI automático

## 📁 Estructura del Proyecto

```
club id invest/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py           # Business rules & constants
│   │   └── database.py         # SQLAlchemy connection
│   ├── models/
│   │   ├── __init__.py
│   │   ├── users.py            # User authentication
│   │   ├── legal_entities.py   # Corporate structures
│   │   ├── memberships.py      # Investor tiers
│   │   ├── projects.py         # Investment projects
│   │   ├── investments.py      # Investment tracking
│   │   ├── contracts.py        # Legal contracts
│   │   └── audit_logs.py       # Compliance audit trail
│   ├── schemas/                # Pydantic schemas
│   ├── services/               # Business logic
│   └── api/                    # REST endpoints
├── tests/
│   ├── __init__.py
│   └── test_business_rules.py  # Unit tests
├── docs/
│   └── ERD.md                  # Database diagram
├── requirements.txt
├── .env.example
└── README.md
```

## 🚀 Instalación

### Prerrequisitos

- Python 3.11+
- PostgreSQL 15+
- Redis 7+

### Pasos de Instalación

1. **Clonar el repositorio**
```bash
git clone <repository-url>
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

## 🔐 Seguridad

- JWT con RBAC (4 roles: investor, project_manager, admin, super_admin)
- Encriptación de contraseñas con bcrypt
- Audit logging de todas las operaciones críticas
- Retención de logs: 7 años (2555 días)
- Validación estricta con Pydantic

## 📝 Fases de Desarrollo

- [x] **Fase 1**: Modelado de datos (SQLAlchemy)
- [ ] **Fase 2**: Lógica de negocio (Servicios)
- [ ] **Fase 3**: API REST & Seguridad
- [ ] **Fase 4**: Frontend (Next.js)

## 📄 Licencia

Propiedad privada - Club ID Invest

## 👥 Equipo

Desarrollado por el equipo de Club ID Invest

---

**Nota**: Este proyecto está en desarrollo activo. Para producción, usar migraciones de Alembic en lugar de `init_db()`.
