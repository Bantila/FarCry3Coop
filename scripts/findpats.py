import sys
pats = {
 "mpdlc1_aegir": b"mpdlc1_aegir\0",
 "bounds 1536 block": bytes.fromhex("55555555555545"),
 "push8 serialize": bytes.fromhex("558bec6a08ff710c8b4d08e8"),
 "push6 serialize": bytes.fromhex("558bec6a06ff710c8b4d08e8"),
 "push7 serialize": bytes.fromhex("558bec6a07ff710c8b4d08e8"),
 "CoopNameplatesUI": b"CoopNameplatesUI\0",
 "fBlendOutFOVTime": b"fBlendOutFOVTime\0",
}
for path in sys.argv[1:]:
    d = open(path, "rb").read()
    print(path)
    for k, p in pats.items():
        n = d.count(p)
        print(f"  {k}: {n} hit(s)" + (f" first at 0x{d.find(p):x}" if n else ""))
