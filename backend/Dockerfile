FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install --omit=dev

COPY prisma ./prisma/
RUN npx prisma generate

COPY src ./src/

RUN mkdir -p uploads/avatars uploads/documents uploads/logos

EXPOSE 3000

# Write the entrypoint inline to avoid COPY + stale-cache issues.
# If arguments are passed (e.g. from docker-compose command:), they replace
# the default `node src/server.js` so nodemon works in dev.
RUN printf '#!/bin/sh\nset -e\necho "Running Prisma db push..."\nnpx prisma db push --accept-data-loss\nif [ "$SEED_DB" = "true" ]; then\n  echo "Seeding database..."\n  node prisma/seed.js\nfi\necho "Starting server..."\nif [ $# -gt 0 ]; then\n  exec "$@"\nelse\n  exec node src/server.js\nfi\n' > /entrypoint.sh && chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
