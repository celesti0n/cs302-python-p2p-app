import hmac, base64, struct, hashlib, time, random, login

# HASHING ALGORITHM - SHA256
def hash(str):
    hashed_str = hashlib.sha256(str + 'COMPSYS302-2017').hexdigest() #hexdigest returns hex in string form, use digest for byte form
    return hashed_str

# generating a random base32 16-character string based on a 10 character string input.
# Taken from https://gist.github.com/ebsaral/9246709

def generateBase32(secret):
    prefix = unicode(secret)  # we use the user's UPI (7 char max)
    prefix_len = len(prefix)
    if prefix_len > 10:
        return None  # 10 char max input
    remaining = 10 - prefix_len
    random_int_str = ''
    if remaining != 0:
          random_from = 10 ** (remaining-1)
          random_to = (10 ** remaining) - 1
          random_int = random.randint(random_from, random_to)
          random_int_str = unicode(random_int)
    str_to_encode = prefix + random_int_str
    encoded_str = base64.b32encode(str_to_encode)
    return encoded_str

def getTotpToken(secret):
    key = base64.b32decode(secret, True) # decode given b32 string
    msg = struct.pack(">Q", int(time.time())//30) # convert to byte string in correct format, big endian + unsigned long long
    hmac_hash = hmac.new(key, msg, hashlib.sha1).digest() # run hmac with SHA1
    o = ord(hmac_hash[19]) & 0xf #ord returns unicode code-point of 19th element in hmac, append 15 (aka 0xf)
    # token result is hmac's first 4 values concat with largest 32 bit number,  unpacked to big endian, unsigned int format with string
    token = (struct.unpack(">I", hmac_hash[o:o+4])[0] & 0x7fffffff) % 1000000  # modulo this by 10^6 (for 6 digit auth code)
    return token
