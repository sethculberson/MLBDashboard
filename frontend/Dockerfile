# Stage 1: Build the React application
FROM node:18-alpine AS builder

WORKDIR /app

COPY frontend/package.json frontend/yarn.lock* frontend/package-lock.json* ./

# Install frontend dependencies
RUN npm install

COPY frontend/ .

# Build the React application for production
ARG VITE_FLASK_API_URL
ENV VITE_FLASK_API_URL=$VITE_FLASK_API_URL
RUN npm run build

FROM nginx:alpine

RUN rm /etc/nginx/conf.d/default.conf

COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
