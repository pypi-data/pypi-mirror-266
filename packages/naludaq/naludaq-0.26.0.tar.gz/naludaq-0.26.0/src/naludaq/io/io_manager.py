"""IO module

Collection of IO functions to support disk IO.
"""
import csv
import gzip
import logging
import os
import pickle
import re

import numpy as np

from naludaq.helpers.exceptions import InvalidClockFileError
from naludaq.io.csv_writer import get_csv_writer

LOGGER = logging.getLogger(__name__)


class IOManager:
    """
    IO Controller handles all IO interactions with csv, yaml, etc. files for
    purposes such as exporting events and generating config files.

    Attributes:
        params (dict): Dictionary of parameters. Must include key: ``model``.
    """

    def __init__(self, params: dict = None):
        self.params = params
        self.model = None
        if params is not None:
            self.model = params.get("model", None)

    def export_acq_to_bin(self, filename: str, acqs: list):
        """Exporting multiple acquisitions to a bin file.

        Args:
            filename (str): full filepath inlcuding directory and filename.
            acqs (list): list of acquisitions to export data from.

        Output:
            bin file written to disk.
        """
        LOGGER.debug("Exporting %s acquisitions to bin", len(acqs))

        if not isinstance(acqs[0], dict):
            events = self._compress_acquisitions(acqs)
        else:
            events = acqs

        path, _ = os.path.split(filename)
        if not os.path.isdir(path):
            raise NotADirectoryError(f"Not a valid directory: {path}")

        with open(filename, mode="wb") as evt_file:
            pickle.dump(events, evt_file)

    def export_acq_to_csv(
        self, filename: str, acqs: list, max_channels=None, time_per_channel=False
    ):
        """Exporting multiple acquisitions to a csv file.
        Args:
            filename (str): full filepath inlcuding directory and filename.
            acqs (list): list of acquisitions to export data from.
            max_channels (int): set the maximum channels to readout.
            time_per_channel (bool): export time per channel rather than per row.

        Output:
            csv file written to disk.
        """
        csv_writer = get_csv_writer(self.params)
        csv_writer.export_acq_to_csv(filename, acqs, max_channels, time_per_channel)

    @staticmethod
    def _compress_acquisitions(acquisitions):
        """Converts multiple acquisitions into a single
        acquistion.

        Args:
            acquisitions (list): A list of acquisition

        Returns:
            acquisition (list): Combined acquisition of all events
        """
        events = list()
        for acq in acquisitions:
            events.extend(acq)

        return events

    @staticmethod
    def import_data_from_csv(
        filename: str, channels: list
    ):  # TODO(Marcus): Update for upac
        """
        Reads a csv file that has stored events and stored that data into a
        variant of the acquisition structure, called a kacquisition. (Name is a WIP)
        The difference is that a kacq flattens all events into a single list

        Args:
            filename (str): Filename
            channels (list): Specific channels to parse out of the csv

        """

        if not isinstance(channels, list):
            raise TypeError(f"Expected chans to be list, got {type(channels)}")

        with open(filename) as open_file:
            csv_f = csv.reader(open_file)

            acq = {
                "evt_num": [],
                "windnum": [],
                "data": [],
                "time": [],
            }

            for chan in channels:
                acq["evt_num"].append([])
                acq["windnum"].append([])
                acq["data"].append([])
                acq["time"].append([])

            _ = next(csv_f)
            if _[0] == "acq_num":
                for row in csv_f:
                    for index, chan in enumerate(channels):
                        acq["evt_num"][index].append(int(row[1]))
                        acq["windnum"][index].append(int(row[(chan * 3) + 2]))
                        acq["data"][index].append(int(float(row[(chan * 3) + 3])))
                        acq["time"][index].append(int(row[(chan * 3) + 4]))
            else:
                for row in csv_f:
                    for index, chan in enumerate(channels):
                        acq["evt_num"][index].append(int(row[0]))
                        acq["windnum"][index].append(int(row[(chan * 3) + 1]))
                        acq["data"][index].append(int(float(row[(chan * 3) + 2])))
                        acq["time"][index].append(int(row[(chan * 3) + 3]))

        return acq

    @staticmethod
    def import_data_from_bin(filename: str):
        """
        Reads a bin file that has stored events in a acquisition. Bin file has
        been pickled.

        Args:
            filename (str): Filename
            channels (list): Specific channels to parse out of the csv

        """

        with open(filename, mode="rb") as open_file:
            acq = pickle.load(open_file)

        return acq

    def import_data_from_directory(self, directory: str, chans: list):
        """Gets data from all csv files in a directory.

        Primarily for importing frequency sweep results.

        Args:
            directory (str): Path to folder where files to be imported are located
            chans (list): List of channels to import.

        Returns:
            freq_manifold (list): List of frequecies labeled in the filenames
            data_manifold (list): List of events that was imported from the csv file

        Raises:
            TypeError if chans is not list
        """

        data_manifold = []
        freq_manifold = []
        for file in os.listdir(directory):
            filename = os.fsdecode(file)
            if filename.endswith(".csv"):
                data_manifold.append(
                    self.import_data_from_csv(
                        os.path.join(directory, filename),
                        channels=chans,
                    )
                )
                freq_manifold.append(int(file[:-4]))

        return freq_manifold, data_manifold

    def export_sweep_results(self, directory: str, sweep_results: list):
        """Takes the results of a parameter sweep and stores the results as a collection of csvs
        inside of a folder.

        Args:
            directory (str): Location where to store all the csvs
            sweep_results (list): List of data acquisitions from varying parameters
        """

        for item in sweep_results:
            freq_num = str(int(item[0] / 1000000))
            while len(freq_num) < 4:
                freq_num = "0{0}".format(freq_num)

            filename = directory + "/" + freq_num + ".csv"
            self.export_acq_to_csv(filename, [item[1]])

    def export_pedestals_csv(self, board, filename: str, pedestals: dict):
        """Export all data from the pedestals to CSV.

        Please note this will only export the data, not the information regarding the pedestals.
        This function also assumes filename is in the correct format.
        It will override any existing file.

        Args:
            board (Board): A board object with the pedestals data attached to it.
            filename (path): Filename for the csv file.
        """
        get_csv_writer(self.params).export_pedestals_csv(board, filename, pedestals)


