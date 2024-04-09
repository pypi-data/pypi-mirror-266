import sys

from .cleaner import clean_metadata

with open(sys.argv[2], "rb") as f:
    with open(sys.argv[2] + ".cleaned.pdf", "wb") as w:
        w.write(clean_metadata(f.read(), sys.argv[1]))
