FROM homeassistant/home-assistant
RUN pdocker exec -it --user=root homeassistant pip3 install --upgrade https://github.com/teharris1/pyinsteon/archive/master.zip
