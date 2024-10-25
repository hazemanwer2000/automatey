@ECHO OFF

REM Track all non-ignored file(s).
git add .

REM Remove all untracked file(s).
git clean -fdx

REM Re-install 'automatey' package.
py -m pip install -e .