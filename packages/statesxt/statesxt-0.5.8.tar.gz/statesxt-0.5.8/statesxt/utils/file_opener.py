import csv


class FileOpener:
    """To import, open, and read file"""

    @staticmethod
    def openCSV(path, withHeader=False):
        dataList = []
        reader = csv.reader(open(path, "r"))
        if withHeader:
            next(reader)
        for row in reader:
            dataList.append(row)
        return dataList
