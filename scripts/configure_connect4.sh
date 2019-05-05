#!/bin/sh
#
# NAME: CONFIG CONNECT4


echo "Installing required python packages..."

if ! which pip3 > /dev/null; then
    echo -e "pip3 not found! install it? (Y/n) \c"
    read
    if "$REPLY" = "n"; then
        exit 0
    fi
    apt install pip3
fi

pip install colorama loguru

echo "Installed required python packages succesfully."

exit 0
