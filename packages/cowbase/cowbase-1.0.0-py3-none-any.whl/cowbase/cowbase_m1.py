import json
import os
import platform
import re
import shutil
import zipfile
from datetime import datetime
from pathlib import Path

import pandas as pd
import tomli


def initCowBase(rootdir: str) -> None:
    """
    Initializes the folder structure in which the CowBase package will be mainly operating.

    Parameters
    ----------
    rootdir : str or Path
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

    rootdir_INPUT = rootdir_cowbase / "INPUT"
    rootdir_INPUT.mkdir(exist_ok=True, parents=True)

    rootdir_INPUT_dtest = rootdir_INPUT / "d_farmname"
    rootdir_INPUT_dtest.mkdir(exist_ok=True)

    rootdir_INPUT_ltest = rootdir_INPUT / "l_farmname"
    rootdir_INPUT_ltest.mkdir(exist_ok=True)

    rootdir_OUTPUT = rootdir_cowbase / "OUTPUT"
    rootdir_OUTPUT.mkdir(exist_ok=True)

    rootdir_temp = rootdir_cowbase / "temp"
    rootdir_temp.mkdir(exist_ok=True)

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


def extracttable(
    tabledict: dict,
    table: str,
    robottype: str,
    dbname: str,
    filename_out: str,
    config: dict,
) -> None:
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
    filename_out : str or Path
        filepath and name to which the extracted data will be saved to
    config : dict
        config file with user settings

    """

    osname = os.name
    columnnames = ", ".join(tabledict[robottype][table])
    # export table
    sql = f"SELECT {columnnames} FROM {dbname}.dbo.{table}"
    servername = config["user"]["servername"]
    if osname == "nt":
        cmd = f'bcp "{sql}" queryout {filename_out} -d{dbname} -c -C 65001 -t"^^" -m 9999  -b 10000 -a 10000 -k -T -S {servername}'
    elif osname == "posix":
        pwd = config["user"]["serverpwd"]
        cmd = f'bcp "{sql}" queryout {filename_out} -d {dbname} -c -u -C 65001 -t"^^" -m 9999  -b 10000 -a 10000 -k -U sa -P "{pwd}" -S {servername}'
    else:
        print(f"CowBase is not yet adapted to your operating system ({os.name}).")
        return

    os.system(cmd)
    try:
        # with open(filename_out, "rb") as source_file:
        #     with open(filename_out, "wb") as dest_file:
        #         contents = source_file.read()
        #         dest_file.write(contents.replace(b"\x00", b""))
        datatable = pd.read_csv(
            filename_out, header=None, delimiter="\^\^", engine="python"
        )
        datatable = datatable.replace({";": ","}, regex=True)
        datatable.to_csv(
            filename_out,
            header=tabledict[robottype][table],
            index=False,
            sep=";",
            escapechar="\\",
        )
    except pd.errors.EmptyDataError:
        os.remove(filename_out)
        print(f"File removed! No data available for {table}!")


