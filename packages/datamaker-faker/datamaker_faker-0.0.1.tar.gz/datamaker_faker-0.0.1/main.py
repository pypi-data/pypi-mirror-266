import json
from datamaker_faker import Faker

# define your data model
model = {
    "first": "first_name",
    "last": "last_name",
    "sex": "sex",
    "city": "city",
    "country": "country",
}

# create a new faker instance
faker = Faker(model, seed=9)

# generate some fake data
df = faker.generate(10)

# write the data to a csv file
df.to_csv("datafaker.csv")

# or leverage pandas to convert the data to json
data = df.to_dict("records")
print(json.dumps(data, indent=2))
