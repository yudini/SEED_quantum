from projectq import MainEngine
from projectq.ops import H, CNOT, Measure, Toffoli, X, All, T, Tdag
from projectq.backends import CircuitDrawer, ResourceCounter, ClassicalSimulator
from projectq.meta import Loop, Compute, Uncompute, Control

# Permutation
# [1 0 0 0 0 0 0 0]
# [0 0 0 0 1 0 0 0]
# [0 1 0 0 0 0 0 0]
# [0 0 0 0 0 1 0 0]
# [0 0 1 0 0 0 0 0]
# [0 0 0 0 0 0 0 1]
# [0 0 0 1 0 0 0 0]
# [0 0 0 0 0 0 1 0]
#
# Lower
# [1 0 0 0 0 0 0 0]
# [0 1 0 0 0 0 0 0]
# [0 0 1 0 0 0 0 0]
# [0 0 0 1 0 0 0 0]
# [0 0 0 0 1 0 0 0]
# [0 0 0 0 0 1 0 0]
# [0 0 0 0 0 1 1 0]
# [0 0 0 0 1 0 0 1]
#
# Upper
# [1 0 0 0 1 1 1 0]
# [0 1 0 0 0 1 0 1]
# [0 0 1 0 0 0 1 0]
# [0 0 0 1 1 1 0 1]
# [0 0 0 0 1 1 0 0]
# [0 0 0 0 0 1 1 0]
# [0 0 0 0 0 0 1 0]
# [0 0 0 0 0 0 0 1]
def SEED(eng):

    x = eng.allocate_qureg(8)
    if(resource_check!= 1):
        Round_constant_XOR(eng, x, 0xff, 8)

    x = squaring(eng, x)
    print_state(eng, x, 8)

def Round_constant_XOR(eng, k, rc, bit):
    for i in range(bit):
        if (rc >> i & 1):
            X | k[i]

def print_state(eng, b, n):

    All(Measure) | b
    for i in range(n):
        print(int(b[n-1-i]),end='')
    print('\n')

def squaring(eng, a):
    CNOT | (a[4], a[0])
    CNOT | (a[5], a[0])
    CNOT | (a[6], a[0])
    CNOT | (a[5], a[1])
    CNOT | (a[7], a[1])
    CNOT | (a[6], a[2])
    CNOT | (a[4], a[3])
    CNOT | (a[5], a[3])
    CNOT | (a[7], a[3])
    CNOT | (a[5], a[4])
    CNOT | (a[6], a[5])
    CNOT | (a[4], a[7])
    CNOT | (a[5], a[6])

    # logical swap
    out = []
    out.append(a[0])
    out.append(a[4])
    out.append(a[1])
    out.append(a[5])
    out.append(a[2])
    out.append(a[7])
    out.append(a[3])
    out.append(a[6])

    return out

global resource_check
print('Generate Ciphertext...')
Simulate = ClassicalSimulator()
eng = MainEngine(Simulate)
resource_check = 0
SEED(eng)

print('Estimate cost...')
Resource = ResourceCounter()
eng = MainEngine(Resource)
resource_check = 1
SEED(eng)
print(Resource)
print('\n')
eng.flush()