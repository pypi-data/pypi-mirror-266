"""Define utility methods to read from and write to various filetypes.
"""
from __future__ import annotations

import copy
import csv
import json
import logging
import pickle
import shutil
from collections import defaultdict
from datetime import datetime
from itertools import zip_longest
from pathlib import Path
from typing import Any, MutableSequence
from xml.etree import ElementTree as eTree

import blosc
import numpy
import yaml

from utilities import dictutils, listutils, pathutils

logger = logging.getLogger(__name__)

READFILE_EXTENSIONS = [".csv", ".dat", ".json", ".yaml", ".yml"]


def combine_json_files(filepaths: list[Path], *, saveto: Path) -> None:
    """Takes in a list of filepaths, assumed to be all type json, and combines them into a
    single json file at the specified filepath.
    """
    suffixes = list(set([f.suffix.lower() for f in filepaths]))

    if not all([confirm_filetype(f, "json") for f in filepaths]):
        raise ValueError(
            f"All filepaths must be of type JSON. Received the following file "
            f"extensions: {suffixes}."
        )

    if not confirm_filetype(saveto, "json"):
        raise ValueError(
            f"Parameter <<savetojson>> must have extension 'json'. Received:"
            f" {saveto}."
        )

    savetoparent = filepaths[0].parent

    if not savetoparent.is_dir():
        logger.info(f"Directory {savetoparent} does not exist. Creating it.")
        savetoparent.mkdir(parents=True, exist_ok=True)

    data = {}
    for f in filepaths:
        if f.is_file():
            filedata = readfile(f)
            if filedata:
                data.update(filedata)
            else:
                logger.warning(f"File {f} has no data. Nothing to do.")
        else:
            logger.warning(f"File {f} does not exist. Skipping it.")
            continue

    writefile(saveto, data=data)


def confirm_filetype(filepath: Path, extension: str) -> bool:
    """Return boolean True if the given filepath has the specified extension.
    """
    if not extension.startswith("."):
        extension = f".{extension}"
    suffix = filepath.suffix
    return suffix.lower() == extension.lower()


def convert_types_for_json(
    seq: MutableSequence, i: int = 0, *, persist: bool = False
) -> MutableSequence | None:
    """Recursively scan the given sequence and convert numpy.ndarray to list and
    datetime.datetime to str. If optional "persists" is True, this method modifies the given
    sequence in place, and if False, it returns a new sequence without modifying the given
    sequence.

    :param seq: any MutableSequence
    :param i: recursion level
    :param persist: True to return a new sequence, False to modify in place
    :return:
    """
    if persist:
        working_seq = copy.deepcopy(seq)
    else:
        working_seq = seq

    if isinstance(working_seq, dict):
        for k, v in working_seq.items():
            if isinstance(v, numpy.ndarray):
                working_seq[k] = v.tolist()
            elif isinstance(v, datetime):
                working_seq[k] = v.isoformat()
            elif isinstance(v, MutableSequence):
                convert_types_for_json(v, i=i + 1)  # recursive call
    else:
        for item in seq:
            if isinstance(item, numpy.ndarray):
                index = working_seq.index(item)
                working_seq[index] = item.tolist()
            elif isinstance(item, datetime):
                index = working_seq.index(item)
                working_seq[index] = item.isoformat()
            elif isinstance(item, MutableSequence):
                convert_types_for_json(seq, i=i + 1)  # recursive call

        if working_seq is seq:
            return
        else:
            return working_seq


def create_backup_file(filepath: Path) -> None:
    """Create a backup of the given file, appending a datestamp to the filename."""
    if not filepath.exists():
        logger.warning(f"{filepath} does not exist. Nothing to do.")
        return

    today = datetime.today().strftime("%Y-%m-%d-%H-%M-%S")
    fileparent = filepath.parent
    filestem = filepath.stem
    filesuffix = filepath.suffix
    newfilename = f"{today}-{filestem}{filesuffix}"
    newfilepath = f"{fileparent}/{newfilename}"

    try:
        shutil.copy2(filepath, newfilepath)
    except FileNotFoundError:
        logger.warning(
            f"Error copying source {filepath} to destination {newfilepath}: {filepath} "
            f"does not exist. Nothing to do."
        )
        return

    logger.info(f"{filepath} copied to {newfilepath}.")


