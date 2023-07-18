# Python 3 server.

Python server controlling simple robot movements (turning left/right, going straight) in a 2D space. The objective is to navigate the robot to a specific set of coordinates and locate a special coordinate with a "treasure". The server utilizes threading, allowing for the simultaneous operation of multiple robots.

---
To perform testing, there is provided tester `psi-tester-2018-t1-v3_x64` simulating the robot clients prompting server for instructions.

Follow these steps:
1. Start the server in the background.
2. Run the tester with the following parameters: `PORT` (set to 14781) and `HOST` (for testing purposes, use "localhost").
```
    python3 pycharm/main.py & ./psi-tester-2018-t1-v3_x64 14781 0.0.0.0
```
 
The tester will execute a series of 30 tests to check the server's functionality.
