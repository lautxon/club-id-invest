#!/bin/bash
# Club ID Invest - Post-Start Script
# Se ejecuta cada vez que se inicia el Codespace

set -e

echo "🚀 Club ID Invest - Iniciando servicios..."

# Verificar si PostgreSQL está disponible
echo "⏳ Esperando a que PostgreSQL esté disponible..."
until pg_isready -h postgres -U postgres; do
    echo "   PostgreSQL no está disponible aún..."
    sleep 2
done
echo "✅ PostgreSQL está listo!"

# Verificar si Redis está disponible
echo "⏳ Esperando a que Redis esté disponible..."
until redis-cli -h redis ping; do
    echo "   Redis no está disponible aún..."
    sleep 2
done
echo "✅ Redis está listo!"

# Inicializar base de datos si es necesario
echo "📊 Verificando base de datos..."
python -c "
from app.core.database import SessionLocal
try:
    db = SessionLocal()
    db.execute('SELECT 1')
    print('✅ Conexión a base de datos exitosa!')
    db.close()
except Exception as e:
    print(f'⚠️ Error de conexión: {e}')
" || true

echo "✅ Servicios listos para desarrollar!"