def __handle_csv(
    filepath: Path,
    *,
    as_rows: bool,
    data: dict | defaultdict | list,
    exclude_keys: list,
    header_row: list[Any] = None,
    include_keys: bool,
    max_rows: int,
    mode: str,
    use_legacy: bool = False,
) -> None:
    """Call the appropriate method to write data to a CSV file. If use_legacy is True,
    only data, max_rows, and mode are relevant-- all other keys are ignored.
    """
    if use_legacy:
        write_csvfile_from_dicts_legacy(
            filepath, data=data, max_rows=max_rows, mode=mode
        )

    if type(data) in [dict, defaultdict]:
        if as_rows:
            write_csvfile_d2r(
                filepath,
                data=data,
                exclude_keys=exclude_keys,
                header_row=header_row,
                include_keys=include_keys,
                mode=mode,
            )
        else:
            write_csvfile_d2c(filepath, data=data, exclude_keys=exclude_keys, mode=mode)
    elif type(data) is list:
        write_csvfile_l2rc(
            filepath, as_rows=as_rows, data=data, header_row=header_row, mode=mode
        )


def read_csvfile(filepath: Path, delimiter: str = ",") -> list[list]:
    """Takes in a filepath and loads the data in the CSV file into a list of lists, with one outer
    list for each row of the file. Each inner list contains the individual data elements for a
    particular row.
    """
    with open(filepath, "r", newline="\n") as f:
        lines = f.readlines()

    return [line.strip().split(delimiter) for line in lines]


def read_datfile(filepath: Path) -> dict:
    """Takes in filepath and loads the data in the DAT file into a dictionary. It is assumed the
    DAT file is blosc-compressed pickle of a Python dictionary object.
    """
    with open(filepath, "rb") as f:
        try:
            data = pickle.loads(blosc.decompress(f.read()))
        except EOFError as e:  # no other blosc exception?
            logger.warning(
                f"Could not load cached data from {filepath}: {e.__str__()}. "
                f"Returning empty dictionary."
            )
            data = {}

    return data


def readfile(filepath: Path) -> list | dict | None:
    """Takes in a Path instance, calls the appropriate read method based on the filename
    extension, and returns the content of the file.
    """
    if not filepath.is_file():
        logger.warning(f"{filepath} does not exist. Nothing to do.")
        return

    if filepath.suffix in READFILE_EXTENSIONS:
        return {
            ".csv": read_csvfile,
            ".dat": read_datfile,
            ".json": read_jsonfile,
            ".yaml": read_yamlfile,
            ".yml": read_yamlfile,
        }[filepath.suffix](filepath)
    else:
        raise ValueError(
            f"Parameter <<filepath>> must have one of the following extensions: "
            f"{listutils.get_string(READFILE_EXTENSIONS)}. Received: {filepath}."
        )


def read_jsonfile(filepath: Path) -> list | dict:
    """Takes in a Path instance and loads the data in the file into either a list or dictionary.
    """
    with open(filepath, "r") as f:
        try:
            data = json.load(f)
        except json.decoder.JSONDecodeError as e:
            err_msg = f"Could not read file {filepath}."
            raise json.decoder.JSONDecodeError(err_msg, str(filepath), 0) from e
    return data


def read_yamlfile(filepath: Path) -> list | dict:
    """Takes in a Path instance and loads the data in the file into either a list or dictionary.
    """
    with open(filepath, "r") as f:
        data = yaml.safe_load(f)

    return data


def set_mode(filepath: Path) -> str:
    """Set the mode flag based on the incoming filepath. If the file exists, mode is set to
    <<a>>. If it does not exist, mode is set to <<w>>.
    """
    return {True: "a", False: "w"}[filepath.is_file()]


