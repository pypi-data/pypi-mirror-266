import os
import json
import shutil
import platform
import pandas as pd
import tomli
from datetime import datetime, timedelta
from pathlib import Path


def initCowBase_farm(rootdir):
    """
    Initializes the folder structure in which the CowBase package will be mainly operating.

    Parameters
    ----------
    rootdir : str
        Root directory in which the CowBase folder structure should be implemented in.

    Notes
    ----------
    A number of folders and files is created when initializing:
    1. CowBase - parent directory
    2. CowBase/INPUT - folder in which the AMS (automatic milking system) backup files (.bak.zip/.zip) should be saved
    3. CowBase/INPUT/d_farmname - Backups from DeLaval systems should always be saved in folders starting with 'd_' and followed by the farmname
    4. CowBase/INPUT/l_farmname - Backups from Lely systems should always be saved in folders starting with 'l_' and followed by the farmname
    5. CowBase/OUTPUT - folder in which the unpacked data files (.csv) will be later saved
    6. CowBase/temp - folder in which temparary files are stored
    7. CowBase/config - folder in which a user config file and dictionaries are stored

    """

    rootdir = Path(rootdir)

    # initialize folder structure
    rootdir_cowbase = rootdir / "CowBase"
    rootdir_cowbase.mkdir(exist_ok=True, parents=True)

    rootdir_OUTPUT = rootdir_cowbase / "OUTPUT"
    rootdir_OUTPUT.mkdir(exist_ok=True)

    rootdir_config = rootdir_cowbase / "config"
    rootdir_config.mkdir(exist_ok=True)

    # add config and tableDict to the config folder for individual settings
    for config_file in (Path(__file__).parent / "utils").glob("*"):
        # If the config file is already in dir, don't copy again
        if (rootdir_config / config_file.name).exists():
            continue

        shutil.copy(
            config_file,
            rootdir_config / config_file.name,
        )

    # set the rootdir in the config file to the defined rootdir
    # TODO: if the config file has already been edited, don't overwrite
    osname = os.name
    fin = open((Path(__file__).parent / "utils" / "config.toml"), "rt")
    fout = open(f"{rootdir_config / 'config.toml'}", "wt")
    for line in fin:
        # read replace the string and write to output file
        if osname == "nt":
            hostname = platform.node()
            fout.write(
                line.replace("SERVERNAME", f"{hostname}\SQLEXPRESS").replace(
                    "rootdir_cowbase", str(rootdir_cowbase)
                )
            )
        elif osname == "posix":
            fout.write(
                line.replace("SERVERNAME", "localhost").replace(
                    "rootdir_cowbase", str(rootdir_cowbase)
                )
            )
    # close input and output files
    fin.close()
    fout.close()
    dtransfer_summary = pd.DataFrame(
        {
            "timestamp": ["20230101000000"],
            "OID": [1],
            "OID2": [1],
            "issaved": [1],
            "issend": [1],
            "isdel": [1],
        }
    )
    dtransfer_summary.to_csv(rootdir_config / "cb_data_summary.csv", index=False)