def save_calibration_data(board, filename):
    """Save calibration data from the board object.

    Args:
        board: good ol' Board object
        filename: filepath and filename
    """
    caldata = getattr(board, "caldata", None)

    if not isinstance(caldata, dict):
        raise TypeError(f"pedestals must be a dict, got {type(caldata)}")
    if filename is None:
        raise TypeError("Supplied pathname is NoneType.")
    path, _ = os.path.split(filename)
    if not os.path.isdir(path):
        raise NotADirectoryError(f"Not a valid directory: {path}")

    try:
        sfile = gzip.GzipFile(filename, "w", compresslevel=4)
        pickle.dump(caldata, sfile, protocol=pickle.HIGHEST_PROTOCOL)
    except IOError as error_msg:
        LOGGER.error("File could not be created. %s", error_msg)
    except pickle.PicklingError as error_msg:
        LOGGER.error("Saving pedestals failed: %s", error_msg)


def load_calibration_data(filename):
    """Load calibration data.

    Args:
        filename: the path to the file containing calibration data

    Returns:
        caldata dictionary.
    """
    if not os.path.isfile(filename):
        raise FileNotFoundError(f"No file found: {filename}")

    try:
        sfile = gzip.GzipFile(filename, "r")
        outped = pickle.load(sfile)
    except EOFError as error_msg:
        LOGGER.error("Reached the end of the file, msg: %s", error_msg)
    except IOError as error_msg:
        LOGGER.error("File could not be loaded. %s", error_msg)
    except pickle.UnpicklingError as error_msg:
        LOGGER.error("Loading data failed: %s", error_msg)
    else:
        if not isinstance(outped, dict):
            raise TypeError(f"Not a valid Calibration file: {filename}")

        return outped


