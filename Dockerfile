FROM python:3.12-slim
WORKDIR /app
COPY bridge /app/bridge
COPY web /app/web
RUN useradd --uid 10001 --create-home lymyt && mkdir /data && chown lymyt:lymyt /data
USER lymyt
EXPOSE 8787
VOLUME /data
CMD ["python", "bridge/lymyt.py", "--data-dir", "/data", "serve", "--relay", "--host", "0.0.0.0"]
