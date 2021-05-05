import logging
import csv
import StringIO

# based on https://stackoverflow.com/a/19766056
class CsvFormatter(logging.Formatter):
    def __init__(self):
        super(CsvFormatter, self).__init__()
        self.output = StringIO.StringIO()
        self.writer = csv.writer(self.output)

    def format(self, record):
        self.writer.writerow([record.created, record.levelname] + list(record.msg))
        data = self.output.getvalue()
        self.output.truncate(0)
        self.output.seek(0)
        return data.strip()

def create_csv_logger(filename):
    logger = logging.getLogger(filename)
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler(filename)
    fh.setLevel(logging.DEBUG)

    fh.setFormatter(CsvFormatter())
    logger.propagate = False # make sure msg are not sent to the default logger
    logger.addHandler(fh)

    return logger


