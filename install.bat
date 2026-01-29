
poetry build

for %%F in (dist\automatey-*-py3-none-any.whl) do (
    python -m pip install "%%F" --force-reinstall
)

pause