# Agavecli on Containers

The collection of dirs under `docker/` serve a dual purpose:
1. Run Agavecli on a conatiner
2. Integration tests


So go ahead and give it a try!

First build the image (this will create `agavecli` image)
```shell
./build-agavecli.sh  
```

then go ahead and use it as normal:
```shell
./run-agavecli.sh -h

./run-agavecli.sh tenant init <your fav tenant>

./run-agavecli.sh fs ls tacc-globalfs-user
```
