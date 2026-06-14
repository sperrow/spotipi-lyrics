#!/bin/bash

echo "======================================="
echo "Spotipi Configuration"
echo "======================================="
echo ""

# Load existing config if it exists
if [ -f .spotipi-config ]; then
    echo "Existing configuration found. Press Enter to keep current value, or enter a new one."
    echo ""
    source .spotipi-config
else
    echo "No existing configuration found."
    echo ""
fi

# Spotify Client ID
echo "Enter your Spotify Client ID:"
if [ -n "$SPOTIPY_CLIENT_ID" ]; then
    echo "(Current: $SPOTIPY_CLIENT_ID)"
fi
read -r input
spotify_client_id=$(echo "${input:-$SPOTIPY_CLIENT_ID}" | xargs)

# Spotify Client Secret
echo "Enter your Spotify Client Secret:"
if [ -n "$SPOTIPY_CLIENT_SECRET" ]; then
    echo "(Current: $SPOTIPY_CLIENT_SECRET)"
fi
read -r input
spotify_client_secret=$(echo "${input:-$SPOTIPY_CLIENT_SECRET}" | xargs)

# Spotify Redirect URI
echo "Enter your Spotify Redirect URI:"
if [ -n "$SPOTIPY_REDIRECT_URI" ]; then
    echo "(Current: $SPOTIPY_REDIRECT_URI)"
fi
read -r input
spotify_redirect_uri=$(echo "${input:-$SPOTIPY_REDIRECT_URI}" | xargs)

# Spotify Username
echo "Enter your Spotify username:"
if [ -n "$SPOTIPY_USERNAME" ]; then
    echo "(Current: $SPOTIPY_USERNAME)"
fi
read -r input
spotify_username=$(echo "${input:-$SPOTIPY_USERNAME}" | xargs)

# sp_dc Cookie
echo "Enter your sp_dc cookie for lyrics:"
echo "(Find this in your Spotify Web Player cookies: https://github.com/libre-lyrics/librelyrics-spotify)"
if [ -n "$SPOTIPY_SP_DC" ]; then
    echo "(Current: $SPOTIPY_SP_DC)"
fi
read -r input
sp_dc=$(echo "${input:-$SPOTIPY_SP_DC}" | xargs)

echo ""
echo "Saving configuration to .spotipi-config"
cat > .spotipi-config << EOF
# Spotipi Configuration
# Edit this file to change settings, then run: sudo systemctl restart spotipi

SPOTIPY_CLIENT_ID='$spotify_client_id'
SPOTIPY_CLIENT_SECRET='$spotify_client_secret'
SPOTIPY_REDIRECT_URI='$spotify_redirect_uri'
SPOTIPY_USERNAME='$spotify_username'
SPOTIPY_SP_DC='$sp_dc'
EOF
chmod 600 .spotipi-config

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
echo "Restarting the spotipi service to apply changes..."
sudo systemctl restart spotipi
echo "Service restarted."
