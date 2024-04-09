import operator
import copy
from .bd import Database
from itertools import product, zip_longest

# Parte 1: Generación de combinaciones
def generate_combinations(database:Database, protocol_id:int, iterlist:list[str], num_situations:int):
    # Comprova que tot el llistat de variables de iterlist existeixin.
    var_ids = [database.get_variable_id(protocol_id,var) for var in iterlist]
    # Si no existeixen, es retorna None perque no es pot realitzar 
    # l'operació amb els elements de iterlist introduits.
    for var in var_ids:
        if var is None:
            return None
    
    # Obtenim tota la informació de les variables de iterlist.
    all_var_info = [database.get_info_from_variable(v_id=ids) for ids in var_ids]

    # Filtrem la informació de les variables de iterlist amb només la informació necessaria (0.is_signed,1.nºbits,2.factor multiplicador,3.factor divisor).
    need_var_info = [(d["variable_is_signed"],d["variable_mask"].count("1"),d["variable_mul"],d["variable_div"]) for d in all_var_info]
    # Realitzem el càlcul en funció de si la variable és signed o no.
    ranges = [range(0,2**nbits,int((1*mul)/div)) if signed == 0 else range(-2**(nbits-1),2**(nbits-1),int((1*mul)/div)) for signed, nbits, mul, div in need_var_info]
    # print(ranges)
    lista_final = []
    combinaciones = []
    for values in product(*ranges):
        combinacion = dict(zip(iterlist, values))
        combinacion["**time"] = 100
        combinacion["**functions"] = {}
        combinaciones.append(combinacion)

    lista_final = [copy.deepcopy(elemento) for elemento in combinaciones for _ in range(num_situations)]
    return lista_final # combinaciones



# Parte 2: Filtración avanzada de combinaciones
def filtrar_combinaciones_mixtas(combinaciones, condiciones):
    operadores = {
        "==": operator.eq,
        "!=": operator.ne,
        "<": operator.lt,
        "<=": operator.le,
        ">": operator.gt,
        ">=": operator.ge,
    }

    combinaciones_filtradas = []
    
    for combinacion in combinaciones:
        resultado_previo = None
        operacion_logica_anterior = None
        
        for i, cond in enumerate(condiciones):
            clave, operador, valor, operacion_logica = cond
            funcion_operador = operadores[operador]
            resultado_actual = funcion_operador(combinacion[clave], valor)
            
            if i == 0:
                resultado_previo = resultado_actual
            else:
                if operacion_logica_anterior == "AND":
                    resultado_previo = resultado_previo and resultado_actual
                elif operacion_logica_anterior == "OR":
                    resultado_previo = resultado_previo or resultado_actual
            
            operacion_logica_anterior = operacion_logica
        
        if resultado_previo:
            combinaciones_filtradas.append(combinacion)

    return combinaciones_filtradas

# Ejemplo de uso
if __name__ == "__main__":
    import time
    # from config_mod import get_db_path
    # db = Database(get_db_path())
    protocol = 1
    db = "C:/Users/aamat/.akitacan/data.db"

    variables = ["BAT_NUMBER_OF_BATTERIES", "BAT_VIRTUAL_BATTERY_SOC"]
    # variables = ["BAT_VIRTUAL_BATTERY_SOC"]
    condiciones = [
        # ("A", "==", 1, None),
        ("BAT_NUMBER_OF_BATTERIES", "==", 0, "AND"),
        ("BAT_VIRTUAL_BATTERY_SOC", "==", 1, "OR"),
        ("BAT_NUMBER_OF_BATTERIES", "==", 1, "AND"),
        ("BAT_VIRTUAL_BATTERY_SOC", "==", 0, None)
    ]
    init_time = time.time()
    combinaciones = generate_combinations(db,protocol,variables,1)
    print(combinaciones)
    combinaciones_filtradas = filtrar_combinaciones_mixtas(combinaciones, condiciones)
    print(combinaciones_filtradas)
    print(time.time()-init_time)
    with open("E:/prova_autogen.txt", "w") as f:
        for e in combinaciones:
            f.write(str(e)+"\n")

