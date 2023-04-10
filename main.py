# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/


def Sbox1(eng,x,n):
    x = Squaring(eng, x, n)
    x = Squaring(eng, x, n)
    x = Squaring(eng, x, n)

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

    if (resource_check != 1):
        print("sbox1")
        print_state(eng, out, 8)


def Sbox2(eng,x,n):
    x = Squaring(eng, x, n)
    x = Squaring(eng, x, n)
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


    out =[]
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

    if (resource_check != 1):
        print("sbox2")
        print_state(eng, out, 8)
