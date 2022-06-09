Requirements:  
> git clone --recurse-submodules https://github.com/ikaneViasat/gRPC-Fuzzer.git

> sudo apt install -y protobuf-compiler python3 python3-pip git cmake

> pip3 install -r requirements.txt

> cd dependencies/protofuzz && sudo python3 setup.py install

Inside dependencies/protofuzz if changes are made to protofuzz sudo pip3 uninstall it and install it using:
 > sudo python3 setup.py install

Note that compiled_proto has a symlink to /tmp which is where protofuzz puts compiled proto files.

To Run:
python3 client.py

To add your own proto:
Create a client in the main function of client.py
