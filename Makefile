# Makefile

# Variables
PYINSTALLER = pyinstaller
MAIN_SCRIPT = main.py
BINARY = ".\mouse\Lib\site-packages\autoit\lib\AutoItX3_x64.dll;autoit\lib"
ZIP_FILE = ro_script.zip

# PyInstaller command
.PHONY: all clean main package upload

all: clean main package upload

main:
	$(PYINSTALLER) --onefile --add-binary $(BINARY) $(MAIN_SCRIPT)

package:
	@echo Packaging files into $(ZIP_FILE)...
	powershell -NoProfile -Command "Compress-Archive -Path 'lib', 'dist/main.exe', 'start.bat', 'photo', 'clean.bat' -DestinationPath '$(ZIP_FILE)' -Force"

# Clean up build files
clean:
	rm -rf build dist *.spec __pycache__ $(ZIP_FILE)

upload:
	cp dist/main.exe .
	cmd "/C upload.bat"