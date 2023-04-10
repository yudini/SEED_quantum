import math

from projectq import MainEngine
from projectq.ops import H, CNOT, Measure, Toffoli, X, All, T, Tdag, S
from projectq.backends import CircuitDrawer, ResourceCounter, ClassicalSimulator
from projectq.meta import Loop, Compute, Uncompute, Control, Dagger

def inversion(eng,a,ancilla):
    # x = (a*a^2)*(a^64)*((a*a^2)^4)*((a*a^2)^16)^2
    n = 8
    a1 = eng.allocate_qureg(n)

    count = 0

    copy(eng, a, a1, n) # a1 = a
    a1 = Squaring(eng, a1, n) # a1 = a^2

    a2 = []
    a2, count, ancilla = recursive_karatsuba(eng, a, a1, n, count, ancilla) #(a*a^2)
    a2 = Reduction(eng, a2)

    # (a * a^2)* a^64
    a = Squaring(eng, a, n)
    a = Squaring(eng, a, n)
    a = Squaring(eng, a, n)
    a = Squaring(eng, a, n)
    a = Squaring(eng, a, n)
    a = Squaring(eng, a, n) #a^64

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

    return a5

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

def Sbox1(eng,x,n,ancilla):
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

   x= inversion(eng,x,ancilla)

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


def Sbox2(eng,x,n,ancilla):
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

    x= inversion(eng,x,ancilla)

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

def GFunction(eng,x,ancilla):
    c = eng.allocate_qureg(8)
    c1 = eng.allocate_qureg(8)
    c2 = eng.allocate_qureg(8)
    c3 =  eng.allocate_qureg(8)
    Y0=[]
    Y1=[]
    Y2=[]
    Y3=[]
    Z0=[]
    Y0 = Sbox1(eng, x[0:8],8,ancilla[0:38]) # Y0
    Y1 = Sbox2(eng, x[8:16], 8,ancilla[38:76])  # Y1
    Y2 = Sbox1(eng, x[16:24], 8,ancilla[76:114])
    Y3 = Sbox2(eng, x[24:32], 8,ancilla[114:152])

    # 3F7F11EF

    for i in range(6): #Y0&fc
        CNOT | (Y0[2+i], c[2+i])

    #Y1 & f3
    CNOT | (Y1[1], c[1])
    CNOT | (Y1[0], c[0])
    for i in range(4):
        CNOT | (Y1[4+i], c[4+i])

    for i in range(4): #Y2 & cf
        CNOT | (Y2[i],c[i])

    CNOT | (Y2[6],c[6])
    CNOT | (Y2[7],c[7])

    for i in range(6): #Y3 & 3f
        CNOT | (Y3[i],c[i])

    x[0:8] = c

    #Y0&f3
    CNOT | (Y0[1], c1[1])
    CNOT | (Y0[0], c1[0])
    for i in range(4):
        CNOT | (Y0[4+i], c1[4+i])

    for i in range(4): # Y1 & cf
        CNOT | (Y1[i],c1[i])
    CNOT | (Y1[6],c1[6])
    CNOT | (Y1[7],c1[7])

    for i in range(6): #Y2 & 3f
        CNOT | (Y2[i],c1[i])

    for i in range(6): #Y3 & fc
        CNOT | (Y3[2+i], c1[2+i])

    x[8:16] = c1

    for i in range(4): # Y0 & cf
        CNOT | (Y0[i],c2[i])
    CNOT | (Y0[6],c2[6])
    CNOT | (Y0[7],c2[7])

    for i in range(6): #Y1 & 3f
        CNOT | (Y1[i],c2[i])

    for i in range(6): #Y2 & fc
        CNOT | (Y2[2+i], c2[2+i])

    #Y3 & f3
    CNOT | (Y3[1], c2[1])
    CNOT | (Y3[0], c2[0])
    for i in range(4):
        CNOT | (Y3[4+i], c2[4+i])
    x[16:24] = c2

    for i in range(6):  # Y0 & 3f
        CNOT | (Y0[i], c3[i])

    for i in range(6):  #Y1 &  fc
        CNOT | (Y1[2 + i], c3[2 + i])

    #Y2 & f3
    CNOT | (Y2[1], c3[1])
    CNOT | (Y2[0], c3[0])
    for i in range(4):
        CNOT | (Y2[4 + i], c3[4 + i])

    for i in range(4):  # Y3 & cf
        CNOT | (Y3[i], c3[i])
    CNOT | (Y3[6], c3[6])
    CNOT | (Y3[7], c3[7])
    x[24:32] = c3

