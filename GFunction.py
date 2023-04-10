import math

from projectq import MainEngine
from projectq.ops import H, CNOT, Measure, Toffoli, X, All, T, Tdag, S
from projectq.backends import CircuitDrawer, ResourceCounter, ClassicalSimulator
from projectq.meta import Loop, Compute, Uncompute, Control

def inversion(eng,a):

    n = 8
    a1 = eng.allocate_qureg(n)

    ancilla  = eng.allocate_qureg(38)
    count = 0

    copy(eng, a, a1, n) # a1 = a
    a1 = Squaring(eng, a1, n) # a1 = a^2

    a2 = []
    a2, count, ancilla = recursive_karatsuba(eng, a, a1, n, count, ancilla) #(a*a^2)
    a2 = Reduction(eng, a2)

    # (a * a^2) ^64
    # a = Squaring(eng, a, n)
    a1 = Squaring(eng, a1, n)
    a1 = Squaring(eng, a1, n)
    a1 = Squaring(eng, a1, n)
    a1 = Squaring(eng, a1, n)
    a1 = Squaring(eng, a1, n) #^64

    count = 0
    a3 = []
    a3, count, ancilla = recursive_karatsuba(eng, a2, a1, n, count, ancilla) #(a*a^2)*a^64
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
    if (resource_check != 1):
        a5, count, ancilla = recursive_karatsuba(eng, a2, a4, n, count, ancilla)
    else:
        a5, count, ancilla = recursive_karatsuba_omit_reverse(eng, a2, a4, n, count, ancilla)
    a5 = Reduction(eng, a5)

    # (a*a^2)*(a^64)*((a*a^2)^4)*((a*a^2)^16)^2
    a5 = Squaring(eng, a5, n)

    return a5

def copy(eng, a, b, n):
    for i in range(n):
        CNOT | (a[i], b[i])

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

def Squaring(eng,a,n):

    CNOT | (a[4], a[0])
    CNOT | (a[5], a[1])
    CNOT | (a[5], a[0])
    CNOT | (a[7], a[1])
    CNOT | (a[6], a[0])
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


def Toffoli_gate(eng, a, b, c):
    if (resource_check):
        if (AND_check):
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
    else:
        Toffoli | (a, b, c)

def Sbox1(eng,x,n):
   # a^-1 = a^254=((α·α^2)·(α·α^2)^4 ·(α·α^2)^16 ·α^64)^2,
   # Z2^8 A(i) * x^247 xor 169    // A(i) * (x^-1)^8 xor 169

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

   x= inversion(eng,x)

   x = Squaring(eng, x, n)
   x = Squaring(eng, x, n)
   x = Squaring(eng, x, n)

   # # U
   CNOT | (x[5], x[0])
   CNOT | (x[6], x[1])
   CNOT | (x[4], x[2])
   CNOT | (x[7], x[3])
   CNOT | (x[5], x[4])
   CNOT | (x[6], x[4])
   CNOT | (x[7], x[6])
   #
   # # # L
   CNOT | (x[1], x[7])
   CNOT | (x[3], x[7])
   CNOT | (x[6], x[7])
   CNOT | (x[0], x[6])
   CNOT | (x[2], x[6])
   CNOT | (x[4], x[6])
   CNOT | (x[1], x[5])
   CNOT | (x[2], x[5])
   CNOT | (x[3], x[5])
   CNOT | (x[0], x[4])
   CNOT | (x[2], x[4])

   out = []
   out.append(x[2])
   out.append(x[3])
   out.append(x[0])
   out.append(x[4])
   out.append(x[1])
   out.append(x[6])
   out.append(x[5])
   out.append(x[7])

   # 169 XOR
   X | out[0]
   X | out[3]
   X | out[5]
   X | out[7]

   return out


def Sbox2(eng,x,n):
    # a^-1 = a^254=((α·α^2)·(α·α^2)^4 ·(α·α^2)^16 ·α^64)^2,
    # Z2^8 A(i) * x^251 xor 56  // A(i) * (x^-1)^4 xor 56
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

    x= inversion(eng,x)

    x = Squaring(eng, x, n)
    x = Squaring(eng, x, n)

    # # U
    CNOT | (x[5], x[0])
    CNOT | (x[6], x[1])
    CNOT | (x[4], x[2])
    CNOT | (x[6], x[3])
    CNOT | (x[7], x[3])
    CNOT | (x[5], x[4])
    CNOT | (x[7], x[4])
    CNOT | (x[6], x[5])
    #
    # # # L
    CNOT | (x[0], x[7])
    CNOT | (x[2], x[7])
    CNOT | (x[4], x[7])
    CNOT | (x[6], x[7])
    CNOT | (x[3], x[6])
    CNOT | (x[1], x[5])
    CNOT | (x[2], x[5])
    CNOT | (x[3], x[5])
    CNOT | (x[0], x[4])
    CNOT | (x[2], x[4])
    CNOT | (x[1], x[3])

    out = []
    out.append(x[2])
    out.append(x[1])
    out.append(x[6])
    out.append(x[3])
    out.append(x[0])
    out.append(x[5])
    out.append(x[4])
    out.append(x[7])

    X | out[3]
    X | out[4]
    X | out[5]


    return out

