import csv
import json
import random
import threading


class CsvUtil:

    @staticmethod
    def write_json_to_csv_file(csv_path: str, content: json):
        count: int = 0
        try:
            data_file = open(csv_path, 'w', newline='')
            csv_writer = csv.writer(data_file)
            for data in content:
                if count == 0:
                    header = data.keys()
                    csv_writer.writerow(header)
                    count += 1
                csv_writer.writerow(data.values())
        except FileNotFoundError:
            raise f'Can not found {csv_path} file'
        data_file.close()

    @staticmethod
    def convert_csv_file_to_dictionary(f_path: str, headers: list = None):
        with open(f_path, 'r') as file:
            reader = csv.DictReader(
                file, fieldnames=headers)
            return [row for row in reader]

    @staticmethod
    def write_to_csv_file(csv_path, data: list):
        with open(csv_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(data)
        file.close()

    @staticmethod
    def convert_csv_to_json(csv_file: str) -> [dict]:
        data = []
        with open(csv_file, 'r') as file:
            csv_data = csv.DictReader(file)
            for row in csv_data:
                data.append(row)
        return data

    @staticmethod
    def generate_random_data(csv_file, num_threads):
        """usage with locust.
        The csv file still be the path the file
        for num_threads, it should be the total CCU that scenarios is handling, you can get this number by
`       self.environment.runner.user_count
        Args:
            csv_file (_type_): _description_
            num_threads (_type_): _description_
        """
        generator = RandomDataGenerator(csv_file)
        threads = []

        def worker():
            random_data = generator.get_random_data()
            print(random_data)  # Do something with the random data

        for _ in range(num_threads):
            thread = threading.Thread(target=worker)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

class RandomDataGenerator:
    def __init__(self, csv_file):
        self.csv_file = csv_file
        self.lock = threading.Lock()
        self.used_indices = set()
        self.data = self._read_csv()

    def _read_csv(self):
        with open(self.csv_file, 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            return list(reader)

    def _get_random_row(self):
        while True:
            index = random.randint(0, len(self.data) - 1)
            if index not in self.used_indices:
                with self.lock:
                    if index not in self.used_indices:
                        self.used_indices.add(index)
                        return self.data[index]

    def get_random_data(self):
        return self._get_random_row()

