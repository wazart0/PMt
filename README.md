## Requirements

- Windows 10 PRO (on Linux should be possible to run, but it haven't tested yet)

- Docker:
    * https://docs.docker.com/install/
    * post instalation steps for Linux for using docker without sudo:
        * https://docs.docker.com/install/linux/linux-postinstall/
        
- Docker network, where host computer has IP address: 10.0.75.1

- PowerShell with privileges to run scripts:
  * eg. 'Set-ExecutionPolicy -Scope CurrentUser Unrestricted'
        
## Run

- Windows:
  * Database: './runDB.ps1'
  * Backend: './runBackend.ps1'
  
- Linux (not tested yet):
  * Database: 'bash ./runDB.ps1'
  * Backend: 'bash ./runBackend.ps1'
  
