FROM entity-image AS node

COPY ./entity.sh /
RUN chmod +x entity.sh

# ENTRYPOINT service ssh start && /node.sh
ENTRYPOINT ["/bin/bash", "/entity.sh"]
