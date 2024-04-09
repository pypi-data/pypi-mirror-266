# CowBase

<!-- ![Tests](https://github.com/Mat092/CowBase/actions/workflows/tests.yml/badge.svg) -->

## Module overview

![Module overview](https://gitlab.kuleuven.be/livestock-technology/cowbase/-/raw/main/src/cowbase/fig/MM_software_structure.drawio.png)

## Prerequisits

CowBase can run on either Windows or Linux and requires:

1. Python 3.7+
2. (optional when restoring backups) An installation of Microsoft SQL Server **express**

## Working with backups of DeLaval or Lely farm databases 

**An example script of how to run CowBase for backups is given in "example/example_backup_extraction.ipynb"**

When working with backups of DeLaval or Lely farm databases, it is necessary to restore the database before being able to extract data. For this an installation of Microsoft SQL Server & Microsoft SQL Server Management Studio (2017 or newer) is required. 

1. Download and install Microsoft SQL Server **express** (https://www.microsoft.com/en-gb/sql-server/sql-server-downloads)
2. (optional) Download and install Microsoft SQL Server Management Studio (SSMS) (https://learn.microsoft.com/en-us/sql/ssms/download-sql-server-management-studio-ssms?view=sql-server-ver16) - SSMS allows to manually restore a database backup and view all content

Either:

a. Install CowBase using `pip install cowbase`

or 

b. To install the package, first create a new environment with `conda` or `virtualenv`, clone the repository with:

```bash
git clone https://gitlab.kuleuven.be/livestock-technology/cowbase.git
```

enter the repository with:

```bash
cd CowBase
```

and install requirements (optional) and package it with pip:

```bash
pip install -r requirements.txt
pip install -e .
```

## Usage

![Environmental structure](https://gitlab.kuleuven.be/livestock-technology/cowbase/-/raw/main/src/cowbase/fig/MM_prerequisites.drawio.png)

Prerequisites and workflow when using CowBase. When using the backup-based workflow (M1), Python 3.7+/CowBase & a Microsoft SQL Server installation is necessary; when using the real-time-based workflow, Python 3.7+ & a data transfer method is necessary.


![Workflow](https://gitlab.kuleuven.be/livestock-technology/cowbase/-/raw/main/src/cowbase/fig/MM_modules.drawio.png)

Overview of the workflow when using CowBase. On every system using CowBase, an installation of Python 3.7+ and a pip installation of CowBase is required. (M1) In the case of extracting data from farm management system backups (.zip), additionally, an installation of Microsoft SQL Server is required. A full guide to the setup is given above/can be found on the download page. After initializing the CowBase file structure by calling "initCowBase()'', the dictionary specifying the tables & columns that will be extracted can be specified ("CowBase/config/M1_tableDict.json"). Next, for each farm, the collected backups (in .zip format) need to be copied into separate folders, containing the database type ("d_" for DeLaval, "l_" for Lely) and farmname ("_farmname"). Finally, after calling "restoreDB_all()", the defined databases are automatically restored and the data extracted. (M2) In the case of extracting data directly from the farm management system, similar to M1, the necessary folder structure needs to be once initialized ("initCowBase_farm()"), the tables/columns to be extracted can be modified (optional, "CowBase/config/M2_tableDict.json") and the data can then be extracted ("farmExtract()"). (M3) To standardize the data and generate the new table structure optimized for research purpose, the function "mergeTables_all()" can be called, after optionally modifying the tables/columns ("CowBase/config/M3_tableDict.json"). (M4) Finally, to generate a database to store and link all extracted data, tables/columns to be considered can be specified ("CowBase/config/M4_tableDict.json") and the farm location needs to be added to "CowBase/config/M4_sqlupdate.json". To initialize a database containing the predefined structure, "initiateDatabase()" needs to be called. To add the previously extracted data to the newly created database, call "updateDatabaseFull". Finally, to optionally mine weather data using MeteoStat (https://meteostat.net/en/) and add weather data to the database, the functions "meteostatExtract()" and "writeWeather()" can be called.

## Prerequisits

CowBase can run on either Windows or Linux and requires:

1. Python 3.7+
2. Download and install Microsoft SQL Server **express** (https://www.microsoft.com/en-gb/sql-server/sql-server-downloads)
3. (optional) Download and install Microsoft SQL Server Management Studio (SSMS) (https://learn.microsoft.com/en-us/sql/ssms/download-sql-server-management-studio-ssms?view=sql-server-ver16) - SSMS allows to manually restore a database backup and view all content

## Module 1: Restore database local and extract data tables

To initate the repository in which all data handeling will be conducted, use the function initCowBase

```python
from cowbase import cowbase_m1

cowbase_m1.initCowBase('D:/')
```

A new folder will be created containing:

1. config - a folder containing all configuration and parameter files
2. INPUT - a folder in which the backups should be organized
3. temp - a folder for temporary files (used in the restoring processed)

### TODO

1. Save any backup files in a folder containing the abbreviation of the farm management system ('d_' for DeLaval, 'l_'
for Lely) and the farmname ('farmname' --> e.g. 'd_farmname')
2. Edit the config.toml file (i.e. in Notepad)
   - servername: For linux the defined servername when installing MSQL (e.g. 'localhost'); for Windows 'PC-name\SQLEXPRESS' (e.g. use command 'hostname' in the Command Promt)
   - rootdir: File path of CowBase (e.g. 'D:\\CowBase')
   (usually this should already be created correctly when initializing)

After following the previous steps, the 'restoreDB' command can be used. When executing, following steps will be taken:

1. The backup will be unpacked and saved in the temp folder
2. From the temporary files, a database will be recovered
3. From the recovered database, the predefined tables will be extracted and saved in data files (.csv in the OUTPUT folder)
4. The recovered database will be dropped and temporary files deleted

```python
from cowbase import cowbase_m1

cowbase_m1.restoreDB_single(rootdir='D://CowBase/', farm='d_testfarm')

or

cowbase_m1.restoreDB_all(rootdir='D://CowBase/')
```

While with 'restoreDB_single' you can specify a single farm for which all backups in the INPUT folder is unpacked,
'restoreDB_all' iterates over all available folders and unpacks and restores all available backups found in INPUT.


### Functionality

From a DeLaval/Lely backup

- 1.1: Restore a MSQL database locally (Windows or Linux, installation of MSQL necessary, query to restore database in restoreDB.sql)
- 1.2: Extract data from local database (defined by tableDict.json), drop database and delete temp files

## Module 3: Standardize and rename data

To make working with backup data easier and to generate a company independent standarization, a new database table schema was designed independent of farm management software (DeLaval, Lely, ...).

To merge the tables according to the new schema, the function 'mergeTables_single' or 'mergeTables_all' can be used. Herefore specify:

1. rootdir: The filepath CowBase root directory
2. farmname: Name of the farm/folder (including the abbreviation for the milking system ['d_', 'l_'])
3. newtable: name of the new table out of ['animal','lactation','milking','cleaning','insemination','herdnavigator','bcs','activity'] - depending on the sensor availability on farm

```python
from cowbase import cowbase_m3

# Run fow a single table of a single farm
cowbase_m3.mergeTables_single(rootdir='D://CowBase/', farmname='d_testfarm', newtable='tablename')

or

# Run fow all tables of a single farm
cowbase_m3.mergeTables_all(rootdir='D://CowBase/', farmname='d_testfarm')

or

# Run fow all tables of all given farm
for farm in ['d_testfarm']:
    print(farm)
    cowbase_m3.mergeTables_all('D:/CowBase/', farm)
```

When running 'mergeTables_all', all available tables for a single farm system will be iterated.

## Module 4: Generate database

To better maintain data from multiple farms and data sources, and to make working with the data easier, a database can be created. It can be chosen between a server-based database (PostgreSQL or MySQL) or a file-based database (SQLite). The database scheme is given in a config file (/CowBase/config/M4_tableDict.json). 

1. Depending on the database used, first the database management software needs to be installed, follow the instructions given on the respective homepage
    i. PostgreSQL (https://www.postgresql.org/)
    ii. MySQL (https://www.mysql.com/)
    iii. SQLite (https://www.sqlite.org/index.html) (for simplicity SQLite is used in this short tutorial, since the installation and use is the easiest; PostgreSQL and MySQL are especially recommended for multi-user application or if a more feature rich environment is required)
2. Edit the *serverSettings.json* file (e.g. in Notepad):
    - "ssh" - **mandatory** - boolean - False indicates that the database is not connected via ssh
    - "ssh_host" - optional (mandatory if ssh==True) - string - host address to where the ssh connection should be made
    - "ssh_port"  - optional (mandatory if ssh==True) - string - port to where the ssh connection should be made
    - "ssh_user"  - optional (mandatory if ssh==True) - string - username of the ssh user
    - "keybased"  - optional (mandatory if ssh==True) - boolean - True if a ssh-key-pair is used for the ssh connection
    - "ssh_pwd" - optional (mandatory if ssh==True) - string - password of the ssh user 
    - "ssh_pkey" - optional (mandatory if ssh==True) - string - location of the ssh private key
    - "db_host" - optional (mandatory if PostgreSQL or MySQL) - string - host address of the database (e.g. localhost)
    - "db_port" - optional (mandatoryif PostgreSQL or MySQL) - string - port of the database (e.g. 5432 for postgres)
    - "db" - **mandatory** - string - database name
    - "sql_user" - optional (mandatory if PostgreSQL or MySQL) - string - sql user name
    - "sql_pass" - optional (mandatory if PostgreSQL or MySQL) - string - sql password
    - "dbtype" - **mandatory** - string - the name of the database management software that should be used ('postgres', 'mysql', '**sqlite**')
    - "sqlitepath": - optional (**mandatory** if SQLite) - string - filepath to where the sqlite database should be saved (e.g., "D:\\")
3. First the database needs to be initialized according to the database scheme defined in (/CowBase/config/M4_tableDict.json). Run initiateDatabase(rootdir="/path/to/CowBase/", dbtype='sqlite')
4. (*optional*) If desired, a module is included to extract weather data using the **Meteostat** Python package. In before the farms location and altitude needs to be added to the */CowBase/config/M4_sqlupdate.json* (farminfo - farm_location - "farmname" : [latitude, longitude, altitude]). The weather is automatically estimated using the a weighted average of the closest 4 weather stations. To run the weather extraction use *meteostatExtract("/path/to/CowBase/")*
5. Finally the data can be added to the database. This can be done for all tables of a single farm and for the weather seperatly:
    i. updateDatabaseFull(rootdir="/path/to/CowBase/", farm_to_update="d_testfarm", anonymizeFarmlocation=False)
    ii. writeWeather(rootdir="/path/to/CowBase/")
In that process it can be specified if the farmlocation should be anonymized (random location in 10km distance of the farm)


```python
from cowbase import cowbase_m4

# initialize a database (name of the database specified in serverSettings.json)
cowbase_m4.initiateDatabase("D:/CowBase/", "sqlite")
```

```python
from cowbase import cowbase_m4

# Write all availale data from a single farm to the database (name of the database specified in serverSettings.json)
for farm in ['d_testfarm']:
    print(farm)
    cowbase_m4.updateDatabaseFull("D:/CowBase/", farm, False)
```

```python
from cowbase import cowbase_m4

# Extract weather data using Meteostat for all farms specified in "/CowBase/config/M4_sqlupdate.json" - (farminfo - farm_location - "farmname" : [latitude, longitude, altitude])
cowbase_m4.meteostatExtract("D:/CowBase/")
```

```python
from cowbase import cowbase_m4

# Write all extracted weatherdata to the database (name of the database specified in serverSettings.json)
cowbase_m4.writeWeather("D:/CowBase/")
```

## Working with real-time extraction of DeLaval or Lely farm databases (module 2)

When working with the real-time extraction (module 2), following steps need to be considered:

1. Install Python 3.7+ and CowBase on the farm PC (that either runs DelPro or Lely Horizon)
2. Run "initCowBase_farm(rootdir)" where you secify "rootdir" as the filepath, in which you want to save the extracted data.
3. Create a Python/bash script to run "farmExtract()" (To avoid a terminal popping up every time the script is run, a .pyw file format can be used. An example of a daily executable file is given in the example folder)
4. Create a timer in Windows Task Scheduler to run the created Python/bash script (e.g., every day at 7:00)
5. Transfer the extracted data to your own server/PC using e.g., globus connect, ftp or a cloud API of choice (Azure, AWS, ...)
6. Continue with the data preprocessing/standardization and creating a database as before (modules 3 & 4)

## Authors

* <img src="https://gitlab.kuleuven.be/uploads/-/system/user/avatar/3051/avatar.png?width=400" width="25px"> **Martin Julius Gote** [GitLab](https://gitlab.kuleuven.be/u0141520), [KULeuven](https://www.kuleuven.be/wieiswie/en/person/00141520)
* <img src="https://gitlab.kuleuven.be/uploads/-/system/user/avatar/2429/avatar.png?width=400" width="25px"> **Ines Adriaens** [GitLab](https://gitlab.kuleuven.be/u0084712), [KULeuven](https://www.kuleuven.be/wieiswie/en/person/00084712)
* <img src="https://avatars0.githubusercontent.com/u/41483077?s=400&v=4" width="25px;"/> **Mattia Ceccarelli** [GitHub](https://github.com/Mat092), [Unibo](https://www.unibo.it/sitoweb/mattia.ceccarelli5/)
* <img src="https://www.kuleuven.be/wieiswie/en/person/00144565/photo" width="25px"> **Dyan Meuwissen** [GitLab](https://gitlab.kuleuven.be/u0141520), [KULeuven](https://www.kuleuven.be/wieiswie/en/person/00144565)
* <img src="https://www.kuleuven.be/wieiswie/en/person/00132268/photo" width="25px"> **Lore D'Anvers** [GitLab](https://gitlab.kuleuven.be/u0141520), [KULeuven](https://www.kuleuven.be/wieiswie/en/person/00132268)
* <img src="https://www.kuleuven.be/wieiswie/en/person/00072735/photo" width="25px"> **Ben Aernouts** [GitLab](https://gitlab.kuleuven.be/u0072735), [KULeuven](https://www.kuleuven.be/wieiswie/en/person/00072735)
