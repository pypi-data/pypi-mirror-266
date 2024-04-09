# Quickstart

This quickstart takes you through the basic building blocks of Rel: objects, rules, and functions. We'll walkthrough a simple banking fraud example to ground ourselves. Here's what it'll look like by the end, just to give you a sense of what Rel is like.

```
use csv
use snowflake.fraud.{Transaction, Criminal, ReviewQueue}
use graph.{shortest, edge!}

add {Person name:"Joe" age:30}
add {Person name:"Jane" age:30}

if {:person Person age > 18}
    then person.Adult

// Load and validate people

if let {name, age, account?} = csv.load("people.csv")
   ensure {:person Person name age}
   and if account
       then {:person Customer account}

if {:c Customer} and not c.Adult
    then {Error message: "Customers must be adults"}

// Look for suspicious transactions

if {:txn Transaction from:{Customer} to:{Criminal}}
   then txn.Suspicious
   if txn.amount > 10_000
       then {:txn ImmediateReview review_reason: "Large transaction to criminal"}

let Transfer = edge!(Transaction, Transaction.from, Transaction.to)

if path = shortest({Criminal} to {Transfer} 1..2 to {Criminal})
   start = path.edges[0]
   then {:start ImmediateReview
                path:path.edges
                review_reason:"Criminal to criminal transaction"}

// Write back to the ReviewQueue in snowflake

if {Transaction:txn ImmediateReview}
    then add {ReviewQueue transaction:txn reason:txn.review_reason path:txn.path or [txn]}

```



## Objects

Rel is a relational language, which means that under the covers everything is represented as normalized tables, but that can be quite hard to work with. So instead, Rel presents us with objects, which you can think of as being similar to JSON objects with a little bit of sugar to make working with them nicer. As an example, let's add a couple of objects into our system.

```
add {Person name:"Joe" age:30}
add {Person name:"Jane" age:48}
```

Since we don't give the `Person` property a value, it acts as a boolean. By convention we capitalize properties that represent types (e.g Person, Student, Employee) and put them first to make the intent clearer.

Like in JSON, these objects can be nested:

```
add {Person name:"Derek" age:26 pet: {Dog name:"Henry"}}
```

And since types are represented as boolean properties, there's no problem with having multiple:

```
add {Person Student name:"Swetha" age:14}
```

## Rules
Now that we have data to work with, we want to be able to query it and do something with the results. Rules allow us to search for logical patterns and then specify what we'd like to happen if that pattern is found. Patterns look just like the objects we added above, so if we wanted to find all the people named Bob and get their age we could write:

```
{Person name:"Bob" age:age}
```

That pattern would find all the people with a name property equal to "Bob" and bind their age to an `age` variable. Since the name of the property and the name of the variable are the same, you could leave out the `:age` and get the same result:

```
{Person name:"Bob" age}
```

Now that we have age bound to a variable, we can add a constraint that age must be greater than 18:

```
{Person age} and age > 18
```

You could also inline that constraint directly if you don't need the age variable for anything else:

```
{Person age > 18}
```

The last thing we need from patterns is a way to reference this particular object. We do that by binding the object to a variable using `:some_name` after the `{`.

```
{:bob Person name:"Bob"} and bob.age > 18
```

Great, so we have the ability to create patterns of objects to find, let's use that to create a rule that says any person under 18 is a minor:

```
if {:person Person age < 18}
    then person.Minor
```

Rules always have this structure of `if ... some patterns ... then ... some actions ...` and they're automatically maintained by the system. Since Rel is relational, actions take the form of changing data. So in this case, if a new person under the age of 18 is added they will have the `Minor` property added to them. Similarly if a person's age changes to be 18 or older, the `Minor` property will be removed from them. As long as all the patterns in the rule match, the person will be a Minor. That's the guarantee this rule makes.

We could add the equivalent rule for adults:

```
if {:person Person age >= 18}
    then person.Adult
```

It's worth noting we could also write this as an extension of the person object, which can be nice if you have multiple properties to set:

