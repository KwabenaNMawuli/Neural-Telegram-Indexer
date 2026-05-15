# Build context is the project root (set by docker-compose) so this Dockerfile
# can COPY both bot/ and shared/ into the image.

FROM node:20-slim

# Best-practice env settings for Node in containers.
ENV NODE_ENV=production \
    NPM_CONFIG_UPDATE_NOTIFIER=false \
    NPM_CONFIG_FUND=false

WORKDIR /app/bot

# Copy package files FIRST so the npm install layer is cached and only re-runs
# when dependencies change.
COPY bot/package.json bot/package-lock.json ./
RUN npm ci --omit=dev

# Now copy the rest of the bot's source AND the shared/ folder
# (the bot reads shared/qdrant.json at startup).
COPY bot/    /app/bot/
COPY shared/ /app/shared/

CMD ["node", "index.js"]