def GFunction(eng,x):
    c = eng.allocate_qureg(8)
    c1 = eng.allocate_qureg(8)
    c2 = eng.allocate_qureg(8)
    c3 =  eng.allocate_qureg(8)
    Y0=[]
    Y1=[]
    Y2=[]
    Y3=[]
    Z0=[]
    Y0 = Sbox1(eng, x[0:8],8) # Y0
    Y1 = Sbox2(eng, x[8:16], 8)  # Y1
    Y2 = Sbox1(eng, x[16:24], 8)
    Y3 = Sbox2(eng, x[24:32], 8)

    for i in range(6):  # fc
        CNOT | (Y0[2 + i], c[2 + i])

    # f3
    CNOT | (Y1[1], c[1])
    CNOT | (Y1[0], c[0])
    for i in range(4):
        CNOT | (Y1[4 + i], c[4 + i])

    for i in range(4):  # cf
        CNOT | (Y2[i], c[i])
    CNOT | (Y2[6], c[6])
    CNOT | (Y2[7], c[7])

    for i in range(6):  # 3f
        CNOT | (Y3[i], c[i])

    x[0:8] = c

    # f3
    CNOT | (Y0[1], c1[1])
    CNOT | (Y0[0], c1[0])
    for i in range(4):
        CNOT | (Y0[4 + i], c1[4 + i])

    for i in range(4):  # cf
        CNOT | (Y1[i], c1[i])
    CNOT | (Y1[6], c1[6])
    CNOT | (Y1[7], c1[7])

    for i in range(6):  # 3f
        CNOT | (Y2[i], c1[i])

    for i in range(6):  # fc
        CNOT | (Y3[2 + i], c1[2 + i])

    x[8:16] = c1

    for i in range(4):  # cf
        CNOT | (Y0[i], c2[i])
    CNOT | (Y0[6], c2[6])
    CNOT | (Y0[7], c2[7])

    for i in range(6):  # 3f
        CNOT | (Y1[i], c2[i])

    for i in range(6):  # fc
        CNOT | (Y2[2 + i], c2[2 + i])

    # f3
    CNOT | (Y3[1], c2[1])
    CNOT | (Y3[0], c2[0])
    for i in range(4):
        CNOT | (Y3[4 + i], c2[4 + i])
    x[16:24] = c2

    for i in range(6):  # 3f
        CNOT | (Y0[i], c3[i])

    for i in range(6):  # fc
        CNOT | (Y1[2 + i], c3[2 + i])

    # f3
    CNOT | (Y2[1], c3[1])
    CNOT | (Y2[0], c3[0])
    for i in range(4):
        CNOT | (Y2[4 + i], c3[4 + i])

    for i in range(4):  # cf
        CNOT | (Y3[i], c3[i])
    CNOT | (Y3[6], c3[6])
    CNOT | (Y3[7], c3[7])
    x[24:32] = c3

    if (resource_check != 1):
        print_state(eng, x,32)

def CNOT32(eng, a, b):
    for i in range(32):
        CNOT | (a[i], b[i])

def Round_constant_XOR(eng, k, rc, bit):
    for i in range(bit):
        if (rc >> i & 1):
            X | k[i]
    # print_state(eng,k,bit)


def print_state(eng, b, n):
    All(Measure) | b
    print('Result : ', end='')
    for i in range(n):
        print(int(b[n - 1 - i]), end='')
    print('\n')

def Run(eng):
    x = eng.allocate_qureg(32)

    if (resource_check != 1):
        Round_constant_XOR(eng, x, 0x61c88647, 32)  #BFBC2A56

    GFunction(eng,x)

global resource_check
global AND_check
print('Generate Ciphertext...')
resource_check = 0
classic = ClassicalSimulator()
eng = MainEngine(classic)
Run(eng)
eng.flush()
print('\n')

print('Estimate cost...')
resource_check = 1
AND_check = 0
Resource = ResourceCounter()
eng = MainEngine(Resource)
Run(eng)
print('\n')
print(Resource)
eng.flush()