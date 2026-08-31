FROM node:20-alpine AS build

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# 최종 빌드 산출물 공유용
FROM alpine:latest
WORKDIR /dist
COPY --from=build /app/dist .
CMD ["sh", "-c", "cp -r /dist/* /target/"]