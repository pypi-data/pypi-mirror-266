import os
import random
import time

from eth_abi import abi
from tqdm import tqdm

import allopy

SIG = "(uint256,address[],(bytes32[],int8))"


def rand_address() -> str:
    s = "0x"
    for _ in range(40):
        s += random.choice("1234567890abcdef")
    return s


def rand_bytes32() -> bytes:
    return os.urandom(32)


DATA = (
    1000 * (10**18),
    [rand_address() for _ in range(1000)],
    ([rand_bytes32() for _ in range(1000)], 7),
)

t1 = time.time()
results = []
for _ in tqdm(range(1000)):
    results.append(abi.encode([SIG], [DATA]))
t2 = time.time()

results = []
for _ in tqdm(range(1000)):
    results.append(allopy.encode(DATA, SIG))
t3 = time.time()

print(f"ETH ABI took {t2 - t1}")
print(f"ALLOY took {t3 - t2}")
