# IMDB titles

This example demonstrates importing a small portion of 10,000 rows from [imdb title data](https://datasets.imdbws.com/) into Snowflake database and finding the top 25 documentaries released after 1915 using the `relational` Python package.

# Files
1. `README.md` - this file
2. `imdb.csv` - the 10,000 rows of data for the import
3. `imdb.py` - the Python file using `relationalai` package

# Steps
1. Import the data into Snowflake via the Snowflake console
2. Sync the data with RAI via `rai CLI`
3. Query the data with Python via `imdb.py`


# 1. Snowflake console setup & data import

- Make sure you are logged in with a role allowing database/schema creation (`ACCOUNTADMIN` for example) or if you already have a database you have permissions to import data into a table.
- For this example the db name will be `imdb_example`. Create the database if you have not already.
- Create schema called `imdb`
- Create a table via the dropdown menu by selecting `Table/From file`
- Select a warehouse and the `imdb.csv` file when prompted. Name the table `Titles`

- In the `Edit Schema` modal we will not do any changes. Click `Load`.
- You should see a modal saying `Successfully Loaded Data`. Click `Done`.

> :bulb: Make sure the role that you are using in your `rai config` has the required permissions to access thew new database and its schemas.

# 2. Syncing the data with `rai cli`

Now that we have the data into Snowflake we need to sync it via data stream into RAI database. Make sure you have the `rai cli` installed and working in order to use it for this step. If you already have the rai cli setup running `python imdb.py` should show a message stating that `imdb_example.imdb.title hasn't been imported into RAI`.

To import use `rai cli` and run:

```
rai imports:stream --source imdb_example.imdb.titles --model IMDB_EXAMPLE
```
You should see a confirmation:
`Stream for imdb_example.imdb.titles created  `

# 3. Querying with PyRel

If the sync was successful we can now query the imported data via `imdb.py` with:

```
python imdb.py
```

> :bulb: In case you see no results check the status of the stream via executing this Snowflake query:

```
SELECT * FROM <YOUR APP NAME>.API.DATA_STREAMS
```
Find the status column for your database stream. It should be in status `CREATED`. If not you need to figure out why the data stream did not work successfully. Executing this stored procedure might give you clues as to why the sync has failed:

```
CALL <YOUR APP NAME>.API.GET_DATA_STREAM('imdb_example.imdb.titles', 'IMDB_EXAMPLE');
```

> :bulb: For more information about loading data into RAI visit [this page](https://github.com/RelationalAI/rai-sf-app-docs/wiki/Reference-%E2%80%90-Loading-Data-into-RAI)
