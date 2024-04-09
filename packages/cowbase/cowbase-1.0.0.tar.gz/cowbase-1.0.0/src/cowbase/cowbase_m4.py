import datetime as dt
import json
import os
import random
import re

import numpy as np
import pandas as pd

from cowbase.cowbase_m5 import DB_connect

import sqlite3
from pathlib import Path
from meteostat import Point, Hourly, Stations


def initiateDatabase(rootdir: str | Path, dbtype: str) -> None:
    """
    Creates a new database using CowBase's data scheme

    Parameters
    ----------
    rootdir : str or Path
        Filepath to CowBase root directory (e.g. linux: '/var/lib/'; windows: 'C:\\Users\\user\\Documents\\')
    dbtype : str
        postgres, mysql, sqlite - database management software needs to be downloaded and installed prior to this
    """

    rootdir = Path(rootdir)

    with open(rootdir / "config" / "serverSettings.json") as file:
        serverSettings = json.load(file)
    with open(rootdir / "config" / "M4_tableDict.json") as file:
        tableDict = json.load(file)

    db_connect = DB_connect(**serverSettings)
    db_connect.create_db()

    dbtype = serverSettings["dbtype"]

    for tables in tableDict:
        sql_statement = f"CREATE TABLE IF NOT EXISTS {tables} ("
        for columnnames in tableDict[tables][dbtype]:
            sql_statement += f"{columnnames} {tableDict[tables][dbtype][columnnames]}, "
        for pkeys in tableDict[tables]["p_key"]:
            sql_statement += f"PRIMARY KEY ({pkeys}), "
        for fkeys in tableDict[tables]["f_keys"]:
            sql_statement += f"FOREIGN KEY ({fkeys}) REFERENCES {tableDict[tables]['f_keys'][fkeys]}, "
        sql_statement += f"UNIQUE({', '.join(tableDict[tables]['unique'])}), "
        sql_statement = sql_statement[0:-2] + ");"
        db_connect.execute(query=sql_statement)

    if dbtype == "postgres":
        sql_statement = """
        do
        $$
        begin
            if not exists (select * from pg_user where usename = 'dbview') then
                create role dbview password 'view';
            end if;
        end
        $$
        ;
        do
        $$
        begin
            if not exists (select * from pg_user where usename = 'dbwrite') then
                create role dbwrite password 'write';
            end if;
        end
        $$
        ;
        GRANT SELECT ON ALL TABLES IN SCHEMA public TO dbview;
        GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO dbwrite;
        """
        db_connect.execute(query=sql_statement)


def create_sql_insert_update(db_update: dict) -> str:
    """
    Creates an upsert sql statement from a dictionary containing necessary parameters (table, insert, conflict, update)

    Parameters
    ----------
    db_update : dict
        dictionary containing information to generate a sql statement

    Return
    ------
    update_sql : str
        sql statement
    """
    update_sql = f'INSERT INTO {db_update["table"]}'

    if db_update["insert"]:
        update_sql += f" ("
        for elem in db_update["insert"]:
            update_sql += f"{elem}, "
        update_sql = update_sql[:-2] + f") VALUES ("
        for elem in db_update["insert"]:
            update_sql += f":{elem}, "
        update_sql = update_sql[:-2] + f") "

    if db_update["conflict"]:
        update_sql += f"ON CONFLICT ("
        for elem in db_update["conflict"]:
            update_sql += f"{elem}, "
        update_sql = update_sql[:-2] + f") "

    if db_update["update"]:
        update_sql += f"DO UPDATE SET "
        for elem in db_update["update"]:
            update_sql += f"{elem} = EXCLUDED.{elem}, "
        update_sql = update_sql[:-2]

    update_sql += ";"
    return update_sql


def create_sql_update(db_update: dict) -> str:
    """
    Creates an update sql statement from a dictionary containing necessary parameters (table, update, where)

    Parameters
    ----------
    db_update : dict
        dictionary containing information to generate a sql statement

    Return
    ------
    update_sql : str
        sql statement
    """
    update_sql = f'UPDATE {db_update["table"]}'

    if db_update["update"]:
        update_sql += f" SET "
        for elem in db_update["update"]:
            update_sql += f"{elem} = :{elem}, "
        update_sql = update_sql[:-2]

    if db_update["where"]:
        update_sql += f" WHERE "
        for elem in db_update["where"]:
            update_sql += f"{elem} = :{elem} AND "
        update_sql = update_sql[:-4]

    update_sql += ";"
    return update_sql


def readData(
    filepath: str | Path, tablename: str, tableDict: dict, farmtype: str
) -> pd.DataFrame:
    """
    Read data from file (pandas)

    Parameters
    ----------
    filepath : str
        path to datafile (.csv)
    tablename : str
        name of the table/file
    tableDict : dict
        dictionary containing information about the table schema of the target database
    farmtype : str
        milking system identifier (d- delaval, l- lely)

    Return
    ------
    df_data : pandas dataframe

    """
    df_data = pd.read_csv(filepath, delimiter=";", header=0, engine="python")

    notnull_columns = tableDict[tablename][f"not_null_read"]

    if len(notnull_columns) > 0:
        for column in list(notnull_columns):
            df_data = df_data.loc[~pd.isnull(df_data[column])]

    datetime_columns = tableDict[tablename][f"{farmtype}_datetime"]

    if len(datetime_columns) > 0:
        for datetime_column in datetime_columns:
            df_data[datetime_column] = df_data[datetime_column].apply(pd.to_datetime)
            df_data[datetime_column] = df_data[datetime_column].dt.floor("s")
    return df_data


