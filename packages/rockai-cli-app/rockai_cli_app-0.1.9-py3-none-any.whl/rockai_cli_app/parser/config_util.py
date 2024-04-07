import yaml

def parse_config_file(file_path):
    with open(file_path, 'r') as file:
        config = yaml.safe_load(file)
    return config


# Example usage
# config_file_path = '/Users/jyz/Desktop/rockai-cli-app/rockai_cli_app/server/test/test_config.yaml'
# parsed_config = parse_config_file(config_file_path)
# print(parsed_config)
def get_predictor_path(config_map):
    predict_config = config_map['predict']
    splited = predict_config.split(":")
    # the first element should a python file, the second element should be Class name
    return splited[0]

def get_predictor_class_name(config_map):
    predict_config = config_map['predict']
    splited = predict_config.split(":")
    # the first element should a python file, the second element should be Class name
    return splited[1]
