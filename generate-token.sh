sudo apt install python3-pip python3-venv

echo "Creating python virtual environment..."
python3 -m venv spotipi_venv --system-site-packages
source spotipi_venv/bin/activate
echo "Virtual environment activated"

echo "Installing spotipy library:"
pip3 install spotipy --upgrade

echo "Enter your Spotify Client ID:"
read spotify_client_id
export SPOTIPY_CLIENT_ID=$spotify_client_id

echo "Enter your Spotify Client Secret:"
read spotify_client_secret
export SPOTIPY_CLIENT_SECRET=$spotify_client_secret

echo "Enter your Spotify Redirect URI:"
read spotify_redirect_uri
export SPOTIPY_REDIRECT_URI=$spotify_redirect_uri

echo "Enter your spotify username:"
read spotify_username

python3 python/generateToken.py $spotify_username

echo
echo "###### Spotify Token Created ######"
echo "Filename: .cache"

deactivate