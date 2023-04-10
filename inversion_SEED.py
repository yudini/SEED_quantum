import math

from projectq import MainEngine
from projectq.ops import H, CNOT, Measure, Toffoli, X, All, T, Tdag, S, Swap
from projectq.backends import CircuitDrawer, ResourceCounter, ClassicalSimulator
from projectq.meta import Loop, Compute, Uncompute, Control


def Reduction(eng, result):
    CNOT | (result[8], result[0])
    CNOT | (result[10], result[0])
    CNOT | (result[11], result[0])
    CNOT | (result[12], result[0])

    CNOT | (result[8], result[1])
    CNOT | (result[9], result[1])
    CNOT | (result[10], result[1])
    CNOT | (result[13], result[1])

    CNOT | (result[9], result[2])
    CNOT | (result[10], result[2])
    CNOT | (result[11], result[2])
    CNOT | (result[14], result[2])

    CNOT | (result[10], result[3])
    CNOT | (result[11], result[3])
    CNOT | (result[12], result[3])

    CNOT | (result[11], result[4])
    CNOT | (result[12], result[4])
    CNOT | (result[13], result[4])

    CNOT | (result[8], result[5])
    CNOT | (result[10], result[5])
    CNOT | (result[11], result[5])
    CNOT | (result[13], result[5])
    CNOT | (result[14], result[5])

    CNOT | (result[8], result[6])
    CNOT | (result[9], result[6])
    CNOT | (result[10], result[6])
    CNOT | (result[14], result[6])

    CNOT | (result[9], result[7])
    CNOT | (result[10], result[7])
    CNOT | (result[11], result[7])

    return result[0:8]

def Sbox1(eng,a5,n):
    a5 = Squaring(eng, a5, n)
    a5 = Squaring(eng, a5, n)
    a5 = Squaring(eng, a5, n)

    # [0 0 1 0 1 0 0 0]
    # [0 0 0 1 0 0 0 1]
    # [1 0 0 0 0 1 0 0]
    # [1 0 1 0 0 0 1 0]
    # [0 1 0 0 0 0 1 0]
    # [1 0 1 0 0 0 0 1]
    # [0 1 1 1 1 1 1 1]
    # [0 1 0 1 0 0 0 1]
    #
    # LUP
    # Decomposition…
    # Permutation
    # [0 0 1 0 0 0 0 0]
    # [0 0 0 1 0 0 0 0]
    # [1 0 0 0 0 0 0 0]
    # [0 0 0 0 1 0 0 0]
    # [0 1 0 0 0 0 0 0]
    # [0 0 0 0 0 0 1 0]
    # [0 0 0 0 0 1 0 0]
    # [0 0 0 0 0 0 0 1]
    #
    # Lower
    # [1 0 0 0 0 0 0 0]
    # [0 1 0 0 0 0 0 0]
    # [0 0 1 0 0 0 0 0]
    # [0 0 0 1 0 0 0 0]
    # [1 0 1 0 1 0 0 0]
    # [0 1 1 1 0 1 0 0]
    # [1 0 1 0 1 0 1 0]
    # [0 1 0 1 0 0 1 1]
    #
    # Upper
    # [1 0 0 0 0 1 0 0]
    # [0 1 0 0 0 0 1 0]
    # [0 0 1 0 1 0 0 0]
    # [0 0 0 1 0 0 0 1]
    # [0 0 0 0 1 1 1 0]
    # [0 0 0 0 0 1 0 0]
    # [0 0 0 0 0 0 1 1]
    # [0 0 0 0 0 0 0 1]

    # # U
    CNOT | (a5[5], a5[0])
    CNOT | (a5[6], a5[1])
    CNOT | (a5[4], a5[2])
    CNOT | (a5[7], a5[3])
    CNOT | (a5[5], a5[4])
    CNOT | (a5[6], a5[4])
    CNOT | (a5[7], a5[6])
    #
    # # # L
    CNOT | (a5[1], a5[7])
    CNOT | (a5[3], a5[7])
    CNOT | (a5[6], a5[7])
    CNOT | (a5[0], a5[6])
    CNOT | (a5[2], a5[6])
    CNOT | (a5[4], a5[6])
    CNOT | (a5[1], a5[5])
    CNOT | (a5[2], a5[5])
    CNOT | (a5[3], a5[5])
    CNOT | (a5[0], a5[4])
    CNOT | (a5[2], a5[4])

    out = []
    out.append(a5[2])
    out.append(a5[3])
    out.append(a5[0])
    out.append(a5[4])
    out.append(a5[1])
    out.append(a5[6])
    out.append(a5[5])
    out.append(a5[7])

    # 169 XOR
    X | out[0]
    X | out[3]
    X | out[5]
    X | out[7]

    if (resource_check != 1):
        print("sbox1")
        print_state(eng, out, 8)


