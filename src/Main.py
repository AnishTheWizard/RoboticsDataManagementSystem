"""Main Code Compiling and Handling All Parts of Data"""
from src.DataManagement import *
from src.DataErrors import *
import sys
import os
import json
import logging

__author__ = "Anish Chandra"
__version__ = "1.0"


def compile_all_team_data(targetLocation: str) -> None:
    compiledJSON = open(targetLocation, "w")
    compiledJSON.write("[")

    for index, file in enumerate(os.listdir()):
        if file.find(".json") != -1 and file.find("-") != -1:
            with open(file, "r") as f:
                compiledJSON.write(f.read())

            if index <= len(os.listdir()) - 2:
                compiledJSON.write(", \n")

    compiledJSON.write("]")


if __name__ == '__main__':
    # Setup
    logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)

    # Get all configuration parameters
    args = sys.argv[1:]

    working_directory = str()
    target_json = str()
    target_csv = str()
    label_order = list()

    if len(args) == 4:
        working_directory = args[0]
        target_csv = args[1]
        label_order = args[2]

    elif len(args) == 1:
        try:
            config = json.loads(open(args[0], "r").read())
            working_directory = config["Working_Directory"]
            target_json = config["Target_JSON"]
            target_csv = config["Target_CSV"]
            label_order = config["Label_Order"]
        except FileNotFoundError:
            logging.critical(f"Config File Does Not Exist")
            exit(ExitDueToFailure("This Code will Exit"))
        except json.decoder.JSONDecodeError:
            logging.critical(f"Config File is not formatted properly")
            exit(ExitDueToFailure("This Code will Exit"))

    else:
        logging.critical(f"Incorrect Number of Arguments Passed")
        exit(ExitDueToFailure("This Code will Exit"))

    # Check if all parameters are correct
    if None in [working_directory, target_json, target_csv, label_order]:
        logging.critical(f"One of the arguments is of NoneType")
        exit(ExitDueToFailure("This Code will Exit"))

    # Set working directory
    os.chdir(working_directory)

    # Find files to reformat
    filesToReformat = list()
    for file in os.listdir():
        if file.find(".json") != -1 and file.find("-") != -1:
            filesToReformat.append(file)

    logging.debug(f"Files to reformat: {str(filesToReformat)}")

    # Reformat Files into Labeled Data
    if len(filesToReformat) == 0:
        logging.critical(f"There are no files to reformat in the directory {os.getcwd()}")
        exit(1)

    reformatter = ScoutingJSONReformatter(filesToReformat[0], label_order)

    for file in filesToReformat:
        try:
            reformatter.change_file(file)
            reformatter.add_labels()
            reformatter.save_file()
            logging.info(f"Successfully Reformatted File {file}")
        except ImproperlyFormattedJSONError:
            logging.warning(f"File {file} may have already been formatted")
        except DuplicationError as dup:
            logging.warning(f"File {file} has a duplicate or is corrupted\n{dup}")

    # Compile all Data into one JSON
    compile_all_team_data(target_json)
    logging.info("Successfully Created Compiled JSON")

    # Compile all Data into one CSV

    compositor = CSVCompositor(target_csv, label_order)
    compositor.convert_json_to_csv(json.dumps(json.loads(open(target_json, "r").read())))
    compositor.save_file()
    logging.info("Successfully Created Compiled CSV")
    logging.info("Done")
