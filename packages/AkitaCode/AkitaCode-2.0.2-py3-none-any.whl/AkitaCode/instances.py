import random
import os

random.seed(os.getpid()*2)

class UnknownCommand(Exception):
    """
    Classe que llença una excepció quan es detecten dades no esperades.
    """
    def __init__(self, message:str) -> None:
        self.message = message

    def __str__(self) -> str:
        return "UnknownCommand Exception launched: {}".format(self.message)


class Instance(object):
  """
  Clase genèrica d'instància.
  """
  def __init__(self,nline:int) -> None:
      self.error = False
      self.error_msg = None
      self.nline = nline


  def is_error(self) -> bool:
      return self.error
  

  def get_error(self) -> str|None:
      return self.error_msg


class SkipInstance(Instance):
    """
    Es tracta d'un indicador de línia a ser ignorat.
    """
    def __init__(self, nline: int) -> None:
        super().__init__(nline)
        pass


class ErrorInstance(Instance):
    """
    Indica que una línia conté errors i que no s'ha pogut convertir. Preveu l'execució malintencionada de comanda ''Line.convert()''.
    """
    def __init__(self,nline:int,error_msg:str) -> None:
        super().__init__(nline=nline)
        self.error = True
        self.error_msg = "[CompilationError <Line {}>] Line cannot be converted because it contains errors.\n{}".format(nline,error_msg)


class UndefinedInstance(Instance):
    """
    Indica que la línia és vàlida però que no està definida i, per tant no s'ha pogut convertir.
    """
    def __init__(self,nline:int) -> None:
        super().__init__(nline)
        self.error = True
        self.error_msg = "[CompilationError <Line {}>] Undefined or unknown line type. Report this bug via email to aamat@ausa.com.".format(nline)


class ProtocolInstance(Instance):
    """
    Representa una línia Protocol.
    """
    def __init__(self, nline:int, line_parsed:list[str]) -> None:
        super().__init__(nline=nline)
        self.ids = None
        self.name = None
        try:
            self.name = line_parsed[2]
        except:
            self.error = True 


class VariableInstance(Instance):
    """
    Representa una línia Variable.
    """
    def __init__(self, nline:int, line_parsed:list[str]) -> None:
        super().__init__(nline=nline)
        # Variable propierties.
        self.ids = None
        self.name = None
        self.value = None
        self.is_response = None
        # Check propierties.
        self.__check(line_parsed)

    def __check(self,args:list[str]):
        """
        Comprova les propietats de la línia variable.
        """
        try:
            if len(args) == 4:
                self.name = args[1]
                self.value = args[3]
            elif len(args) == 2:
                self.name = args[1]
            else:
                raise UnknownCommand("Length for arguments on variable instance not expected.")
        except UnknownCommand as e:
            self.error = True
            self.error_msg = e


class FunctionInstance(Instance):
    """
    Representa una línia Funció.
    """
    def __init__(self, nline:int, line_parsed:list[str]) -> None:
        super().__init__(nline)
        # Function propierties.
        self.ids:int = None
        self.name:str = None
        self.arguments:dict = {}
        # Check propierties.
        self.__check(line_parsed)

    def __check(self,args:list[str]):
        """
        Comprova les propietats de la línia funció.
        """
        try:
            self.name = args[1]
            open_query = args.index("(")
            close_query = args.index(")")
            rawquery = args[open_query+1:close_query]
            query = [i for i in rawquery if i != "|"]
            
            for e in tuple(range(0,len(query)-1,2)):
                self.arguments[query[e]] = query[e+1]
        except:
            self.error = True
            self.error_msg = "Function description error."


class ForInstance(Instance):
    """
    Representa una línia For.
    """
    def __init__(self, nline:int, line_parsed:list[str]) -> None:
        super().__init__(nline)
        # For propierties.
        self.iter = []
        self.nsituations = 0
        # Check propierties.
        self.__check(line_parsed)

    def __check(self,args:list[str]):
        """
        Comprova les propietats de la línia for.
        """
        try:
            open_query = args.index("(")
            close_query = args.index(")")
            args = args[open_query+1:close_query]
            self.iter=[args[e] for e in range(0,close_query-open_query,2)]
        except:
            self.error = True
            self.error_msg = "For description error."


class TimeInstance(Instance):
    """
    Representa una línia Time.
    """
    def __init__(self, nline:int, line_parsed:list[str]) -> None:
        super().__init__(nline)
        # For propierties.
        self.time = 100
        # Check propierties.
        self.__check(line_parsed)

    def __check(self,args:list[str]):
        """
        Comprova les propietats de la línia for.
        """
        try:
            self.time = args[1]
            self.time = int(self.time)
        except:
            self.error = True
            self.error_msg = "[TimeInstanceError] Invalid time (ms) format. Only accepts integer values in decimal."

        
class SituationInstance(Instance):
    """
    Representa una línia Situació.
    """
    def __init__(self, nline:int, line_parsed:list[str]) -> None:
        super().__init__(nline)
        # Situation propierties.
        self.name = None
        self.time = None
        # Check propierties.
        self.__check(line_parsed)

    
    def __check(self,args:list[str]):
        """
        Comprova les propietats de la línia Situació.
        """
        try:
            self.name = args[2]
            if self.name == "_":
                self.name = hex(random.randint(0,2**48))[2:]
                
            self.time = args[5]
            self.time = int(self.time)
        except:
            self.error = True
            self.error_msg = "[VariableError] Invalid time (ms) format. Only accepts integer values in decimal."


class EnviromentInstance(Instance):
    """
    Representa una línia entorn.
    """
    def __init__(self, nline:int, line_parsed:list[str]) -> None:
        super().__init__(nline)
        # Enviroment propierties.
        self.name = None
        # Check propierties.
        self.__check(line_parsed)

    
    def __check(self,args:list[str]):
        """
        Comprova les propietats de la línia entorn.
        """
        try:
            self.name = args[2]
            if self.name == "_":
                self.name = hex(random.randint(0,2**48))[2:]
        except:
            self.error = True


class EndInstance(Instance):
    """
    Representa una línia end.
    """
    def __init__(self, nline:int, line_parsed:list[str]) -> None:
        super().__init__(nline=nline)
        try:
            if line_parsed[0] != "end":
                self.error = True
        except:
            self.error = True


if __name__ == "__main__":
    pass