def save_timingcal_data(board, filename):
    """Save timing calibration data from the board object.

    Args:
        board: good ol' Board object
        filename: filepath and filename

    Raises:
        TypeError if
        NotADirectoryError if the filename is not in a valid path
    """
    caldata = getattr(board, "timingcal", None)
    if caldata is None:
        raise TypeError(f"Timingcal data is not valid, got {type(caldata)}")

    if filename is None:
        raise TypeError("Supplied pathname is NoneType.")
    path, _ = os.path.split(filename)
    if not os.path.isdir(path):
        raise NotADirectoryError(f"Not a valid directory: {path}")

    try:
        sfile = gzip.GzipFile(filename, "w", compresslevel=4)
        pickle.dump(caldata, sfile, protocol=pickle.HIGHEST_PROTOCOL)
    except IOError as error_msg:
        LOGGER.error("File could not be created. %s", error_msg)
    except pickle.PicklingError as error_msg:
        LOGGER.error("Saving pedestals failed: %s", error_msg)


def load_timingcal_data(filename):
    """Load timing calibration data.

    Args:
        filename: the path to the file containing timing calibration data

    Returns:
        timingcal data

    Raises:
        FileNotFoundError if filename is not a file.
    """
    if not os.path.isfile(filename):
        raise FileNotFoundError(f"No file found: {filename}")

    try:
        sfile = gzip.GzipFile(filename, "r")
        output = pickle.load(sfile)
    except EOFError as error_msg:
        LOGGER.error("Reached the end of the file, msg: %s", error_msg)
    except IOError as error_msg:
        LOGGER.error("File could not be loaded. %s", error_msg)
    except pickle.UnpicklingError as error_msg:
        LOGGER.error("Loading data failed: %s", error_msg)
    else:
        return output


def save_gzip_data(filename, data):
    """Save data to a gzip pickled file.

    Args:
        filename: filepath and filename
        data: python data to save

    Raises:
        TypeError if
        NotADirectoryError if the filename is not in a valid path
    """
    if data is None:
        raise TypeError(f"isel is not valid, got {type(data)}")

    if filename is None:
        raise TypeError("Supplied pathname is NoneType.")
    path, _ = os.path.split(filename)
    if not os.path.isdir(path):
        raise NotADirectoryError(f"Not a valid directory: {path}")

    try:
        sfile = gzip.GzipFile(filename, "w", compresslevel=4)
        pickle.dump(data, sfile, protocol=pickle.HIGHEST_PROTOCOL)
    except IOError as error_msg:
        LOGGER.error("File could not be created. %s", error_msg)
    except pickle.PicklingError as error_msg:
        LOGGER.error("Saving data failed: %s", error_msg)


def load_clockfile(filename):
    """Turns a .txt file into a list, used for clock file loading.

    Returns:
        list of the loaded clock commands.

    Raises:
        FileNotFoundError if filename is not a valid text file.
        Error ifr loadtxt function fails for an unknown reason (The numpy function is fragile).
        TypeError if clock data type is not a str
        InvalidClockFileError if the clock data format is incorrect
    """
    if not os.path.exists(filename) or not os.path.split(filename)[-1].endswith(".txt"):
        raise FileNotFoundError(
            f"File {filename} does not exist. Please provide the path to a valid clockfile."
        )

    try:
        data = np.loadtxt(filename, dtype=str, delimiter=",")
    except Exception:
        raise
    validate_clock_data_or_raise(data)
    return data


def validate_clock_data_or_raise(clock_data):
    header = ["Address", "Data"]
    try:
        if not np.array_equal(clock_data[0], header):
            raise
    except:
        raise InvalidClockFileError(
            "Invalid clock data header, expected: 'Address', 'Data'"
        )
    for line, value in enumerate(clock_data[1:]):
        try:
            val_addr = re.fullmatch("0x[a-fA-F0-9]{4}", value[0])
            val_data = re.fullmatch("0x[a-fA-F0-9]{2}", value[1])
        except TypeError:
            raise TypeError(
                f"Clock data on line {line + 1} is of the wrong type, got address type {type(value[0])} and data type {type(value[1])}"
            )
        except (IndexError, KeyError):
            raise InvalidClockFileError(
                f"Clock data on line {line + 1} is of incorrect length or type"
            )
        if not val_addr or not val_data:
            raise InvalidClockFileError(
                f"Invalid clock data on line {line+1}: addr={value[0]}, data={value[1]}"
            )
