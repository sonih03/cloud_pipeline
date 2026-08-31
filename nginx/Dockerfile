FROM nginx:alpine

# 기본 설정 제거 및 커스텀 설정 복사
RUN rm /etc/nginx/conf.d/default.conf 2>/dev/null || true
COPY nginx.config /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]