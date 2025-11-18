REM -------------------------------------------------------------------------
REM 3) Clone ou mise à jour du dépôt
REM -------------------------------------------------------------------------

where git >nul 2>&1
if errorlevel 1 (
    echo Git n'est pas installe. Installe Git puis relance ce script.
    goto :end
)

if exist "%TARGET_DIR%\.git" (
    echo.
    echo Projet detecte. Recherche de mises a jour...
    pushd "%TARGET_DIR%"

    git fetch origin %GIT_BRANCH%

    for /f "usebackq" %%A in (`git rev-parse HEAD`) do set LOCAL_COMMIT=%%A
    for /f "usebackq" %%B in (`git rev-parse origin/%GIT_BRANCH%`) do set REMOTE_COMMIT=%%B

    if /I "!LOCAL_COMMIT!"=="!REMOTE_COMMIT!" (
        echo Le projet est deja a jour.
    ) else (
        echo Mise a jour disponible. Application...
        git reset --hard origin/%GIT_BRANCH%
    )

    popd
) else (
    echo.
    echo Aucun projet detecte, clonage...
    pushd "%APP_ROOT_DIR%"
    git clone "%REPO_URL%" "%PROJECT_FOLDER_NAME%"
    if errorlevel 1 (
        echo Echec du clonage du projet. Abandon.
        goto :end
    )
    popd
)

REM -------------------------------------------------------------------------
REM 4) Vérification UV
REM -------------------------------------------------------------------------

echo.
echo Vérification de la présence de uv...
where uv >nul 2>&1
if errorlevel 1 (
    echo uv non trouve. Installation via pip...
    python -m pip install uv
    if errorlevel 1 (
        echo Echec installation de uv. Abandon.
        goto :end
    )
)

REM -------------------------------------------------------------------------
REM 5) Aller dans le dossier du projet et lancer Chavost
REM -------------------------------------------------------------------------

echo.
echo Déplacement vers le dossier : "%TARGET_DIR%"
cd "%TARGET_DIR%"

echo ================== LANCEMENT DE CHAVOST ==================
%UV_RUN_COMMAND%