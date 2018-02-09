# Locally debugging your Reactor

Reactors are containers that Abaco runs according to some easily-emulated 
conventions. This is helpful for local debugging! Here are some helpful recipes
for local testing during development. 

## Build just the target Reactor container

`abaco deploy -R`

Your deploy will terminate with test resembling

```shell
Successfully built 501bb032c449
Successfully tagged sd2e/manifest_to_fcs_etl_param:0.1
[INFO] Stopping deployment as this was only a dry run!
```

Snippet `sd2e/manifest_to_fcs_etl_param:0.1` is the value for 
`CONTAINER_IMAGE` in recipes below.

## Running your Reactor container with one or more environment variables

```shell
docker run -e KEY1=VALUE1 -e KEY2=VALUE3 CONTAINER_IMAGE
```

If you were to inspect the `Reactor.context` you would see there are two
environment variables, `KEY1` and `KEY2` with value of `VALUE1` and `VALUE3`
respectively available inside the container. 

## Running your Reactor with a message

To keep things simple, almost all messages sent a Reactor are via the `MSG`
environment variable. There's a special binary class of Reactor but that's
outside present scope. To message your Reactor, set a variable `MSG`. The 
only tricky part is wrapping JSON. Use the example here as a guide. 

```shell
docker run -e MSG='{"key1":"value1", "key2":"value3"}' CONTAINER_IMAGE
```

Inside the Reactor, `Reactors.context.message_dict` will contain these 
key:value pairs derived from the JSON message.

## Running your Reactor with a bootstrapped Agave client

Reactors act as Agave scripting environments because the Abaco platform boot-
straps a temporary, fully-authenticated Agave API client which is available as 
`Reactor.client`. Since you're working with Reactors already, you have a local
client that can be borrowed for local testing. To do this, we need to inject 
your personal client into the container at the appropriate path.

```shell
docker run -v $HOME/.agave:/root/.agave \
           -e MSG='{"key1":"value1", "key2":"value3"}' CONTAINER_IMAGE

```

Now, any AgavePy calls made to `Reactor.client` will run. One caveat here is 
that those calls will be made with your personal authorization so if you're
building something that assumes somehow to run under a different TACC Cloud 
account (a rare use case but one that does happen), your mileage may vary.

## Running your Reactor with a bootstrapped local directory

Reactors default to reading and writing to `/mnt/ephemeral-01` which is
readable and writeable by any uid/gid combination. It's guaranteed to be
empty each time for each new execution. 

Create a temporary directory, make sure it's empty, and do the following to
emulate this process. 

```shell
TEMP=`mktemp -d $PWD/tmp.XXXXXX` \
docker run -v $TEMP:/mnt/ephemeral-01 CONTAINER_IMAGE
```

## Overriding the default entrypoint

By default, a Reactor will try to just run `python /reactor.py` but if you
want to override that behavior, pass `--entrypoint ` and, if needed, options 
for the commmand to run Here's an example.

```shell
# Command only
docker run --entrypoint uname CONTAINER_IMAGE

# Command with parameters
docker run --entrypoint uname CONTAINER_IMAGE -a
```

## Getting an interactive session

To get deep in the innards of your Reactor, pass `-it` and set the entrypoint 
to a shell you know is in the container image. TACC Reactors' base image is
derived from ubuntu:xenial at present at has a reasonable complement of shells.
If you are working with a container and get an error no matter what shell you
try, it's probably derived from a minimal image like `alpine' in which case 
the shell you have at your disposal is good old `sh`

```shell
docker run -it --entrypoint bash CONTAINER_IMAGE
```

Combine any of the other options above with this recipe to set up the 
environment you expect your Reactor container to have during an execution 
instance. Good luck!

