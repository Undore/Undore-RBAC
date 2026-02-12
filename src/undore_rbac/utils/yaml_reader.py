import yaml


class YAMLReader:
    @staticmethod
    def read_yaml(path: str) -> dict:
        with open(path) as f:
            return yaml.safe_load(f)