def Sbox2(eng,a5,n):
    a5 = Squaring(eng, a5, n)
    a5 = Squaring(eng, a5, n)
    # [0 0 1 0 1 0 0 0]
    # [0 1 0 0 0 0 1 0]
    # [0 0 0 1 0 0 0 1]
    # [0 1 0 1 0 0 0 1]
    # [1 0 0 0 0 1 0 0]
    # [0 1 1 1 1 1 1 1]
    # [1 0 1 0 0 0 0 1]
    # [1 0 1 0 0 0 1 0]
    #
    # LUP
    # Decomposition…
    # Permutation
    # [0 0 1 0 0 0 0 0]
    # [0 1 0 0 0 0 0 0]
    # [0 0 0 0 0 0 1 0]
    # [0 0 0 1 0 0 0 0]
    # [1 0 0 0 0 0 0 0]
    # [0 0 0 0 0 1 0 0]
    # [0 0 0 0 1 0 0 0]
    # [0 0 0 0 0 0 0 1]
    #
    # Lower
    # [1 0 0 0 0 0 0 0]
    # [0 1 0 0 0 0 0 0]
    # [0 0 1 0 0 0 0 0]
    # [0 1 0 1 0 0 0 0]
    # [1 0 1 0 1 0 0 0]
    # [0 1 1 1 0 1 0 0]
    # [0 0 0 1 0 0 1 0]
    # [1 0 1 0 1 0 1 1]
    #
    # Upper
    # [1 0 0 0 0 1 0 0]
    # [0 1 0 0 0 0 1 0]
    # [0 0 1 0 1 0 0 0]
    # [0 0 0 1 0 0 1 1]
    # [0 0 0 0 1 1 0 1]
    # [0 0 0 0 0 1 1 0]
    # [0 0 0 0 0 0 1 0]
    # [0 0 0 0 0 0 0 1]

    # # U
    CNOT | (a5[5], a5[0])
    CNOT | (a5[6], a5[1])
    CNOT | (a5[4], a5[2])
    CNOT | (a5[6], a5[3])
    CNOT | (a5[7], a5[3])
    CNOT | (a5[5], a5[4])
    CNOT | (a5[7], a5[4])
    CNOT | (a5[6], a5[5])
    #
    # # # L
    CNOT | (a5[0], a5[7])
    CNOT | (a5[2], a5[7])
    CNOT | (a5[4], a5[7])
    CNOT | (a5[6], a5[7])
    CNOT | (a5[3], a5[6])
    CNOT | (a5[1], a5[5])
    CNOT | (a5[2], a5[5])
    CNOT | (a5[3], a5[5])
    CNOT | (a5[0], a5[4])
    CNOT | (a5[2], a5[4])
    CNOT | (a5[1], a5[3])


    out =[]
    out.append(a5[2])
    out.append(a5[1])
    out.append(a5[6])
    out.append(a5[3])
    out.append(a5[0])
    out.append(a5[5])
    out.append(a5[4])
    out.append(a5[7])

    X | out[3]
    X | out[4]
    X | out[5]

    if (resource_check != 1):
        print("sbox2")
        print_state(eng, out, 8)


