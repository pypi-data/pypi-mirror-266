import relationalai as rai
from relationalai.std import alias

model = rai.Model('EVPenetrationExample')
State = model.Type('State')

# Load data from azure blob storage before running the script
# rai imports:snapshot --source "azure://raidocs.blob.core.windows.net/datasets/states/state_stats.csv" schema:state_name=string schema:area=int schema:population=int schema:ev_registration_count=int

# Or load data from a local CSV file using either a relative path, as below, or an absolute path.
# rai imports:snapshot --source "examples/ev_penetration/state_stats.csv" schema:state_name=string schema:area=int schema:population=int schema:ev_registration_count=int

# Read data from csv file
with model.read("state_stats.csv") as row:
    state = State.add(name=row.state_name).set(area=row.area, population=row.population, ev_registration=row.ev_registration_count)

# Query the collection
with model.query() as select:
    state = State()
    ev_penetration = 1000 * state.ev_registration / state.population
    response = select(
        state.name,
        state.population,
        state.ev_registration,
        alias(ev_penetration, "ev_penetration"),
    )

# Display the results sorted in descending order by the `ev_penetration` column
print(response.results.sort_values(by="ev_penetration", ascending=False))

