#!/bin/sh
PORT=${PORT:-80}
BACKEND=${BACKEND_URL:-http://backend:8000}

cat > /etc/nginx/conf.d/default.conf << EOF
server {
    listen $PORT;
    root /usr/share/nginx/html;
    index index.html;

    location /api/ {
        proxy_pass $BACKEND/api/;
        proxy_set_header Host \$host;
        proxy_read_timeout 120s;
    }

    location / {
        try_files \$uri \$uri/ /index.html;
    }
}
EOF

echo "Starting nginx on port $PORT proxying to $BACKEND"
exec nginx -g 'daemon off;'
