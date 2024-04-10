import csv


class CSVUtil:
    def __init__(self, file_path):
        self.file_path = file_path

    def read(self):
        data = []
        with open(self.file_path, 'r') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                data.append(row)
        return data

    def write(self, data):
        with open(self.file_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            for row in data:
                writer.writerow(row)