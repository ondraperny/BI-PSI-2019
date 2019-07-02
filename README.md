# BI-PSI-2019

Python server that control simple robot movements(turn left/right, go straight) in 2D space. 
Robot must be navigated to specific set of coordinates and there seek special coordinate with "treasure".
Server use threading. Therefore can operate multiple robots simultaneously.

---
For testing is provided compiled file `psi-tester-2018-t1-v3_x64`. First start server in background and then tester
with parameters `PORT` (14781) and `HOST` (for testing purposes used localhost). Series of 30 tests will be executed.

    python3 pycharm/main.py &
    ./psi-tester-2018-t1-v3_x64 14781 0.0.0.0
    

	