def write_csvfile_from_dicts_legacy(
    filepath: Path,
    *,
    data: dict,
    exclude_keys: list = None,
    max_rows: int = None,
    mode: str = "w",
) -> None:
    """
    WARNING: This is a legacy method that will be removed by 2025-01-01.

    Write the given data dictionary to one or more CSV files. Each k-v pair of the data
    dictionary represents one row of data, and v is itself a dictionary for which the keys
    correspond to the column headers. It is assumed that all such dictionaries have the same
    key-set.

    NOTES:
        1. The values in data must all be of the same type, either dict or list. If all are of type
            list, this method calls write_csvfile_lists. If values are not all dict or list,
            nothing will be written to disk.

        2. If max rows is given, write this many rows (including the header) in a csv file,
            and create as many csv files as necessary to write the entire data dictionary. A
            positive-integer suffix (starting with 1) is added to each filename based on the given
            filepath.

        3. Any key names provided in optional parameter <<exclude_keys>> will be ignored.
    """
    if not data:
        return

    data_value_types = list(set([type(v) for v in data.values()]))

    if all([dvt is list for dvt in data_value_types]):
        return write_csvfile_d2r(
            filepath, data=data, mode=mode, exclude_keys=exclude_keys
        )
    elif not all([dvt is dict for dvt in data_value_types]):
        logger.warning(
            f"All values in parameter <<data>> must be of type dict. Received types "
            f"{data_value_types}. Data WAS NOT WRITTEN to disk."
        )
        return

    def _write_csvdata(
        data: dict, filepath: Path, mode: str, exclude_keys: list[str] = None
    ):
        exclude_keys = [] if exclude_keys is None else exclude_keys

        with open(filepath, mode, newline="") as f:
            # Get the column names from the first row of the data map--- we assume all rows have the
            # same keys--- but only if mode == "w". If writing in append mode, assume that we
            # already have the header row.

            column_names = [k for k in list(data.values())[0] if k not in exclude_keys]
            writer = csv.DictWriter(f, column_names)

            if mode == "w":
                writer.writeheader()

            for row_key, row_data in data.items():
                row = {}
                for col_name in column_names:
                    try:
                        row[col_name] = row_data[col_name]
                    except KeyError:
                        logger.warning(
                            f"Column name missing from row data: {col_name}."
                        )
                        row[col_name] = "missing"
                writer.writerow(row)

    if max_rows is not None:
        if not isinstance(max_rows, int) or max_rows < 2:
            raise ValueError(
                f"Parameter <<max_rows>> must be a positive integer >= 2. "
                f"Received {max_rows}."
            )

    data = dictutils.get_pure_dict(data)
    exclude_keys = [] if exclude_keys is None else exclude_keys
    working_filepath = Path(copy.deepcopy(filepath))

    if max_rows:
        filecounter = 1
        for subdata in dictutils.get_smaller_dicts(data, max_keys=max_rows):
            _write_csvdata(subdata, working_filepath, mode)
            filecounter += 1
            working_filepath = pathutils.add_suffix_to_path(
                path=filepath, suffix=str(filecounter)
            )
    else:
        _write_csvdata(data, working_filepath, mode, exclude_keys)


def write_csvfile_d2c(
    filepath: Path,
    *,
    data: dict[str : list[float]] | defaultdict[str : list[float]],
    exclude_keys: list[Any] = None,
    mode: str = "w",
) -> None:
    """Write the given data to a CSV file. Assume the given data represents columns in the CSV
    file, with each key being the column header and each value being the data in that column. If
    optional exclude_keys is provided, those keys will be ignored when parsing data.

    :param filepath: where the CSV file will be written
    :param data: the data to write to the CSV file
    :param mode: python write mode; default is "w"
    :param exclude_keys: optional; keys in this list will be ignored
    :return:
    """
    data = dictutils.get_pure_dict(data)
    if exclude_keys is None:
        exclude_keys = []
    column_names = [k for k in list(data.keys()) if k not in exclude_keys]
    column_lists = [v for k, v in data.items() if k not in exclude_keys]
    rows = zip_longest(*column_lists, fillvalue="")

    with open(filepath, mode, newline="") as f:
        writer = csv.writer(f)
        writer.writerow(column_names)
        for row in rows:
            writer.writerow(row)


