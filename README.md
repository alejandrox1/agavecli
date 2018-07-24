# AGAVECLI

`agavecli` is a command line interface, writen in python, for the Agave platform.
This is arewriting of [TACC-Cloud/agave-cli](https://github.com/TACC-Cloud/agave-cli).

This repo is still under development. New commands will be added along with
patches unles a change is require of the interface.

Working towards a complete test coverage and full documentation of `agavecli`,
the (Agave API](https://agaveapi.co/), along with developer documentation. So
there is plenty more to come!


## Taking `AGAVECLI` out for a Test Drive
Right now the package can only be installed from source so...
```shell
git clone https://github.com/alejandrox1/agavecli && \
    cd agavecli && \
    make install
```

Test it out:
```shell
# List all commands
agavecli -h
```

### Agavecli Container
You know what's even better than installing from source? Installing nothing at
all! Check out [agavecli conatiners](/docker) and simply use the helper scripts
`run-agavecli.sh` instead of `agavecli`. 

For example, go to [agavecli alpine container](/docker/alpine_python3)
and run:
```shell
./build-agavecli.sh

./run-agavecli.sh tenant ls
```

## Agave Credentials
User credentials and tenant information will be stored by default on the user's
home directory in a file named agave.json.

To switch between tenants simply use the command `tenant init <tenant>`.



## Working with Agave Tenants
```shell
# See all commands available to manage agave tenants
agavecli tenant -h

agavecli tenant ls

agavecli tenant init <tenant name>
```

## Managing Oauth Clients
```shell
# See all commands available to manage clients
agavecli client -h

agavecli client ls

agavecli client create -n agavecli_client -d "testing agavecli"
```

## Obtain an Access Token
```shell
# Create an access token
agavecli auth create
```

## Working with Execution and Storage Systems
```shell
# List all execution systems
agavecli system ls -x

# List all storage systems
agavecli system ls -s
```

## Operations on Storage Systems
```shell
# See all commands to work with files
agavecli fs -h


# List contents of a remote storage system.
agavecli fs ls tacc-globalfs-user

# Create directories.
agavecli fs mkdir tacc-globalfs-user/cptests
agavecli fs mkdir tacc-globalfs-user/tests
agavecli fs ls tacc-globalfs-user

# Copy a file from local to remote and back
echo "some txt" > copy.txt
agavecli fs cp copy.txt agave://tacc-globalfs-user/cptests/
agavecli fs cp agave://tacc-globalfs-user/cptests/copy.txt downloaded.txt


# Copy files between remote systems (it does not have to be between same
# storage system ;) )
agavecli fs cp agave://tacc-globalfs-user/cptests/copy.txt agave://tacc-globalfs-user/tests/


# Coolest command (it adapts to the size of your terminal)!
agavecli fs ls tacc-globalfs-user

agavecli fs ls -l tacc-globalfs-user
```
