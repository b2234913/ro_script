## Overview
This repository contains scripts to execute tasks for the Ragnarok game and manage the environment for the tasks. There are two main components: a Python script to run specific tasks and a batch script to facilitate execution.

## Usage

### Python Script: `main.py`

This script is designed to execute various tasks for the Ragnarok game with an optional delay for sending keys.

### Usage:
```
python main.py [-h] -t {make_money,enter_fire_lake,make_fire_lake} [-d DELAY]
```

### Arguments:

- -h, --help: Show help message and exit.
- -t {make_money,enter_fire_lake,make_fire_lake}, --task {make_money,enter_fire_lake,make_fire_lake}: The task to execute. This argument is required.
- -d DELAY, --delay DELAY: The delay time (in milliseconds) for sending keys. Default is 500ms.

### Example:

```
python main.py --task make_money --delay 350
```

This command runs the make_money task with a delay of 350 milliseconds for sending keys.


### Batch Script: `start.bat`

This script is designed to help users select and run the desired task with appropriate permissions and parameters.

### Usage:

1. Open a command prompt with administrator privileges.
2. Navigate to the directory containing start.bat.
3. Run the script by typing start.bat and pressing Enter.

The script will:

1. Check for administrator privileges.
2. Prompt the user to select a task by entering the corresponding number:
    1. make_money
    2. enter_fire_lake
    3. make_fire_lake
3. Prompt the user to enter a delay time in milliseconds. If no input is provided, the default value of 350ms will be used.
4. Run the main.exe with the selected task and delay parameters.

### Example Session:

```
Select the task to execute:
1. make_money
2. enter_fire_lake
3. make_fire_lake
Enter the number of the task: 3
Enter the delay time in milliseconds (default is 350ms):
Running task make_fire_lake with a delay of 350 milliseconds...
```

## Additional Information

To ensure proper functioning of the scripts, make sure to place lib/libomp140.x86_64.dll in the C:\Windows\System32\ directory. This DLL is required for some operations within the scripts.

