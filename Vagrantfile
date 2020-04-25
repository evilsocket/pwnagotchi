# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/bionic64"

  config.vm.provider :virtualbox do |v|
    v.memory = 1024
    v.linked_clone = true
  end

  config.vm.provision "shell", inline: <<-SHELL
    apt-get -y update || true
    apt-get -y install qemu-system-arm qemu-user-static binfmt-support bmap-tools kpartx unzip zip
    curl -O "https://dl.google.com/go/go1.14.2.linux-amd64.tar.gz"
    tar -C /usr/local/ -xf go1.14.2.linux-amd64.tar.gz
    ln -s /usr/local/go/bin/go /usr/bin/go
    update-binfmts --display
    cd /vagrant
    make clean
    make install
    make image -e PWN_HOSTNAME=pwnagotchi PWN_VERSION=$(git rev-parse --short HEAD)
  SHELL
end