def write_csvfile_d2r(
    filepath: Path,
    *,
    data: dict[str : list[float]] | defaultdict[str : list[float]],
    exclude_keys: list[str] = None,
    header_row: list[Any] = None,
    include_keys: bool = False,
    mode: str = "w",
) -> None:
    """Write the given data to a CSV file. Assume that each kv-pair in data represents one row
    of data. If include_keys is True, the key in each kv-pair will be included as the first
    element on the row. The value in each pair will comprise the (remaining) elements on the row.
    If optional exclude_keys is given, those keys in data will be ignored.

    :param filepath: where the CSV file will be written
    :param data: the data to write to the CSV file
    :param exclude_keys: optional; ignore these keys in data
    :param header_row: optional; header row
    :param include_keys: optional; if True, include the key as the first element on a row
    :param mode: python write mode; default is "w"
    :return:
    """
    data = dictutils.get_pure_dict(data)

    if exclude_keys is None:
        exclude_keys = []
    data_rows = []

    for key, values in data.items():
        if key in exclude_keys:
            continue
        this_row = []
        if include_keys:
            this_row.append(key)
        this_row.extend(values)
        data_rows.append(this_row)

    with open(filepath, mode, newline="") as f:
        writer = csv.writer(f)
        if header_row:
            writer.writerow(header_row)
        for row in data_rows:
            writer.writerow(row)


def write_csvfile_l2rc(
    filepath: Path,
    *,
    as_rows: bool = True,
    data: list[list[float]],
    header_row: list[Any] = None,
    mode: str = "w",
) -> None:
    """Write the given data to a CSV file. If as_rows is True, assume each list in data represents
    one row, and if False assume each list in data represents one column. If provided, include the
    optional header_row as the first line of the CSV file.

    :param filepath: where the CSV file will be written
    :param as_rows: if True assume data lists correspond to rows, otherwise columns
    :param data: the data to write to the CSV file
    :param mode: python write mode; default is "w"
    :param header_row: optional header row
    :return:
    """
    if as_rows:
        rows = data
    else:
        rows = zip_longest(*data, fillvalue="")

    with open(filepath, mode, newline="") as f:
        writer = csv.writer(f)
        if header_row:
            writer.writerow(header_row)
        for row in rows:
            writer.writerow(row)


def write_datfile(filepath: Path, *, data: dict) -> None:
    """Takes in a filepath and a data dictionary, blosc-compresses a pickle of the data,
    and writes the compressed pickle to disk as a DAT file.
    """
    if filepath.is_file():
        current = readfile(filepath)
        data.update(current)

    with open(filepath, "wb") as f:
        f.write(blosc.compress(pickle.dumps(data)))


def writefile(
    filepath: Path,
    *,
    as_rows: bool = True,
    data: dict | defaultdict | list,
    exclude_keys: list[Any] = None,
    header_row: list[Any] = None,
    include_keys: bool = False,
    max_rows: int = None,
    mode: str = "w",
    root: eTree.Element = None,
) -> None:
    """Takes in a stringutils or Path instance filepath, a data dictionary or list, and one or
    more optional parameters, and calls the appropriate write method based on the filepath
    extension.

    NOTES:

        (1) If the filepath extension is ".csv":

            (a) If parameter <<as_lists>> is False, parameter <<exclude_keys>> is ignored.
            (b) If parameter <<as_rows>> is False, parameter <<col_indexes>> is ignored.

        (2) If the filepath extension is NOT ".csv", parameters <<as_lists>>, <<as_rows>>,
            <<exclude_keys>>, and <<col_indexes>> are ignored.
        (3) If the filepath extension is ".dat", parameter <<data>> must be of type <<dict>>.
        (4) If the filepath extension is ".dat" OR ".xml", parameter <<mode>> is ignored.
        (5) If the filepath extension is ".xml", parameter <<root>> is required.
        (6) If the filepath extension is NOT ".xml", parameter <<root>> is ignored.
    """
    suffix = filepath.suffix

    if suffix == ".csv":
        __handle_csv(
            filepath,
            as_rows=as_rows,
            data=data,
            exclude_keys=exclude_keys,
            header_row=header_row,
            include_keys=include_keys,
            max_rows=max_rows,
            mode=mode,
        )
    elif filepath.suffix == ".dat":
        write_datfile(filepath, data=data)
    elif filepath.suffix == ".json":
        write_jsonfile(filepath, data=data, mode=mode)
    elif filepath.suffix in [".yaml", "yml"]:
        write_yamlfile(filepath, data=data, mode=mode)
    elif filepath.suffix == ".xml":
        write_xmlfile(filepath, root=root)
    else:
        logger.warning(
            f"Parameter <<max_rows>> must be a positive integer >= 2. Received "
            f"{max_rows}. Data WAS NOT WRITTEN to disk."
        )
        return

    logger.info(f"Data written to file: {filepath.name}.")


