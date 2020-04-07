FROM homeassistant/home-assistant
RUN python3 -m pip install --upgrade https://github.com/teharris1/pyinsteon/archive/master.zip
