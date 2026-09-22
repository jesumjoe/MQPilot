FROM ubuntu:22.04
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    suricata \
    iptables \
    python3 \
    python3-pip \
    --no-install-recommends \
 && rm -rf /var/lib/apt/lists/*

RUN pip3 install scikit-learn numpy joblib

COPY setup_edge.sh /edge_sensor/setup_edge.sh
RUN chmod +x /edge_sensor/setup_edge.sh

CMD ["/bin/bash", "-c", "bash /edge_sensor/setup_edge.sh && tail -f /dev/null"]
