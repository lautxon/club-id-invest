# Club ID Invest - Codespaces Configuration
# Documentación de prebuilds y configuración avanzada

## Prebuild Configuration

Los prebuilds de Codespaces se activan automáticamente cuando hay cambios en:
- `.devcontainer/**`
- `docker-compose.yml`
- `requirements.txt`
- `frontend/package.json`

## Cómo activar Prebuilds manualmente

### Opción 1: Desde GitHub UI

1. Andá a **https://github.com/lautxon/club-id-invest/settings/codespaces**
2. En "Prebuilds", hacé clic en **"Add prebuild"**
3. Configurá:
   - **Branch**: `main`
   - **Devcontainer configuration**: `.devcontainer/devcontainer.json`
   - **Prebuild frequency**: `Every push` o `On demand`
4. Hacé clic en **"Save"**

### Opción 2: GitHub CLI

```bash
# Listar prebuilds existentes
gh codespace list --prebuild

# Crear nuevo prebuild
gh codespace create --branch main --devcontainer-path .devcontainer/devcontainer.json
```

## Tiempos estimados

| Tipo | Tiempo de apertura |
|------|-------------------|
| Sin prebuild | 3-5 minutos |
| Con prebuild | 30-60 segundos |

## Qué incluye el prebuild

✅ Python 3.11 + Node.js 20 instalados
✅ Extensiones de VS Code pre-instaladas
✅ Dependencias de Python (`requirements.txt`)
✅ Dependencias de Node (`frontend/package.json`)
✅ Configuración de Docker Compose

## Qué se ejecuta al abrir

### Post-Create Script (una sola vez)
- `pip install -r requirements.txt`
- `npm install` en frontend/
- Creación de `.env` desde `.env.example`
- Creación de directorios necesarios

### Post-Start Script (cada vez que se inicia)
- Verifica disponibilidad de PostgreSQL
- Verifica disponibilidad de Redis
- Valida conexión a base de datos

## Monitoreo de Prebuilds

Para ver el estado de los prebuilds:

1. **GitHub Actions**: https://github.com/lautxon/club-id-invest/actions
   - Workflow: "Update Codespaces Prebuild"

2. **Codespaces Settings**: https://github.com/lautxon/club-id-invest/settings/codespaces
   - Sección: "Prebuilds"

## Troubleshooting

### Prebuild no se actualiza

Verificá el workflow en `.github/workflows/codespaces-prebuild.yml`

### Error en post-create.sh

Revisá los logs en la terminal del Codespace durante la creación.

### Servicios no inician

Verificá `docker-compose.yml` y ejecutá:
```bash
docker-compose config
docker-compose up -d
docker-compose ps
```
