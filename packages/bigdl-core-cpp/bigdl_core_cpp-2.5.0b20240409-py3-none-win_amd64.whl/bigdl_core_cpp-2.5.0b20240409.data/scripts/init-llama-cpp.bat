@echo off
for /f "delims=" %%i in ('python -c "import bigdl.cpp; print(bigdl.cpp.__file__)"') do set "cpp_file=%%i"
for %%a in ("%cpp_file%") do set "cpp_dir=%%~dpa"

set "cpp_dir=%cpp_dir:~0,-1%"
set "lib_dir=%cpp_dir%\libs"
set "destination_folder=%cd%"

pushd "%lib_dir%"
for %%f in (*) do (
    mklink "%destination_folder%\%%~nxf" "%%~ff"
)
popd

copy "%cpp_dir%\convert.py" .