def restoreDB_single(
    rootdir: str = "/var/lib/CowBase", farm: str = "d_farmname"
) -> None:
    """
    1. Restores MSQL database from backup-dump file (.bak)
    2. Calls extracttable() - extracts data tables defined in tabelDict.json (located in the config folder after initializing the pipeline)
    3. Drops the database and deletes temporary files

    Parameters
    ----------
    rootdir : str or Path
        Filepath to CowBase root directory
    farm : str
        Name of the single farm-directory for which data should be restored

    Note
    ----------
    Currently only backups from milking systems form DeLaval or Lely are supported.\n
    Further, currently only posix and windows nt based systems are supported.

    """
    rootdir = Path(rootdir)

    filepath_config = rootdir / "config" / "config.toml"
    filepath_tdict = rootdir / "config" / "M1_tableDict.json"
    with open(filepath_config, mode="rb") as ctomli:
        config = tomli.load(ctomli)
    osname = os.name

    # Specify the folder where the backups are placed and create a temp folder to temporary store the unzipped backups
    # as well as the OUTPUT folder where the extracted data gets stored
    with open(filepath_tdict) as file:
        tabledict = json.load(file)

    sql_template = rootdir / "config" / "M1_restoreDB.sql"
    config_user_rootdir = Path(config["user"]["rootdir"])

    rootdir_temp = config_user_rootdir / "temp"
    rootdir_temp.mkdir(exist_ok=True)

    rootdir_in = config_user_rootdir / "INPUT"
    rootdir_in.mkdir(exist_ok=True)

    rootdir_out = config_user_rootdir / "OUTPUT"
    rootdir_out.mkdir(exist_ok=True)

    # Check for backup files in folder farm and start extraction process
    print(f"Extracting data for farm {farm}!")
    filepath_in = rootdir_in / farm
    filepath_out = rootdir_out / farm / "01_full_table"
    filepath_out.mkdir(exist_ok=True, parents=True)

    for foldername in os.listdir(filepath_in):
        filetype = None
        filedate = None
        # Lely and DeLaval have .zip/.bak.zip directories for their backup files
        if ".zip" in foldername:
            filetype = "zip"
            filename = foldername.replace(".zip", "")
        if ".bak" in foldername:
            filetype = "bak" + filetype
            filename = foldername.replace(".bak", "")
        # Restore database for backup files/folders
        if filetype == "zip" or filetype == "bakzip":
            print(f"Extracting data for backup {filename}!")
            robottype = farm[0:1]

            # Search for robotversion and file date in file string
            robotversion_searchstr = re.search(r"DelPro+[3-6]+\.[0-9]{1,2}", filename)
            filedate_searchstr = re.search(
                r"20+[0-2]+[0-9]+[0-1]+[0-9]+[0-3]+[0-9]", filename
            )
            if robotversion_searchstr != None:
                robotversion = float(robotversion_searchstr.group()[6:])
            else:
                robotversion = 1.0
            if filedate_searchstr != None:
                filedate = filedate_searchstr.group()
            else:
                filedate = datetime.now().strftime("%Y%m%d")
            # For DeLaval database version 3.7, there is a seperate, slightly different database scheme available
            if robotversion == 3.7:
                robottype = "d_37"

            # Unzip file to temp folder
            with zipfile.ZipFile(filepath_in / foldername, "r") as zip:
                files = zip.namelist()
                for file in files:
                    filename, extension = os.path.splitext(file)
                    if extension == ".bak":
                        zip.extract(file, rootdir_temp)

            backup_string = ""
            num_bfiles = 0
            # TODO: I think this should only loop on .bak files
            for bfiles in os.listdir(rootdir_temp):
                num_bfiles += 1
                backup_string = (
                    backup_string + f"DISK = N''' + @DirOutput + '{bfiles}'', "
                )
            backup_1 = os.listdir(rootdir_temp)[0]
            backup_string = backup_string[:-2]

            # Check that there is only one backup file, if corrupted and the backup file is split, return with an error message
            if num_bfiles == 1:
                fin = open(sql_template, "rt")
                fout = open(f"{rootdir_temp / 'restoreDB.sql'}", "wt")
                for line in fin:
                    # read replace the string and write to output file
                    fout.write(
                        line.replace("VARTEMPDIR", str(rootdir_temp) + os.sep)
                        .replace("VARBACKUPNAMES", backup_string)
                        .replace("VARBACKUPNAME1", backup_1)
                    )
                # close input and output files
                fin.close()
                fout.close()

                # Restore database
                if osname == "nt":
                    cmd = f'''sqlcmd -S {config['user']['servername']} -E -i "{rootdir_temp / 'restoreDB.sql'}" -o "{rootdir_temp / 'sqlout.txt'}"'''
                elif osname == "posix":
                    cmd = f'''sqlcmd -S {config['user']['servername']} -U SA -P '{config['user']['serverpwd']}' -C -i "{rootdir_temp / 'restoreDB.sql'}" -o "{rootdir_temp / 'sqlout.txt'}"'''
                else:
                    print(
                        f"CowBase is not yet adapted to your operating system ({os.name})."
                    )
                    return
                os.system(cmd)

                with open(rootdir_temp / "sqlout.txt") as f:
                    lines = f.readlines()
                list_sqlout = [re.sub(r"[\n\t\s]*", "", i) for i in lines]
                dbname = list_sqlout[list_sqlout.index("dbname") + 1]
                dblog = list_sqlout[list_sqlout.index("dblog") + 1]

                # print("\n\n***DEBUG: DBNAME = ", dbname, "\n\n")

                # For all data tables, query database and extract according to table dictionary (tabledict)
                for table in tabledict[robottype]:
                    if robotversion == 3.7:
                        filepath_out2 = filepath_out / (filedate + "_37")
                    else:
                        filepath_out2 = filepath_out / filedate

                    filepath_out2.mkdir(exist_ok=True, parents=True)
                    filename_out = filepath_out2 / f"{farm}_{filedate}_{table}.csv"
                    extracttable(
                        tabledict, table, robottype, dbname, filename_out, config
                    )
            else:
                print("Error: Backup is corrupted and can not be restored!")

            # Drop any database if still running
            if osname == "nt":
                cmd = f'''sqlcmd -S {config['user']['servername']} -E -Q "IF DB_ID ('DDM') IS NOT NULL DROP DATABASE DDM;"'''
            elif osname == "posix":
                cmd = f'''sqlcmd -S {config['user']['servername']} -U SA -P '{config['user']['serverpwd']}' -C -Q "IF DB_ID ('DDM') IS NOT NULL DROP DATABASE DDM;"'''
            else:
                print(
                    f"CowBase is not yet adapted to your operating system ({os.name})."
                )
                return
            os.system(cmd)

            if osname == "nt":
                cmd = f'''sqlcmd -S {config['user']['servername']} -E -Q "IF DB_ID ('DDMVMS') IS NOT NULL DROP DATABASE DDMVMS;"'''
            elif osname == "posix":
                cmd = f'''sqlcmd -S {config['user']['servername']} -U SA -P '{config['user']['serverpwd']}' -C -Q "IF DB_ID ('DDMVMS') IS NOT NULL DROP DATABASE DDMVMS;"'''
            else:
                print(
                    f"CowBase is not yet adapted to your operating system ({os.name})."
                )
                return
            os.system(cmd)

            if osname == "nt":
                cmd = f'''sqlcmd -S {config['user']['servername']} -E -Q "IF DB_ID ('LELY_Data') IS NOT NULL DROP DATABASE LELY_Data;"'''
            elif osname == "posix":
                cmd = f'''sqlcmd -S {config['user']['servername']} -U SA -P '{config['user']['serverpwd']}' -C -Q "IF DB_ID ('LELY_Data') IS NOT NULL DROP DATABASE LELY_Data;"'''
            else:
                print(
                    f"CowBase is not yet adapted to your operating system ({os.name})."
                )
                return
            os.system(cmd)

            # remove the .bak files from temporary storage
            for items in os.listdir(rootdir_temp):
                os.remove(os.path.join(rootdir_temp, items))


