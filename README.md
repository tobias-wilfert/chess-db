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