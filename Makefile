PACKER_VERSION := 1.8.3
PWN_HOSTNAME := pwnagotchi
PWN_VERSION := $(shell cut -d"'" -f2 < pwnagotchi/_version.py)
PWN_RELEASE := pwnagotchi-raspios-lite-$(PWN_VERSION)

MACHINE_TYPE := $(shell uname -m)
ifneq (,$(filter x86_64,$(MACHINE_TYPE)))
GOARCH := amd64
else ifneq (,$(filter i686,$(MACHINE_TYPE)))
GOARCH := 386
else ifneq (,$(filter arm64% aarch64%,$(MACHINE_TYPE)))
GOARCH := arm64
else ifneq (,$(filter arm%,$(MACHINE_TYPE)))
GOARCH := arm
else
GOARCH := amd64
$(warning Unable to detect CPU arch from machine type $(MACHINE_TYPE), assuming $(GOARCH))
endif

# The Ansible part of the build can inadvertently change the active hostname of
# the build machine while updating the permanent hostname of the build image.
# If the unshare command is available, use it to create a separate namespace
# so hostname changes won't affect the build machine.
UNSHARE := $(shell command -v unshare)
ifneq (,$(UNSHARE))
UNSHARE := $(UNSHARE) --uts
endif

all: clean install image

langs:
	@for lang in pwnagotchi/locale/*/; do\
		echo "compiling language: $$lang ..."; \
		./scripts/language.sh compile $$(basename $$lang); \
	done

PACKER := /tmp/pwnagotchi/packer
PACKER_URL := https://releases.hashicorp.com/packer/$(PACKER_VERSION)/packer_$(PACKER_VERSION)_linux_$(GOARCH).zip
$(PACKER):
	mkdir -p $(@D)
	curl -L "$(PACKER_URL)" -o $(PACKER).zip
	unzip $(PACKER).zip -d $(@D)
	rm $(PACKER).zip
	chmod +x $@

SDIST := dist/pwnagotchi-$(PWN_VERSION).tar.gz
$(SDIST): setup.py pwnagotchi
	python3 setup.py sdist

# Building the image requires packer, but don't rebuild the image just because packer updated.
$(PWN_RELEASE).img: | $(PACKER)

# If the packer or ansible files are updated, rebuild the image.
$(PWN_RELEASE).img: $(SDIST) builder/pwnagotchi.json builder/pwnagotchi.yml $(shell find builder/data -type f)
	sudo $(PACKER) plugins install github.com/solo-io/arm-image
	cd builder && sudo $(UNSHARE) $(PACKER) build -var "pwn_hostname=$(PWN_HOSTNAME)" -var "pwn_version=$(PWN_VERSION)" pwnagotchi.json
	sudo chown -R $$USER:$$USER builder/output-pwnagotchi
	mv builder/output-pwnagotchi/image $@

# If any of these files are updated, rebuild the checksums.
$(PWN_RELEASE).sha256: $(PWN_RELEASE).img
	sha256sum $^ > $@

# If any of the input files are updated, rebuild the archive.
$(PWN_RELEASE).zip: $(PWN_RELEASE).img $(PWN_RELEASE).sha256
	zip $(PWN_RELEASE).zip $^

.PHONY: image
image: $(PWN_RELEASE).zip

clean:
	- python3 setup.py clean --all
	- rm -rf dist pwnagotchi.egg-info
	- rm -f $(PACKER)
	- rm -f $(PWN_RELEASE).*
	- sudo rm -rf builder/output-pwnagotchi builder/packer_cache