def updateFarm(
    df_data: pd.DataFrame,
    db_connect: DB_connect,
    farmname: str,
    milkingSystem: str,
    sqlupdateDict: dict,
) -> tuple[pd.DataFrame, int]:
    """
    Update farm information

    Parameters
    ----------
    df_data : pandas dataframe
        dataframe for a single table
    db_connect : sql engine
        engine to connect ot database
    farmname : str
        name of farm for which data is processed
    milkingSystem : str
        milking system identifier (d- delaval, l- lely)
    sqlupdateDict : dict
        dictionary containing information to generate a sql statement

    Return
    ------
    df_data : pandas dataframe
    farm_id : int

    """

    farm_sql = """
    SELECT farm_id, farmname, created_on
    FROM farm
    ;
    """
    farm_db = db_connect.query(query=farm_sql)

    if farmname in farm_db.loc[:, "farmname"].tolist():
        farm_update = pd.DataFrame(
            {
                "farmname": [str(farmname)],
                "created_on": [
                    farm_db.loc[farm_db["farmname"] == farmname, "created_on"].iloc[0]
                ],
                "updated_on": [dt.date.today()],
                "milking_system_type": [milkingSystem],
            }
        )

        # Update database table 'farm' with data from .txt file - insert if no data entry exist yet, update else

        farm_update_sql = create_sql_update(sqlupdateDict["sql_update"]["farm_upd"])
        db_connect.insert(query=farm_update_sql, data=farm_update.to_dict("records"))

    else:
        farm_update = pd.DataFrame(
            {
                "farmname": [str(farmname)],
                "created_on": [dt.date.today()],
                "updated_on": [dt.date.today()],
                "milking_system_type": [milkingSystem],
            }
        )

        # Insert into database table 'farm' with data from .txt file - insert if no data entry exist yet, update else

        farm_update_sql = create_sql_insert_update(sqlupdateDict["sql_update"]["farm"])
        db_connect.insert(query=farm_update_sql, data=farm_update.to_dict("records"))

    farm_id = db_connect.query(
        query=f"""SELECT farm_id FROM farm WHERE farmname = '{farmname}';"""
    ).squeeze()

    df_data["farm_id"] = farm_id
    return df_data, farm_id


def updateAnimal(
    df_data: pd.DataFrame, db_connect: DB_connect, farm_id: int, sqlupdateDict: dict
) -> pd.DataFrame:
    """
    Update animal table

    Parameters
    ----------
    df_data : pandas dataframe
        dataframe for a single table
    db_connect : sql engine
        engine to connect ot database
    farm_id : integer
        id of farm for which data is processed
    sqlupdateDict : dict
        dictionary containing information to generate a sql statement
    """

    # animal update
    animal_sql = """
    SELECT farm_id, animal_oid
    FROM animal
    ;
    """
    animal_db = db_connect.query(query=animal_sql)

    df_check_animal = df_data.copy(deep=True)
    df_check_animal = df_check_animal[["farm_id", "animal_oid"]].drop_duplicates()

    df_check_animal = df_check_animal.loc[~pd.isnull(df_check_animal.animal_oid)]
    df_check_animal.animal_oid = df_check_animal.animal_oid.astype(int)

    df_animal_update = df_check_animal.merge(
        animal_db[["farm_id", "animal_oid"]],
        how="left",
        on=["farm_id", "animal_oid"],
        indicator=True,
    )

    df_animal_update = df_animal_update.loc[
        df_animal_update["_merge"] == "left_only"
    ].drop(columns=["_merge"])

    df_animal_update = df_animal_update.loc[~pd.isnull(df_animal_update.animal_oid)]

    df_animal_update.animal_oid = df_animal_update.animal_oid.astype(int)

    df_animal_update["updated_on"] = dt.date.today()

    if len(df_animal_update) >= 1:
        # Update database table 'animal' with data from lactation data - insert if no data entry exist yet, update else

        df_animal_update = df_animal_update.drop(columns=["animal_id"])
        animal_update_sql = create_sql_insert_update(
            sqlupdateDict["sql_update"]["animal_table"]
        )
        db_connect.insert(
            query=animal_update_sql, data=df_animal_update.to_dict("records")
        )

    animal_ids = db_connect.query(
        query=f"""SELECT animal_id, animal_oid FROM animal WHERE farm_id = {farm_id};"""
    )

    dict_animal_ids = pd.Series(
        animal_ids.animal_id.values, index=animal_ids.animal_oid
    ).to_dict()

    df_data["animal_id"] = df_data["animal_oid"].map(dict_animal_ids)

    df_data = df_data.drop(columns=["animal_oid"])

    return df_data


def checkDatabase(
    df_data: pd.DataFrame,
    db_connect: DB_connect,
    table: str,
    farm_id: int,
    tableDict: dict,
) -> pd.DataFrame:
    """
    Check database for already present data

    Parameters
    ----------
    df_data : pandas dataframe
        dataframe for a single table
    db_connect : sql engine
        engine to connect ot database
    table : str
        name of the table/file
    farm_id : integer
        id of farm for which data is processed
    tableDict : dict
        dictionary containing information about the table schema of the target database

    Return
    ------
    data_update_new : pandas dataframe

    """
    data_sql = f"""
    SELECT {', '.join(tableDict[table]['unique'])}
    FROM {table}
    WHERE farm_id = {farm_id}
    ;
    """
    data_db = db_connect.query(query=data_sql)

    df_data = df_data.drop_duplicates(subset=tableDict[table]["unique"])

    data_update_new = df_data.merge(
        data_db,
        how="left",
        on=tableDict[table]["unique"],
        indicator=True,
    )

    data_update_new = data_update_new.loc[
        data_update_new["_merge"] == "left_only"
    ].drop(columns=["_merge"])

    return data_update_new


def writeData(
    df_data: pd.DataFrame, db_connect, table: str, tableDict: dict, farmtype: str
) -> None:
    """
    Write new data to 'table'

    Parameters
    ----------
    df_data : pandas dataframe
        dataframe for a single table
    db_connect : sql engine
        engine to connect ot database
    table : str
        name of the table/file
    tableDict : dict
        dictionary containing information about the table schema of the target database
    farmtype : str
        milking system identifier (d- delaval, l- lely)
    """
    df_data["updated_on"] = dt.date.today()

    datetime_columns = tableDict[table][f"{farmtype}_datetime"]
    if len(datetime_columns) > 0:
        for column in datetime_columns:
            df_data[column] = df_data[column].dt.strftime("%Y-%m-%d %H:%M:%S")

    notnull_columns = tableDict[table][f"not_null_write"]

    if len(notnull_columns) > 0:
        for column in list(notnull_columns):
            df_data_remove = df_data.loc[pd.isnull(df_data[column])]
            df_data = df_data.loc[~pd.isnull(df_data[column])]
            if len(df_data_remove) > 0:
                print('NOT NULL constraint failed; Data has been removed!')
                print(df_data_remove)

    df_data.to_sql(
        f"{table}", con=db_connect.ret_con(), if_exists="append", index=False
    )


