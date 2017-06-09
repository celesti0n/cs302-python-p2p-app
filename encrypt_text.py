import hashlib

def hash(str):
    hashed_str = hashlib.sha256(str + 'COMPSYS302-2017').hexdigest() #hexdigest returns hex in string form, use digest for byte form
    return hashed_str
password = 'd9e19f477a2ebebe6d1b1931e620b4ceede511e7430820f8578a572be5ea5ddc'
print hash('addcemetery')
if (password == hash('addcemetery')):
    print('success')
else:
    print('error')

error = "0, user and logged in"
error_code,error_message = error.split(',')
print(error_code)
