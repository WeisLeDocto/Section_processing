:: File for compiling the image selection into an executable file in windows

where /q pyinstaller
if errorlevel 1 (
    echo You need to install the python module pyinstaller for compiling the image selection script !
) else (
    pyinstaller selection.py --name section_selection --paths .\venv\Lib\site-packages\ --noconfirm --add-data ".\openslide-win64\;openslide-win64"
)