def updateMilking(
    df_milking: pd.DataFrame,
    db_connect,
    farm_id: int,
    farmname: str,
    farmtype: str,
    sqlupdateDict: dict,
    tableDict: dict,
) -> None:
    """
    Update milking table

    Parameters
    ----------
    df_milking : pandas dataframe
        dataframe for the milking table
    db_connect : sql engine
        engine to connect ot database
    farm_id : integer
        id of farm for which data is processed
    farmname : str
        name of farm for which data is processed
    farmtype : str
        milking system identifier (d- delaval, l- lely)
    sqlupdateDict : dict
        dictionary containing information to generate a sql statement
    tableDict : dict
        dictionary containing information about the table schema of the target database
    """
    milking_sql = f"""
    SELECT farm_id, animal_id, milking_oid, started_at, ended_at
    FROM milking
    WHERE farm_id = {farm_id}
    ;
    """
    milking_db = db_connect.query(query=milking_sql)

    df_milking["farm_id"] = farm_id

    df_milking = df_milking.drop_duplicates(
        subset=["farm_id", "animal_id", "milking_oid", "started_at", "ended_at"]
    )

    milking_update_new = df_milking.merge(
        milking_db[["farm_id", "animal_id", "milking_oid"]],
        how="left",
        on=["farm_id", "animal_id", "milking_oid"],
        indicator=True,
    )

    milking_update_new.started_at = milking_update_new.started_at.apply(pd.to_datetime)
    milking_update_new.ended_at = milking_update_new.ended_at.apply(pd.to_datetime)

    ################################################################################################################
    # apply lactation_ids, parities and calving dates to milking_update_new

    lactation_sql = f"""
    SELECT farm_id, animal_id, lactation_oid, calving, parity
    FROM lactation
    WHERE farm_id = {farm_id}
    ;
    """
    lactation_db = db_connect.query(query=lactation_sql)

    if len(milking_update_new) > 0:
        for lacids in sorted(lactation_db.lactation_oid.unique()):
            aniid = lactation_db.loc[
                lactation_db.lactation_oid == lacids, "animal_id"
            ].values[0]
            calvingdate = (
                lactation_db.loc[lactation_db.lactation_oid == lacids, "calving"]
                .apply(pd.to_datetime)
                .values[0]
            )
            if calvingdate == None:  # fixing error when calvingdate == None
                calvingdate = milking_update_new.loc[
                    (milking_update_new.animal_id == aniid), "started_at"
                ].min()

            lacno = lactation_db.loc[
                lactation_db.lactation_oid == lacids, "parity"
            ].values[0]
            milking_update_new.loc[
                (milking_update_new.animal_id == aniid)
                & (milking_update_new.started_at >= calvingdate),
                "lactation_oid_db",
            ] = lacids
            milking_update_new.loc[
                (milking_update_new.animal_id == aniid)
                & (milking_update_new.started_at >= calvingdate),
                "parity_db",
            ] = lacno
            milking_update_new.loc[
                (milking_update_new.animal_id == aniid)
                & (milking_update_new.started_at >= calvingdate),
                "calving_db",
            ] = calvingdate

        ################################################################################################################
        # correct for missed/wrong lactation ids

        # delete if no milking_oid available
        milking_update_new = milking_update_new.loc[
            ~pd.isnull(milking_update_new["milking_oid"])
        ]

        # sort milk data and calculate gaps
        milking_update_new = milking_update_new.sort_values(
            by=["animal_id", "started_at"]
        ).reset_index(drop=True)
        milking_update_new["gap"] = (
            milking_update_new.groupby(by="animal_id")
            .started_at.diff()
            .dt.total_seconds()
            / 86400
        )

        milking_update_new.loc[pd.isnull(milking_update_new.gap), "gap"] = 0
        milking_update_new.loc[milking_update_new.gap < 10, "gap"] = 0
        milking_update_new.loc[milking_update_new.gap > 0, "gap"] = 1
        if farmtype == "d":
            if farmname in list(sqlupdateDict["farminfo"]["lacgapstart"]):
                milking_update_new.loc[
                    (
                        milking_update_new.started_at
                        < dt.datetime.strptime(
                            sqlupdateDict["farminfo"]["lacgapstart"][farmname],
                            "%d-%m-%Y",
                        )
                    )
                    & (
                        (
                            milking_update_new.started_at
                            - milking_update_new.calving_db
                        ).dt.total_seconds()
                        / 86400
                        < 300
                    ),
                    "gap",
                ] = 0
            else:
                startingdate = df_milking.started_at.max() - dt.timedelta(180)
                milking_update_new.loc[
                    (milking_update_new.started_at < startingdate)
                    & (
                        (
                            milking_update_new.started_at
                            - milking_update_new.calving_db
                        ).dt.total_seconds()
                        / 86400
                        < 300
                    ),
                    "gap",
                ] = 0
        # define periods restricted by gaps of at least 10 days
        milking_update_new["periods"] = milking_update_new.groupby(
            by="animal_id"
        ).gap.cumsum()
        # introduce parameter that gives 1 to periods that were fully in a period that we trust (started after data was contiouusly collected)
        milking_update_new.loc[milking_update_new.periods == 0, "trust_cal"] = 0
        milking_update_new.loc[milking_update_new.periods > 0, "trust_cal"] = 1
        # define the calculated calving date as the date of the first milking in each period
        milking_update_new["calving_cal"] = milking_update_new.groupby(
            by=["animal_id", "periods"]
        ).started_at.transform("min")
        milking_update_new["calving_cal"] = milking_update_new["calving_cal"].dt.date
        # set the parity to 1 if the parity was 0
        milking_update_new.loc[
            (milking_update_new.parity_db == 0)
            | pd.isnull(milking_update_new.parity_db),
            "parity_db",
        ] = 1
        # the calculated parity is the sum of the minimal parity for each cow and the period counter calculated based on gaps of min 10 days
        milking_update_new["parity"] = milking_update_new.groupby(
            by=["animal_id"]
        ).parity_db.transform("min")
        milking_update_new["parity"] = (
            milking_update_new["parity"] + milking_update_new["periods"]
        )
        # if there were gaps of less than 10 days between calvings (and those were recorded), correct for that
        for wp_ani_id in milking_update_new.loc[
            milking_update_new.parity_db > milking_update_new.parity, "animal_id"
        ].unique():
            while (
                milking_update_new.loc[
                    (milking_update_new.animal_id == wp_ani_id)
                    & (milking_update_new.parity_db > milking_update_new.parity)
                ].empty
                == False
            ):
                inc_time = milking_update_new.loc[
                    (milking_update_new.animal_id == wp_ani_id)
                    & (milking_update_new.parity_db > milking_update_new.parity),
                    "started_at",
                ].min()
                milking_update_new.loc[
                    (milking_update_new.animal_id == wp_ani_id)
                    & (milking_update_new.started_at >= inc_time),
                    "parity",
                ] += 1

        # the final calvingdate and lactation_oid is defined as:
        # taken from the farm database if the calculated and the predicted parity are the same and the calvingdate is before the first milking of that period
        # as the first day in the milking otherwise

        # if the calving was before the data where continouus data was collected, or
        # if the parity is the same for calculated and in the database and the calving in the database is before the calculated, trust the database
        milking_update_new.loc[
            (milking_update_new.parity_db == milking_update_new.parity)
            & (milking_update_new.calving_db <= milking_update_new.calving_cal)
            | (milking_update_new.trust_cal == 0),
            "calving",
        ] = milking_update_new.loc[
            (milking_update_new.parity_db == milking_update_new.parity)
            & (milking_update_new.calving_db <= milking_update_new.calving_cal)
            | (milking_update_new.trust_cal == 0),
            "calving_db",
        ].apply(
            pd.to_datetime
        )
        milking_update_new.loc[
            (milking_update_new.parity_db == milking_update_new.parity)
            & (milking_update_new.calving_db <= milking_update_new.calving_cal)
            | (milking_update_new.trust_cal == 0),
            "lactation_oid",
        ] = milking_update_new.loc[
            (milking_update_new.parity_db == milking_update_new.parity)
            & (milking_update_new.calving_db <= milking_update_new.calving_cal)
            | (milking_update_new.trust_cal == 0),
            "lactation_oid_db",
        ]

        # Otherwise, trust the calculated values
        milking_update_new.loc[
            (milking_update_new.parity_db == milking_update_new.parity)
            & (milking_update_new.calving_db > milking_update_new.calving_cal)
            & (milking_update_new.trust_cal == 1),
            "calving",
        ] = milking_update_new.loc[
            (milking_update_new.parity_db == milking_update_new.parity)
            & (milking_update_new.calving_db > milking_update_new.calving_cal)
            & (milking_update_new.trust_cal == 1),
            "calving_cal",
        ].apply(
            pd.to_datetime
        )

        # if the parity is not the same, we assume that a new lactation was not inserted into the database
        milking_update_new.loc[
            (milking_update_new.parity_db != milking_update_new.parity), "calving"
        ] = milking_update_new.loc[
            (milking_update_new.parity_db != milking_update_new.parity), "calving_cal"
        ].apply(
            pd.to_datetime
        )

        milking_update_new.loc[
            pd.isnull(milking_update_new.calving), "calving"
        ] = milking_update_new.loc[
            pd.isnull(milking_update_new.calving), "calving_cal"
        ].apply(
            pd.to_datetime
        )

        # if the lactation_oid was not define, create a new lactation_id out of the unique animal_id and the parity
        milking_update_new.loc[
            pd.isnull(milking_update_new.lactation_oid), "lactation_oid"
        ] = milking_update_new.loc[
            pd.isnull(milking_update_new.lactation_oid), "animal_id"
        ].astype(
            "int64"
        ) * 10**9 + milking_update_new.loc[
            pd.isnull(milking_update_new.lactation_oid), "parity"
        ].astype(
            "int64"
        )

        # drop columns that were only used for calculations
        milking_update_new = milking_update_new.drop(
            columns=[
                "calving_cal",
                "parity_db",
                "lactation_oid_db",
                "calving_db",
                "gap",
                "periods",
                "trust_cal",
            ]
        )

        # Calculate new DIM
        milking_update_new.loc[
            ~pd.isnull(milking_update_new.ended_at)
            & ~pd.isnull(milking_update_new.calving),
            "dim",
        ] = (
            (
                milking_update_new.loc[
                    ~pd.isnull(milking_update_new.ended_at)
                    & ~pd.isnull(milking_update_new.calving),
                    "ended_at",
                ].apply(pd.to_datetime)
                - milking_update_new.loc[
                    ~pd.isnull(milking_update_new.ended_at)
                    & ~pd.isnull(milking_update_new.calving),
                    "calving",
                ].apply(pd.to_datetime)
            ).dt.total_seconds()
            / 86400
        ).round(
            decimals=2
        )

        # update lactation table
        lac_update = (
            milking_update_new[
                ["farm_id", "animal_id", "lactation_oid", "calving", "parity"]
            ]
            .drop_duplicates()
            .reset_index(drop=True)
        )
        lac_update.lactation_oid = lac_update.lactation_oid.astype(int)
        lac_update.loc[pd.isnull(lac_update.parity)] = 0
        lac_update.parity = lac_update.parity.astype(int)
        lac_update["calving"] = lac_update["calving"].apply(pd.to_datetime)
        lac_update["updated_on"] = dt.date.today()

        lac_update["calving"] = lac_update["calving"].dt.strftime("%Y-%m-%d %H:%M:%S")

        lactation_sql = create_sql_insert_update(
            sqlupdateDict["sql_update"]["milking_lactation_table"]
        )
        db_connect.insert(query=lactation_sql, data=lac_update.to_dict("records"))

        ################################################################################################################

        # add the lactation_ids back to the milking dataframe
        lactation_ids = db_connect.query(
            query=f"""SELECT lactation_id, lactation_oid FROM lactation WHERE farm_id = {farm_id};"""
        )

        dict_lactation_ids = pd.Series(
            lactation_ids.lactation_id.values, index=lactation_ids.lactation_oid
        ).to_dict()

        milking_update_new["lactation_id"] = milking_update_new["lactation_oid"].map(
            dict_lactation_ids
        )

        milking_update_new = milking_update_new.drop(columns=["lactation_oid"])

        # drop the data that was already available in the database
        milking_update_new["updated_on"] = dt.date.today()
        milking_update_db_data = (
            milking_update_new.loc[milking_update_new["_merge"] != "left_only"]
            .copy()
            .drop(columns=["_merge"])
        )
        milking_update_new = milking_update_new.loc[
            milking_update_new["_merge"] == "left_only"
        ].drop(columns=["_merge"])

        milking_update_new = milking_update_new.loc[
            ~pd.isnull(milking_update_new.milking_oid)
        ]
        milking_update_new = milking_update_new.loc[
            ~pd.isnull(milking_update_new.animal_id)
        ]
        milking_update_new = milking_update_new.loc[
            ~pd.isnull(milking_update_new.lactation_id)
        ]
        # milking_update_new = milking_update_new.loc[
        #     ~pd.isnull(milking_update_new.milking_system_oid)
        # ]

    ################################################################################################################

    if len(milking_update_db_data) > 0:
        # update milking table
        milking_sql = create_sql_update(
            sqlupdateDict["sql_update"]["milking_milking_table"]
        )

        db_connect.insert(
            query=milking_sql, data=milking_update_db_data.to_dict("records")
        )

    if len(milking_update_new) > 0:
        ################################################################################################################
        # if the milkings system oid is missing in the original backup data, create a new id, to indicate this and add the data regardsless to our database
        milking_update_new.loc[
            pd.isnull(milking_update_new.milking_system_oid), "milking_system_oid"
        ] = int(farm_id * 1000 + 999)

        ################################################################################################################
        # update milking system table
        milking_system_update = (
            milking_update_new[["farm_id", "milking_system_oid", "updated_on"]]
            .copy()
            .drop_duplicates(subset=["farm_id", "milking_system_oid"])
        )
        ms_update_sql = create_sql_insert_update(
            sqlupdateDict["sql_update"]["milking_system_milking_table"]
        )
        db_connect.insert(
            query=ms_update_sql, data=milking_system_update.to_dict("records")
        )

        ################################################################################################################
        # map milking system ids to milking system oids
        milking_system_ids = db_connect.query(
            query=f"""SELECT milking_system_id, milking_system_oid FROM milking_system WHERE farm_id = {farm_id};"""
        )

        dict_ms_ids = pd.Series(
            milking_system_ids.milking_system_id.values,
            index=milking_system_ids.milking_system_oid,
        ).to_dict()

        milking_update_new["milking_system_id"] = milking_update_new[
            "milking_system_oid"
        ].map(dict_ms_ids)

        milking_update_new = milking_update_new.drop(columns=["milking_system_oid"])

        ################################################################################################################

        milking_update_new = milking_update_new.drop(columns=["calving"])

        # insert new milkings into milking table
        datetime_columns = tableDict["milking"][f"{farmtype}_datetime"]
        for column in datetime_columns:
            milking_update_new[column] = milking_update_new[column].dt.strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        milking_update_new.to_sql(
            "milking", con=db_connect.ret_con(), if_exists="append", index=False
        )


