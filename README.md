Requirements:  
git clone --recurse-submodules #TODO: update giturl
> sudo apt install -y protobuf-compiler python3 python3-pip git cmake

> pip3 install -r requirements.txt

inside dependencies/protofuzz:
 > sudo python3 setup.py install
 
If changes are made to protofuzz pip3 uninstall it and reinstall.

inside dependencies/your-api-proto:  
 > make python_out

> PYTHONPATH=. python3 client.py