def Karatsuba_Toffoli_Depth_1(eng) :

    n = 8
    a = eng.allocate_qureg(n)
    a1 = eng.allocate_qureg(n)

    check = eng.allocate_qureg(n)
    if (resource_check != 1):
        Round_constant_XOR(eng, a, 0x02, n)
        Round_constant_XOR(eng, check, 0x02, n)
        print("a=")
        print_state(eng,a,n)


    ancilla  = eng.allocate_qureg(38)
    count = 0

    copy(eng, a, a1, n) # a1 = a
    a1 = Squaring(eng, a1, n) # a1 = a^2

    a2 = []
    a2, count, ancilla = recursive_karatsuba(eng, a, a1, n, count, ancilla) #(a*a^2)
    a2 = Reduction(eng, a2)

    # (a * a^2) ^64
    a = Squaring(eng, a, n)
    a = Squaring(eng, a, n)
    a = Squaring(eng, a, n)
    a = Squaring(eng, a, n)
    a = Squaring(eng, a, n)
    a = Squaring(eng, a, n) #^64

    count = 0
    a3 = []
    a3, count, ancilla = recursive_karatsuba(eng, a2, a, n, count, ancilla) #(a*a^2)*a^64
    a3 = Reduction(eng, a3)

    # (a*a^2)^4
    a2 = Squaring(eng, a2, n)
    a2 = Squaring(eng, a2, n)

    #(a*a^2)*(a^64)*((a*a^2)^4)
    count = 0
    a4 = []
    a4, count, ancilla = recursive_karatsuba(eng, a2, a3, n, count, ancilla)
    a4 = Reduction(eng, a4)

    # (a * a ^ 2) ^ 16
    a2 = Squaring(eng, a2, n)
    a2 = Squaring(eng, a2, n)

    count = 0
    a5 = []
    # (a*a^2)*(a^64)*((a*a^2)^4)*((a*a^2)^16)

    a5, count, ancilla = recursive_karatsuba(eng, a2, a4, n, count, ancilla)

    a5 = Reduction(eng, a5)

    # (a*a^2)*(a^64)*((a*a^2)^4)*((a*a^2)^16)^2
    a5 = Squaring(eng, a5, n)

    #Sbox1(eng, a5,n)
    #Sbox2(eng, a5,n)


def copy(eng, a, b, n):
    for i in range(n):
        CNOT | (a[i], b[i])


def Squaring(eng, a, n):
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

