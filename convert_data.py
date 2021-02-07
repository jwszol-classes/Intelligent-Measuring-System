import os

files = os.listdir()
for file in files:
    if file in ["convert.py"]:
        continue

    zoom, col, row = file.split(".")[0].split("-")
    if int(col) < 10:
        col = "0" + col
    if int(row) < 10:
        row = "0" + row

    new_name = zoom + "-" + col + "-" + row + ".png"
    os.rename(file, new_name)
