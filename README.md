# Airflow Spell Operator

## Install

Checkout locally; 

`$ git clone --recurse-submodules git@github.com:healx/airflow-spell.git`


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
- `$ make build` - builds the airflow environment with `spell` installed
- `$ make webserver` - launches airflow environment with dags in `integraion-test/dags` mounted as a dag bag.
