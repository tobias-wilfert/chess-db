# chess-db
A Python-based chess explorer.


## Installation of Pylucene

See [here](https://lucene.apache.org/pylucene/install.html) for more details.

```bash
cd pylucene-9.7.0/jcc
python setup.py build
sudo python setup.py install
cd ../
make
make test
sudo make install
```

__Notes:__ Make sure to be in the venv and to use the correct version of java for the gradle and to adjust the makefile to your system. The python in the make needs to point to the python in the venv. Also that python needs to have wheel installed


# ON Windows via WSL
1. Fetch the tar.gz file from the apache website (I used pylucene-9.4.1 as 9.7.0 seems to contain a bug)
## JCC
2. Read the notes for Linux to setup your WSL environment
```bash
sudo -s
apt install wget apt-transport-https gnupg
wget -O - https://packages.adoptium.net/artifactory/api/gpg/key/public | apt-key add -
echo "deb https://packages.adoptium.net/artifactory/deb $(awk -F= '/^VERSION_CODENAME/{print$2}' /etc/os-release) main" | tee /etc/apt/sources.list.d/adoptium.list
apt update


apt install temurin-17-jdk


sudo apt install gcc-x86-64-linux-gnu g++-x86-64-linux-gnu make
sudo apt install python3.9-dev python3-venv python3-setuptools

```

 
3. Connect to WSL via VSCode: [link](https://ruslanmv.com/blog/Python3-in-Windows-with-Ubuntu) 
4. open the project by navigating to `mnt/c/Users/your_user/.../chess-db`
5. `(Optional)` make virtual environment 
```bash	
sudo apt-get install python3.9-venv
python3.9 -m venv myenv
source myenv/bin/activate
```
6. if not using virtual environment, make sure to use the correct python version (in `bin/` folder and not `usr/bin/`)
