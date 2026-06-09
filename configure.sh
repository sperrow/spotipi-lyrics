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

install_path=$(pwd)

# Spotify Client ID
echo "Enter your Spotify Client ID:"
if [ ! -z "$SPOTIPY_CLIENT_ID" ]; then
    echo "(Current: ${SPOTIPY_CLIENT_ID:0:10}...)"
fi
read input
if [ ! -z "$input" ]; then
    spotify_client_id=$(echo "$input" | xargs)
else
    spotify_client_id="$SPOTIPY_CLIENT_ID"
fi

# Spotify Client Secret
echo "Enter your Spotify Client Secret:"
if [ ! -z "$SPOTIPY_CLIENT_SECRET" ]; then
    echo "(Current: ${SPOTIPY_CLIENT_SECRET:0:4}****${SPOTIPY_CLIENT_SECRET: -4})"
fi
read input
if [ ! -z "$input" ]; then
    spotify_client_secret=$(echo "$input" | xargs)
else
    spotify_client_secret="$SPOTIPY_CLIENT_SECRET"
fi

# Spotify Redirect URI
echo "Enter your Spotify Redirect URI:"
if [ ! -z "$SPOTIPY_REDIRECT_URI" ]; then
    echo "(Current: $SPOTIPY_REDIRECT_URI)"
fi
read input
if [ ! -z "$input" ]; then
    spotify_redirect_uri=$(echo "$input" | xargs)
else
    spotify_redirect_uri="$SPOTIPY_REDIRECT_URI"
fi

# Spotify Username
echo "Enter your Spotify username:"
if [ ! -z "$SPOTIPY_USERNAME" ]; then
    echo "(Current: $SPOTIPY_USERNAME)"
fi
read input
if [ ! -z "$input" ]; then
    spotify_username=$(echo "$input" | xargs)
else
    spotify_username="$SPOTIPY_USERNAME"
fi

# sp_dc Cookie
echo "Enter your sp_dc cookie for lyrics:"
echo "(Guide: https://github.com/akashrchandran/syrics/wiki/Finding-sp_dc)"
if [ ! -z "$SPOTIPY_SP_DC" ]; then
    echo "(Current: ${SPOTIPY_SP_DC:0:10}****${SPOTIPY_SP_DC: -10})"
fi
read input
if [ ! -z "$input" ]; then
    sp_dc=$(echo "$input" | xargs)
else
    sp_dc="$SPOTIPY_SP_DC"
fi

echo ""
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
echo "Restart the service to apply changes:"
echo "  sudo systemctl restart spotipi"
