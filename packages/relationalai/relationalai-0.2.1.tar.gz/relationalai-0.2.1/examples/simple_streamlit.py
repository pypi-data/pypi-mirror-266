#pyright: reportUnusedExpression=false

import relationalai as rai
import streamlit as st
import pandas as pd

model = rai.Model("MyCoolDatabase")
Person = model.Type("Person")
Adult = model.Type("Adult")

Person.add(name="Joe", age=54)
Person.add(name="Bob", age=40)
Person.add(name="Jane", age=10)

with model.rule():
    p = Person()
    p.age > 18
    p.set(Adult)

st.header("Adults above a certain age")
min_age = st.number_input("Age", min_value=0, max_value=100, value=18, step=1, key="age")

with st.spinner("Running query..."):
    with model.query() as select:
        a = Adult()
        a.age > min_age
        z = select(a, a.name, a.age)

st.table(pd.DataFrame(z.results, columns=["id", "name", "age"]))



