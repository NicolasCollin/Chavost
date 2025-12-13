@echo off
setlocal EnableExtensions

REM ============================================================================
REM  CHAVOST.bat
REM  - Installe les prerequis (Git, Python, uv)
REM  - Clone ou met a jour le projet prive (GitLab) via user+token
REM  - Cree un lanceur local + un raccourci Bureau
REM ============================================================================

REM ================== CONFIG PROJET CHAVOST ==================
set "APP_ROOT_FOLDER=application chavost"
set "PROJECT_FOLDER_NAME=chavost"
set "GIT_BRANCH=main"
set "UV_RUN_COMMAND=uv run src/main.py"

REM ================== AUTHENTIFICATION GITLAB ==================
REM Renseigner ici l'utilisateur et le token GitLab (Jeton de deploiement)
set "GIT_AUTH_USER=gitlab+deploy-token-12"
set "GIT_AUTH_TOKEN=gldt-iayk9cXgyKL11nn8CU35"

REM URL du depot avec authentification (repo prive)
set "REPO_URL=https://%GIT_AUTH_USER%:%GIT_AUTH_TOKEN%@gitlab-mi.univ-reims.fr/coll0155/chavost.git"
REM =============================================================

call :banner

REM --------------------------------------------------------------------------
REM 0) Verifier / installer Git
REM --------------------------------------------------------------------------
call :ensure_winget
call :ensure_git

REM --------------------------------------------------------------------------
REM 1) Verifier / installer Python
REM --------------------------------------------------------------------------
call :ensure_python

REM --------------------------------------------------------------------------
REM 2) Choisir dossier installation
REM --------------------------------------------------------------------------
call :select_install_dir

REM --------------------------------------------------------------------------
REM 3) Clone ou mise a jour du projet
REM --------------------------------------------------------------------------
call :sync_repo

REM --------------------------------------------------------------------------
REM 4) Verifier / installer uv
REM --------------------------------------------------------------------------
call :ensure_uv

REM --------------------------------------------------------------------------
REM 5) Creation lanceur local
REM --------------------------------------------------------------------------
call :create_launcher

REM --------------------------------------------------------------------------
REM 6) Creation raccourci Bureau
REM --------------------------------------------------------------------------
call :create_shortcut

REM --------------------------------------------------------------------------
REM 7) Proposer de lancer immediatement
REM --------------------------------------------------------------------------
call :prompt_run

call :ok "FIN DU SCRIPT"
goto :end


REM ============================== FONCTIONS ===============================

:banner
call :ok "INSTALLATION / MISE A JOUR CHAVOST"
exit /b 0

:ok
echo.
echo ================== %~1 ==================
echo.
exit /b 0

:fail
echo.
echo [ERREUR] %~1
echo.
pause
exit /b 1

:ensure_winget
where winget >nul 2>&1
if errorlevel 1 (
    call :fail "winget n'est pas disponible sur cette machine. Installe Git et Python manuellement puis relance."
)
exit /b 0

:ensure_git
call :ok "Verification de Git"
where git >nul 2>&1
if errorlevel 1 (
    echo Git non detecte. Installation via winget...
    winget install -e --id Git.Git
    if errorlevel 1 call :fail "Echec de l'installation de Git."
)
where git >nul 2>&1
if errorlevel 1 call :fail "Git reste introuvable apres installation."
for /f "tokens=*" %%G in ('git --version 2^>nul') do echo %%G
exit /b 0

:ensure_python
call :ok "Verification de Python"
where python >nul 2>&1
if errorlevel 1 (
    echo Python non detecte. Installation via winget...
    winget install -e --id Python.Python.3.12
    if errorlevel 1 call :fail "Echec de l'installation de Python."
)
where python >nul 2>&1
if errorlevel 1 call :fail "Python reste introuvable apres installation."
for /f "tokens=*" %%P in ('python --version 2^>nul') do echo %%P

REM S'assure que pip est disponible
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo pip non detecte. Tentative d'activation...
    python -m ensurepip --upgrade >nul 2>&1
    python -m pip --version >nul 2>&1
    if errorlevel 1 call :fail "pip est indisponible."
)
exit /b 0

:select_install_dir
call :ok "Choix du dossier d'installation"
set "INSTALL_DIR="
set /p INSTALL_DIR="Chemin d'installation (ex: C:\Users\utilisateur\Documents) : "
if "%INSTALL_DIR%"=="" call :fail "Aucun chemin saisi."

