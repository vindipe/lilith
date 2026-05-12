#!/bin/bash

export DEBIAN_FRONTEND=noninteractive

# Avvia il servizio SSH in background
service ssh start

# Attendi che il servizio sia completamente avviato
while ! nc -z localhost 22; do   
  sleep 1 # Attendi 1 secondo prima di controllare di nuovo
done

service vnstat start
# MaxAuthTries 20
# MaxSessions 50
# MaxStartups 100
# ClientAliveCountMax 6
# ClientAliveInterval 10
# EOF

# sudo service ssh restart