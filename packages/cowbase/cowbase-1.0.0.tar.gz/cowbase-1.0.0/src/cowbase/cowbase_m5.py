import json
import os
import pandas as pd
import numpy as np
from sshtunnel import SSHTunnelForwarder
from sqlalchemy import create_engine
from sqlalchemy import inspect
from sqlalchemy import text
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.ext.declarative import declarative_base
import pandas as pd
import os
import json

# import getpass


class DB_connect(object):

    """
    The class 'LT_connect' can be used to connect to the LT postgres database
    via a ssh connection.\n

    Functions:
    ----------

    tables(self, db, schema, sql_user, sql_pass)\n
    print_columns(self, db, table_name, sql_user, sql_pass)\n
    query(self, db, query, sql_user, sql_pass)\n
    execute(self, db, query, sql_user, sql_pass)\n
    insert(self, db, query, data, sql_user, sql_pass)\n
    ret_con(self, db, sql_user, sql_pass)\n
    create_db(self, db, sql_user, sql_pass)

    Parameters
    ----------

    db : name of a postgres database that should be accessed \n
    p_host : address of the database of the system
    (usually localhost - 127.0.0.1) \n
    p_port : port for postgresql (usually 5432) \n
    ssh : if a ssh connection is necessary insert 'True' \n
    ssh_user : account name of the ssh user \n
    ssh_host : ip address of the server to which to connect \n
    ssh_pkey : filepath to the ssh key for faster access \n
    sql_user : account name of the postgres user \n
    sql_pass : password for the postgres account \n

    Return
    ------

    None


    """

    def __init__(
        self,
        ssh,
        ssh_host,
        ssh_port,
        ssh_user,
        keybased,
        ssh_pwd,
        ssh_pkey,
        db_host,
        db_port,
        db,
        sql_user,
        sql_pass,
        dbtype,
        sqlitepath,
    ):
        """
        __init__(self, db_host, db_port, db, ssh, ssh_user, ssh_host, ssh_pkey, sql_user, sql_pass):
        -----------------------------------------------
        defines global class parameters for ssh connection\n

        Parameters
        ----------
        ssh : if a ssh connection is necessary insert 'True' \n
        ssh_host : ip address of the server to which to connect \n
        ssh_port : port of the server to which to connect \n
        ssh_user : account name of the ssh user \n
        keybased : boolean - True if ssh-key is used to connect to server \n
        ssh_pwd : password for ssh connection \n
        ssh_pkey : filepath to the ssh key for faster access \n
        db_host : address of the database of the system
        (usually localhost - 127.0.0.1) \n
        db_port : port for postgresql (usually 5432) \n
        db : name of a postgres database that should be accessed \n
        sql_user : account name of the postgres user \n
        sql_pass : password for the postgres account \n
        dbtype : dbtype used (postgres, mysql, sqlite)

        Returns:
        --------
        None
        """
        # SSH Tunnel Variables
        self.db_host = db_host
        self.db_port = db_port
        self.sql_user = sql_user
        self.sql_pass = sql_pass
        self.ssh_port = ssh_port
        self.dbtype = dbtype
        self.db = db
        self.echoparam = False
        
        if ssh == True:
            if keybased == True:
                self.server = SSHTunnelForwarder(
                    (ssh_host, ssh_port),
                    ssh_username=ssh_user,
                    ssh_pkey=ssh_pkey,
                    remote_bind_address=(db_host, db_port),
                )
                server = self.server
                server.start()  # start ssh server
                self.local_port = server.local_bind_port
                print(f"Server connected via SSH ...")
            else:
                self.server = SSHTunnelForwarder(
                    (ssh_host, ssh_port),
                    ssh_username=ssh_user,
                    ssh_password=ssh_pwd,
                    remote_bind_address=(db_host, db_port),
                )
                server = self.server
                server.start()  # start ssh server
                self.local_port = server.local_bind_port
                print(f"Server connected via SSH ...")
        else:
            self.local_port = db_port
        
        if dbtype == "postgres":
            self.enginestr = f"postgresql://{self.sql_user}:{self.sql_pass}@{self.db_host}:{self.local_port}/{self.db}"

        elif dbtype == "mysql":
            self.enginestr = f"mysql+mysqldb://{self.sql_user}:{self.sql_pass}@{self.db_host}:{self.local_port}/{self.db}"

        elif dbtype == "sqlite":
            if not os.path.exists(sqlitepath):
                os.makedirs(sqlitepath)
            self.enginestr = f"sqlite:///{sqlitepath}\\{self.db}.db"

    def tables(self, schema):
        """
        tables(self, db, schema, sql_user, sql_pass):
        -----------------------------------------------
        returns all table names in a given 'schema' of a database 'db'\n

        Parameters:
        ----------

        db : name of a postgres database that should be accessed \n
        schema : name of the schema that should be analyzed\n
        sql_user : account name of the postgres user \n
        sql_pass : password for the postgres account \n

        Returns:
        --------
        tables_df (pandas dataframe of table names)

        """

        # create an engine to connect to the postgreSQL database, documentation
        # of functions can be found at https://docs.sqlalchemy.org/en/14/

        if self.dbtype == "sqlite":
            engine = create_engine(self.enginestr, echo=True)
        else:
            engine = create_engine(self.enginestr)
        conn = engine.connect() 
        inspector = inspect(engine)
        tables = inspector.get_table_names(schema=schema)
        self.tables_df = pd.DataFrame(tables, columns=["table name"])
        engine.dispose()
        return self.tables_df

    def print_columns(self, table_name):
        """
        print_columns(self, db, table_name, sql_user, sql_pass)
        -----------------------------------------------
        returns all table names in a given 'schema' of a database 'db'\n

        Parameters:
        ----------

        db : name of a postgres database that should be accessed \n
        table_name : name of the table for which the columns schould be checked \n
        sql_user : account name of the postgres user \n
        sql_pass : password for the postgres account \n

        Returns:
        --------
        tables_df (pandas dataframe of column names)

        """

        # create an engine to connect to the postgreSQL database, documentation
        # of functions can be found at https://docs.sqlalchemy.org/en/14/

        engine = create_engine(self.enginestr, echo=self.echoparam)

        if " " in table_name:
            if '"' in table_name:
                pass
            else:
                table_name = "'" + table_name + "'"
        query = (
            """
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = %s
        ;
        """
            % table_name
        )
        self.table_df = pd.read_sql(query, engine)
        engine.dispose()
        return self.table_df

    def query(self, query):
        """
        query(self, db, query, sql_user, sql_pass)
        -----------------------------------------------
        executes a postgreSQL query in the database 'db' (return = true)\n

        Parameters:
        ----------

        db : name of a postgres database that should be accessed \n
        query : insert char string of postgreSQL code that should be queried \n
        sql_user : account name of the postgres user \n
        sql_pass : password for the postgres account \n

        Returns:
        --------
        query_df (pandas dataframe of query result)

        """
        # create an engine to connect to the postgreSQL database, documentation
        # of functions can be found at https://docs.sqlalchemy.org/en/14/
        engine = create_engine(self.enginestr, echo=self.echoparam)
        self.query_df = pd.read_sql(query, engine)
        engine.dispose()
        return self.query_df

    def execute(self, query):
        """
        execute(self, db, query, sql_user, sql_pass)
        -----------------------------------------------
        executes a postgreSQL query in the database 'db' (return = false)\n

        Parameters:
        ----------

        db : name of a postgres database that should be accessed \n
        query : insert char string of postgreSQL code that should be queried \n
        sql_user : account name of the postgres user \n
        sql_pass : password for the postgres account \n

        Returns:
        --------
        None

        """
        # create an engine to connect to the postgreSQL database, documentation
        # of functions can be found at https://docs.sqlalchemy.org/en/14/
        engine = create_engine(self.enginestr, echo=self.echoparam)
        with engine.begin() as connection:
            connection.execute(text(query))
        # engine.execute(text(query))
        engine.dispose()

    def insert(self, query, data):
        """
        insert(self, db, query, data, sql_user, sql_pass)
        -----------------------------------------------
        executes a postgreSQL query in the database 'db' (return = false),
        used to insert data with parameter data, use '%(name)s' in the query text
        and a dictionary ({name : value}) for data \n

        Parameters:
        ----------

        db : name of a postgres database that should be accessed \n
        query : insert char string of postgreSQL code that should be queried \n
        data : dictionary of data that should be used in the query \n
        sql_user : account name of the postgres user \n
        sql_pass : password for the postgres account \n

        Returns:
        --------
        None

        """
        # create an engine to connect to the postgreSQL database, documentation
        # of functions can be found at https://docs.sqlalchemy.org/en/14/
        engine = create_engine(self.enginestr, echo=self.echoparam)

        with engine.begin() as connection:
            connection.execute(text(query), data)
        # engine.execute(text(query), data[0])
        engine.dispose()

    def ret_con(self):
        """
        ret_con(self, db, sql_user, sql_pass)
        -----------------------------------------------
        returns the engine to connect to the database 'db'\n

        Parameters:
        ----------

        db : name of a postgres database that should be accessed \n
        sql_user : account name of the postgres user \n
        sql_pass : password for the postgres account \n

        Returns:
        --------
        engine

        """
        # create an engine to connect to the postgreSQL database, documentation
        # of functions can be found at https://docs.sqlalchemy.org/en/14/
        engine = create_engine(self.enginestr, echo=self.echoparam)
        return engine

    def create_db(self):
        """
        create_db(self, db, sql_user, sql_pass)
        -----------------------------------------------
        creates the database 'db'\n

        Parameters:
        ----------

        db : name of a postgres database that should be accessed \n
        sql_user : account name of the postgres user \n
        sql_pass : password for the postgres account \n

        Returns:
        --------
        None

        """
        # create an engine to connect to the postgreSQL database, documentation
        # of functions can be found at https://docs.sqlalchemy.org/en/14/

        print(self.dbtype)
        if self.dbtype == "sqlite":
            engine = create_engine(self.enginestr, echo=self.echoparam)
            Base = declarative_base()
            Base.metadata.create_all(engine)
        else:
            engine = create_engine(self.enginestr)
            if not database_exists(engine.url):
                create_database(engine.url)
            else:
                print('A database with the name "' + self.db + '" already exists')