def mapMilkingSystem(df_data: pd.DataFrame, db_connect, farm_id: int) -> pd.DataFrame:
    """
    Update milking system table

    Parameters
    ----------
    df_data : pandas dataframe
        dataframe for a single table
    db_connect : sql engine
        engine to connect ot database
    farm_id : integer
        id of farm for which data is processed

    Return
    ------
    df_data : pandas dataframe
        dataframe with new milking_system_ids
    """
    milking_system_ids = db_connect.query(
        query=f"""SELECT milking_system_id, milking_system_oid FROM milking_system WHERE farm_id = {farm_id};"""
    )

    dict_ms_ids = pd.Series(
        milking_system_ids.milking_system_id.values,
        index=milking_system_ids.milking_system_oid,
    ).to_dict()

    ################################################################################################################
    # if the milkings system oid is missing in the original backup data, create a new id, to indicate this and add the data regardsless to our database
    df_data.loc[pd.isnull(df_data.milking_system_oid), "milking_system_oid"] = int(
        farm_id * 1000 + 999
    )

    df_data["milking_system_id"] = df_data["milking_system_oid"].map(dict_ms_ids)
    df_data.milking_system_id = df_data.milking_system_id.astype(float).astype('Int64')

    df_data = df_data.drop(columns=["milking_system_oid"])
    return df_data


