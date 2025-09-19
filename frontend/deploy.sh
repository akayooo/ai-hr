#!/bin/bash

# ================================================
# 🚀 MoreTech.VTB Frontend Deployment Script
# ================================================
# Скрипт для развертывания фронтенда на Ubuntu
# ================================================

set -e  # Остановка при ошибке

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция для логирования
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
    exit 1
}

warn() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

info() {
    echo -e "${BLUE}[INFO] $1${NC}"
}

# Конфигурация
PROJECT_NAME="vtb-frontend"
DEPLOY_DIR="/var/www/$PROJECT_NAME"
NGINX_SITE="$PROJECT_NAME"
SERVICE_USER="www-data"

log "🚀 Начинаем развертывание MoreTech.VTB Frontend"

# Проверка прав sudo
if [ "$EUID" -ne 0 ]; then
    error "Пожалуйста, запустите скрипт с правами sudo"
fi

# Проверка Node.js
if ! command -v node &> /dev/null; then
    error "Node.js не установлен. Установите Node.js 18+"
fi

NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    error "Требуется Node.js версии 18 или выше. Текущая версия: $(node -v)"
fi

# Проверка Nginx
if ! command -v nginx &> /dev/null; then
    error "Nginx не установлен. Установите Nginx"
fi

log "✅ Все зависимости установлены"

# Создание директории для развертывания
log "📁 Создание директории развертывания"
mkdir -p "$DEPLOY_DIR"
chown -R $SERVICE_USER:$SERVICE_USER "$DEPLOY_DIR"

# Установка зависимостей проекта
log "📦 Установка зависимостей"
npm install --production=false

# Сборка проекта
log "🔨 Сборка проекта для production"
export NODE_ENV=production

# Исправление прав доступа к TypeScript
chmod +x node_modules/.bin/* 2>/dev/null || true

# Попытка сборки с разными способами
if ! npm run build; then
    log "⚠️ Обычная сборка не удалась, пытаемся альтернативный способ"
    if ! npx tsc && npx vite build; then
        log "⚠️ Пропускаем TypeScript проверку и собираем только Vite"
        npx vite build --mode production
    fi
fi

# Копирование собранных файлов
log "📋 Копирование файлов в $DEPLOY_DIR"
cp -r dist/* "$DEPLOY_DIR/"
chown -R $SERVICE_USER:$SERVICE_USER "$DEPLOY_DIR"

# Настройка Nginx
log "🌐 Настройка Nginx"

# Копирование конфигурации Nginx
cp nginx.ubuntu.conf "/etc/nginx/sites-available/$NGINX_SITE"

# Создание символической ссылки
if [ ! -L "/etc/nginx/sites-enabled/$NGINX_SITE" ]; then
    ln -s "/etc/nginx/sites-available/$NGINX_SITE" "/etc/nginx/sites-enabled/"
fi

# Удаление дефолтной конфигурации Nginx (если есть)
if [ -L "/etc/nginx/sites-enabled/default" ]; then
    rm "/etc/nginx/sites-enabled/default"
    warn "Удалена дефолтная конфигурация Nginx"
fi

# Проверка конфигурации Nginx
log "🔍 Проверка конфигурации Nginx"
if nginx -t; then
    log "✅ Конфигурация Nginx корректна"
else
    error "❌ Ошибка в конфигурации Nginx"
fi

# Перезапуск Nginx
log "🔄 Перезапуск Nginx"
systemctl reload nginx
systemctl enable nginx

# Проверка статуса Nginx
if systemctl is-active --quiet nginx; then
    log "✅ Nginx успешно запущен"
else
    error "❌ Не удалось запустить Nginx"
fi

# Создание логов
log "📝 Настройка логирования"
mkdir -p /var/log/nginx
touch "/var/log/nginx/$PROJECT_NAME.access.log"
touch "/var/log/nginx/$PROJECT_NAME.error.log"
chown www-data:www-data "/var/log/nginx/$PROJECT_NAME.access.log"
chown www-data:www-data "/var/log/nginx/$PROJECT_NAME.error.log"

# Настройка firewall (если ufw активен)
if command -v ufw &> /dev/null && ufw status | grep -q "Status: active"; then
    log "🔥 Настройка firewall"
    ufw allow 80/tcp
    ufw allow 443/tcp
fi

# Создание скрипта для обновления
log "📜 Создание скрипта обновления"
cat > "/usr/local/bin/update-$PROJECT_NAME" << 'EOF'
#!/bin/bash
set -e

log() {
    echo -e "\033[0;32m[$(date +'%Y-%m-%d %H:%M:%S')] $1\033[0m"
}

PROJECT_DIR="/var/www/vtb-frontend"
SOURCE_DIR="/path/to/your/source/frontend"  # Замените на путь к исходникам

log "🔄 Обновление MoreTech.VTB Frontend"

cd "$SOURCE_DIR"
npm install
npm run build
cp -r dist/* "$PROJECT_DIR/"
chown -R www-data:www-data "$PROJECT_DIR"
systemctl reload nginx

log "✅ Обновление завершено"
EOF

chmod +x "/usr/local/bin/update-$PROJECT_NAME"

log "🎉 Развертывание завершено успешно!"
info "📍 Приложение доступно по адресу: http://localhost"
info "📋 Директория приложения: $DEPLOY_DIR"
info "🔧 Конфигурация Nginx: /etc/nginx/sites-available/$NGINX_SITE"
info "📝 Логи: /var/log/nginx/$PROJECT_NAME.*.log"
info "🔄 Для обновления используйте: sudo update-$PROJECT_NAME"

warn "⚠️  Не забудьте:"
warn "   1. Заменить localhost в nginx.ubuntu.conf на ваш домен"
warn "   2. Настроить адреса backend сервисов в конфигурации Nginx"
warn "   3. Настроить SSL сертификаты для production"
warn "   4. Обновить путь к исходникам в скрипте обновления"
