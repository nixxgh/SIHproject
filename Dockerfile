# 1. Choose the base environment
FROM node:20-alpine

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy dependency files first (for caching)
COPY package*.json ./

# 4. Install dependencies inside the container
RUN npm install

# 5. Copy the rest of your application code
COPY . .

# 6. Document which port the app runs on
EXPOSE 3000

# 7. Define the command to start your app
CMD ["npm", "start"]
