from bit import Key
from bit.format import bytes_to_wif
# https://ofek.dev/bit/guide/keys.html#what-is-a-private-key

# key = Key.from_hex('bebb3940cd0fc1491'.rjust(64, '0'))
# print("Private Key (WIF):", key.to_wif())
# print("Address:", key.address)

def p1():
    # puzzle 1
    key = Key("5JMTiDVHj3pj8VfaTe6pDtD9byZr6too3PD3AGBJrXF1hVsitc8")
    print("Address:", key.address)

def p3():
    # puzzle 3
    key = Key.from_hex("6008c37d0aa226dbbe611be64106964bca6cbba7098fe4602a932c590e14b074")
    wif = bytes_to_wif(key.to_bytes(), compressed=False)
    un_compressed_key = Key(wif)
    print("Address:", un_compressed_key.address)


p1()
p3()