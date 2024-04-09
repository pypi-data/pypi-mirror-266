def to_signed_format(n):
    """
    Aquesta funció converteix un enter negatiu a la seva representació en complement a dos.
    
    :param n: Enter que es vol convertir a complement a dos.
    :type n: int
    :return: Representació en binari signat en complement a dos o False si n no és un enter negatiu.
    :rtype: int (or False)
    """
    if type(n) == int:
        if n < 0:
            nstr = "{0:b}".format(n)
            aux = int(nstr[1:],2)
            exp = 0
            for e in list(range(0,64)):
                if (2**e) >= aux:
                    exp = e
                    break
            r = n + (2*(2**exp))
            return r
        else:
            return False
    else:
        False



def to_int_format(n):
    """
    Aquesta funció converteix un enter en format de complement a dos (utilitzat en la codificació de números negatius) 
    a un enter negatiu.

    :param n: Valor que es vol convertir a format de complement a dos.
    :type n: int
    :return: Valor resultant de la conversió o False si n no és un enter.
    :rtype: int (or False)
    """
    if type(n) == int:
        if n > 0:
            nstr = "{0:b}".format(n)
            newval = 0
            for i in list(range(len(nstr))):
                if i == 0:
                    newval -= 2**((len(nstr)-1)-i)*int(nstr[i])
                else:
                    newval += 2**((len(nstr)-1)-i)*int(nstr[i])
            
            return newval
            
        else:
            return False
    else:
        return False
    

def list_to_int(l:list):
    """
    Converteix una llista de enters compressos entre 0-255, en un enter.
    """
    return int.from_bytes(bytes(l))


def ss_to_signed_format(n):
    """
    Convierte un entero negativo a su representación en complemento a dos.

    :param n: Entero que se quiere convertir a complemento a dos.
    :type n: int
    :return: Representación en binario signado en complemento a dos o False si n no es un entero negativo.
    :rtype: str or bool
    """
    if isinstance(n, int):
        if n < 0:
            # Obtener el número binario sin el signo
            nbits = len(bin(n)[2:])
            binary = bin(n & (2**(nbits)-1))[2:]
            # Extender el número binario a 64 bits si es necesario
            # binary = binary.zfill(64)
            return int(binary,2)
        else:
            return False
    else:
        return False



def ss_to_int_format(n):
    """
    Convierte un entero en formato de complemento a dos a un entero negativo.

    :param n: Valor que se quiere convertir a formato de complemento a dos.
    :type n: int
    :return: Valor resultante de la conversión o False si n no es un entero.
    :rtype: int or bool
    """
    if isinstance(n, int):
        if n & (1 << 63):  # Comprueba si el bit más significativo está encendido
            complement = n ^ ((1 << 64) - 1)  # Calcula el complemento a uno
            return -(complement + 1)  # Calcula el complemento a dos
        else:
            return False
    else:
        return False




if __name__ == "__main__":
    # a = -4
    # print(to_signed_format(a))
    a = -12
    b = -5
    c = -27
    d = -1
    e = -129
    # print(to_signed_format(a))
    print(ss_to_signed_format(a))
    print(ss_to_signed_format(b))
    print(ss_to_signed_format(c))
    print(ss_to_signed_format(d))
    print(ss_to_signed_format(e))
    a = 20
    b = 11
    c = 37
    d = 3
    e = 383
    print(ss_to_int_format(a))
    print(ss_to_int_format(b))
    print(ss_to_int_format(c))
    print(ss_to_int_format(d))
    print(ss_to_int_format(e))
    # print(to_int_format(d))
    