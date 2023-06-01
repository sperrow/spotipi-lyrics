# Spotipi
### Overview
This project is to display lyrics from the Spotify web api on a 64x32 led matrix.
### Getting Started
Guide: https://www.ryanwardtech.com/guides/how-to-install-spotify-cover-art-display/
* Create a new application within the [Spotify developer dashboard](https://developer.spotify.com/dashboard/applications) <br />
* Edit the settings of the application within the dashboard.
    * Set the redirect uri to any local url such as http://127.0.0.1/callback
* First step is to ssh to your raspberry pi to clone the repository
```
git clone https://github.com/sperrow/spotipi-lyrics
```
* Next go ahead and change into the directory using 
```
cd spotipi
```
* Run the generate token script and enter the prompted spotify credentials using
```
bash generate-token.sh
```
* This will generate a file named `.cache` which will be used for authentication
    * A url will show up in the terminal window and you must copy this into your own web broswer
    * The url will redirect you to another url and you need to copy/paste this in the terminal when prompted.
   
* Install the software: <br />
```
cd spotipi
sudo bash setup.sh
```
* Edit settings on the web app: <br />
```
navigate to http://<raspberrypi_hostname or ip_address> within a web browser
```

### Final Product
https://www.youtube.com/shorts/PKM1I0vdbhE
