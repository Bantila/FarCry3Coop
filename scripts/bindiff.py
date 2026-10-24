import sys

a = open(sys.argv[1], "rb").read()
b = open(sys.argv[2], "rb").read()
assert len(a) == len(b), "sizes differ"
runs = []
i = 0
while i < len(a):
    if a[i] != b[i]:
        j = i
        while j < len(a) and a[j] != b[j]:
            j += 1
        runs.append((i, j))
        i = j
    else:
        i += 1
print("differing runs:", len(runs), "bytes:", sum(j - i for i, j in runs))
for i, j in runs[:40]:
    print(f"  file+0x{i:08x} len {j - i}: {a[i:j].hex()} -> {b[i:j].hex()}")
