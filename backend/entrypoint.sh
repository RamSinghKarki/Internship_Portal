#!/bin/sh
set -e

echo "Pushing Prisma schema to database..."
npx prisma db push --accept-data-loss

if [ "$SEED_DB" = "true" ]; then
  echo "Seeding database with demo data..."
  node prisma/seed.js
fi

echo "Starting server..."
exec node src/server.js
