import relationalai as rai
from relationalai.std import alias

model = rai.Model('EVPenetrationExample')
State = model.Type('State')

# Add some data to the collection
with model.rule():
    State.add(name='California', population=39_512_223, ev_registration=425_300)
    State.add(name="Delaware", population=973_764, ev_registration=1950)
    State.add(name="Missouri", population=6_137_428, ev_registration=6740)

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
