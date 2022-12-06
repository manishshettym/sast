if data:
    with open(self.output_path, 'w') as f:
        json.dump(data, f)