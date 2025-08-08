FROM debian:bullseye-slim
RUN apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends \
    bash python3 pip libstdc++6 libc6 \
 && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN mkdir -p /comsa/modules
RUN mkdir -p /comsa/bin
RUN mkdir -p /shared
COPY ./modules/* /comsa/modules/
COPY ./bin/* /comsa/bin/
RUN chmod +x /comsa/bin/*
COPY ./comsa_toolbox.py /comsa/
WORKDIR /shared
ENTRYPOINT ["python3", "/comsa/comsa_toolbox.py", "--executables_folder_path", "/comsa/bin/"]
