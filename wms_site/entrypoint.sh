#!/bin/sh
# Replace BACKEND_URL_PLACEHOLDER in the nginx config with the real value.
# BACKEND_URL defaults to docker-compose internal name; on Render set it to
# the api-gateway public URL: https://wms-api-gateway.onrender.com
BACKEND_URL="${BACKEND_URL:-http://api-gateway:8000}"

sed -i "s|BACKEND_URL_PLACEHOLDER|${BACKEND_URL}|g" \
    /etc/nginx/conf.d/default.conf

exec nginx -g "daemon off;"
