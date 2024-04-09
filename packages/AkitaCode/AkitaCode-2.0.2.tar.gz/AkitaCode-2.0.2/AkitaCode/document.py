
from .line import *
from .bd import *
from pathlib import Path
from .protocol import Protocol, Vector
from .conditionals import generate_combinations
import pickle
import time
from queue import Queue

VERSION = "2.0.2"

class Document(object):
    """
    La classe ``Document`` permet comprovar ràpidament la sintaxi dels documents de testeig i generar un testbench binari executable. Aquest mòdul requereix la classe "Line" (veure :doc:`mòdul Line <line>`), la qual també està documentada i pot gestionar la informació continguda en un objecte de la classe "Line" eficientment.
    """

    def __init__(self, file="", db="") -> None:
        """
        Inicialitzador de la classe Document.
        """
        self._error = False
        self._error_msg = None
        self.__document: list[Instance] = []
        self.__db = None
        self.__protocol_id = None
        if not Path(file).exists():
            self._error = True
            self._error_msg = f"[PathError] The selected file '{str(Path(file))}' does not exist or is not accessible at this time."
        else:
            if not Path(db).exists():
                self._error = True
                self._error_msg = "[DatabaseError] The specified database path does not exist, is corrupt, or is not currently accessible."
            else:
                self.__db = Database(db)
                with open(file, "r") as f:
                    nline = 1
                    for l in f:
                        line_instance = Line(n=nline, line=l)
                        if not line_instance.have_error():
                            converted_instance = line_instance.convert()
                            if converted_instance.is_error():
                                self._error = True
                                self._error_msg = converted_instance.get_error()
                                self.__document = []
                                break
                            else:
                                self.__document += [converted_instance]
                                nline += 1
                        else:
                            self._error = True
                            self._error_msg = line_instance.get_error()
                            self.__document = []
                            break



    def check_syntax(self, q: Queue) -> bool:
        """
        Comprova l'estrucura a nivell de document. <q> és una cua de missatges multiprocés.
        :return: True si l'estructura és vàlida, False altrament.
        :rtype: bool
        """
        for_instance:ForInstance = None
        time_statement = False
        level = 0
        if self._error:
            q.put(self._error_msg)
            return False
        for instance in self.__document:
            if isinstance(instance, SkipInstance):
                pass
            elif level == 0:
                if isinstance(instance, ProtocolInstance):
                    level += 1
                else:
                    q.put("[StructureError <Line {line}>] Protocol needs to be defined before other statements.".format(
                        line=instance.nline))
                    return False

            elif level == 1:
                if isinstance(instance, EnviromentInstance):
                    level += 1
                elif isinstance(instance,ForInstance):
                    level += 3
                    for_instance = instance
                else:
                    if isinstance(instance, SituationInstance):
                        q.put("[StructureError <Line {line}>] Cannot declare a Situation without first declaring an Environment statement.".format(
                            line=instance.nline))
                        return False
                    else:
                        q.put("[StructureError <Line {line}>] Statement not expected.".format(
                            line=instance.nline))
                        return False

            elif level == 2:
                if isinstance(instance, SituationInstance):
                    level += 1
                elif isinstance(instance, EndInstance):
                    level -= 1
                else:
                    q.put("[StructureError <Line {line}>] Statement not expected.".format(
                        line=instance.nline))
                    return False

            elif level == 3:
                if isinstance(instance, EndInstance):
                    level -= 1
                elif isinstance(instance, (VariableInstance, FunctionInstance)):
                    pass
                else:
                    q.put("[StructureError <Line {line}>] Statement not expected.".format(
                        line=instance.nline))
                    return False
                
            elif level == 4:
                if isinstance(instance,TimeInstance):
                    time_statement = True
                    level += 1
                else:
                    q.put("[StructureError <Line {line}>] Statement not expected.".format(
                        line=instance.nline))
                    return False
            
            elif level == 5:
                if isinstance(instance,(VariableInstance, FunctionInstance)): # // Quan estiguin disponibles les funcions.
                    if time_statement:
                        for_instance.nsituations += 1 
                    time_statement = False

                elif isinstance(instance,TimeInstance):
                    if time_statement:
                        q.put("[StructureError <Line {line}>] Time instance not expected after another Time instance.".format(
                        line=instance.nline))
                        return False
                    else:
                        time_statement = True
                elif isinstance(instance, EndInstance):
                    if time_statement:
                        q.put("[StructureError <Line {line}>] End instance not expected after Time instance. Must be declare variables or functions before End instance after Time instance.".format(
                        line=instance.nline))
                        return False
                    else:
                        for_instance = None
                        level -= 4
                else:
                    q.put("[StructureError <Line {line}>] Statement not expected.".format(
                        line=instance.nline))
                    return False     
        if level == 1:
            q.put("[Success!] No errors detected during structuration phase.")
            return True
        return False



    def check_spell(self, q:Queue):
        """
        Comprova que la informació facilitada per l'usuari sigui correcta, vàlida i coherent.
        """
        # Variables que s'accepten com a valors (han d'estar definides prèviament abans de ser usades i han de ser de tipus TX).
        layer = 0
        inside_for = False
        const_vars:dict = {}
        for instance in self.__document:
            if isinstance(instance, ProtocolInstance):
                p_id = self.__db.get_protocol_id(instance.name)
                if p_id is not None:
                    self.__protocol_id = p_id
                else:
                    q.put("[ProtocolError <Line {line}>] The ''{name}'' protocol not exist on database.".format(
                        line=instance.nline, name=instance.name))
                    return False

            elif isinstance(instance, VariableInstance):
                v_id = self.__db.get_variable_id(
                    p_id=self.__protocol_id, v_name=instance.name)
                if v_id is False:
                    q.put("[VariableError <Line {line}>] Variable ''{name}'' is not defined in ''{protocol}'' protocol.".format(
                        line=instance.nline, name=instance.name, protocol=self.__db.get_protocol_name(self.__protocol_id)))
                    return False
                instance.ids = v_id
                v_info = self.__db.get_info_from_variable(v_id)
                nbits: str = v_info["variable_mask"]
                nbits = nbits.count("1")
                instance.is_response = True if v_info["variable_direction"] == 1 else False
                if instance.value is None:
                    instance.value = v_info["variable_default"]
                try:
                    # print("Instance Value A:",instance.value, type(instance.value))
                    if not isinstance(instance.value,int):
                        v_value:int = int(instance.value,0)
                    else:
                        v_value = instance.value
                    # print("Instance Value B:",instance.value)
                    instance.value = v_value
                    if nbits > 1:
                        mult = int(v_info["variable_mul"])
                        div = int(v_info["variable_div"])
                        offset = int(v_info["variable_offset"])
                        v_value = int((v_value*mult)/div)+offset
                        # Cal comprovar si el valor hi té cabuda.
                        if v_info["variable_is_signed"] == 1:
                            if v_value not in range(-2**(nbits-1), 2**(nbits-1)):
                                q.put("[ValueError <Line {line}>] Value {value} exceeds minimum or maximum {variable} value. Overflow!".format(
                                    line=instance.nline, value=v_value, variable=instance.name))
                                return False
                        else:
                            if v_value not in range(0, 2**(nbits)):
                                q.put("[ValueError <Line {line}>] Value {value} exceeds maximum {variable} value. Overflow!".format(
                                    line=instance.nline, value=v_value, variable=instance.name))
                                return False

                        if v_info["variable_direction"] == 0:
                            const_vars[instance.name] = instance.value

                    elif nbits == 1:
                        if v_value not in range(0, 2):
                            q.put("[ValueError <Line {line}>] Value {value} exceeds maximum {variable} value. Overflow!".format(
                                line=instance.nline, value=v_value, variable=instance.name))
                            return False

                        if v_info["variable_direction"] == 0:
                            const_vars[instance.name] = instance.value

                    else:
                        q.put("[ValueError <Line {line}>] Unexpected number of bits".format(
                            line=instance.nline))
                        return False
                except:
                    v_value:str = instance.value
                    # print(v_value)
                    if (v_value == "True" and nbits == 1) or (v_value == "False" and nbits == 1) or (v_value is None):
                        instance.value = 1 if v_value == "True" else 0
                        const_vars[instance.name] = instance.value
                    elif (v_value == "True" and nbits != 1) or (v_value == "False" and nbits != 1):
                        q.put("[ValueError <Line {line}>] Value ''{value}'' is only valid for boolean variables. Evaluated variable is {name}.".format(
                                line=instance.nline, value=v_value, name=instance.name))
                        return False
                    elif v_value in list(const_vars.keys()):
                        # Busquem la informació de la variable de la qual es vol afegir el valor.
                        # Han de compartir tipus, signe i longitud. En cas contrari, haurà de donar error.
                        value_variable_id = self.__db.get_variable_id(
                            p_id=self.__protocol_id, v_name=v_value)
                        value_variable_info = self.__db.get_info_from_variable(
                            v_id=value_variable_id)
                        value_nbits: str = value_variable_info["variable_mask"]
                        if value_variable_info["variable_direction"] == 1:
                            q.put("[ValueError <Line {line}>] Value of {value} cannot be used as the value of variable {name} because output assignment is not allowed.".format(
                                line=instance.nline, value=v_value, name=instance.name))
                            return False
                        if value_nbits.count("1") != nbits:
                            print(value_nbits.count("1"), nbits)
                            q.put("[ValueError <Line {line}>] Value of {value} cannot be used as the value of variable {name} because they differ in bit length.".format(
                                line=instance.nline, value=v_value, name=instance.name))
                            return False
                        if value_variable_info["variable_is_signed"] != v_info["variable_is_signed"]:
                            q.put("[ValueError <Line {line}>] Value of {value} cannot be used as the value of variable {name} because they differ in the type of variable.".format(
                                line=instance.nline, value=v_value, name=instance.name))
                            return False
                        if not inside_for:
                            instance.value = const_vars[v_value]
                        const_vars[instance.name] = instance.value
                    elif v_value not in list(const_vars.keys()):
                        print(const_vars)
                        q.put("[AssignmentError <Line {line}>] Value ''{value}'' is not defined previously and cannot be assigned.".format(
                            line=instance.nline, value=v_value, name=instance.name))
                        return False
                    else:
                        q.put("[ValueError <Line {line}>] Value {value} on variable ''{name}'' is not a valid value.".format(
                            line=instance.nline, value=v_value, name=instance.name))
                        return False

            elif isinstance(instance, FunctionInstance):
                # Busquem l'identificació de la funció amb el nom de la instància funció.
                f_id = self.__db.get_function_id(p_id=self.__protocol_id,f_name=instance.name)
                # Si no existeix llançem error i retornem False.
                if f_id is None:
                    q.put("[FunctionError <Line {line}>] Function ''{name}'' is not defined in ''{protocol}'' protocol.".format(
                        line=instance.nline, name=instance.name, protocol=self.__db.get_protocol_name(self.__protocol_id)))
                    return False
                # Si la funció existeix obtemim els arguments que conté i els comparem amb els que té la instáncia.
                instance.ids = f_id
                f_args = self.__db.get_arguments_from_function(f_id)
                instance_len = len(instance.arguments.keys())
                args_len = len(f_args)
                # Comprovem el nombre d'arguments esperats.
                if instance_len != args_len:
                    q.put("[FunctionError <Line {line}>] Function ''{name}'' have {args_len} arguments but given {instance_len}. Number of arguments mismatch.".format(
                        line=instance.nline, name=instance.name, args_len=args_len, instance_len=instance_len))
                    return False
                # Si coincideixen el nombre d'arguments amb els de la instància, comprovem si existeixen per la funció objectiu.
                for arg in instance.arguments.keys():
                    if arg not in f_args:
                        q.put("[ArgumentError <Line {line}>] Argument ''{arg}'' is not a valid argument for {function_name} function. Possible arguments must be: {args}.".format(
                            line=instance.nline, arg=arg, function_name=instance.name, args=f_args))
                        return False
                    else:
                        # Processem la informació de cada un dels arguments.
                        a_id = self.__db.get_argument_id(
                            f_id=f_id, a_name=arg)
                        if a_id is None:
                            q.put("[ArgumentError <Line {line}>] Argument ''{name}'' is not defined in ''{function_name}'' function.".format(
                                line=instance.nline, name=instance.name, protocol=instance.name))
                            return False
                        arg_info = self.__db.get_info_from_argument(a_id)
                        nbits: str = arg_info["argument_mask"]
                        nbits = nbits.count("1")
                        try:
                            arg_value = int(instance.arguments[arg],0)
                            instance.arguments[arg] = arg_value
                            if nbits > 1:
                                mult = int(arg_info["argument_mul"])
                                div = int(arg_info["argument_div"])
                                offset = int(arg_info["argument_offset"])
                                arg_value = int((arg_value*mult)/div)+offset
                                # Cal comprovar si el valor hi té cabuda.
                                if arg_info["argument_is_signed"] == 1:
                                    if arg_value not in range(-2**(nbits-1), 2**(nbits-1)):
                                        q.put("[ValueError <Line {line}>] Value {value} exceeds minimum or maximum {argument} argument value. Overflow!".format(
                                            line=instance.nline, value=arg_value, argument=instance.name))
                                        return False
                                else:
                                    if arg_value not in range(0, 2**(nbits)):
                                        q.put("[ValueError <Line {line}>] Value {value} exceeds maximum {argument} argument value. Overflow!".format(
                                            line=instance.nline, value=arg_value, argument=instance.name))
                                        return False

                            elif nbits == 1:
                                if arg_value not in range(0, 2):
                                    q.put("[ValueError <Line {line}>] Value {value} exceeds maximum {argument} argument value. Overflow!".format(
                                        line=instance.nline, value=arg_value, argument=instance.name))
                                    return False

                            else:
                                q.put("[ValueError <Line {line}>] Unexpected number of bits".format(
                                    line=instance.nline))
                                return False
                        except:
                            v_value = instance.arguments[arg]
                            if (v_value == "True" and nbits.count("1") == 1) or (v_value == "False" and nbits.count("1") == 1) or (v_value is None):
                                instance.arguments[arg] = 1 if v_value == "True" else 0
                            elif v_value in list(const_vars.keys()):
                                # Busquem la informació de la variable de la qual es vol afegir el valor.
                                # Han de compartir tipus, signe i longitud. En cas contrari, haurà de donar error.
                                value_variable_id = self.__db.get_variable_id(
                                    p_id=self.__protocol_id, v_name=v_value)
                                value_variable_info = self.__db.get_info_from_variable(
                                    v_id=value_variable_id)
                                value_nbits: str = value_variable_info["variable_mask"]
                                if value_variable_info["variable_direction"] == 1:
                                    q.put("[ValueError <Line {line}>] Value of {value} cannot be used as the value of argument {name} because output assignment is not allowed.".format(
                                        line=instance.nline, value=v_value, name=instance.name))
                                    return False
                                if value_nbits.count("1") != nbits:
                                    q.put("[ValueError <Line {line}>] Value of {value} cannot be used as the value of argument {name} because they differ in bit length.".format(
                                        line=instance.nline, value=v_value, name=instance.name))
                                    return False
                                if value_variable_info["variable_is_signed"] != arg_info["argument_is_signed"]:
                                    q.put("[ValueError <Line {line}>] Value of {value} cannot be used as the value of argument {name} because they differ in the type of variable.".format(
                                        line=instance.nline, value=v_value, name=instance.name))
                                    return False
                                if not inside_for:
                                    instance.arguments[arg] = const_vars[v_value]
                            elif v_value not in list(const_vars.keys()):
                                q.put("[AssignmentError <Line {line}>] Value {value} is not defined previously and cannot be assigned.".format(
                                    line=instance.nline, value=v_value, name=instance.name))
                                return False
                            else:
                                q.put("[ValueError <Line {line}>] Value {value} on variable ''{name}'' is not a valid value.".format(
                                    line=instance.nline, value=v_value, name=instance.name))
                                return False

            elif isinstance(instance, ForInstance):
                inside_for = True
                layer += 1
                for item in instance.iter:
                    v_id = self.__db.get_variable_id(self.__protocol_id,item)
                    if v_id is None:
                        q.put("[VariableError <Line {line}>] Variable ''{name}'' is not defined in ''{protocol}'' protocol.".format(
                            line=instance.nline, name=item, protocol=self.__db.get_protocol_name(self.__protocol_id)))
                        return False
                    # print(instance.iter)
                    v_info = self.__db.get_info_from_variable(v_id)["variable_direction"]
                    if v_info == 1:
                        q.put("[ForVariableError <Line {line}>] Variable ''{name}'' is defined as input, not as output. For instance not allow input variables.".format(
                            line=instance.nline, name=item))
                        return False
                    const_vars[item] = None                
            
            elif isinstance(instance, EndInstance):
                if (inside_for and layer == 1) or (not inside_for and layer == 2):
                    inside_for = False
                    const_vars = {}
                layer -= 1
            
            elif isinstance(instance, TimeInstance):
                pass
            
            elif isinstance(instance, (EnviromentInstance, SituationInstance)):
                layer += 1
            
            elif isinstance(instance, SkipInstance):
                pass
            
            else:
                q.put("[TypeError <Line {line}>] {instance_type} is not already defined. Report bug via email to aamat@ausa.com.".format(
                    line=instance.nline, instance_type=str(instance)))
                return False
        q.put("[Success!] No errors detected during spell phase.")
        return True



    def makec(self,q:Queue,pathname:Path|str,emulate:bool=False,autoclose:bool=False):
        """
        Crea el document executable per la realització de la validació.
        """
        emu = emulate
        p_id = None
        protocol = None
        exportable = []
        in_for = False
        current_for_situation:int = 0
        for_number_of_situations:int = 0
        for_situations:list[dict]|None = None
        instance_level = 0
        timeTotal = 0
        timeA = time.perf_counter()
        for instance in self.__document:

            if time.perf_counter()-timeA >= 1:
                timeTotal += time.perf_counter()-timeA
                timeA = time.perf_counter()
                print(timeTotal)

            if isinstance(instance,ProtocolInstance):
                p_id = self.__db.get_protocol_id(instance.name)
                protocol = Protocol(instance.name)
                instance_level += 1

            elif isinstance(instance, EnviromentInstance):
                exportable += [Vector(instance.name,"E",None)]
                instance_level +=1

            elif isinstance(instance, SituationInstance):
                exportable += [Vector(instance.name, "S", instance.time)]
                instance_level +=1

            elif isinstance(instance,VariableInstance):
                if not in_for:
                    exportable += [Vector(ids=instance.ids,data_type="R" if instance.is_response else "T", value=instance.value)]
                else:
                    if isinstance(instance.value,int):
                        for i in range(current_for_situation-1,len(for_situations),for_number_of_situations):
                            for_situations[i][instance.name] = instance.value
                    else:
                        for i in range(current_for_situation-1,len(for_situations),for_number_of_situations):
                            for_situations[i][instance.name] = for_situations[i][instance.value]

            elif isinstance(instance,FunctionInstance):
                if not in_for:
                    exportable += [Vector(instance.ids,"F",None)]
                    for arg in tuple(instance.arguments.keys()):
                        exportable += [Vector(ids=self.__db.get_argument_id(instance.ids,arg),data_type="A",value=instance.arguments[arg])]
                else:
                    # Recorrem el llistat de situacions
                    for i in range(current_for_situation-1,len(for_situations),for_number_of_situations):
                        for_situations[i]["**functions"][instance.name] = {}
                        for argument in tuple(instance.arguments.keys()):
                            if isinstance(instance.arguments[argument],int):
                                for_situations[i]["**functions"][instance.name][argument] = instance.arguments[argument]
                            else:
                                for_situations[i]["**functions"][instance.name][argument] = for_situations[i][instance.arguments[argument]]
                            # Es possible que pugui donar error d'indexació quan s'intenta afegir el valor d'una variable anterior definida a l'hora de passar-ho com argument.
                            # Intentar detectar l'error i, si es possible, manipular-ho amb conseqüència.
                    # #######  Revisar!!

            elif isinstance(instance, EndInstance):
                instance_level -=1
                if in_for:
                    in_for = False
                    curr_env_name = None
                    # Itera per totes les situacions
                    for i in range(0, len(for_situations)):
                        if time.perf_counter()-timeA >= 1:
                            timeTotal += time.perf_counter()-timeA
                            timeA = time.perf_counter()
                            q.put(timeTotal)
                        # Busca la primera situació de cada entorn i inicialitza l'entorn.
                        if i % for_number_of_situations == 0:
                            exportable += [Vector(ids=curr_env_name,data_type="E",value=None)]
                        # Creem una nova situació per cada diccionari de la llista.
                        exportable += [Vector(ids=0,data_type="S",value=for_situations[i]["**time"])]
                        # Cerquem totes les variables
                        sit_variables = [element for element in list(for_situations[i].keys()) if element not in ("**time","**functions")]
                        # Creem els Vectors en funció del tipus de variable.
                        for var in sit_variables:
                            var_id = self.__db.get_variable_id(self.__protocol_id,var)
                            exportable += [Vector(
                                ids=var_id,
                                data_type= "T" if self.__db.get_info_from_variable(var_id)["variable_direction"] == 0 else "R",
                                value=for_situations[i][var])]
                            
                        # Creem els Vectors de les funcions
                        sit_fn = [element for element in list(for_situations[i]["**functions"].keys())]
                            # Si un argument depén d'una variable, s'ha de comprovar.
                        for fn in sit_fn:
                            fn_id = self.__db.get_function_id(self.__protocol_id,fn)
                            exportable += [Vector(
                                ids=fn_id,
                                data_type="F",
                                value=None
                            )]
                            fn_arg_names = self.__db.get_arguments_from_function(fn_id)
                            fn_arg_id = self.__db.get_all_argument_id_from_function(fn_id)
                            for arg in range(len(fn_arg_id)):
                                exportable += [Vector(
                                    ids=fn_arg_id[arg],
                                    data_type="A",
                                    value=for_situations[i]["**functions"][fn][fn_arg_names[arg]]
                                )]

                        

            elif isinstance(instance, ForInstance):
                instance_level += 1
                in_for = True
                current_for_situation = 0
                for_number_of_situations = instance.nsituations
                for_situations = generate_combinations(database=self.__db,
                                                       protocol_id=self.__protocol_id,
                                                       iterlist=instance.iter,
                                                       num_situations=instance.nsituations)
                

            elif isinstance(instance, TimeInstance):
                current_for_situation += 1
                for i in range(current_for_situation-1,len(for_situations),for_number_of_situations):
                    for_situations[i]["**time"] = instance.time
                    
                




        if instance_level == 1:
            the_file = {
                "protocol": protocol,
                "data": exportable,
                "compiler_version": VERSION
            }
            try:
                pickle.dump(the_file,open(str(pathname),"wb"))
                q.put("Make testbench operation completed successfuly.")
                q.put(autoclose)
                return 0
            except:
                q.put("[ERROR] Operation make failed!")
                q.put(False)
                return 3
        else:
            return 4


if __name__ == "__main__":
    # Create a database instance.
    # import config_mod
    import queue
    q = queue.Queue()
    # db = config_mod.get_db_path()
    db = "C:/Users/aamat/.akitacan/data.db"
    # Get path of file.
    filename = "prova_for_time"
    in_filename = "E:/Akitacan/dev/AkitaCode/test/{}{}".format(filename,".atd")
    out_filename = "E:/Akitacan/dev/AkitaCode/test/{}{}".format(filename,".akita")

    # Create a document instance.
    doc = Document(in_filename, db)

    # print(doc._error)
    # print(doc._error_msg) if doc._error_msg is not None else print("Success!!")

    fase_A = doc.check_syntax(q)
    print("FASE A: {}".format(fase_A))
    print(q.get())
    if fase_A:
        fase_B = doc.check_spell(q)
        print("FASE B: {}".format(fase_B))
        print(q.get())
        if fase_B:
            fase_C = doc.makec(q,out_filename,autoclose=True)
            print("FASE C: {}".format(fase_C))
            print(q.get())
            if fase_C == 0:
                f = pickle.load(open(out_filename,"rb"))
                f = f["data"]
                for l in f:
                    print(repr(l)+"\r")
                # print(f)
            print(q.get())