def recursive_karatsuba(eng, a, b, n, count, ancilla): #n=4

    if(n==1):
        c = eng.allocate_qubit()
        Toffoli_gate(eng, a, b, c)

        return c, count, ancilla

    c_len = 3**math.log(n, 2) #9 #3
    r_low = n//2    #2 #1

    if(n%2!=0):
        r_low = r_low +1 # n=3 -> 2, n=4 -> 2

    r_a = []
    r_b = []

    # Provide rooms and prepare operands
    r_a = ancilla[count:count + r_low]
    #print(count, count + r_low)

    #r_a = room(eng, r_low) #2qubits for r

    count = count + r_low

    r_b = ancilla[count:count + r_low]
    #print(count, count + r_low)

    #r_b = room(eng, r_low) #2qubits for r

    count = count + r_low

    with Compute(eng):
        for i in range(r_low):
            CNOT | (a[i], r_a[i])
        for i in range(n//2):
            CNOT | (a[r_low + i], r_a[i])
        for i in range(r_low):
            CNOT | (b[i], r_b[i])
        for i in range(n//2):
            CNOT | (b[r_low + i], r_b[i])

    # upper-part setting
    if(r_low == 1):
        c = eng.allocate_qureg(3)
        Toffoli_gate(eng, a[0], b[0], c[0])
        Toffoli_gate(eng, a[1], b[1], c[2])
        CNOT | (c[0], c[1])
        CNOT | (c[2], c[1])
        Toffoli_gate(eng, r_a, r_b, c[1])

        Uncompute(eng)
        return c, count, ancilla

    c_a = []
    c_b = []
    c_r = []

    c_a, count, ancilla = recursive_karatsuba(eng, a[0:r_low], b[0:r_low], r_low, count, ancilla)# 2 qubits     # 0~2
    c_b, count, ancilla = recursive_karatsuba(eng, a[r_low:n], b[r_low:n], n//2, count, ancilla)#2 qubits        # 3~5
    c_r, count, ancilla = recursive_karatsuba(eng, r_a[0:r_low], r_b[0:r_low], r_low, count, ancilla) #2qubits  # 6~8

    Uncompute(eng)
    #print('check initialize')
    #print_state(eng, r_a, r_low)
    result = []
    result = combine(eng, c_a, c_b, c_r, n)

    return result, count, ancilla

def recursive_karatsuba_omit_reverse(eng, a, b, n, count, ancilla): #n=4

    if(n==1):
        c = eng.allocate_qubit()
        Toffoli_gate(eng, a, b, c)

        return c, count, ancilla

    c_len = 3**math.log(n, 2) #9 #3
    r_low = n//2    #2 #1

    if(n%2!=0):
        r_low = r_low +1 # n=3 -> 2, n=4 -> 2

    r_a = []
    r_b = []

    # Provide rooms and prepare operands
    r_a = ancilla[count:count + r_low]
    #print(count, count + r_low)

    #r_a = room(eng, r_low) #2qubits for r

    count = count + r_low

    r_b = ancilla[count:count + r_low]
    #print(count, count + r_low)

    #r_b = room(eng, r_low) #2qubits for r

    count = count + r_low

    with Compute(eng):
        for i in range(r_low):
            CNOT | (a[i], r_a[i])
        for i in range(n//2):
            CNOT | (a[r_low + i], r_a[i])
        for i in range(r_low):
            CNOT | (b[i], r_b[i])
        for i in range(n//2):
            CNOT | (b[r_low + i], r_b[i])

    # upper-part setting
    if(r_low == 1):
        c = eng.allocate_qureg(3)
        Toffoli_gate(eng, a[0], b[0], c[0])
        Toffoli_gate(eng, a[1], b[1], c[2])
        CNOT | (c[0], c[1])
        CNOT | (c[2], c[1])
        Toffoli_gate(eng, r_a, r_b, c[1])


        return c, count, ancilla

    c_a = []
    c_b = []
    c_r = []

    c_a, count, ancilla = recursive_karatsuba(eng, a[0:r_low], b[0:r_low], r_low, count, ancilla)# 2 qubits     # 0~2
    c_b, count, ancilla = recursive_karatsuba(eng, a[r_low:n], b[r_low:n], n//2, count, ancilla)#2 qubits        # 3~5
    c_r, count, ancilla = recursive_karatsuba(eng, r_a[0:r_low], r_b[0:r_low], r_low, count, ancilla) #2qubits  # 6~8

    #print('check initialize')
    #print_state(eng, r_a, r_low)
    result = []
    result = combine(eng, c_a, c_b, c_r, n)

    return result, count, ancilla

def combine(eng, a, b, r, n):
    if (n % 2 != 0):
        # n = 13########
        for i in range(n):
            CNOT | (a[i], r[i])
        for i in range(n - 2):
            CNOT | (b[i], r[i])

        for i in range(n // 2):
            CNOT | (a[n // 2 + 1 + i], r[i])
        for i in range(n // 2):
            CNOT | (b[i], r[n // 2 + 1 + i])

        out = []
        for i in range(n // 2 + 1):  # (2n-1) = n//2 + 1 + n ? / 13 = 3+1+7+?
            out.append(a[i])
        for i in range(n):
            out.append(r[i])
        for i in range((2 * n - 1) - n // 2 - 1 - n):
            out.append(b[n // 2 + i])

        return out

    half_n = int(n/2) #n=4
    for i in range(n-1):
        CNOT | (a[i], r[i])
        CNOT | (b[i], r[i])
    for i in range(half_n-1):
        CNOT | (a[half_n+i], r[i])
        CNOT | (b[i], r[half_n+i])

    result = []
    for i in range(half_n):
        result.append(a[i])
    for i in range(n-1):
        result.append(r[i])
    for i in range(half_n):
        result.append(b[half_n-1+i])

    return result

def Toffoli_gate(eng, a, b, c):

    if(NCT):
        Toffoli | (a, b, c)
    else:
        if (resource_check):
            if(AND_check):
                ancilla = eng.allocate_qubit()
                H | c
                CNOT | (b, ancilla)
                CNOT | (c, a)
                CNOT | (c, b)
                CNOT | (a, ancilla)
                Tdag | a
                Tdag | b
                T | c
                T | ancilla
                CNOT | (a, ancilla)
                CNOT | (c, b)
                CNOT | (c, a)
                CNOT | (b, ancilla)
                H | c
                S | c

            else:
                Tdag | a
                Tdag | b
                H | c
                CNOT | (c, a)
                T | a
                CNOT | (b, c)
                CNOT | (b, a)
                T | c
                Tdag | a
                CNOT | (b, c)
                CNOT | (c, a)
                T | a
                Tdag | c
                CNOT | (b, a)
                H | c


def Round_constant_XOR(eng, k, rc, bit):
    for i in range(bit):
        if (rc >> i & 1):
            X | k[i]

def print_state(eng, b, n):
    All(Measure) | b
    print('Result : ', end='')
    for i in range(n):
        print(int(b[n-1-i]), end='')
    print('\n')

global resource_check
global AND_check
global NCT

NCT = 1
resource_check = 0
classic = ClassicalSimulator()
eng = MainEngine(classic)
Karatsuba_Toffoli_Depth_1(eng)
eng.flush()
print('\n')

resource_check = 1
NCT = 0
AND_check = 0
Resource = ResourceCounter()
eng = MainEngine(Resource)
Karatsuba_Toffoli_Depth_1(eng)
print('\n')
print(Resource)