def mapAnimalid(df_data: pd.DataFrame, db_connect, farm_id: int) -> pd.DataFrame:
    """
    Map new animal_ids to the animal_id used on the farm

    Parameters
    ----------
    df_data : pandas dataframe
        dataframe for a single table
    db_connect : sql engine
        engine to connect ot database
    farm_id : int
        id of farm for which data is processed

    Return
    ------
    df_data : pandas dataframe
        dataframe with new animal_ids
    """
    animal_ids = db_connect.query(
        query=f"""SELECT animal_id, animal_oid FROM animal WHERE farm_id = {farm_id};"""
    )

    dict_animal_ids = pd.Series(
        animal_ids.animal_id.values, index=animal_ids.animal_oid
    ).to_dict()

    df_data["animal_id"] = df_data["animal_oid"].map(dict_animal_ids)

    df_data = df_data.drop(columns=["animal_oid"])
    return df_data


def mapLactationid(
    df_data: pd.DataFrame, db_connect, farm_id: int, tablename: str
) -> pd.DataFrame:
    """
    Map new lactation_ids to the lactation_id used on the farm

    Parameters
    ----------
    df_data : pandas dataframe
        dataframe for a single table
    db_connect : sql engine
        engine to connect ot database
    farm_id : integer
        id of farm for which data is processed
    tablename : str
        name of the table/file

    Return
    ------
    df_data : pandas dataframe
        dataframe with new lactation_ids
    """
    lactation_sql = f"""
    SELECT farm_id, animal_id, lactation_id, calving, parity
    FROM lactation
    WHERE farm_id = {farm_id}
    ;
    """
    lactation_db = db_connect.query(query=lactation_sql)

    for lacids in list(
        lactation_db.sort_values(by=["animal_id", "calving"]).lactation_id
    ):
        aniid = lactation_db.loc[
            lactation_db.lactation_id == lacids, "animal_id"
        ].values[0]
        calvingdate = (
            lactation_db.loc[lactation_db.lactation_id == lacids, "calving"]
            .apply(pd.to_datetime)
            .values[0]
        )
        lacno = lactation_db.loc[lactation_db.lactation_id == lacids, "parity"].values[
            0
        ]
        df_data.loc[
            (df_data.animal_id == aniid) & (df_data.measured_on >= calvingdate),
            "lactation_id",
        ] = lacids
        df_data.loc[
            (df_data.animal_id == aniid) & (df_data.measured_on >= calvingdate),
            "calvingdate",
        ] = calvingdate
        df_data.loc[
            (df_data.animal_id == aniid) & (df_data.measured_on >= calvingdate),
            "parity",
        ] = lacno
    # calculate the dim
    df_data["dim"] = (
        df_data.measured_on - pd.to_datetime(df_data.calvingdate, format="%Y-%m-%d")
    ) / np.timedelta64(1, "D")
    if tablename in ["bcs", "activity"]:
        df_data = df_data.drop(columns=["calvingdate"])
    return df_data


