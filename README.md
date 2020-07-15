# Airflow Spell Operator

## Install

One of;
- Run `$ pip install -e .` in this directory
- Add `airflow_spell` to the `PYTHONPATH` environment variable
- Add `airflow_spell` to the airflow plugins directory


## Connection

The default connection id is called `spell_conn_id` (but this can be over-ridden in `SpellRunOperator`). 

The following fields in the connection map to the spell.run authentication system;
    
- `password: str` put your spell.run `token` here (from `~/.spell/config` when authenticated from the CLi).
- `host: Optional[str]` your spell.run "owner" - the entity that "owns" some object in spell - useful if 
you wish to launch runs in a team account, where `host` could be your team name. 

## Testing

Run a demonstration airflow environment;
- `$ make build` - builds the airflow docker image with `spell` installed
- `$ make up` - launches airflow environment at http:/0.0.0.0:8080

### Testing DAGs

DAGs in [`dags`](dags/) directory will be visible to the testing airflow instance

### Provisioning the Spell Connection

Put the token from above in a file in the root of the directory called `settings.env`

```
SPELL_TOKEN=<... your spell token ...>
```

Then issue `$ make add-spell-connection` and (as long as the docker-compose cluster is running)
the spell credentials are added to the airflow connections list.

## Building and Releasing

To build the source and binary distributions run

```
$ make release
```
This requires `twine` to be installed - it is listed in [`dev-requirements.txt`](dev-requirements.txt).

(Remember to bump the version number in [`setup.py`!](setup.py).)

To upload the release, run

```
$ make upload-release
```
NB You will be prompted for a pypi username and password.

## Notes about previous versions

* apache-airflow 1.10.6

This version has an unmet / unlisted dependecy on `blinker`. The `blinker` module must be installed when
installing this version of apache-airflow.
