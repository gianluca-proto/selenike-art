from argon2 import PasswordHasher

ph = PasswordHasher()
hashed_password = ph.hash("76H*G4re9BDehX#CCzv8")

print(hashed_password)  # Salvalo nel database
