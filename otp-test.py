import hmac, base64, struct, hashlib, time, random
secret = 'MNXW24DTPFZTGMBS'
def get_totp_token(secret):
    key = base64.b32decode(secret, True) # decode given b32 string
    msg = struct.pack(">Q", int(time.time())//30) # convert to byte string in correct format, big endian + unsigned long long
    hmac_hash = hmac.new(key, msg, hashlib.sha1).digest() # run hmac with SHA1
    o = ord(hmac_hash[19]) & 0xf #ord returns unicode code-point of 19th element in hmac, append 15 (aka 0xf)
    # token result is hmac's first 4 values concat with largest 32 bit number,  unpacked to big endian, unsigned int format with string
    token = (struct.unpack(">I", hmac_hash[o:o+4])[0] & 0x7fffffff) % 1000000  # modulo this by 10^6 (for 6 digit auth code)
    return token


print secret
print get_totp_token(secret)
