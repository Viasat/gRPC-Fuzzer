Requirements:  
git clone --recurse-submodules #TODO: update giturl
> sudo apt install -y protobuf-compiler python3 python3-pip git cmake

> pip3 install -r requirements.txt

Inside dependencies/protofuzz if changes are made to protofuzz pip3 uninstall it and install it using:
 > sudo python3 setup.py install

symlink compiled_proto/x to your x python gRPC files which you can submodule in dependencies.

python3 client.py
