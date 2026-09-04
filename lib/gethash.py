import xxhash
import os
import sys
import json

mmmx = {}

dt = os.listdir(".")
for r in dt:
    if r.startswith("RBX"):
        with open(r, "rb") as file:
            data = bytearray(file.read())
            hsh = xxhash.xxh3_64_hexdigest(data)
            mmmx[r] = hsh
            print(hsh)

json.dump(mmmx, open("hashdump2.json", "w"), indent=2)