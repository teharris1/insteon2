# insteon2
Home Assistant Insteon component version 2

This is a beta version of the Insteon v2 component for Home-Assistant. It is still under development but has a lot 
of new features.

- Auto discovery also identifies battery operated devices just by triggering the device rahter than using device overrides
- The All-Link database is used to determine cascading state changes (ie. device 1 triggers device 2)
- Operating flags and extended properties are loaded and used to identify device behaviors in the following devices:
  - Thermostat
  - IOLinc
  - KeypadLinc
- Events are published and can be listened for like double tap on/off (May requre a python script however)
- Hub users can use it interchangably with the Hub app. The state will updated in HA.

Download these files and either put them in `<config>/custom_components/insteon2` director. <config> is the location
where your `configuration.yaml` file is. The `custom_components` folder will likely not exist so you need to create it.

You can download these files here: https://github.com/teharris1/insteon2/archive/master.zip

Install the `pyinsteon` library using this command:
```
python3 -m pip install --upgrade https://github.com/teharris1/pyinsteon/archive/master.zip
```

Please provide feedback so we can make this rock solid before releasing to Home Assistant!

Thanks
Tom
