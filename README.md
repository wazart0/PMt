## Requirements

- Windows 10 PRO (on Linux should be possible to run, but it haven't tested yet)

- Docker:
    * https://docs.docker.com/install/
    * post instalation steps for Linux for using docker without sudo:
        * https://docs.docker.com/install/linux/linux-postinstall/
        
- Docker network, where host computer has IP address: 10.0.75.1

- PowerShell with privileges to run scripts:
    * eg. `Set-ExecutionPolicy -Scope CurrentUser Unrestricted`

   
## Run

- Windows:
    1. Database: `./runDB.ps1`
    2. Backend: `./runBackend.ps1`
    3. Frontend: `todo`

- Linux (not tested yet):
    1. Database: `bash ./runDB.ps1`
    2. Backend: `bash ./runBackend.ps1`
    3. Frontend: `todo`


## Server accesss
- DB: http://localhost:54321/
- Backend: http://localhost:8000/
- Frontend: `todo`
