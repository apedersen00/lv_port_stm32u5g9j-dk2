@echo off

REM Define paths
set PROGRAMMER_CLI="C:\Program Files\STMicroelectronics\STM32Cube\STM32CubeProgrammer\bin\STM32_Programmer_CLI.exe"
set EXTERNAL_LOADER="C:\Program Files\STMicroelectronics\STM32Cube\STM32CubeProgrammer\bin\ExternalLoader\MX66LM1G45G_STM32U5G9J-DK2.stldr"

REM Define files and addresses
set INPUT_BIN=%~dp0build\STM32U5G9J-DK2_LVGL.elf

REM Flashing the signed binary
%PROGRAMMER_CLI% -c port=SWD mode=NORMAL freq=8000 -el %EXTERNAL_LOADER% -d %INPUT_BIN% -s