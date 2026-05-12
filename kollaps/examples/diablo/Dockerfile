FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# general dependencies
RUN apt-get update -y 

RUN apt-get install -y \
        openssh-client openssh-server \
        net-tools netcat \
        cloud-utils cloud-guest-utils jq \
        curl wget dnsutils rsync \
        iputils-ping iperf3 \
        vnstat procps sysstat bc \
        git python3-pip \
        psmisc gzip \        
        clang cmake pkg-config \
        libudev-dev llvm ninja-build libboost-all-dev \  
        libjson-perl libyaml-perl \   
        tzdata \
        nano bash sudo

        # build-essential bind9utils make gcc util-linux parted e2fsprogs \
        # perl-base libconfig-yaml-perl libcapture-tiny-perl libbz2-dev libreadline-dev libssl-dev libffi-dev libsqlite3-dev libncurses5-dev libncursesw5-dev liblzma-dev \

# Solana-Solang dep.
RUN apt-get install -y \
        g++ rustc cargo llvm-dev libpcp3-dev libpthread-stubs0-dev libudev-dev

# Diem dep.
RUN apt-get install -y \
        libssl-dev zlib1g-dev      

SHELL ["/bin/bash", "-c"]

# Modifying the sudoers file to allow the use of sudo without a password.
RUN echo "ALL ALL=(ALL:ALL) NOPASSWD: ALL" > /etc/sudoers.d/nopasswd

# Copy the SSH private key to the container
COPY id_ed25519.pub /root/.ssh/id_ed25519.pub
COPY id_ed25519.pub /root/.ssh/authorized_keys

# Create and add content to the SSH config file
# RUN echo "RemoteCommand cd /; \$SHELL -il" > /root/.ssh/config
RUN echo "StrictHostKeyChecking no" >> /root/.ssh/config

# Set correct permissions for the SSH private key
RUN chmod 600 /root/.ssh/authorized_keys && \ 
    chmod 600 /root/.ssh/id_ed25519.pub && \
    chmod 600 /root/.ssh/config

RUN echo "cd /" >> /root/.bashrc
RUN source /root/.bashrc
# RUN echo "cd /" >> /root/.bash_profile
# RUN source /root/.bash_profile
RUN exec bash


# Disable password authentication and only allow public key authentication
RUN sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config && \
    sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config 

# Expose SSH port
EXPOSE 22
EXPOSE 443
EXPOSE 5000


RUN apt-get upgrade -y
RUN apt-get clean; rm -rf /var/lib/apt/lists/


ADD ./resources-measure.sh /
RUN chmod +x resources-measure.sh

RUN mkdir -p /results
RUN mkdir -p /results/latencies
RUN mkdir -p /results/workloads
# RUN mkdir -p /results/workloads/gafam
# RUN mkdir -p /results/workloads/dota
# RUN mkdir -p /results/workloads/football
# RUN mkdir -p /results/workloads/10000
# CMD ["/bin/bash", "/resources-measure.sh", "&"]