if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%" >nul 2>&1
if errorlevel 1 call :fail "Impossible de creer le dossier d'installation."

set "APP_ROOT_DIR=%INSTALL_DIR%\%APP_ROOT_FOLDER%"
set "TARGET_DIR=%APP_ROOT_DIR%\%PROJECT_FOLDER_NAME%"

if not exist "%APP_ROOT_DIR%" mkdir "%APP_ROOT_DIR%" >nul 2>&1
if errorlevel 1 call :fail "Impossible de creer le dossier application."

echo Dossier application : "%APP_ROOT_DIR%"
echo Dossier projet      : "%TARGET_DIR%"
exit /b 0

:sync_repo
call :ok "Synchronisation du projet"

if exist "%TARGET_DIR%\.git" (
    echo Mise a jour du projet...
    pushd "%TARGET_DIR%" || call :fail "Impossible d'entrer dans le dossier projet."
    git remote set-url origin "%REPO_URL%"
    if errorlevel 1 (popd & call :fail "Echec configuration remote Git.")
    git fetch --prune
    if errorlevel 1 (popd & call :fail "Echec git fetch.")
    git checkout %GIT_BRANCH% >nul 2>&1
    git pull origin %GIT_BRANCH%
    if errorlevel 1 (popd & call :fail "Echec git pull.")
    popd
) else (
    echo Clonage du projet...
    pushd "%APP_ROOT_DIR%" || call :fail "Impossible d'entrer dans le dossier application."
    git clone "%REPO_URL%" "%PROJECT_FOLDER_NAME%"
    if errorlevel 1 (popd & call :fail "Echec du clonage.")
    popd

    pushd "%TARGET_DIR%" || call :fail "Projet clone mais dossier inaccessible."
    git remote set-url origin "%REPO_URL%"
    if errorlevel 1 (popd & call :fail "Echec configuration remote Git apres clone.")
    git checkout %GIT_BRANCH% >nul 2>&1
    popd
)

exit /b 0

:ensure_uv
call :ok "Verification de uv"
where uv >nul 2>&1
if errorlevel 1 (
    echo uv non trouve. Installation via pip...
    python -m pip install --upgrade uv
    if errorlevel 1 call :fail "Echec installation uv."
)
for /f "tokens=*" %%U in ('uv --version 2^>nul') do echo uv : %%U
exit /b 0

:create_launcher
call :ok "Creation du lanceur local"
set "LAUNCHER_PATH=%APP_ROOT_DIR%\lanceur_chavost.bat"

(
    echo @echo off
    echo setlocal EnableExtensions
    echo cd /d "%TARGET_DIR%"
    echo REM Mise a jour du depot (repo prive)
    echo git remote set-url origin "%REPO_URL%"
    echo git pull origin %GIT_BRANCH%
    echo %UV_RUN_COMMAND%
    echo pause
) > "%LAUNCHER_PATH%"

if errorlevel 1 call :fail "Impossible de creer le lanceur."

echo Lanceur : "%LAUNCHER_PATH%"
exit /b 0

:create_shortcut
call :ok "Creation du raccourci Bureau"

set "DESKTOP_DIR=%USERPROFILE%\Desktop"
if not exist "%DESKTOP_DIR%" set "DESKTOP_DIR=%USERPROFILE%\Bureau"

set "SHORTCUT_PATH=%DESKTOP_DIR%\Chavost.lnk"
set "ICON_PATH=%TARGET_DIR%\image\logo.ico"

REM Cree le raccourci via PowerShell
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
"$s=(New-Object -COM WScript.Shell).CreateShortcut('%SHORTCUT_PATH%');" ^
"$s.TargetPath='%LAUNCHER_PATH%';" ^
"$s.WorkingDirectory='%APP_ROOT_DIR%';" ^
"if (Test-Path '%ICON_PATH%') { $s.IconLocation='%ICON_PATH%' }" ^
"$s.Save();"

if errorlevel 1 call :fail "Echec creation du raccourci Bureau."

echo Raccourci : "%SHORTCUT_PATH%"
exit /b 0

:prompt_run
call :ok "Lancement"
choice /M "Lancer Chavost maintenant"
if errorlevel 2 exit /b 0
call "%LAUNCHER_PATH%"
exit /b 0

:end
endlocal
exit /b 0
