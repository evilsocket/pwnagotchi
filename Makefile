PWN_HOSTNAME=pwnagotchi
PWN_VERSION=master

all: install image clean

install:
	curl https://releases.hashicorp.com/packer/1.3.5/packer_1.3.5_linux_amd64.zip -o /tmp/packer.zip
	unzip /tmp/packer.zip -d /tmp
	mv /tmp/packer /usr/bin/packer
	git clone https://github.com/solo-io/packer-builder-arm-image /tmp/packer-builder-arm-image
	cd /tmp/packer-builder-arm-image && go get -d ./... && go build
	cp /tmp/packer-builder-arm-image/packer-builder-arm-image /usr/bin

image:
	cd builder && sudo /usr/bin/packer build pwnagotchi.json
	mv builder/output-pwnagotchi/image pwnagotchi-raspbian-lite-$(PWN_VERSION).img
	zip pwnagotchi-raspbian-lite-$(PWN_VERSION).zip pwnagotchi-raspbian-lite-$(PWN_VERSION).img

clean:
	rm -rf /tmp/packer-builder-arm-image
	rm -f pwnagotchi-raspbian-lite.img
	rm -rf builder/output-pwnagotchi  builder/packer_cache