def CDKM(eng, a, b, c, n):
    for i in range(n - 2):
        CNOT | (a[i + 1], b[i + 1])

    CNOT | (a[1], c)
    Toffoli_gate(eng, a[0], b[0], c)
    CNOT | (a[2], a[1])
    Toffoli_gate(eng, c, b[1], a[1])
    CNOT | (a[3], a[2])

    for i in range(n - 5):
        Toffoli_gate(eng, a[i + 1], b[i + 2], a[i + 2])
        CNOT | (a[i + 4], a[i + 3])

    Toffoli_gate(eng, a[n - 4], b[n - 3], a[n - 3])
    CNOT | (a[n - 2], b[n - 1])
    CNOT | (a[n - 1], b[n - 1])
    Toffoli_gate(eng, a[n - 3], b[n - 2], b[n - 1])

    for i in range(n - 3):
        X | b[i + 1]

    CNOT | (c, b[1])

    for i in range(n - 3):
        CNOT | (a[i + 1], b[i + 2])

    Toffoli_gate(eng, a[n - 4], b[n - 3], a[n - 3])

    for i in range(n - 5):
        Toffoli_gate(eng, a[n - 5 - i], b[n - 4 - i], a[n - 4 - i])
        CNOT | (a[n - 2 - i], a[n - 3 - i])
        X | (b[n - 3 - i])

    Toffoli_gate(eng, c, b[1], a[1])
    CNOT | (a[3], a[2])
    X | b[2]
    Toffoli_gate(eng, a[0], b[0], c)
    CNOT | (a[2], a[1])
    X | b[1]
    CNOT | (a[1], c)

    for i in range(n-1):
        CNOT | (a[i], b[i])

def CDKM_minus(eng, a, b, c, n):
    with Dagger(eng):
        for i in range(n - 2):
            CNOT | (a[i + 1], b[i + 1])

        CNOT | (a[1], c)
        Toffoli_gate(eng, a[0], b[0], c)
        CNOT | (a[2], a[1])
        Toffoli_gate(eng, c, b[1], a[1])
        CNOT | (a[3], a[2])

        for i in range(n - 5):
            Toffoli_gate(eng, a[i + 1], b[i + 2], a[i + 2])
            CNOT | (a[i + 4], a[i + 3])

        Toffoli_gate(eng, a[n - 4], b[n - 3], a[n - 3])
        CNOT | (a[n - 2], b[n - 1])
        CNOT | (a[n - 1], b[n - 1])
        Toffoli_gate(eng, a[n - 3], b[n - 2], b[n - 1])

        for i in range(n - 3):
            X | b[i + 1]

        CNOT | (c, b[1])

        for i in range(n - 3):
            CNOT | (a[i + 1], b[i + 2])

        Toffoli_gate(eng, a[n - 4], b[n - 3], a[n - 3])

        for i in range(n - 5):
            Toffoli_gate(eng, a[n - 5 - i], b[n - 4 - i], a[n - 4 - i])
            CNOT | (a[n - 2 - i], a[n - 3 - i])
            X | (b[n - 3 - i])

        Toffoli_gate(eng, c, b[1], a[1])
        CNOT | (a[3], a[2])
        X | b[2]
        Toffoli_gate(eng, a[0], b[0], c)
        CNOT | (a[2], a[1])
        X | b[1]
        CNOT | (a[1], c)

        for i in range(n-1):
            CNOT | (a[i], b[i])

def copy(eng, a, b, n):
    for i in range(n):
        CNOT | (a[i], b[i])

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

def FFunction(eng,R0,R1,key0,key1,ancilla):
    c = eng.allocate_qubit()

    CNOT32(eng,key0,R0)
    CNOT32(eng,key1,R1)
    CNOT32(eng,R0,R1)
    GFunction(eng,R1,ancilla)
    CDKM(eng,R1,R0,c,32)
    GFunction(eng, R0,ancilla)
    CDKM(eng,R0,R1,c,32)
    GFunction(eng, R1, ancilla)
    CDKM(eng, R1, R0, c, 32)

#01111100100011111000110001111110
def KeySched0(eng,A,C,KC,ancilla):
    c = eng.allocate_qubit()
    C2 = eng.allocate_qureg(32)
    copy(eng,C,C2,32)
    CDKM(eng,A,C,c,32)   # error
    CDKM_minus(eng,KC,C,c,32)
    GFunction(eng,C,ancilla)
    return C, C2

#11000111001101111010001000101100
def KeySched1(eng,B,D,KC,ancilla):
    c = eng.allocate_qubit()
    D2 = eng.allocate_qureg(32)
    copy(eng,D,D2,32)
    CDKM_minus(eng,B,D,c,32)
    CDKM(eng,KC,D,c,32)
    GFunction(eng, D,ancilla)
    return D,D2

def RightShift(eng,A,B):
    q = eng.allocate_qureg(8)
    A_result = []
    B_result = []
    for i in range(24):
        A_result.append(A[8 + i])
        B_result.append(B[8 + i])
    for i in range(8):
        A_result.append(q[i])  #(qubit) , error
        B_result.append(A[i])

    return A_result , B_result

def LeftShift(eng,C,D):
    q = eng.allocate_qureg(8)
    C_result =[]
    D_result = []
    for i in range(8):
        C_result.append(D[i+24])
        D_result.append(q[i])
    for i in range(24):
        C_result.append(C[i])
        D_result.append(D[i])

    return C_result,D_result

