# app.py

from flask import Flask, render_template, request
import os
import configparser
import dbus

app = Flask(__name__)
app.config["CACHE_TYPE"] = "null"

dir = os.path.dirname(__file__)
config_path = os.path.join(dir, '../../config/rgb_options.ini')

sysbus = dbus.SystemBus()
systemd1 = sysbus.get_object('org.freedesktop.systemd1', '/org/freedesktop/systemd1')
manager = dbus.Interface(systemd1, 'org.freedesktop.systemd1.Manager')


class ConfigManager:
    def __init__(self, filepath):
        self.filepath = filepath
        self.config = configparser.ConfigParser()
        self.load()
    
    def load(self):
        self.config.read(self.filepath)
    
    def get_all_settings(self):
        return {
            'brightness': int(self.config['DEFAULT']['brightness']),
            'width': int(self.config['DEFAULT']['rows']),
            'height': int(self.config['DEFAULT']['columns']),
            'power': self.config['DEFAULT']['power'],
            'refresh_rate': int(self.config['DEFAULT']['refresh_rate'])
        }
    
    def set_value(self, key, value):
        self.config.set('DEFAULT', key, str(value))
    
    def save(self):
        with open(self.filepath, 'w') as configfile:
            self.config.write(configfile)


config_manager = ConfigManager(config_path)


def restart_service():
    manager.RestartUnit('spotipi.service', 'fail')


def get_template_data():
    settings = config_manager.get_all_settings()
    return {
        'brightness': settings['brightness'],
        'width': settings['width'],
        'height': settings['height'],
        'power': settings['power'],
        'refresh_rate': settings['refresh_rate']
    }


@app.route("/")
def saved_config():
    return render_template('index.html', **get_template_data())


@app.route("/power", methods=["GET", "POST"])
def handle_power():
    power = request.form['power']
    config_manager.set_value('power', power)
    if power == 'on':
        manager.StartUnit('spotipi.service', 'replace')
    else:
        manager.StopUnit('spotipi.service', 'replace')
    return render_template('index.html', **get_template_data())


@app.route('/brightness', methods=['POST'])
def handle_brightness():
    brightness = request.form['brightness']
    config_manager.set_value('brightness', brightness)
    config_manager.save()
    restart_service()
    return render_template('index.html', **get_template_data())


@app.route('/size', methods=['POST'])
def handle_size():
    config_manager.set_value('rows', request.form['width'])
    config_manager.set_value('columns', request.form['height'])
    config_manager.save()
    restart_service()
    return render_template('index.html', **get_template_data())


@app.route('/refresh-rate', methods=['POST'])
def handle_refresh_rate():
    config_manager.set_value('refresh_rate', request.form['refresh_rate'])
    config_manager.save()
    restart_service()
    return render_template('index.html', **get_template_data())


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80) 