```
if {:person Person age >= 18}
    then {:person Adult Voter}
```

In some cases, you want to permanently say something about an object and not have the rule retract what it said if the conditions are no longer met. To do that you would use the `add` action:

```
if {:person Person age < 18}
    then add person.Minor
```

Now the `Minor` attribute will be added to any person under 18, but it won't be removed if they grow up. Instead you'd have to write a rule that removes it:

```
if {:person Person age >= 18}
    then remove person.Minor
```

In general, it's best to just make statements about the world and let the system handle keeping them up to date, but this power of complete control is there if you need it.

## Loading data and validating it

Let's breakdown a more sophisticated rule that loads some data about people from a CSV file:

```
use csv

if let {name, age, account?} = csv.load("people.csv")
   ensure {:person Person name age}
   and if account
      then {:person Customer account}
```

The `use csv` statement here imports the CSV library and makes it available to us. We then call the `csv.load` function to parse a CSV file into objects per row with properties based on the column headers. The `let` keyword makes sure that our pattern isn't matched with other objects in the system, just the ones `csv.load` returns. This makes it similar to destructing in other languages you may be familiar with.

You'll also note that the account property has a `?` at the end of it. Rel doesn't allow nulls to enter the system, but external resources often have missing data. The `?` here says that we know account may not be provided for each row and we'll have to explicitly check for its existence before using it. If we didn't have the `?` the first time we tried to load a row without an account column, we'd get an error.

```
    ensure {:person Person name age}
```

The next line uses the `ensure` keyword, which you can think of as "find or insert." So in this case, it says that if we have a person with the name and age in the CSV, then we should use that person, otherwise we should add a new person with those values.

Because both the found person and the added person are bound to the `person` variable, we can use that variable in the rest of the rule to correctly refer to whichever is chosen.

```
    and if account
       then {:person Customer account}
```

The last two lines then check if the account column was provided and if so, we reference our person object and extend with a Customer property and the account value from the CSV.

Now that we have a bunch of customers loaded, we want to make sure our data is correct. As an example validation, let's say that all customers must be adults:

```
if {:c Customer} and not c.Adult
    then {Error message: "Customers must be adults"}
```

By creating an `Error` object, we're telling the system that integrity has been violated and we should abort the current transaction. Because we can express validataion as just regular rules that produce `Error` objects, we have the full power of the language to express our intent.

## Analyzing data in Snowflake using graphs

As a coprocessor, we can also write rules that query data in our Snowflake databases. For example, we could write a rule that finds all transactions from a customer to a criminal and marks them as suspicious. The first step is to bring in some of our Snowflake tables.

```
use snowflake.fraud.{Transaction, Criminal}
```

Snowflake tables are represented as objects, just like all the rest of the data in the system, so now that we have a reference to the properties that identify transactions and criminals, we can write a rule like normal:

```
if {:txn Transaction from:{Customer} to:{Criminal}}
   then txn.Suspicious
   if txn.amount > 10_000
      then {:txn ImmediateReview review_reason:"Large transaction to criminal"}
```

We can also do some more sophisticated graph traversal, for example we can check for transactions that connect criminals in 2 hops or less and mark those for review:

```
use graph.{shortest, edge!}

let Transfer = edge!(Transaction, Transaction.from, Transaction.to)

if path = shortest({Criminal} to {Transfer} 1..2 to {Criminal})
   start = path.edges[0]
   then {:start ImmediateReview
                path:path.edges
                review_reason:"Criminal to criminal transaction"}
```

These two rules tell us which transactions we need to review, but our review systems query the `ReviewQueue` table in Snowflake, so we need to write our analysis back into that table. Fortunately, we can write to Snowflake in a very similar way to how we read from it; by using objects.

```
use snowflake.fraud.{ReviewQueue}

if {:txn Transaction ImmediateReview}
    then add {ReviewQueue transaction:txn reason:txn.review_reason path:txn.path or [txn]}
```