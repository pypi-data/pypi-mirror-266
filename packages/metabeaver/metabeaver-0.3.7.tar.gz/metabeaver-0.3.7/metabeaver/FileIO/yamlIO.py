import yaml


from pathlib import Path


# Given a valid filepath for the project configuration settings, will return yaml as a Python dict.
def load_yaml_to_dict(config_path: str= 'config.yaml') -> Dict[str, Any]:

    # Resolve the yaml file path
    yaml_config_path = Path(config_path).resolve()

    # Raise FileNotFoundError if the provided path is actually invalid.
    if not yaml_config_path.is_file():
        raise FileNotFoundError(f"The file {config_path} does not exist.")

    # If we got a valid path, try to safeload and return the yaml as a python dictionary
    with yaml_config_path.open('r') as file:
        # Try to do a valid load of the yaml file to python dictionary.
        try:
            config = yaml.safe_load(file)
            return config
        # Raise a ValueError is we could not parse the YAML file.
        except yaml.YAMLError as exc:
            raise ValueError(f"Error parsing YAML file: {exc}")