import yaml

config = {}
with open('config.yml', 'r') as f:
    config = yaml.load(f)

print(config)