def EndianChange(eng,L0,L1,R0,R1):
    new_L0 = []
    new_L1 = []
    new_R0 = []
    new_R1 = []

    for i in range(8):
        new_L0.append(L0[24 + i])
        new_L1.append(L1[24 + i])
        new_R0.append(R0[24 + i])
        new_R1.append(R1[24 + i])

    for i in range(8):
        new_L0.append(L0[16 + i])
        new_L1.append(L1[16 + i])
        new_R0.append(R0[16 + i])
        new_R1.append(R1[16 + i])

    for i in range(8):
        new_L0.append(L0[8+ i])
        new_L1.append(L1[8+ i])
        new_R0.append(R0[8+ i])
        new_R1.append(R1[8+ i])

    for i in range(8):
        new_L0.append(L0[i])
        new_L1.append(L1[i])
        new_R0.append(R0[i])
        new_R1.append(R1[i])

    return new_L0,new_L1,new_R0,new_R1


def encrypt(eng,L0,L1,R0,R1,key0,key1,ancilla):
    old_R0 = eng.allocate_qureg(32)
    old_R1 = eng.allocate_qureg(32)
    copy(eng,R0,old_R0,32)
    copy(eng,R1,old_R1,32)
    FFunction(eng,R0,R1,key0,key1,ancilla)
    for i in range(32):
        CNOT | (L0[i],R0[i])
        CNOT | (L1[i],R1[i])

    return old_R0,old_R1


def Run(eng):
    L0 = eng.allocate_qureg(32)
    L1 = eng.allocate_qureg(32)
    R0 = eng.allocate_qureg(32)
    R1 = eng.allocate_qureg(32)
    A = eng.allocate_qureg(32)
    B = eng.allocate_qureg(32)
    C = eng.allocate_qureg(32)
    D = eng.allocate_qureg(32)
    key0 = eng.allocate_qureg(32)
    key1 = eng.allocate_qureg(32)
    KC_q = eng.allocate_qureg(32)
    KC_q2 = eng.allocate_qureg(32)
    ancilla = eng.allocate_qureg(152) # 38 * 4
    ancilla1 = eng.allocate_qureg(152)
    #key 1,0 = 7c8f8c7e / 1,1 = c737a22c
    KC = [0x9e3779b9, 0x3c6ef373, 0x78dde6e6, 0xf1bbcdcc, 0xe3779b99, 0xc6ef3733, 0x8dde6e67, 0x1bbcdccf,
          0x3779b99e,0x6ef3733c,0xdde6e678, 0xbbcdccf1, 0x779b99e3 ,0xef3733c6, 0xde6e678d , 0xbcdccf1b]


    if (resource_check != 1):
        Round_constant_XOR(eng, A, 0x00000000, 32)
        Round_constant_XOR(eng, B, 0x00000000, 32)
        Round_constant_XOR(eng, C, 0x00000000, 32)
        Round_constant_XOR(eng, D, 0x00000000, 32)
        Round_constant_XOR(eng, L0, 0x03020100, 32)
        Round_constant_XOR(eng, L1, 0x07060504, 32)
        Round_constant_XOR(eng, R0, 0x0B0A0908, 32)
        Round_constant_XOR(eng, R1, 0x0F0E0D0C, 32)

    L0,L1,R0,R1= EndianChange(eng,L0,L1,R0,R1)

    for i in range(16):
        if (resource_check!=1):
            Round_constant_XOR(eng, KC_q, KC[i], 32)
            Round_constant_XOR(eng, KC_q2, KC[i], 32)
        key0, C = KeySched0(eng, A, C, KC_q, ancilla)
        key1, D = KeySched1(eng, B, D, KC_q2, ancilla1)
        Round_constant_XOR(eng, KC_q, KC[i], 32)     #reverse, KC_q =0
        Round_constant_XOR(eng, KC_q2, KC[i], 32)
        L0,L1 = encrypt(eng, L0, L1, R0, R1, key0, key1, ancilla)

        if(i%2 ==0):
            A,B=  RightShift(eng, A, B)
        else :
            C,D = LeftShift(eng, C, D)

    #endian change & restore switching
    R0,R1,L0,L1= EndianChange(eng,L0,L1,R0,R1)

    if(resource_check!=1):
        print_state(eng,R0,32)
        print_state(eng,R1,32)
        print_state(eng,L0,32)
        print_state(eng,L1,32)



# global resource_check
# global AND_check
# print('Generate Ciphertext...')
# resource_check = 0
# classic = ClassicalSimulator()
# eng = MainEngine(classic)
# Run(eng)
# eng.flush()
# print('\n')

print('Estimate cost...')
resource_check = 1
AND_check = 0
Resource = ResourceCounter()
eng = MainEngine(Resource)
Run(eng)
print('\n')
print(Resource)
eng.flush()