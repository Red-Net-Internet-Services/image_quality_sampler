@echo off

for /r %%i in (*.pyc) do del /f /q "%%i" 2>nul
for /r %%i in (Thumbs.db) do del /f /q "%%i" 2>nul
for /r %%i in (*~) do del /f /q "%%i" 2>nul
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d" 2>nul

rmdir /s /q .cache 2>nul
rmdir /s /q .pytest_cache 2>nul
rmdir /s /q .mypy_cache 2>nul
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul
rmdir /s /q *.egg-info 2>nul
rmdir /s /q htmlcov 2>nul
rmdir /s /q .tox 2>nul
rmdir /s /q docs/_build 2>nul
