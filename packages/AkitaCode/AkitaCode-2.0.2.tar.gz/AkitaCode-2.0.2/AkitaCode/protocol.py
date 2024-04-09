from .bd import Database

class Vector(object):
    """
    Objecte que conté la informació mínima per dur a terme una execució mitjançant l'arquitectura relacional per vectors.
    """
    def __init__(self,ids:int,data_type:str,value:int):
        """
        Crea un objecte de tipus Vector.

        :param ids: Identificador de la dada.
        :type ids: int
        :param data_type: Tipus de dada.
        :type data_type: str
        :param value: Valor que es vol assignar.
        :type value: int
        :rtype: None
        """
        self.ids = ids
        self.datatype = data_type
        self.value = value

    def __str__(self):
        """
        Retorna un string informatiu de la informació del vector.
        """
        str(dict(ids=self.ids,datatype=self.datatype,value=self.value))
        
        
    def __repr__(self) -> str:
        """
        Retorna representada la informació del vector.
        """
        return str(dict(ids=self.ids,datatype=self.datatype,value=self.value))


class Protocol(object):
    """
    La classe Protocol conté la definició d'un protocol estucturat per tal de facilitar la construcció de situacions (VSE).
    """
    def __init__(self, protocol_name:str):
        """
        Crea un objecte protocol del protocol <protocol_name> de la base de dades.
        Un cop creat l'objecte protocol, aquest es bloqueja i no pot ser modificat.

        :param protocol_name: Nom del protocol
        :type protocol_name: str
        :rtype: None
        """
        self.__lock = False
        self.__variables_rx = {}
        self.__variables_tx = {}
        self.__functions = {}
        self.__arguments = {}
        self.name = protocol_name


    def search(self,vector:Vector) -> dict|bool:
        """
        Cerca al protocol l'informació associada a un Vector <vector>.

        :param vector: Vector que es vol analizar.
        :type ids: Vector
        :return: Tota la informació solicitada ordenada amb els camps corresponents.
        :rtype: dict
        """
        if self.__lock:
            if vector.datatype == "F":
                if vector.ids in tuple(self.__functions.keys()):
                    return self.__functions[vector.ids]
                return False

            elif vector.datatype == "T":
                if vector.ids in tuple(self.__variables_tx.keys()):
                    return self.__variables_tx[vector.ids]
                return False

            elif vector.datatype == "R":
                if vector.ids in tuple(self.__variables_rx.keys()):
                    return self.__variables_rx[vector.ids]
                return False
                
            elif vector.datatype == "A":
                if vector.ids in tuple(self.__arguments.keys()):
                    return self.__arguments[vector.ids]
                return False
            return False
        return False
    


    def import_protocol(self, db:Database, p_id:int):
        """
        Importa el protocol amb identificador <p_id> de la instància de la base de dades <db>.
        """
        full_protocol = db.extract_protocol(p_id)
        self.__functions = full_protocol[0]
        self.__variables_tx = full_protocol[1]
        self.__variables_rx = full_protocol[2]
        self.__arguments = full_protocol[3]
        self.__lock = True
        return 0
    


if __name__ == "__main__":
    pass