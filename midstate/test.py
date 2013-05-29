#!/bin/env python3

from midstate import SHA256
from binascii import hexlify

data = \
		'01000000' + \
		'e4e89df8481bc576b99f665762cb8266f855c6684016b8b4d16976f200000000' + \
		'e1d14f0898e61d024f0e0172fc634669f5fcd56d4e01ca10e9377b056863d155' + \
		'c866204f' + \
		'f8ff071d' + \
		'00000000' + \
		'000000800000000000000000000000000000000000000000000000000000000000000000000000000000000080020000'
target_midstate = \
		b'b8101f7c4a8e294ecbccb941dde17fd461dc39ff102bc37bb7ac7d5b95290166'

datab = bytes.fromhex(data);

#for i in range(1000000): SHA256(datab)

print("target:")
print(target_midstate)
print("got:")
print("%8x%8x%8x%8x%8x%8x%8x%8x" % SHA256(datab))
print(SHA256(b"This is just a test, ignore it. I am making it over 64-bytes long.") == (0x755f1a94, 0x999b270c, 0xf358c014, 0xfd39caeb, 0x0dcc9ebc, 0x4694cd1a, 0x8e95678e, 0x75fac450))
#print(hexlify(midstate(datab)))
#SHA256("");
#SHA256(b"");
