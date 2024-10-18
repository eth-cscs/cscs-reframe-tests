# Configuration autodectection for new systems

The ReFrame configuration file can be automatically generated for a new system using ```generate_config.py```.

The script requires user input to create the final system configuration.

## Running the autodetection

### Install the Jinja2 python package

```sh
pip install jinja2
```

```sh
python3 generate_config.py
```

## Generated configuration files

The script generates a ```json``` and a ```.py``` file with the system configuration

- json: ```<system_name>```_config.json
- .py: ```<system_name>```_config.py
