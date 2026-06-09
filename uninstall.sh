#!/bin/bash

echo "======================================="
echo "Spotipi Uninstall"
echo "======================================="
echo ""
echo "This will remove the spotipi services and virtual environment."
echo "Your configuration file (.spotipi-config) and token (.cache) will be preserved."
echo ""
echo -n "Are you sure? [y/N] "
read
if [[ ! "$REPLY" =~ ^(yes|y|Y)$ ]]; then
    echo "Uninstall cancelled."
    exit 0
fi

echo ""
echo "Stopping services..."
sudo systemctl stop spotipi
sudo systemctl stop spotipi-client

echo "Disabling services..."
sudo systemctl disable spotipi
sudo systemctl disable spotipi-client

echo "Removing service files..."
sudo rm -f /etc/systemd/system/spotipi.service
sudo rm -f /etc/systemd/system/spotipi-client.service
sudo rm -rf /etc/systemd/system/spotipi.service.d
sudo systemctl daemon-reload

echo "Removing virtual environment..."
rm -rf spotipi_venv

echo "Removing rgb-matrix installation..."
sudo rm -rf rpi-rgb-led-matrix

echo ""
echo "======================================="
echo "Uninstall Complete"
echo "======================================="
echo "Preserved files:"
echo "  - .spotipi-config (your configuration)"
echo "  - .cache (your Spotify token)"
echo ""
echo "To reinstall, run:"
echo "  sudo bash setup.sh"
