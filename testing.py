import ruamel.yaml as yaml

with open('locale/en_us.yml') as file:
  yaml_file = yaml.round_trip_load(file)

for key in yaml_file:
  print(yaml_file.get(key))