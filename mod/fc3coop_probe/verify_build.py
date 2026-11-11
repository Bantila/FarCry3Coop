"""verify_build.py -- check the built probe: machine, exports (names + ordinals 1..6), imports.

Usage: python -I verify_build.py [path-to-dll]   (default: build\\dinput8.dll)
Expected: machine 0x14C and exactly the six dinput8 exports on ordinals 1..6.
"""
import sys

import pefile

path = sys.argv[1] if len(sys.argv) > 1 else r"build\dinput8.dll"

EXPECTED = {
    1: "DirectInput8Create",
    2: "DllCanUnloadNow",
    3: "DllGetClassObject",
    4: "DllRegisterServer",
    5: "DllUnregisterServer",
    6: "GetdfDIJoystick",
}

pe = pefile.PE(path, fast_load=True)
print("file                :", path)
print("machine             : 0x%04X  (0x14C = x86 -> %s)"
      % (pe.FILE_HEADER.Machine, "OK" if pe.FILE_HEADER.Machine == 0x14C else "WRONG"))
print("subsystem           :", pe.OPTIONAL_HEADER.Subsystem)
print("image base          : 0x%08X" % pe.OPTIONAL_HEADER.ImageBase)
print("DllCharacteristics  : 0x%04X" % pe.OPTIONAL_HEADER.DllCharacteristics)

pe.parse_data_directories(
    directories=[pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXPORT"]])
exp = pe.DIRECTORY_ENTRY_EXPORT
libname = exp.name.decode() if isinstance(exp.name, bytes) else (
    exp.name.name.decode() if exp.name and exp.name.name else None)
print("export LIBRARY name :", libname)
print("ordinal base        :", exp.struct.Base)
print("NumberOfFunctions   :", exp.struct.NumberOfFunctions)
print("NumberOfNames       :", exp.struct.NumberOfNames)

got = {}
for s in exp.symbols:
    name = s.name.decode() if s.name else None
    got[s.ordinal] = name
    print("  ord %-2s %-22s rva=0x%X  fwd=%s"
          % (s.ordinal, name, s.address, s.forwarder.decode() if s.forwarder else None))

print("export count        :", len(exp.symbols))
ok = True
for ordinal, name in sorted(EXPECTED.items()):
    hit = got.get(ordinal)
    if hit != name:
        ok = False
    print("  expect ord %-2s %-22s -> %s" % (ordinal, name, hit))
byname = {v: k for k, v in got.items() if v}
for ordinal, name in sorted(EXPECTED.items()):
    if byname.get(name) != ordinal:
        ok = False
    print("  expect name %-22s on ord %-2s -> %s" % (name, ordinal, byname.get(name)))
print("EXPORTS CHECK       :", "PASS" if ok and len(exp.symbols) == 6 else "FAIL")

pe.parse_data_directories(
    directories=[pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"]])
print("imports:")
for e in getattr(pe, "DIRECTORY_ENTRY_IMPORT", []):
    names = [(i.name.decode() if i.name else "#ord%s" % i.ordinal) for i in e.imports]
    print("  %s: %d -> %s" % (e.dll.decode(), len(names), ", ".join(names)))
sys.exit(0 if ok and len(exp.symbols) == 6 else 1)
