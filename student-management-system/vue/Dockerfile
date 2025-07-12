# 使用标准node镜像而不是alpine
FROM node:18 AS build

WORKDIR /app

# 设置npm国内源
RUN npm config set registry https://registry.npmmirror.com

# 复制package文件
COPY package*.json ./

# 清理并重新安装
RUN rm -rf node_modules package-lock.json || true && \
    npm cache clean --force && \
    npm install

# 复制源代码
COPY . .

# 构建项目
RUN npm run build

# 第二阶段：轻量级nginx
FROM nginx:alpine

# 复制构建文件
COPY --from=build /app/dist /usr/share/nginx/html

# 复制nginx配置
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"] 