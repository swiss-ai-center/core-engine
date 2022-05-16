FROM node:18.1.0-slim AS build
ARG ENGINE_URL="https://pi-engine.kube.isc.heia-fr.ch"
ENV REACT_APP_ENGINE_URL ${ENGINE_URL}
WORKDIR /tmp
COPY . .
RUN npm install --legacy-peer-deps
RUN npm run build

FROM nginx:stable-alpine
COPY --from=build /tmp/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
CMD sed -i -e 's/$APP_PORT/'"$APP_PORT"'/g' /etc/nginx/conf.d/default.conf && nginx -g 'daemon off;'
