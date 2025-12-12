#!/usr/bin/env python3
"""
Shamir's Secret Sharing – pure Python, no dependencies, works everywhere
Copy the whole thing and run: python3 shamir.py
"""

import random
from secrets import token_bytes

# ==================== CONFIG ====================
SECRET_HEX = "deadbeef1234567890abcdef1234567890abcdef1234567890abcdef12345678"
M = 3          # need 3 shares to recover
N = 5          # create 5 shares total
# ===============================================

secret_int = int(SECRET_HEX, 16)
prime = 2**255 - 19          # safe prime used by Curve25519 / Ed25519

print(f"Original secret: {SECRET_HEX}\n")

def split_secret(secret: int, threshold: int, count: int, prime: int):
    random.seed(token_bytes(32))
    coeffs = [secret]
    for _ in range(threshold - 1):
        coeffs.append(random.randrange(1, prime))

    def poly(x: int) -> int:
        result = coeffs[-1]
        for c in reversed(coeffs[:-1]):
            result = (result * x + c) % prime
        return result

    return [(i, poly(i)) for i in range(1, count + 1)]

def reconstruct_secret(shares, prime: int) -> int:
    secret = 0
    for i, (xi, yi) in enumerate(shares):
        num = den = 1
        for j, (xj, _) in enumerate(shares):
            if i != j:
                num = (num * -xj) % prime
                den = (den * (xi - xj)) % prime
        basis = (num * pow(den, prime - 2, prime)) % prime
        secret = (secret + yi * basis) % prime
    return secret

# ===================== RUN =====================
shares = split_secret(secret_int, M, N, prime)

print(f"Created {N} shares (threshold {M}-of-{N}):\n")
for x, y in shares:
    print(f"  Share {x} → {y}")

print("\nWith only 2 shares → complete garbage")
print("Fake secret starts:", hex(reconstruct_secret(shares[:2], prime))[:20] + "...\n")

print("With any 3 shares → perfect recovery")
recovered = reconstruct_secret(shares[:3], prime)
print(f"Recovered: {recovered.to_bytes(32, 'big').hex()}")
print(f"Match:     {'YES' if recovered == secret_int else 'NO'}\n")

print("Different set of 3 shares (shares 3-5) → still perfect")
recovered2 = reconstruct_secret(shares[2:], prime)
print(f"Recovered: {recovered2.to_bytes(32, 'big').hex()}")
print(f"Match:     {'YES' if recovered2 == secret_int else 'NO'}")
