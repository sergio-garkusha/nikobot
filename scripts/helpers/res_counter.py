import json

with open("./parsed_results.json", encoding='utf-8') as f:
    data = json.load(f)

    counter = 1
    for item in data:
        print(counter)
        counter = counter + 1

    print(f"\nTotal: {counter}")
