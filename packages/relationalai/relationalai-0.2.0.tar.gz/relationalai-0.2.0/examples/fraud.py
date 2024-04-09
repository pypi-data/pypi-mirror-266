import gravis as gv
import relationalai as rai

model = rai.Model("ibdknox")

Person = model.Type("Person")
Adult = model.Type("Adult")
Customer = model.Type("Customer")
Criminal = model.Type("Criminal")
Transaction = model.Type("Transaction")
Suspicious = model.Type("Suspicious")
ImmediateReview = model.Type("ImmediateReview")

with model.rule():
    (id, name, age, account, criminal) = rai.csv.load_file(model, "data/people.csv")
    p = Person.add(name=name, age=age, csv_id=id)
    with account:
        p.set(Customer, account=account)
    with criminal:
        p.set(Criminal)

with model.rule():
    (txn_id, date, from_id, to_id, amount) = rai.csv.load_file(model, "data/transactions.csv")
    Transaction.add(txn_id=txn_id, date=date, from_=Customer(csv_id=from_id), to_=Customer(csv_id=to_id), amount=amount)

with model.query() as select:
    s = Transaction()
    res = select(s, s.from_.name, s.to_.name, s.amount)

with model.rule():
    t = Transaction(from_=Customer(), to_=Criminal())
    t.set(Suspicious)
    with t.amount > 40000:
        t.set(ImmediateReview, review_reason="Large transaction to criminal")

with model.query() as select:
    s = ImmediateReview()
    res = select(s.from_.name, s.to_.name, s.amount)

with model.rule():
    s = Suspicious(Transaction)
    s.from_.set(Suspicious)
    s.to_.set(Suspicious)

with model.query() as select:
    c = Criminal()
    criminals = select(c)

criminals = set(criminals.results['criminal'])

# Create edges

with model.query() as select:
    s = Suspicious(Transaction)
    edges = select(s.from_, s.to_, s.amount)

# Create nodes

with model.query() as select:
    s = Suspicious(Person)
    nodes = select(s, s.name)

graph1 = {
    'graph': {
        'directed': True,
        'metadata': {
            'arrow_size': 5,
            'background_color': 'black',
            'edge_size': 3,
            'edge_label_size': 10,
            'edge_label_color': 'white',
            'edge_color': '#777',
            'node_size': 15,
            'node_color': 'white',
            'node_label_color': 'white',
            'node_label_size': 10,
        },
        'nodes': {
            node_id: {'metadata': {'name': name,
                                  'color': '#f88' if node_id in criminals else 'white',
                                  }} for (node_id, name) in nodes
        },
        'edges': [
            {
                'source': source,
                'target': target,
                'metadata': {
                    'color': '#f44' if amount > 40000 else '#777',
                             'label_color': 'orange' if amount > 40000 else '#ccc',
                            'amount': f"${amount/1000:,.0f}k"}
            } for (source, target, amount) in edges
        ],
    }
}

fig = gv.vis(graph1,
       # show_edge_label=True,
       node_label_data_source='name',
       edge_label_data_source='amount',
       layout_algorithm='forceAtlas2Based',
       central_gravity=2.69,
       spring_length=13)
fig.display()

