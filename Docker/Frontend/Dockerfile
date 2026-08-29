FROM node:20-alpine

WORKDIR /app

# Install dependencies first (for faster Docker caching)
COPY package.json package-lock.json* ./
RUN npm install

# Copy application files
COPY . .

EXPOSE 4321

CMD ["npm", "run", "dev"]
