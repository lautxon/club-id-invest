#!/bin/bash
# Club ID Invest - Post-Create Script
# Se ejecuta una vez después de crear el Codespace

set -e

echo "🚀 Club ID Invest - Configuración inicial del Codespace"

# Instalar dependencias del backend
echo "📦 Instalando dependencias del backend..."
pip install -r requirements.txt

# Instalar dependencias del frontend
echo "📦 Instalando dependencias del frontend..."
cd frontend
npm install
cd ..

# Crear archivo .env si no existe
if [ ! -f .env ]; then
    echo "📝 Creando archivo .env..."
    cp .env.example .env
fi

# Crear directorios necesarios
echo "📁 Creando directorios..."
mkdir -p generated_contracts
mkdir -p templates/contracts

echo "✅ Configuración inicial completada!"
echo ""
echo "📋 Próximos pasos:"
echo "   1. Los servicios (PostgreSQL, Redis) se iniciarán automáticamente"
echo "   2. El backend estará disponible en http://localhost:8000"
echo "   3. El frontend estará disponible en http://localhost:3000"
echo "   4. Swagger docs: http://localhost:8000/api/docs"
echo ""
echo "🔧 Comandos útiles:"
echo "   - Iniciar todos los servicios: docker-compose up -d"
echo "   - Ver logs: docker-compose logs -f"
echo "   - Detener: docker-compose down"
echo "   - Tests: pytest tests/ -v"