def updateFarmLocation(db_connect, sqlupdateDict: dict, anonymized: bool) -> None:
    """
    Update farm location

    Parameters
    ----------
    db_connect : sql engine
        engine to connect ot database
    sqlupdateDict : dict
        dictionary containing information to generate a sql statement
    anonymized : bool
        anonlymize farm location (in a radius of 5 km around original location)
    """
    farm_sql = """
            SELECT *
            FROM farm
            ;
            """
    farm_db = db_connect.query(query=farm_sql)

    dict_farmlocation = sqlupdateDict["farminfo"]["farm_location"]

    dict_farm_lat = dict(
        zip(
            dict_farmlocation.keys(),
            list(list(zip(*list(dict_farmlocation.values())))[0]),
        )
    )
    dict_farm_long = dict(
        zip(
            dict_farmlocation.keys(),
            list(list(zip(*list(dict_farmlocation.values())))[1]),
        )
    )
    dict_farm_alt = dict(
        zip(
            dict_farmlocation.keys(),
            list(list(zip(*list(dict_farmlocation.values())))[2]),
        )
    )

    farm_db["longitude"] = farm_db["farmname"].map(dict_farm_long)
    farm_db["latitude"] = farm_db["farmname"].map(dict_farm_lat)
    farm_db["altitude"] = farm_db["farmname"].map(dict_farm_alt)

    if anonymized == True:
        for index, row in farm_db.iterrows():
            rand_dist = random.randint(0, 2 * np.pi)
            rand_long = np.sin(rand_dist) * 0.1
            rand_lat = np.cos(rand_dist) * 0.1
            farm_db.loc[farm_db.index == index, "longitude"] += rand_long
            farm_db.loc[farm_db.index == index, "latitude"] += rand_lat

    #########################################################################################################################
    # Update database table 'aws' with weather data

    farm_db["updated_on"] = dt.date.today()

    farm_update_sql = create_sql_update(sqlupdateDict["sql_update"]["farm_location"])
    db_connect.insert(query=farm_update_sql, data=farm_db.to_dict("records"))


def updateDatabaseTable(
    db_connect,
    filepath: str | Path,
    tablename: str,
    farmname: str,
    farmtype: str,
    tableDict: dict,
    sqlupdateDict: dict,
) -> None:
    """
    Update farm information

    Parameters
    ----------
    db_connect : sql engine
        engine to connect ot database
    filepath : str or Path
        path to datafile (.csv)
    tablename : str
        name of the table/file
    farmname : str
        name of farm for which data is processed
    farmtype : str
        milking system identifier (d- delaval, l- lely)
    tableDict : dict
        dictionary containing information about the table schema of the target database
    sqlupdateDict : dict
        dictionary containing information to generate a sql statement
    """

    if farmtype == "d":
        milkingSystem = "AMS delaval"
    elif farmtype == "l":
        milkingSystem = "AMS lely"

    df_data = readData(filepath, tablename, tableDict, farmtype)
    df_data, farm_id = updateFarm(
        df_data, db_connect, farmname, milkingSystem, sqlupdateDict
    )

    if tablename == "animal":
        df_data_update = checkDatabase(
            df_data, db_connect, tablename, farm_id, tableDict
        )
        if not df_data_update.empty:
            writeData(df_data_update, db_connect, tablename, tableDict, farmtype)
    elif tablename == "lactation":
        df_data = updateAnimal(df_data, db_connect, farm_id, sqlupdateDict)
        df_data = df_data.loc[~pd.isnull(df_data.animal_id)]
        df_data_update = checkDatabase(
            df_data, db_connect, tablename, farm_id, tableDict
        )
        if not df_data_update.empty:
            writeData(df_data_update, db_connect, tablename, tableDict, farmtype)
    elif tablename == "milking":
        df_data = updateAnimal(df_data, db_connect, farm_id, sqlupdateDict)
        updateMilking(
            df_data, db_connect, farm_id, farmname, farmtype, sqlupdateDict, tableDict
        )
    elif tablename == "cleaning":
        df_data = mapMilkingSystem(df_data, db_connect, farm_id)
        df_data_update = checkDatabase(
            df_data, db_connect, tablename, farm_id, tableDict
        )
        if not df_data_update.empty:
            writeData(df_data_update, db_connect, tablename, tableDict, farmtype)
    elif tablename in ["activity", "herdnavigator", "insemination", "bcs"]:
        df_data = mapAnimalid(df_data, db_connect, farm_id)
        df_data_update = checkDatabase(
            df_data, db_connect, tablename, farm_id, tableDict
        )
        if not df_data_update.empty:
            df_data_update = mapLactationid(
                df_data_update, db_connect, farm_id, tablename
            )
            writeData(df_data_update, db_connect, tablename, tableDict, farmtype)


