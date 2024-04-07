echo off

set version=%1

pushd %~dp0

rmdir /S /Q dist

py -m pip install --upgrade build
py -m build
pip install dist/regis-%version%.tar.gz

popd