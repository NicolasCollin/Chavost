@echo off
setlocal enabledelayedexpansion

REM ================== CONFIG PROJET CHAVOST ==================
set "REPO_URL=https://gitlab-mi.univ-reims.fr/coll0155/chavost.git"
set "APP_ROOT_FOLDER=application chavost"
set "PROJECT_FOLDER_NAME=chavost"
set "GIT_BRANCH=main"
set "UV_RUN_COMMAND=uv run src/main.py"
REM ===========================================================

echo.
echo ================== INSTALLATION / MISE A JOUR CHAVOST ==================
echo.


REM -------------------------------------------------------------------------
REM 0) Vérifier / installer Git
REM -------------------------------------------------------------------------
echo Verification de Git...
where git >nul 2>&1
if errorlevel 1 (
    echo.
    echo Git n'est pas installe. Installation via winget...
    where winget >nul 2>&1
    if errorlevel 1 (
        echo winget n'est pas disponible. Impossible d'installer Git automatiquement.
        echo Installe Git : https://git-scm.com/ puis relance le script.
        goto :end
    )

    winget install -e --id Git.Git
    if errorlevel 1 (
        echo Echec de l'installation de Git. Abandon.
        goto :end
    )

    echo Git installe. Mise a jour du PATH...
    set "PATH=%PATH%;%ProgramFiles%\Git\cmd"
)

where git >nul 2>&1
if errorlevel 1 (
    echo Git n'a pas ete detecte meme apres installation. Abandon.
    goto :end
)

echo Git detecte : OK
echo.


REM -------------------------------------------------------------------------
REM 1) Vérifier / installer Python
REM -------------------------------------------------------------------------
echo Verification de Python...
where python >nul 2>&1
if errorlevel 1 (
    echo.
    echo Python non detecte. Installation via winget...
    where winget >nul 2>&1
    if errorlevel 1 (
        echo winget n'est pas disponible. Impossible d'installer Python automatiquement.
        echo Installe Python : https://www.python.org/downloads/
        goto :end
    )

    winget install -e --id Python.Python.3.12
    if errorlevel 1 (
        echo Echec installation de Python. Abandon.
        goto :end
    )

    set "PATH=%PATH%;%LOCALAPPDATA%\Microsoft\WindowsApps"
)

where python >nul 2>&1
if errorlevel 1 (
    echo Python non detecte. Abandon.
    goto :end
)

echo Python detecte : OK
echo.


REM -------------------------------------------------------------------------
REM 2) Choisir dossier installation
REM -------------------------------------------------------------------------
set /p INSTALL_DIR="Chemin d'installation (ex: C:\Users\utilisateur\Documents) : "

if "%INSTALL_DIR%"=="" (
    echo Aucun chemin saisi. Abandon.
    goto :end
)

if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

set "APP_ROOT_DIR=%INSTALL_DIR%\%APP_ROOT_FOLDER%"
set "TARGET_DIR=%APP_ROOT_DIR%\%PROJECT_FOLDER_NAME%"

if not exist "%APP_ROOT_DIR%" mkdir "%APP_ROOT_DIR%"


REM -------------------------------------------------------------------------
REM 3) Clone ou mise à jour du projet
REM -------------------------------------------------------------------------
if exist "%TARGET_DIR%\.git" (
    echo Mise a jour du projet Chavost...
    pushd "%TARGET_DIR%"
    git pull origin %GIT_BRANCH%
    popd
) else (
    echo Clonage du projet Chavost...
    pushd "%APP_ROOT_DIR%"
    git clone "%REPO_URL%" "%PROJECT_FOLDER_NAME%"
    if errorlevel 1 (
        echo Echec du clonage. Abandon.
        goto :end
    )
    popd
)


REM -------------------------------------------------------------------------
REM 4) Vérifier / installer uv
REM -------------------------------------------------------------------------
echo Verification de uv...
where uv >nul 2>&1
if errorlevel 1 (
    echo uv non trouve. Installation via pip...
    python -m pip install uv
    if errorlevel 1 (
        echo Echec installation uv. Abandon.
        goto :end
    )
)
echo uv detecte : OK
echo.


REM -------------------------------------------------------------------------
REM 5) Creation lanceur local
REM -------------------------------------------------------------------------
set "LAUNCHER_PATH=%APP_ROOT_DIR%\lanceur_chavost.bat"

> "%LAUNCHER_PATH%" echo @echo off
>> "%LAUNCHER_PATH%" echo cd /d "%TARGET_DIR%"
>> "%LAUNCHER_PATH%" echo git pull origin %GIT_BRANCH%
>> "%LAUNCHER_PATH%" echo %UV_RUN_COMMAND%
>> "%LAUNCHER_PATH%" echo pause


REM -------------------------------------------------------------------------
REM 6) Creation raccourci Bureau
REM -------------------------------------------------------------------------
set "DESKTOP_DIR=%USERPROFILE%\Desktop"
if not exist "%DESKTOP_DIR%" set "DESKTOP_DIR=%USERPROFILE%\Bureau"

set "SHORTCUT_PATH=%DESKTOP_DIR%\Chavost.lnk"
set "ICON_PATH=%TARGET_DIR%\image\logo.ico"

powershell -command ^
"$s = (New-Object -COM WScript.Shell).CreateShortcut('%SHORTCUT_PATH%');" ^
"$s.TargetPath = '%LAUNCHER_PATH%';" ^
"$s.WorkingDirectory = '%APP_ROOT_DIR%';" ^
"$s.IconLocation = '%ICON_PATH%';" ^
"$s.Save();"

echo Raccourci cree : %SHORTCUT_PATH%
echo.


REM -------------------------------------------------------------------------
REM 7) Proposer de lancer immédiatement
REM -------------------------------------------------------------------------
choice /M "Lancer Chavost maintenant"
if errorlevel 1 (
    call "%LAUNCHER_PATH%"
)

:end
echo.
echo ================== FIN DU SCRIPT ==================
pause
endlocal