def updateDatabaseFull(
    rootdir: str | Path, farm_to_update: str, anonymizeFarmlocation: bool
) -> None:
    """
    Update farm information

    Parameters
    ----------
    rootdir : str or Path
        path to cowbase rootdir
    farm_to_update : str
        name of farm for which data is processed
    anonymizeFarmlocation : bool
        anonymize farm location (in a radius of 5 km around original location)
    """

    rootdir = Path(rootdir)

    with open(rootdir / "config" / "serverSettings.json") as file:
        serverSettings = json.load(file)
    with open(rootdir / "config" / "M4_tableDict.json") as file:
        tableDict = json.load(file)
    with open(rootdir / "config" / "M4_sqlupdate.json") as file:
        sqlupdateDict = json.load(file)

    db_connect = DB_connect(**serverSettings)

    filepath = rootdir / "OUTPUT"
    farmfound = False
    for farms in os.listdir(filepath):
        farmtype = re.split("_", farms)[0]
        farmname = re.split("_", farms)[1]
        if not farms == farm_to_update:
            continue
        farmfound = True
        for tables in tableDict:
            for files in os.listdir(filepath / farms / "02_merged_table"):
                tablename = re.split("_", files[:-4])[-1]
                if tablename == tables:
                    print(f"Writing data in table {tablename}!")
                    datapath = filepath / farms / "02_merged_table" / files
                    updateDatabaseTable(
                        db_connect,
                        datapath,
                        tablename,
                        farmname,
                        farmtype,
                        tableDict,
                        sqlupdateDict,
                    )
                    print("Done!")
        updateFarmLocation(db_connect, sqlupdateDict, anonymizeFarmlocation)
    if farmfound == False:
        print("Could not find data for the farm that should be analyzed!")


def writeWeather(rootdir):
    rootdir = Path(rootdir)
    rootdir_INPUT_weather = rootdir / "INPUT" / "weather"
    with open(rootdir / "config" / "serverSettings.json") as file:
        serverSettings = json.load(file)
    with open(rootdir / "config" / "M4_sqlupdate.json") as file:
        sqlupdateDict = json.load(file)
    db_connect = DB_connect(**serverSettings)

    df_weather = pd.read_csv(rootdir_INPUT_weather / "weather.csv", header=0)
    df_weather_stations = pd.read_csv(rootdir_INPUT_weather / "aws.csv", header=0)
    df_weather_stations_weights = pd.read_csv(
        rootdir_INPUT_weather / "aws_weights.csv", header=0
    )
    df_weather_stations[
        [
            "hourly_start",
            "hourly_end",
            "daily_start",
            "daily_end",
            "monthly_start",
            "monthly_end",
        ]
    ] = df_weather_stations[
        [
            "hourly_start",
            "hourly_end",
            "daily_start",
            "daily_end",
            "monthly_start",
            "monthly_end",
        ]
    ].apply(
        pd.to_datetime
    )

    for column in [
        "hourly_start",
        "hourly_end",
        "daily_start",
        "daily_end",
        "monthly_start",
        "monthly_end",
    ]:
        df_weather_stations[column] = df_weather_stations[column].dt.strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    df_weather_stations[
        [
            "hourly_start",
            "hourly_end",
            "daily_start",
            "daily_end",
            "monthly_start",
            "monthly_end",
        ]
    ] = df_weather_stations[
        [
            "hourly_start",
            "hourly_end",
            "daily_start",
            "daily_end",
            "monthly_start",
            "monthly_end",
        ]
    ].replace(
        {np.nan: None}
    )

    farm_sql = """
    SELECT farm_id, farmname
    FROM farm
    ;
    """
    farm_db = db_connect.query(query=farm_sql)

    dict_farm_ids = pd.Series(farm_db.farm_id.values, index=farm_db.farmname).to_dict()

    df_weather = df_weather.loc[df_weather.farmname.isin(list(farm_db.farmname))]
    df_weather_stations = df_weather_stations.loc[
        df_weather_stations.farmname.isin(list(farm_db.farmname))
    ]
    df_weather_stations_weights = df_weather_stations_weights.loc[
        df_weather_stations_weights.farmname.isin(list(farm_db.farmname))
    ]

    df_weather["farm_id"] = df_weather["farmname"].map(dict_farm_ids)
    df_weather = df_weather.drop(columns=["farmname"])
    df_weather["updated_on"] = dt.date.today()

    df_weather_stations = df_weather_stations.drop(columns=["farmname"])
    df_weather_stations["updated_on"] = dt.date.today()

    df_weather_stations_weights["farm_id"] = df_weather_stations_weights[
        "farmname"
    ].map(dict_farm_ids)
    df_weather_stations_weights = df_weather_stations_weights.drop(columns=["farmname"])
    df_weather_stations_weights["updated_on"] = dt.date.today()

    df_weather_stations_weights.aws_id_1 = np.floor(pd.to_numeric(df_weather_stations_weights.aws_id_1, errors='coerce')).astype('Int64')
    df_weather_stations_weights.aws_id_2 = np.floor(pd.to_numeric(df_weather_stations_weights.aws_id_2, errors='coerce')).astype('Int64')
    df_weather_stations_weights.aws_id_3 = np.floor(pd.to_numeric(df_weather_stations_weights.aws_id_3, errors='coerce')).astype('Int64')
    df_weather_stations_weights.aws_id_4 = np.floor(pd.to_numeric(df_weather_stations_weights.aws_id_4, errors='coerce')).astype('Int64')

    # ####################################################################################################################
    # drop data that was already in the database
    weather_sql = f"""
    SELECT farm_id, datetime
    FROM weather
    ;
    """
    weather_db = db_connect.query(query=weather_sql)

    df_weather["datetime"] = df_weather["datetime"].apply(pd.to_datetime)
    weather_db["datetime"] = weather_db["datetime"].apply(pd.to_datetime)

    df_weather = df_weather.drop_duplicates(
        subset=["farm_id", "datetime"], keep="first"
    )

    weather_update_new = df_weather.merge(
        weather_db[["farm_id", "datetime"]],
        how="left",
        on=["farm_id", "datetime"],
        indicator=True,
    )

    weather_update_new = weather_update_new.loc[
        weather_update_new["_merge"] == "left_only"
    ].drop(columns=["_merge"])

    weather_update_new["datetime"] = weather_update_new["datetime"].dt.strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    weather_update_new.to_sql(
        "weather", con=db_connect.ret_con(), if_exists="append", index=False
    )

    ####################################################################################################################

    aws_update_sql = create_sql_insert_update(sqlupdateDict["sql_update"]["aws"])
    db_connect.insert(query=aws_update_sql, data=df_weather_stations.to_dict("records"))

    aws_weights_update_sql = create_sql_insert_update(
        sqlupdateDict["sql_update"]["aws_weights"]
    )
    db_connect.insert(
        query=aws_weights_update_sql,
        data=df_weather_stations_weights.to_dict("records"),
    )


