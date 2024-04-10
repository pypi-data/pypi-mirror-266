import time
import relationalai as rai
from relationalai.std import rel
from relationalai.clients.snowflake import Snowflake
from relationalai.std import aggregates

model = rai.Model("IMDB_EXAMPLE")

start = time.time()

sf = Snowflake(model)

Title = sf.imdb_example.imdb.titles

with model.query() as select:
    t = Title()
    rel.regex_match(t.genres, "/Documentary/") # Only show the documentaries
    t.startyear > 1915 # Only show the movies after 1915
    aggregates.rank_desc(t.primarytitle) <= 25 # Only show the top 25 movies
    response = select(t.primarytitle, t.genres, t.startyear) # Select the columns to show

print(response.results)

end = time.time()

print("\nDone in {:.2f}s".format(end - start))