def connCowBaseDB(rootdir):
    """
    Returns connection to database, specify parameters in settings file

    Parameters
    ----------
    rootdir : str
        path to cowbase rootdir
    farm_to_update : str
        name of farm for which data is processed
    anonymizeFarmlocation : bool
        anonlymize farm location (in a radius of 5 km around original location)
    """

    settingsPath = os.path.join(rootdir, "config", "serverSettings.json")

    with open(settingsPath) as file:
        serverSettings = json.load(file)

    # Create a connection to the database
    db_connect = DB_connect(**serverSettings)

    return db_connect


def dailyMY(df_milking):
    """
    Converts raw SESSION milk yield data to standardized DAILY milk yield data
    + some data selection steps (outliers deleted)

    Parameters
    ----------
    df_milking : df
        raw data of one farm from the database containing variables
            * milking_id
            * farm_id
            * animal_id
            * lactation_id
            * parity
            * started_at
            * ended_at
            * mi
            * dim
            * tmy & qmy (mylf, myrf, mylr, myrr)
            * quarter ec (eclf, ecrf, eclr, ecrr)

    Yields
    ------
    df_milking_daily : df
        (daily milk yield) data of one farm containing variables
            * farm_id
            * animal_id
            * lactation_id
            * dim
            * tdmy
            * dmylf, dmyrf, dmylr, dmyrr

    Steps
    -----
        - calculate the proportion of the MI before and after midnight
        - assign that proportion of the MY to the current or previous day (at udder and quarter level)
        - sum the milk yields of each day
        - add 1 to the DIM to avoid problems with log later on
        - standardize by dividing by the sum of all MI assigned to the current day (to account for missing milkings)
        - calculate a 7 day rolling median of the TDMY: delete tdmy values that are lower than 1.5*the rolling median
        - delete observations with TDMY below 75 kg

    """

    # Kick out all entries where mi could not be calculated/was not recorded.
    # This might lead to loss of information, creating a
    # total daily milk yield though would have large deviations if the mi was not guessed correctly.
    df_milking = df_milking.sort_values(
        by=["farm_id", "animal_id", "lactation_id", "milking_id"]
    ).reset_index(drop=True)
    milking = df_milking[df_milking["mi"].notna()].copy()

    # Floor dim for the calculation of daily milk yield
    milking["dim_floor"] = milking["dim"].apply(np.floor)

    # IV_dim_floor gives the time in hours at which the milking started at
    milking["IV_dim_floor"] = 24 * (milking["dim"] - milking["dim_floor"])

    # calculate the time between milkings that was during the previous day (compared to the dim floored)
    milking["mi_day_before"] = milking["mi"] - milking["IV_dim_floor"]
    # you put it to 0 because there was a previous milking on the same day
    milking.loc[milking["mi_day_before"] < 0, "mi_day_before"] = 0

    # calculate the time between milkings that was during the day (dim floored)
    milking["mi_on_day"] = milking["mi"] - milking["mi_day_before"]

    # calulate the proportions of mi on the day and day before
    milking["mi_day_before"] = milking["mi_day_before"] / milking["mi"]
    milking["mi_on_day"] = milking["mi_on_day"] / milking["mi"]

    # create a new table where the time between milkings was spread over two days
    MY_daily_add = milking[milking["mi_day_before"] > 0].copy()

    # multiply the tmy in the first dataset (MY) with the mi in the day to get the propotion of milk yield 'produced' on that day
    # all parts of the milking session before midnight are set to 0. The only milk yields in THIS dataset, are from the sessions completely produced in the current day AND the proportion produced after midnight.
    milking["mi_day_before"] = 0
    milking["tmy"] = milking["tmy"] * milking["mi_on_day"]
    milking["mylf"] = milking["mylf"] * milking["mi_on_day"]
    milking["myrf"] = milking["myrf"] * milking["mi_on_day"]
    milking["mylr"] = milking["mylr"] * milking["mi_on_day"]
    milking["myrr"] = milking["myrr"] * milking["mi_on_day"]

    # multiply the tmy in the second dataset (df_milking_add) with the mi on the day before to get the propotion of milk yield 'produced' on the previous day
    # all complete milk sessions and the part of the milking interval after midnight, are equaled to 0. The only milk yields in THIS dataset are milk yields from the proportion before midnight.
    MY_daily_add["mi_on_day"] = 0
    # change the DIM to the DIM of the previous day (so later you will add this MY to the corresponding day - before midnight)
    MY_daily_add["dim_floor"] -= 1
    # if proportion of MI on the previous day is lower than 0, set equal to 0 (no milk yield assigned to the previous day)
    MY_daily_add[MY_daily_add["dim_floor"] < 0] = 0
    MY_daily_add["tmy"] = MY_daily_add["tmy"] * MY_daily_add["mi_day_before"]
    MY_daily_add["mylf"] = MY_daily_add["mylf"] * MY_daily_add["mi_day_before"]
    MY_daily_add["myrf"] = MY_daily_add["myrf"] * MY_daily_add["mi_day_before"]
    MY_daily_add["mylr"] = MY_daily_add["mylr"] * MY_daily_add["mi_day_before"]
    MY_daily_add["myrr"] = MY_daily_add["myrr"] * MY_daily_add["mi_day_before"]

    # combine both tables and lose unnecessary information
    # df_milking contains the data of milking sessions of the current day (full MI on current day & proportion produced on current day of 'overnight' MI)
    # df_milking_add contains data of milking sessions of the previous day (proportion produced on previous day of 'overnight' MI)
    milking = pd.concat([milking, MY_daily_add])
    milking = milking[
        [
            "farm_id",
            "animal_id",
            "lactation_id",
            "parity",
            "mi",
            "dim_floor",
            "tmy",
            "mylf",
            "myrf",
            "mylr",
            "myrr",
            "mi_day_before",
            "mi_on_day",
        ]
    ]
    del MY_daily_add

    # multiply the mi with the proportion of each day to get the true values of mi per period
    # In df_milking (contains current day info): mi_day_before is always 0, mi_on_day is either 1 (full MI on current day) or smaller than 1 (proportion produced on current day of 'overnight' MI)
    # In df_milking_add (contains previous day): mi_on_day is always 0, mi_day_before lies between 0 and 1 (proportion produced on previous day)
    milking["mi"] = milking["mi"] * (milking["mi_day_before"] + milking["mi_on_day"])

    # group by dim_floor to get the daily milk yields. Add all measurements to the assigned day
    MY_daily = milking.groupby(
        ["farm_id", "animal_id", "lactation_id", "parity", "dim_floor"], dropna=False
    ).sum()
    MY_daily.reset_index(inplace=True)
    MY_daily = MY_daily.rename(
        columns={
            "dim_floor": "dim",
            "tmy": "tdmy",
            "mylf": "dmylf",
            "myrf": "dmyrf",
            "mylr": "dmylr",
            "myrr": "dmyrr",
        }
    )
    del milking

    # add 1 to dim to avoid errors during the fitting process (allow any y offset, might cause problems if y=0 in some models)
    MY_daily["dim"] += 1

    # correct the milk yields to true daily milk yield by deviding through the mi for each my calculation and multiply by 24h (correct for missing data)
    MY_daily["tdmy"] = (MY_daily["tdmy"] / MY_daily["mi"]) * 24
    MY_daily["dmylf"] = (MY_daily["dmylf"] / MY_daily["mi"]) * 24
    MY_daily["dmyrf"] = (MY_daily["dmyrf"] / MY_daily["mi"]) * 24
    MY_daily["dmylr"] = (MY_daily["dmylr"] / MY_daily["mi"]) * 24
    MY_daily["dmyrr"] = (MY_daily["dmyrr"] / MY_daily["mi"]) * 24

    MY_daily = MY_daily[
        [
            "farm_id",
            "animal_id",
            "lactation_id",
            "parity",
            "dim",
            "tdmy",
            "dmylf",
            "dmyrf",
            "dmylr",
            "dmyrr",
        ]
    ]

    # calculate a 7 day rolling median of the tdmy and select for tdmy values that are lower than
    # 1.5*the rolling median and below 75 kg daily milk yield
    MY_daily["tdmy7dm"] = MY_daily["tdmy"].rolling(7).median()
    MY_daily.loc[(MY_daily["dim"] < 7), "tdmy7dm"] = MY_daily.loc[
        (MY_daily["dim"] < 7), "tdmy"
    ]
    MY_daily = MY_daily[(MY_daily["tdmy"] < 1.5 * MY_daily["tdmy7dm"])]
    MY_daily = MY_daily[(MY_daily["tdmy"] < 75)]

    MY_daily = MY_daily[
        [
            "farm_id",
            "animal_id",
            "lactation_id",
            "parity",
            "dim",
            "tdmy",
            "dmylf",
            "dmyrf",
            "dmylr",
            "dmyrr",
        ]
    ]

    return MY_daily
