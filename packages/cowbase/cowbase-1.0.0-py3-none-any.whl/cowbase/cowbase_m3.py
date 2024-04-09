import json
import os
import re
from pathlib import Path

import pandas as pd


def mergeTables_single(rootdir: str | Path, farmname: str, newtable: str) -> None:
    """
    Merge original tables; create tables with new database scheme

    Parameters
    ----------
    rootdir : str or Path
        Filepath to CowBase root directory (e.g. linux: '/var/lib/'; windows: 'C:\\Users\\user\\Documents\\')
    farmname : str
        name of farm to analyze (e.g., 'd_farmname')
    newtable : str
        name of the table to merge
    """

    rootdir = Path(rootdir)
    farmtype = farmname.split("_")[0]

    # Read in all necessary setting files and dictionaries
    with open(rootdir / "config" / "M3_tableDict.json") as file:
        config_json = json.load(file)
        infodict1 = config_json[farmtype]
        infodict2 = config_json["d_37"]
    if newtable not in list(infodict1.keys()):
        print(f"Table {newtable} is not available for farming system {farmtype}!")
        return

    # Initiate savepath
    backupdates = []
    df_data = pd.DataFrame({})
    filepath = rootdir / "OUTPUT" / farmname / "01_full_table"
    savepath = rootdir / "OUTPUT" / farmname / "02_merged_table"
    savepath.mkdir(parents=True, exist_ok=True)

    # Iterate over all backups, read data for each folder (with correct version dictionary) and merge temporal
    for folders in os.listdir(filepath):
        infodict = infodict2 if folders[-3:] == "_37" else infodict1
        df_data_add = pd.DataFrame({})
        df_data_add, savefilename_new, backupdates = readAndMerge(
            infodict, newtable, backupdates, filepath, folders
        )

        if savefilename_new == None:
            continue
        else:
            savefilename = savefilename_new
            df_data_add = df_data_add[infodict[newtable]["rename"].keys()]
            df_data_add.rename(columns=infodict[newtable]["rename"], inplace=True)
            df_data = pd.concat([df_data, df_data_add], ignore_index=True)
            df_data = df_data.drop_duplicates(
                subset=infodict[newtable]["drop_duplicates"], keep="last"
            )
    if df_data.empty == False:
        if newtable == "milking" and (farmtype == "d" or farmtype == "d_37"):
            df_data = calculatingMilkDeLaval(df_data)
        elif newtable == "milking" and farmtype == "l":
            df_data = calculatingMilkLely(df_data)
        df_data.to_csv(savepath / savefilename, sep=";", index=False)


def readAndMerge(
    infodict: dict,
    newtable: str,
    backupdates: list,
    filepath: str | Path,
    folders: str | Path,
) -> tuple[pd.DataFrame, Path | None, list]:
    """
    For a single table, iterate over all files in the folder. If there is data available, read and return

    Parameters
    ----------
    infodict : dict
        Dictionary containing single original tables and columns to open and merge
    newtable : str
        name of the table to merge
    backupdates : list
        list of all backupdates
    filepath : str or Path
        filepath to the dictionary containing backups of a single farm
    folders : str or Path
        name of the folder to run in

    Return
    ------
    df_data_add : dataframe
        dataframe containing data of a single new database table of a single backup
    savefilename : Path
        name to save complete files
    backupdates : list
        list of all backupdates
    """

    # Iterate over all separate raw tables that are needed to create a new database table
    for tables in list(infodict[newtable]["data"].keys()):
        table_available = False
        for files in os.listdir(filepath / folders):
            tablename = re.split("_", files[:-4])[-1]
            if tablename == tables:
                table_available = True
                splitstr = re.split("_", files)
                backupdate = int(re.split("_", files[:-4])[2])
                backupdates.append(backupdate)
                savefilename = f"{splitstr[0]}_{splitstr[1]}_{min(backupdates)}_{max(backupdates)}_{newtable}.csv"

                # load data for table and select for certain columns given in the tabledict
                df_data_file = pd.read_csv(
                    filepath / folders / files,
                    delimiter=";",
                    header=0,
                    engine="c",
                )
        if table_available == False:
            print(f"Skipped {newtable}! Data is not available!")
            return pd.DataFrame({}), None, backupdates
        if "on" in list(infodict[newtable]["data"][tables].keys()):
            if "prerename" in list(infodict[newtable]["data"][tables].keys()):
                df_data_file.rename(
                    columns=infodict[newtable]["data"][tables]["prerename"],
                    inplace=True,
                )
            df_data_add = df_data_add.merge(
                df_data_file,
                on=infodict[newtable]["data"][tables]["on"],
                how=infodict[newtable]["data"][tables]["how"],
            )

        else:
            df_data_add = df_data_file.copy()

    return df_data_add, savefilename, backupdates


