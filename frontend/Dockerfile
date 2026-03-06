# ── 빌드 스테이지 ──
FROM node:18-alpine AS builder
WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

# Docker 환경에서는 API를 Nginx가 프록시하므로 VITE_API_URL 불필요
RUN npm run build

# ── 실행 스테이지: Nginx ──
FROM nginx:alpine
WORKDIR /usr/share/nginx/html

# 빌드 결과물 복사
COPY --from=builder /app/dist .

# Nginx 설정 (API 프록시 → backend 컨테이너)
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
