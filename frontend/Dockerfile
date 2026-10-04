FROM node:20-alpine AS builder

WORKDIR /app
COPY package.json .
RUN npm install

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Startup script replaces BACKEND_URL placeholder at runtime
RUN echo '#!/bin/sh' > /docker-entrypoint.d/replace-backend-url.sh && \
    echo 'BACKEND=${BACKEND_URL:-http://backend:8000}' >> /docker-entrypoint.d/replace-backend-url.sh && \
    echo 'sed -i "s|BACKEND_URL|$BACKEND|g" /etc/nginx/conf.d/default.conf' >> /docker-entrypoint.d/replace-backend-url.sh && \
    chmod +x /docker-entrypoint.d/replace-backend-url.sh

EXPOSE 80
