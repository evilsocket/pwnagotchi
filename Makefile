PACKER_VERSION=1.7.2
PWN_HOSTNAME=pwnagotchi
PWN_VERSION=master

all: clean install image

langs:
	@for lang in pwnagotchi/locale/*/; do\
		echo "compiling language: $$lang ..."; \
		./scripts/language.sh compile $$(basename $$lang); \
    done

image:
	cd builder && \
	docker run \
		--rm \
		--privileged \
		-v ${PWD}:/build \
		ghcr.io/solo-io/packer-plugin-arm-image build -var "pwn_hostname=$(PWN_HOSTNAME)" -var "pwn_version=$(PWN_VERSION)" /build/pwnagotchi.json
	mv builder/output-pwnagotchi/image pwnagotchi-raspbian-lite-$(PWN_VERSION).img
	sha256sum pwnagotchi-raspbian-lite-$(PWN_VERSION).img > pwnagotchi-raspbian-lite-$(PWN_VERSION).sha256
	zip pwnagotchi-raspbian-lite-$(PWN_VERSION).zip pwnagotchi-raspbian-lite-$(PWN_VERSION).sha256 pwnagotchi-raspbian-lite-$(PWN_VERSION).img

clean:
	rm -rf /tmp/packer-builder-arm-image
	rm -f pwnagotchi-raspbian-lite-*.zip pwnagotchi-raspbian-lite-*.img pwnagotchi-raspbian-lite-*.sha256
	rm -rf builder/output-pwnagotchi  builder/packer_cache