def restoreDB_all(rootdir: str = "/var/lib/CowBase") -> None:
    """
    Extracts data tables from restored MSQL database

    Parameters
    ----------
    rootdir : str or Path
        Filepath to CowBase root directory (e.g. linux: '/var/lib/'; windows: 'C:\\Users\\user\\Documents\\')


    Input (config.toml)
    -----
    servername : str
        # e.g. linux: 'localhost'; windows: 'PC-name\SQLEXPRESS' (PC-name can be found by typing 'hostname' in cmd)
    rootdir : str
        Filepath to CowBase root directory (e.g. linux: '/var/lib/'; windows: 'C:\\Users\\user\\Documents\\')
    serverpwd : str
        # usually only necessary for linux; password you set when creating the MSQL server

    """

    rootdir = Path(rootdir)

    filepath_config = rootdir / "config" / "config.toml"
    with open(filepath_config, mode="rb") as ctomli:
        config = tomli.load(ctomli)

    config_user_rootdir = Path(config["user"]["rootdir"])
    rootdir_temp = config_user_rootdir / "temp"
    rootdir_temp.mkdir(exist_ok=True)

    rootdir_in = config_user_rootdir / "INPUT"
    rootdir_in.mkdir(exist_ok=True)

    # Iterate all folders in the rootdir and check if there are any .zip or .bak.zip files
    for folder in os.listdir(rootdir_in):
        if folder[0] == 'd' or folder[0] == 'l':
            restoreDB_single(rootdir=rootdir, farm=folder)
        else:
            print(f'The folder {folder} is not in the right format. Please make sure the AMS type (l = Lely, d = DeLaval) was added to the farmname (d_farmname)!')