def meteostatExtract(rootdir, startdate="2010-01-01", enddate="2023-01-01"):
    start = dt.datetime.strptime(startdate, "%Y-%m-%d")
    end = dt.datetime.strptime(enddate, "%Y-%m-%d")

    with open(os.path.join(rootdir, "config", "M4_sqlupdate.json")) as file:
        sqlupdateDict = json.load(file)

    dict_farmlocation = sqlupdateDict["farminfo"]["farm_location"]

    weather = pd.DataFrame()
    weather_stations = pd.DataFrame()
    weather_stations_weights = pd.DataFrame()
    for farms in dict_farmlocation.keys():
        print(farms)
        farmlocation = Point(
            dict_farmlocation[farms][0],
            dict_farmlocation[farms][1],
            dict_farmlocation[farms][2],
        )
        farmlocation.method = "weighted"
        weather_add = Hourly(farmlocation, start, end)
        weather_add = weather_add.fetch()
        weather_add = weather_add.reset_index()
        weather_add = weather_add.rename(
            columns={
                "time": "datetime",
                "temp": "temperature",
                "dwpt": "dew_point",
                "rhum": "humidity",
                "prcp": "precipitation",
                "snow": "snow",
                "wdir": "wind_direction",
                "wspd": "windspeed",
                "wpgt": "peak_wind_gust",
                "pres": "air_pressure",
                "tsun": "total_sunshine_duration",
                "coco": "weather_condition_code",
            }
        )
        weather_stations_add = Stations()
        weather_stations_add = weather_stations_add.nearby(
            dict_farmlocation[farms][0], dict_farmlocation[farms][1]
        ).fetch(4)
        weather_stations_add = weather_stations_add.reset_index()
        weather_stations_add = weather_stations_add.rename(columns={"id": "aws_id"})
        weather_stations_add = weather_stations_add.loc[~pd.isnull(weather_stations_add.wmo)]
        weather_stations_add = weather_stations_add.reset_index(drop=True)
        weather_stations_add.aws_id = weather_stations_add.aws_id.astype(int)
        if len(weather_stations_add) == 4:
            weather_stations_weighted_add = pd.DataFrame(
                {
                    "farmname": [farms],
                    "aws_id_1": list(weather_stations_add.aws_id.astype(int))[0],
                    "distance_1": list(weather_stations_add.distance.astype(float))[0],
                    "aws_id_2": list(weather_stations_add.aws_id.astype(int))[1],
                    "distance_2": list(weather_stations_add.distance.astype(float))[1],
                    "aws_id_3": list(weather_stations_add.aws_id.astype(int))[2],
                    "distance_3": list(weather_stations_add.distance.astype(float))[2],
                    "aws_id_4": list(weather_stations_add.aws_id.astype(int))[3],
                    "distance_4": list(weather_stations_add.distance.astype(float))[3],
                }
            )
        elif len(weather_stations_add) == 3:
            print('Warning: 1 of the closest weather stations were not registered with WMO and hence removed!')
            weather_stations_weighted_add = pd.DataFrame(
                {
                    "farmname": [farms],
                    "aws_id_1": list(weather_stations_add.aws_id.astype(int))[0],
                    "distance_1": list(weather_stations_add.distance.astype(float))[0],
                    "aws_id_2": list(weather_stations_add.aws_id.astype(int))[1],
                    "distance_2": list(weather_stations_add.distance.astype(float))[1],
                    "aws_id_3": list(weather_stations_add.aws_id.astype(int))[2],
                    "distance_3": list(weather_stations_add.distance.astype(float))[2],
                }
            )
        elif len(weather_stations_add) == 2:
            print('Warning: 2 of the closest weather stations were not registered with WMO and hence removed!')
            weather_stations_weighted_add = pd.DataFrame(
                {
                    "farmname": [farms],
                    "aws_id_1": list(weather_stations_add.aws_id.astype(int))[0],
                    "distance_1": list(weather_stations_add.distance.astype(float))[0],
                    "aws_id_2": list(weather_stations_add.aws_id.astype(int))[1],
                    "distance_2": list(weather_stations_add.distance.astype(float))[1],
                    "aws_id_3": list(weather_stations_add.aws_id.astype(int))[2],
                    "distance_3": list(weather_stations_add.distance.astype(float))[2],
                }
            )
        else:
            print('Warning: More than 2 of the closest weather stations were not registered with WMO and hence removed!')
            weather_stations_weighted_add = pd.DataFrame()

        weather_stations_add = weather_stations_add.drop(columns=["distance"])
        weather_stations_add["farmname"] = farms
        weather_add["farmname"] = farms
        weather = pd.concat([weather, weather_add])
        weather = weather.reset_index(drop=True)
        weather_stations = pd.concat([weather_stations, weather_stations_add])
        weather_stations = weather_stations.drop_duplicates(subset=["aws_id"])
        weather_stations = weather_stations.reset_index(drop=True).sort_values(
            by="aws_id"
        )
        weather_stations_weights = pd.concat(
            [weather_stations_weights, weather_stations_weighted_add]
        )
        weather_stations_weights = weather_stations_weights.reset_index(drop=True)

    rootdir = Path(rootdir)
    rootdir_INPUT_weather = rootdir / "INPUT" / "weather"
    rootdir_INPUT_weather.mkdir(exist_ok=True, parents=True)
    weather.to_csv(rootdir_INPUT_weather / "weather.csv", index=False)
    weather_stations.to_csv(rootdir_INPUT_weather / "aws.csv", index=False)
    weather_stations_weights.to_csv(
        rootdir_INPUT_weather / "aws_weights.csv", index=False
    )
