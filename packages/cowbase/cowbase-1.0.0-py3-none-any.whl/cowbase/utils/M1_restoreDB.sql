BEGIN
DECLARE @DirOutput NVARCHAR(1000)
DECLARE @PathToBackup NVARCHAR(1000)
DECLARE @LogicalNameData varchar(128)
DECLARE @LogicalNameLog varchar(128)
DECLARE @Table TABLE (
        LogicalName varchar(128),
        [PhysicalName] varchar(128),
        [Type] varchar,
        [FileGroupName] varchar(128),
        [Size] varchar(128),
        [MaxSize] varchar(128),
        [FileId] varchar(128),
        [CreateLSN] varchar(128),
        [DropLSN] varchar(128),
        [UniqueId] varchar(128),
        [ReadOnlyLSN] varchar(128),
        [ReadWriteLSN] varchar(128),
        [BackupSizeInBytes] varchar(128),
        [SourceBlockSize] varchar(128),
        [FileGroupId] varchar(128),
        [LogGroupGUID] varchar(128),
        [DifferentialBaseLSN] varchar(128),
        [DifferentialBaseGUID] varchar(128),
        [IsReadOnly] varchar(128),
        [IsPresent] varchar(128),
        [TDEThumbprint] varchar(128),
        [SnapshotUrl] varchar(128)
    );
IF DB_ID ('DDM') IS NOT NULL DROP DATABASE DDM;
IF DB_ID ('DDMVMS') IS NOT NULL DROP DATABASE DDMVMS;
IF DB_ID ('LELY_Data') IS NOT NULL DROP DATABASE LELY_Data;
SET @DirOutput = 'VARTEMPDIR'
SET @PathToBackup = @DirOutput + 'VARBACKUPNAME1'
INSERT INTO @Table EXEC(
        'RESTORE FILELISTONLY FROM DISK=''' + @PathToBackup + ''''
    );
SET @LogicalNameData =(
        SELECT LogicalName
        FROM @Table
        WHERE Type = 'D'
    );
SET @LogicalNameLog =(
        SELECT LogicalName
        FROM @Table
        WHERE Type = 'L'
    );
EXEC(
    'RESTORE DATABASE [' + @LogicalNameData + ']
    FROM VARBACKUPNAMES WITH FILE = 1, REPLACE,
    MOVE N''' + @LogicalNameData + ''' TO N''' + @DirOutput + @LogicalNameData + '.mdf'',
    MOVE N''' + @LogicalNameLog + ''' TO N''' + @DirOutput + @LogicalNameLog + '.ldf'', NOUNLOAD, STATS = 10'
);
PRINT N'dbname';
PRINT @LogicalNameData;
PRINT N'dblog';
PRINT @LogicalNameLog;
END
