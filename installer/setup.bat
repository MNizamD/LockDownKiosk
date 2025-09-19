@echo off
REM ========================================================
REM  Generate Task Scheduler XML + Import + Deploy
REM  XML is stored in the same folder as this script
REM ========================================================

:: CONFIG
set TASKNAME=LockDownKiosk
set USERONLY=Marohom
set APPDIR=C:\Program Files\NizamLab
set APPNAME=Launcher.exe

:: Paths
set CURDIR=%~dp0
set DESTDIR=C:\Program Files\NizamLab
set XMLFILE=%CURDIR%LockDownKiosk.xml
set APPEXEPATH=%APPDIR%\%APPNAME%
set USERNAME=%COMPUTERNAME%\%USERONLY%

:: Build ISO8601 Date for <Date>
for /f "tokens=2 delims==" %%I in ('"wmic os get LocalDateTime /value"') do set ldt=%%I
set DATEISO=%ldt:~0,4%-%ldt:~4,2%-%ldt:~6,2%T%ldt:~8,2%:%ldt:~10,2%:%ldt:~12,2%

echo Generating Task Scheduler XML at "%XMLFILE%"...

> "%XMLFILE%" echo ^<?xml version="1.0" encoding="UTF-16"?^>
>> "%XMLFILE%" echo ^<Task version="1.4" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task"^>
>> "%XMLFILE%" echo   ^<RegistrationInfo^>
>> "%XMLFILE%" echo     ^<Date^>%DATEISO%^</Date^>
>> "%XMLFILE%" echo     ^<Author^>%USERNAME%^</Author^>
>> "%XMLFILE%" echo     ^<Description^>LockDown kiosk launcher task^</Description^>
>> "%XMLFILE%" echo   ^</RegistrationInfo^>
>> "%XMLFILE%" echo   ^<Triggers^>
>> "%XMLFILE%" echo     ^<LogonTrigger^>
>> "%XMLFILE%" echo       ^<Enabled^>true^</Enabled^>
>> "%XMLFILE%" echo       ^<Delay^>PT0S^</Delay^>
>> "%XMLFILE%" echo       ^<UserId^>%USERNAME%^</UserId^>
>> "%XMLFILE%" echo     ^</LogonTrigger^>
>> "%XMLFILE%" echo   ^</Triggers^>
>> "%XMLFILE%" echo   ^<Principals^>
>> "%XMLFILE%" echo     ^<Principal id="Author"^>
>> "%XMLFILE%" echo       ^<UserId^>%USERNAME%^</UserId^>
>> "%XMLFILE%" echo       ^<RunLevel^>HighestAvailable^</RunLevel^>
>> "%XMLFILE%" echo     ^</Principal^>
>> "%XMLFILE%" echo   ^</Principals^>
>> "%XMLFILE%" echo   ^<Settings^>
>> "%XMLFILE%" echo     ^<MultipleInstancesPolicy^>IgnoreNew^</MultipleInstancesPolicy^>
>> "%XMLFILE%" echo     ^<DisallowStartIfOnBatteries^>false^</DisallowStartIfOnBatteries^>
>> "%XMLFILE%" echo     ^<StopIfGoingOnBatteries^>false^</StopIfGoingOnBatteries^>
>> "%XMLFILE%" echo     ^<AllowHardTerminate^>true^</AllowHardTerminate^>
>> "%XMLFILE%" echo     ^<StartWhenAvailable^>true^</StartWhenAvailable^>
>> "%XMLFILE%" echo     ^<RunOnlyIfNetworkAvailable^>false^</RunOnlyIfNetworkAvailable^>
>> "%XMLFILE%" echo   ^</Settings^>
>> "%XMLFILE%" echo   ^<Actions Context="Author"^>
>> "%XMLFILE%" echo     ^<Exec^>
>> "%XMLFILE%" echo       ^<Command^>"%APPEXEPATH%"^</Command^>
>> "%XMLFILE%" echo     ^</Exec^>
>> "%XMLFILE%" echo   ^</Actions^>
>> "%XMLFILE%" echo ^</Task^>

echo Importing task...
schtasks /create /tn "%TASKNAME%" /xml "%XMLFILE%" /f
if %ERRORLEVEL%==0 (
    echo Task imported successfully.

    echo Cleaning old folder...
    if exist "%DESTDIR%" rmdir /S /Q "%DESTDIR%"

    echo Copying files to "%DESTDIR%"...
    mkdir "%DESTDIR%"
    xcopy "%CURDIR%*" "%DESTDIR%\" /E /H /C /I /Y >nul
    if %ERRORLEVEL%==0 (
        echo Files copied successfully.
    ) else (
        echo File copy failed!
    )
) else (
    echo Failed to import task!
)

pause
