@ECHO OFF

REM Remove all untracked file(s) and directories.
git clean -fdx

REM Re-install 'automatey' package.
py -m pip install .