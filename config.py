import json

class Configuration:
  def __init__(self, file_path):
    self.file_path = file_path
    self.data = self.load_config()

  def load_config(self):
    with open(self.file_path, 'r') as file:
      return json.load(file)

  def save_config(self):
    with open(self.file_path, 'w') as file:
      json.dump(self.data, file, indent=4)

  def get_value(self, key):
    return self.data.get(key)

  def update_value(self, key, value):
    self.data[key] = value
    self.save_config()

  def remove_value(self, key):
    if key in self.data:
      del self.data[key]
      self.save_config()