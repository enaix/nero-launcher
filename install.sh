#!/bin/bash

read -p "This script will install nero executable\nDefault installation folder is /usr/bin. Would you like to change it? [y/N]" USER_INPUT

if [ "$USER_INPUT" == "y" ] || [ "$USER_INPUT" == "Y" ]; then
	read -p "Please type the install dir without ending slash:" INSTALL_DIR
else
	INSTALL_DIR="/usr/bin"
fi

NERO_INSTALL_DIR="$(pwd)"

echo "#!/bin/bash" > ./nero

echo "NERO_PATH=\""$NERO_INSTALL_DIR"\"" >> ./nero

echo "python3 \$NERO_PATH/main.py -d \$NERO_PATH" >> ./nero

chmod +x ./nero

cp ./nero $INSTALL_DIR/nero
