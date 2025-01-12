import os
import yaml
from typing import Dict, Any

def load_config(config_path: str = "config/config.yaml") -> Dict[str, Any]:
    """Load configuration from YAML file with environment variable substitution."""
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Replace environment variables
    def replace_env_vars(config_dict):
        for key, value in config_dict.items():
            if isinstance(value, dict):
                replace_env_vars(value)
            elif isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                env_var = value[2:-1].split(":-")
                env_name = env_var[0]
                default_value = env_var[1] if len(env_var) > 1 else None
                config_dict[key] = os.getenv(env_name, default_value)
    
    replace_env_vars(config)
    return config 