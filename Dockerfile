FROM nginx:alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY index.html styles.css baseline-run.json agent-comparison.json /usr/share/nginx/html/

