## Software

- Raspbian + [nexmon patches](https://re4son-kernel.com/re4son-pi-kernel/) for monitor mode, or any Linux with a monitor mode enabled interface (if you tune config.yml).

**Do not try with Kali on the Raspberry Pi 0 W, it is compiled without hardware floating point support and TensorFlow is simply not available for it, use Raspbian.**

## Creating an Image

You can use the `scripts/create_sibling.sh` script to create an - ready to flash - rasbian image with pwnagotchi.

```shell
usage: ./scripts/create_sibling.sh [OPTIONS]

  Options:
    -n <name>    # Name of the pwnagotchi (default: pwnagotchi)
    -i <file>    # Provide the path of an already downloaded raspbian image
    -o <file>    # Name of the img-file (default: pwnagotchi.img)
    -s <size>    # Size which should be added to second partition (in Gigabyte) (default: 4)
    -v <version> # Version of raspbian (Supported: latest; default: latest)
    -p           # Only run provisioning (assumes the image is already mounted)
    -d           # Only run dependencies checks
    -h           # Show this help
```
## Adding a Language

If you want to add a language use the `language.sh` script. If you want to add for example the language **italian** you would type:

```shell
./scripts/language.sh add it
# Now make your changes to the file
# sdcard/rootfs/root/pwnagotchi/scripts/pwnagotchi/locale/it/LC_MESSAGES/voice.po
./scripts/language.sh compile it
# DONE
```

If you changed the `voice.py`- File, the translations need an update. Do it like this:

```shell
./scripts/language.sh update it
# Now make your changes to the file (changed lines are marked with "fuzzy")
# sdcard/rootfs/root/pwnagotchi/scripts/pwnagotchi/locale/it/LC_MESSAGES/voice.po
./scripts/language.sh compile it
# DONE
```

Now you can use the `preview.py`-script to preview the changes:

```shell
./scripts/preview.py --lang it --display ws2 --port 8080 &
./scripts/preview.py --lang it --display inky --port 8081 &
# Now open http://localhost:8080 and http://localhost:8081
```
