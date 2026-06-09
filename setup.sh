#!/bin/bash

echo "======================================="
echo "Spotipi Setup"
echo "======================================="
echo ""
echo "This script will install the hardware bindings and services."
echo ""

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

install_path=$(pwd)

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
sudo systemctl stop spotipi 2>/dev/null || true
sudo rm -rf /etc/systemd/system/spotipi.*
sudo systemctl daemon-reload
echo "...done"

echo "Removing spotipi-client service if it exists:"
sudo systemctl stop spotipi-client 2>/dev/null || true
sudo rm -rf /etc/systemd/system/spotipi-client.*
sudo systemctl daemon-reload
echo "...done"

echo "Creating spotipi service:"
sudo cp ./config/spotipi.service /etc/systemd/system/
sudo sed -i -e "s|EnvironmentFile=.*|EnvironmentFile=${install_path}/.spotipi-config|" /etc/systemd/system/spotipi.service
sudo sed -i -e "/\[Service\]/a ExecStart=${install_path}/spotipi_venv/bin/python3 ${install_path}/python/displayLyrics.py \${SPOTIPY_USERNAME} \${SPOTIPY_SP_DC}" /etc/systemd/system/spotipi.service
sudo systemctl daemon-reload
echo "...done"

echo "Creating spotipi-client service:"
sudo cp ./config/spotipi-client.service /etc/systemd/system/
sudo sed -i -e "/\[Service\]/a ExecStart=${install_path}/spotipi_venv/bin/python3 ${install_path}/python/client/app.py" /etc/systemd/system/spotipi-client.service
sudo systemctl daemon-reload
echo "...done"

echo ""
echo "======================================="
echo "Setup Complete!"
echo "======================================="
echo ""
echo "A reboot is required for the RGB matrix bindings to take effect."
echo -n "REBOOT NOW? [y/N] "
read
if [[ ! "$REPLY" =~ ^(yes|y|Y)$ ]]; then
    echo "Exiting without reboot."
    exit 0
fi
echo "Rebooting..."
sudo reboot
sleep infinity