def calculatingMilkDeLaval(df_data: pd.DataFrame) -> pd.DataFrame:
    """
    For DeLaval, the interval between previous milkings and current milkings are calculated

    Parameters
    ----------
    df_data : dataframe
        dataframe of milking data without milking interval

    Return
    ------
    df_data : dataframe
        dataframe of milking data with milking interval
    """

    df_data[["ended_at", "previously_ended_at"]] = df_data[
        ["ended_at", "previously_ended_at"]
    ].apply(pd.to_datetime)
    df_data.loc[
        ~pd.isnull(df_data.ended_at) & ~pd.isnull(df_data.previously_ended_at),
        "mi",
    ] = (
        (
            df_data.loc[
                ~pd.isnull(df_data.ended_at) & ~pd.isnull(df_data.previously_ended_at),
                "ended_at",
            ]
            - df_data.loc[
                ~pd.isnull(df_data.ended_at) & ~pd.isnull(df_data.previously_ended_at),
                "previously_ended_at",
            ]
        ).dt.total_seconds()
        / 3600
    ).round(
        decimals=2
    )
    return df_data


def calculatingMilkLely(df_data: pd.DataFrame) -> pd.DataFrame:
    """
    For Lely, the time of the previous milkings are calculated based on the milking interval and the current times
    Further the Electrical Conductivity is transformed from Lely units to S/m

    Parameters
    ----------
    df_data : dataframe
        dataframe of milking data without previous milkting time and EC

    Return
    ------
    df_data : dataframe
        dataframe of milking data with previous milkting time and EC
    """

    df_data[["ended_at"]] = df_data[["ended_at"]].apply(pd.to_datetime)
    df_data.mi = pd.to_timedelta(df_data.mi.astype(float), unit="s")
    df_data.loc[
        ~pd.isnull(df_data.ended_at) & ~pd.isnull(df_data.mi),
        "previously_ended_at",
    ] = (
        df_data.loc[
            ~pd.isnull(df_data.ended_at) & ~pd.isnull(df_data.mi),
            "ended_at",
        ]
        - df_data.loc[
            ~pd.isnull(df_data.ended_at) & ~pd.isnull(df_data.mi),
            "mi",
        ]
    )
    df_data["mi"] = ((df_data["mi"] / pd.to_timedelta(1, unit="D")) * 24).round(2)

    df_data["eclf"] = ((0.084 * df_data.eclf_lely) - 1).round(2)
    df_data["ecrf"] = ((0.084 * df_data.ecrf_lely) - 1).round(2)
    df_data["eclr"] = ((0.084 * df_data.eclr_lely) - 1).round(2)
    df_data["ecrr"] = ((0.084 * df_data.ecrr_lely) - 1).round(2)

    df_data.loc[df_data.eclf <= 0, "eclf"] = 0
    df_data.loc[df_data.ecrf <= 0, "ecrf"] = 0
    df_data.loc[df_data.eclr <= 0, "eclr"] = 0
    df_data.loc[df_data.ecrr <= 0, "ecrr"] = 0

    return df_data


def mergeTables_all(rootdir: str | Path, farmname: str) -> None:
    """
    Merge original tables; create tables with new database scheme

    Parameters
    ----------
    rootpath : str or Path
        Filepath to CowBase root directory (e.g. linux: '/var/lib/'; windows: 'C:\\Users\\user\\Documents\\')
    farmname : str
        name of farm to analyze (e.g., 'd_farmname')

    """

    rootdir = Path(rootdir)

    farmtype = farmname.split("_")[0]

    if farmtype == "d":
        tablelist = [
            "animal",
            "lactation",
            "milking",
            "herdnavigator",
            "insemination",
            "bcs",
            "cleaning",
        ]
    elif farmtype == "l":
        tablelist = ["animal", "lactation", "milking", "activity"]

    for tables in tablelist:
        mergeTables_single(rootdir, farmname, tables)
