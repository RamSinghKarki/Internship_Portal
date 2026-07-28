@echo off
REM ============================================================
REM  Run all test cases of the Internship Portal
REM  (uses a separate database: internship_db_test)
REM ============================================================
echo Running all test cases...
echo.
python -m pytest tests/ -v
echo.
pause
