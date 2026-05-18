FROM node:20-alpine

WORKDIR /app

COPY frontend/package.json /app/frontend/package.json

WORKDIR /app/frontend

RUN npm install

COPY frontend /app/frontend

CMD ["npm", "run", "dev", "--", "-H", "0.0.0.0", "-p", "3000"]
