#!/bin/sh
# Preseed the mscorefonts EULA so the non-interactive apt install can't hang.
# Idempotent: writing the same debconf value twice is a no-op (exit 0).
echo "ttf-mscorefonts-installer msttcorefonts/accepted-mscorefonts-eula boolean true" | debconf-set-selections
