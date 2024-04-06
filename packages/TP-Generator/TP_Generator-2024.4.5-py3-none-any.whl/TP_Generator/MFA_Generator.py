# Time-based One-Time Password
def TOTP(secretKey, digits=6, period=30):
	import hashlib, hmac, base64, time

	key = base64.b32decode(secretKey)

	timestamp = int(time.time())
	message = bytes.fromhex(hex(int(timestamp / period))[2:].rjust(16, "0"))

	hmac = hmac.new(key, message, hashlib.sha1).hexdigest()

	offset = int(hmac[len(hmac)-1], 16)

	totp = str(int(hmac[offset*2:offset*2+8], 16) & int("7fffffff", 16))
	totp = totp[max(len(totp)-digits, 0): max(len(totp)-digits, 0)+digits]

	return totp



# HMAC-based One-Time Password
def HOTP(secretKey, counter, digits=6):
	import hashlib, hmac, base64

	key = base64.b32decode(secretKey)

	message = bytes.fromhex(hex(int(counter))[2:].rjust(16, "0"))

	hmac = hmac.new(key, message, hashlib.sha1).hexdigest()

	offset = int(hmac[len(hmac)-1], 16)

	hotp = str(int(hmac[offset*2:offset*2+8], 16) & int("7fffffff", 16))
	hotp = hotp[max(len(hotp)-digits, 0): max(len(hotp)-digits, 0)+digits]

	return hotp