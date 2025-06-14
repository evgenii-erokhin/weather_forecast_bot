FROM ghcr.io/astral-sh/uv:python3.12-alpine
ARG home=/opt
ARG app_dir=weather_forecast_bot
WORKDIR $home/$app_dir
COPY ./pyproject.toml ./uv.lock $home/$app_dir/
RUN uv sync --locked
COPY ./src $home/$app_dir/
CMD ["uv", "run", "main.py"]