# v3
FROM node:20-alpine AS builder

WORKDIR /app
COPY package.json .
RUN npm install

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["/bin/sh", "-c", "\
  PORT=${PORT:-80}; \
  BACKEND=${BACKEND_URL:-http://backend:8000}; \
  echo \"server { listen $PORT; root /usr/share/nginx/html; index index.html; location /api/ { proxy_pass $BACKEND/api/; proxy_set_header Host \\$host; proxy_read_timeout 120s; } location / { try_files \\$uri \\$uri/ /index.html; } }\" > /etc/nginx/conf.d/default.conf && \
  nginx -g 'daemon off;'"]
