@echo off
REM Betfair Paper Trading - Scheduled for 10am daily
REM Runs paper trading study with real Betfair prices

cd C:\Users\aaron\.openclaw\workspace

echo Starting paper trading study at %date% %time% >> paper_trading.log
python paper_trading_study.py >> paper_trading.log 2>&1
echo Completed at %date% %time% >> paper_trading.log
echo ---------------------------------------- >> paper_trading.log