def farmExtract(
    filepath_config="/var/lib/CowBase/config/config_farm.toml",
    filepath_tdict="/var/lib/CowBase/config/M2_tableDict.json",
):
    """
    Extracts data tables from restored MSQL database

    Parameters
    ----------
    tabledict : dict
        dictonary that contains all table and column names from the respective milking system that should be extracted
    table : str
        tablename of the table that should be restored
    robottype : str
        brand of milking system the backup is from (d-DeLaval; l-Lely)
    dbname : str
        name of the database
    filename_out : str
        filepath and name to which the extracted data will be saved to
    config : dict
        config file with user settings

    """
    with open(filepath_config, mode="rb") as ctomli:
        config = tomli.load(ctomli)
    with open(filepath_tdict) as file:
        tabledict = json.load(file)

    dtransfer_summary = pd.read_csv(
        config["user"]["rootdir"] / "config" / "cb_data_summary.csv"
    )
    lastoid = dtransfer_summary.OID.max()
    timenow = datetime.now().strftime("%Y%m%d%H%M")
    timebackups = (datetime.now() + timedelta(days=-1)).strftime("(%Y-%m-%d)")

    # initialize folder structure
    rootdir_OUTPUT = config["user"]["rootdir"] / "OUTPUT"
    rootdir_OUTPUT2 = rootdir_OUTPUT / "01_full_table"
    rootdir_OUTPUT2.mkdir(exist_ok=True)
    rootdir_filedest = rootdir_OUTPUT2 / timenow
    rootdir_filedest.mkdir(exist_ok=True)

    for table in tabledict[config["user"]["robottype"]]:
        if tabledict[config["user"]["robottype"]][table]["extracttype"][0] == "full":
            filename_out = (
                rootdir_filedest
                / f'{config["user"]["robottype"]}_{config["user"]["farmname"]}_{timenow}_{table}.csv'
            )
            columnnames = ", ".join(
                tabledict[config["user"]["robottype"]][table]["columns"]
            )
            # export table
            sql = f'SELECT {columnnames} FROM {config["user"]["dbname"]}.dbo.{table}'
        elif (
            tabledict[config["user"]["robottype"]][table]["extracttype"][0]
            == "datetime"
        ):
            filename_out = (
                rootdir_filedest
                / f'{config["user"]["robottype"]}_{config["user"]["farmname"]}_{timenow}_{table}.csv'
            )
            columnnames = ", ".join(
                tabledict[config["user"]["robottype"]][table]["columns"]
            )
            # export table
            sql = f'SELECT {columnnames} FROM {config["user"]["dbname"]}.dbo.{table} WHERE {tabledict[config["user"]["robottype"]][table]["restrictID"][0]} > {timebackups}'
        elif tabledict[config["user"]["robottype"]][table]["extracttype"][0] == "moid":
            filename_out = (
                rootdir_filedest
                / f'{config["user"]["robottype"]}_{config["user"]["farmname"]}_{timenow}_{table}.csv'
            )
            columnnames = ", ".join(
                tabledict[config["user"]["robottype"]][table]["columns"]
            )
            # export table
            sql = f'SELECT {columnnames} FROM {config["user"]["dbname"]}.dbo.{table} WHERE OID > {lastoid}'
        cmd = (
            'bcp "'
            + sql
            + f'" queryout {filename_out} -d{config["user"]["dbname"]} -c -C 65001 -t"^^" -m 9999  -b 10000 -a 10000 -k -T'
        )
        os.system(cmd)

        try:
            datatable = pd.read_csv(
                filename_out, header=None, delimiter="\^\^", engine="python"
            )
            datatable = datatable.replace({";": ","}, regex=True)
            datatable.to_csv(
                filename_out,
                header=list(tabledict[config["user"]["robottype"]][table]["columns"]),
                index=False,
                sep=";",
                escapechar="\\",
            )
        except pd.errors.EmptyDataError:
            print(f"Skipped! No data available for {table}!")

        if table == "VoluntarySessionMilkYield":
            # Select largest OID from VoluntarySessionMilkYield table
            try:
                df_vsmy = pd.read_csv(filename_out, delimiter=";")
                newoid = df_vsmy.OID.max()
            except pd.errors.EmptyDataError:
                newoid = lastoid

    dtransfer_newentry = pd.DataFrame(
        {
            "timestamp": [timenow],
            "OID": [lastoid],
            "OID2": [newoid],
            "issaved": [1],
            "issend": [0],
            "isdel": [0],
        }
    )

    dtransfer_summary = pd.concat(
        [dtransfer_summary, dtransfer_newentry], ignore_index=True
    )

    dtransfer_summary.to_csv(
        config["user"]["rootdir"] / "config" / "cb_data_summary.csv",
        index=False,
    )


# TODO: add a function for file transfer
def cb_filetransfer():
    """
    Function to handle the data transfer between the farm PC and a research server where the data should be send to
    (ftp, https, ...?)
    """
