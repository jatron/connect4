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
    sudo apt install python3-pip
fi

pip3 install colorama docopt gevent loguru prompt_toolkit tinydb ujson

echo "Installed required python packages succesfully."

exit 0
