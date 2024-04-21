ARG BACKEND_IMAGE=base_image
FROM $BACKEND_IMAGE

RUN apt-get update && apt-get install -y \
    gcc  \
    curl \
    zip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /srv
COPY requirements.txt .
RUN pip install -r requirements.txt
# WORKDIR /app
# COPY . /pyFundcraft
# COPY jupyter_notebook_config.py /root/.jupyter/jupyter_notebook_config.py
# RUN cp /app/app.ini /pyFundcraft/notebooks/
WORKDIR /notebooks
# CMD ["python", "/app/manage.py", "shell_plus", "--notebook"]
EXPOSE 8888
