#!/bin/sh
set -e

echo "Running Prisma db push..."
npx prisma db push --accept-data-loss

if [ "$SEED_DB" = "true" ]; then
  echo "Seeding database..."
  node prisma/seed.js
fi

echo "Starting server..."
if [ $# -gt 0 ]; then
  exec "$@"
else
  exec node src/server.js
fi
