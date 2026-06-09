#!/bin/bash

echo "Ensure packages are installed:"
sudo apt-get install libopenjp2-7 python3-pip python3-dbus python3-venv

echo "Creating python virtual environment..."
venv_directory=spotipi_venv
python3 -m venv $venv_directory --system-site-packages
source $venv_directory/bin/activate
echo "Virtual environment activated"

echo "Installing required libraries:"
pip3 install spotipy --upgrade
pip3 install syrics --upgrade
pip3 install flask --upgrade

echo ""
echo "======================================="
echo "Spotify Configuration"
echo "======================================="
echo "Get these values from https://developer.spotify.com/dashboard"
echo ""

echo "Enter your Spotify Client ID:"
read spotify_client_id
spotify_client_id=$(echo "$spotify_client_id" | xargs)

echo "Enter your Spotify Client Secret:"
read spotify_client_secret
spotify_client_secret=$(echo "$spotify_client_secret" | xargs)

echo "Enter your Spotify Redirect URI:"
read spotify_redirect_uri
spotify_redirect_uri=$(echo "$spotify_redirect_uri" | xargs)

echo "Enter your Spotify username:"
read spotify_username
spotify_username=$(echo "$spotify_username" | xargs)

echo ""
echo "======================================="
echo "Generating Spotify Token"
echo "======================================="
export SPOTIPY_CLIENT_ID=$spotify_client_id
export SPOTIPY_CLIENT_SECRET=$spotify_client_secret
export SPOTIPY_REDIRECT_URI=$spotify_redirect_uri

python3 python/generateToken.py $spotify_username
sudo chmod a+rx .cache

echo ""
echo "Spotify token created: .cache"
echo ""

echo "======================================="
echo "Lyrics Configuration"
echo "======================================="
echo "Enter your sp_dc cookie for lyrics:"
echo "(Guide: https://github.com/akashrchandran/syrics/wiki/Finding-sp_dc)"
read sp_dc
sp_dc=$(echo "$sp_dc" | xargs)

install_path=$(pwd)

echo "Saving configuration to .spotipi-config"
cat > .spotipi-config << EOF
# Spotipi Configuration
# Edit this file to change settings, then run: sudo systemctl restart spotipi

SPOTIPY_CLIENT_ID=$spotify_client_id
SPOTIPY_CLIENT_SECRET=$spotify_client_secret
SPOTIPY_REDIRECT_URI=$spotify_redirect_uri
SPOTIPY_USERNAME=$spotify_username
SPOTIPY_SP_DC=$sp_dc
EOF
chmod 600 .spotipi-config

echo ""
echo "======================================="
echo "Installing RGB Matrix Hardware"
echo "======================================="
echo "Downloading rgb-matrix software setup:"
curl https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/master/rgb-matrix.sh >rgb-matrix.sh

sed -n '/REBOOT NOW?/q;p' < rgb-matrix.sh > rgb-matrix-spotipi.sh

echo "Running rgb-matrix software setup:"
sudo bash rgb-matrix-spotipi.sh

echo "Removing rgb-matrix setup script:"
sudo rm rgb-matrix.sh
echo "...done"

echo "Installing bindings to venv"
cd rpi-rgb-led-matrix/
sudo make install-python
cd ${install_path}

echo ""
echo "======================================="
echo "Installing Services"
echo "======================================="

echo "Removing spotipi service if it exists:"
sudo systemctl stop spotipi
sudo rm -rf /etc/systemd/system/spotipi.*
sudo systemctl daemon-reload
echo "...done"

echo "Removing spotipi-client service if it exists:"
sudo systemctl stop spotipi-client
sudo rm -rf /etc/systemd/system/spotipi-client.*
sudo systemctl daemon-reload
echo "...done"

echo "Creating spotipi service:"
sudo cp ./config/spotipi.service /etc/systemd/system/
sudo sed -i -e "s|EnvironmentFile=.*|EnvironmentFile=${install_path}/.spotipi-config|" /etc/systemd/system/spotipi.service
sudo sed -i -e "/\[Service\]/a ExecStart=${install_path}/spotipi_venv/bin/python3 ${install_path}/python/displayLyrics.py \${SPOTIPY_USERNAME} \${SPOTIPY_SP_DC} < /dev/zero &> /dev/null &" /etc/systemd/system/spotipi.service
sudo systemctl daemon-reload
sudo systemctl start spotipi
sudo systemctl enable spotipi
echo "...done"

echo "Creating spotipi-client service:"
sudo cp ./config/spotipi-client.service /etc/systemd/system/
sudo sed -i -e "/\[Service\]/a ExecStart=${install_path}/spotipi_venv/bin/python3 ${install_path}/python/client/app.py &" /etc/systemd/system/spotipi-client.service
sudo systemctl daemon-reload
sudo systemctl start spotipi-client
sudo systemctl enable spotipi-client
echo "...done"

echo ""
echo "======================================="
echo "Configuration Saved"
echo "======================================="
echo "Your settings have been saved to: .spotipi-config"
echo ""
echo "To view your configuration:"
echo "  cat .spotipi-config"
echo ""
echo "To edit your configuration:"
echo "  nano .spotipi-config"
echo ""
echo "After editing, restart the service:"
echo "  sudo systemctl restart spotipi"
echo ""
echo "A reboot is necessary to finish setup..."
echo -n "REBOOT NOW? [y/N] "
read
if [[ ! "$REPLY" =~ ^(yes|y|Y)$ ]]; then
        echo "Exiting without reboot."
        exit 0
fi
echo "Reboot started..."
reboot
sleep infinity
