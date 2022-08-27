import pathlib

filepath = pathlib.Path(__file__).parent.resolve()
currdir = pathlib.Path().resolve()

print(filepath)
print(currdir)
