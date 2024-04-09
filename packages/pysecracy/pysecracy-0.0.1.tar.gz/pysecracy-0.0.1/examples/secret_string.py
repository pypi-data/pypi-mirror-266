from pysecracy.secret_string import SecretString

test = SecretString(b"my secret")
assert str(test) == "SecretString :: [REDACTED]"
print(test)

assert test.expose_secret() == "my secret"
print(test.expose_secret())
