"""Library to Manage the Data Retrieved by the Scouting System"""

import ast
import csv
import json
from typing import TextIO

from src.DataErrors import *

__author__ = "Anish Chandra"
__version__ = "1.0"


class DataHandler(object):
    def __init__(self, location: str, openType: str) -> None:
        try:
            self.location = location
            self.openType = openType
            self.file = open(location, openType)
        except FileNotFoundError:
            raise FileNotFoundError(f"File {location} does not exist")

    def _close(self) -> None:
        self.file.flush()
        self.file.close()

    def _save_file(self, fileText) -> None:
        output = open(self.location, "w")
        output.write(fileText)
        output.flush()
        output.close()

    def _open_new_file(self, location: str, openType: str) -> None:

        try:
            self.location = location
            self.openType = openType
            self.file = open(location, openType)
        except FileNotFoundError:
            raise FileNotFoundError(f"File {location} does NOT exist")

    def _get_file(self) -> TextIO:
        return self.file


class JSONHandler(DataHandler):
    def __init__(self, location: str) -> None:
        super().__init__(location, "r")
        try:
            self.json = json.loads(super()._get_file().read())
        except json.decoder.JSONDecodeError:
            raise DuplicationError(f"File at location {location} has a duplicate")
        # except more errors in formatting here and create more in DataErrors.py such as
        # except ValueError:
        #   raise SomeNewError()

    def change_file(self, location: str) -> None:
        super()._open_new_file(location, 'r')
        try:
            self.json = json.loads(super()._get_file().read())
        except json.decoder.JSONDecodeError:
            raise DuplicationError(f"File at location {location} has a duplicate")

    def get_file(self):
        return self.json

    def set_file(self, newJSON: str):
        self.json = json.loads(newJSON)

    def save_file(self) -> str:
        super()._save_file(json.dumps(self.json))
        return json.dumps(self.json)


class CSVHandler(DataHandler):
    def __init__(self, location: str, toRead: bool) -> None:
        self.toRead = toRead
        super().__init__(location, "r" if toRead else "w")
        self.csv = csv.reader(self.file) if toRead else csv.writer(self.file)

    def write_row(self, row: list) -> None:
        self.csv.writerow(row)

    def get_file(self):
        return self.csv

    def save_file(self) -> None:
        super()._close()


class ScoutingJSONReformatter(JSONHandler):
    formattedJSON = dict()

    def __init__(self, location: str, labelOrder: list) -> None:
        self.labelOrder = labelOrder
        super().__init__(location)

    def add_labels(self) -> None:
        if type(super().get_file()) is not list or len(self.labelOrder) != len(super().get_file()):
            raise ImproperlyFormattedJSONError(f"File at location {self.location} may already be formatted")

        rawMatchData = self.json
        for i in range(len(rawMatchData)):
            self.formattedJSON[self.labelOrder[i]] = rawMatchData[i]
        self.json = self.formattedJSON

    def export_format(self) -> None:
        super().save_file()


class CSVCompositor(CSVHandler):

    def __init__(self, location: str, headers: list) -> None:
        super().__init__(location, False)
        self.csv.writerow(headers)
        self.lines = 0

    def convert_json_to_csv(self, json: str) -> None:
        json = ast.literal_eval(json)
        for data in json:
            self.csv.writerow(list(data.values()))

    def save_file(self) -> None:
        super().save_file()
