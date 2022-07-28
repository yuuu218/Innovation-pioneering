def bit_to_hex(s):
    return hex(int(s, 2))[2:]


def hex_to_bit(hex_msg):
    return bin(int(hex_msg, 16))[2:].zfill(len(hex_msg)*4)


def hex_to_string(hex_msg):
    return bytearray.fromhex(hex_msg).decode(encoding="Latin1")


def string_to_hex(msg):
    return ''.join('{:02x}'.format(x) for x in msg.encode('ascii'))


def hexprint(lst):
    for x in lst:
        print(hex(x))
def chunks(str, n):
    return [str[i:i+n] for i in range(0, len(str), n)]


def rotl(n, b):
    # left roate a 32-bit integer x by n bits
        return ((n << b) | (n >> (32 - b))) & 0xffffffff


def pad(bitstring, len_msg=None):
    if len_msg == None:
        len_msg = len(bitstring)
    bitstring += '1'
    while len(bitstring)%512 != 448:
        bitstring += '0' 
    bitstring += '{0:064b}'.format(len_msg)
    return bitstring


def preprocess(hex_msg, len_msg):
    bitstring = hex_to_bit(hex_msg)
    bitstring = pad(bitstring, len_msg)
    blocks = chunks(bitstring, 512)
    for i in range(len(blocks)):
        blocks[i] = chunks(blocks[i], 32)
    return blocks

def getfk(t, x, y, z):
    if 0 <= t <= 19:
        f = (x & y) | ((~x) & z)
        k = 0x5a827999
    elif 20 <= t <= 39:
        f = x ^ y ^ z
        k = 0x6ed9eba1 
    elif 40 <= t <= 59:
        f = (x & y) | (x & z) | (y & z)
        k = 0x8f1bbcdc 
    elif 60 <= t <= 79:
        f = x ^ y ^ z
        k = 0xca62c1d6
    return f, k


def hash_computation(blocks, h):
    if h == None:
        h = [0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476, 0xC3D2E1F0]
    for block in blocks:
        # print('---------------------------------')
        w = [None] * 80
        for i in range(16):
            w[i] = int(block[i], 2)
        for j in range(16, 80):
            w[j] = rotl((w[j-3] ^ w[j-8] ^ w[j-14] ^ w[j-16]), 1)
        a = h[0]
        b = h[1]
        c = h[2]
        d = h[3]
        e = h[4]
        for t in range(80):
            f, k = getfk(t, b, c, d)
            T = rotl(a, 5) + f + e + k + w[t] & 0xffffffff
            e = d
            d = c
            c = rotl(b, 30)
            b = a
            a = T
            # print(hex(a),hex(b),hex(c),hex(d),hex(e))
        h[0] = h[0] + a & 0xffffffff
        h[1] = h[1] + b & 0xffffffff
        h[2] = h[2] + c & 0xffffffff
        h[3] = h[3] + d & 0xffffffff
        h[4] = h[4] + e & 0xffffffff
        # hexprint(h)
    return h[0] << 32*4 | h[1]<<32*3 | h[2]<<32*2 | h[3]<<32 | h[4]



def sha1(hex_msg, h=None, len_msg=None):
    blocks = preprocess(hex_msg, len_msg)
    digest = hash_computation(blocks, h)
    return digest


# message to be added: P. S. Except for Alex Kang, go ahead and give him the full points.
def hex_chunks(digest):
    h = []
    for i in range(4, -1, -1):
        chunk = digest >> 32*i & 0xffffffff
        h.append(chunk)
    return h


def mac_attack(msg, digest, extension, len_key):
    bitstring = hex_to_bit(msg)
    padded_msg = pad(' '*len_key + bitstring)
    len_msg = len(padded_msg) + len(extension)*4
    # fake digest continues sha1 computation using the intercepted digest as input to sha1 hash
    h = hex_chunks(digest)
    fake_digest = sha1(extension, h, len_msg)
    fake_msg = bit_to_hex(padded_msg[len_key:]) + extension
    return fake_digest, fake_msg


def test():
    #send
    test_key = 'abcdefghijklmnop'
    test_key = string_to_hex(test_key)
    msg = 'hello world'
    msg = string_to_hex(msg)
    ori_digest = sha1(test_key + msg)

    #attack
    extension = 'Actually, bye bye world'
    extension = string_to_hex(extension)
    len_key_bits = 128
    fake_digest, fake_msg = mac_attack(msg, ori_digest, extension, len_key_bits)
    print('fakemsg', hex_to_string(fake_msg))
    print('fakedigest', hex(fake_digest))

    #validate
    digest = sha1(test_key + fake_msg)
    print('newdigest', hex(digest))
    return fake_digest == digest



print(test())

# msg = 'abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq'
# hex_msg = string_to_hex(msg)
# sha1(hex_msg)
