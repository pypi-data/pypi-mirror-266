import csv


def detect_delimiter(csv_file):
    try:
        with open(csv_file, 'r') as file:
            dialect = csv.Sniffer().sniff(file.read(1024))
        return dialect.delimiter
    except csv.Error:
        return '\001'
