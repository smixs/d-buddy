#!/bin/bash

# Скрипт для быстрого перезапуска Docker контейнера бота

echo "🔄 Перезапуск transcription_bot v2..."

# Остановка текущих контейнеров
echo "⏹️  Остановка контейнеров..."
docker compose down

# Пересборка с обновлениями
echo "🔨 Пересборка образа..."
docker compose build --no-cache

# Запуск в фоновом режиме
echo "🚀 Запуск контейнеров..."
docker compose up -d

# Показать логи
echo "📋 Последние логи:"
docker compose logs --tail=20

echo "✅ Перезапуск завершён!"
echo "💡 Для просмотра логов: docker compose logs -f"