def write_jsonfile(filepath: Path, *, data: dict | list, mode: str = "w") -> None:
    """Takes in Path instance, a data dictionary or list, optional mode
    dictionary or listutils to the specified pathutils in JSON format. If appending, the incoming
    data must be of the same type as that extracted from the given filepath. If it is not,
    this method raises ValueError.
    """
    if mode == "a":
        try:
            existing_data = read_jsonfile(filepath)
        except FileNotFoundError:
            logger.warning(f"Filepath {filepath} not found.")
            pass
        else:
            if type(data) != type(existing_data):
                logger.warning(
                    f"Cannot merge data objects of different types. "
                    f"Received {type(data)} with append mode, but existing data is "
                    f"of type {type(existing_data)}. Data WAS NOT WRITTEN to disk."
                )
                return

            if isinstance(existing_data, list):
                data += existing_data
            elif isinstance(existing_data, dict):
                data = {**existing_data, **data}

    convert_types_for_json(data)

    with open(filepath, "w") as f:
        json.dump(data, f)


def write_xmlfile(filepath: Path, *, root: eTree.Element) -> None:
    """Takes in a stringutils or Path instance filepath and an eTree.Element object, which should
    be the root of an eTree.ElementTree object, and coerces it and its children into
    nicely-formatted XML and writes the data to file.

    NOTE: Relies on an internally-defined recursive method.

    See: https://stackoverflow.com/a/65808327
    """

    def _format_xml(
        element: eTree.Element,
        parent: eTree.Element = None,
        index: int = -1,
        depth: int = 0,
    ) -> None:
        """Format the incoming element and its children into nicely-formatted XML. Recursive.
        """
        for i, node in enumerate(element):
            _format_xml(node, element, i, depth + 1)  # Recursive call.

        if parent is not None:
            if index == 0:
                parent.text = "\n" + ("\t" * depth)
            else:
                parent[index - 1].tail = "\n" + ("\t" * depth)

            if index == len(parent) - 1:
                element.tail = "\n" + ("\t" * (depth - 1))

    _format_xml(root)
    tree = eTree.ElementTree(root)
    tree.write(filepath)


def write_yamlfile(filepath: Path, *, data: dict | list, mode: str = "w") -> None:
    """Takes in a data dictionary or listutils, a stringutils or Path instance, and an optional
    boolean flag and writes the data dictionary or list to the specified path in YAML
    format. If appending, the incoming data must be of the same type as that extracted from the
    given filepath. If it is not, this method raises ValueError.
    """
    if mode == "a":
        try:
            existing_data = read_yamlfile(filepath)
        except FileNotFoundError:
            logger.warning(
                f"Append mode is {mode}, but {filepath} was not found. Data WAS NOT "
                f"WRITTEN to disk."
            )
            return
        else:
            if type(data) != type(existing_data):
                logger.warning(
                    f"Cannot merge data objects of different types. Received"
                    f" {type(data)} "
                    f"with append mode, but existing data is of type {type(existing_data)}. Data "
                    f"WAS NOT WRITTEN to disk."
                )
                return

            if isinstance(existing_data, list):
                data += existing_data
            elif isinstance(existing_data, dict):
                data = {**existing_data, **data}

    with open(filepath, "w") as f:
        yaml.dump(data, f)
