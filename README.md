Requirements:
  cmake for the vulnerable C++ example. Refer to that readme if you would like to run that server.
  python 3.8+
> sudo apt install -y python3 python3-pip git

```
git clone --recurse-submodules git@github.com:Viasat/gRPC-Fuzzer.git
```

```
python3 -m pip install virtualenv
python3 -m virtualenv venv
source venv/bin/activate
venv/bin/pip3 install -r requirements.txt
cd dependencies/protofuzz
sudo ../../venv/bin/python3 setup.py install
cd -
```

A COMMON GOTCHA: Inside dependencies/protofuzz if changes are made to protofuzz:
```
cd dependencies/protofuzz
sudo ../../venv/bin/pip3 uninstall protofuzz
sudo ../../venv/bin/python3 setup.py install
cd -
```

Note that compiled_proto has a symlink to /tmp which is where protofuzz puts compiled proto files.

To Run:
```
If not in venv:
source venv/bin/activate

python3 client.py
python3 client.py -h 
```

To add your own proto:
Create a client in the main function of client.py
