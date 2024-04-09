"""
Àlex Amat - Versión 0.1.0256
"""
from .data import *
from .protocol import Protocol, Vector

class Frame(object):
    """
    La classe Frame representa una trama CAN que serà enviada o rebuda posteriorment. Aquesta classe conté els mètodes per afegir dades específiques de la classe Data a la trama.
    """
    def __init__(self):
        """
        Crea una instància de tipus Frame. La trama és buida quan s'instancia. 
        """
        self._can_id:int = None
        self._is_response:bool = None
        self._is_function:bool = None
        self._datalist:list[Data] = []
        self.__function:Function|None = None



    def add_to_frame(self, vector:Vector, protocol:Protocol) -> int:
        """
        Converteix un objecte de la classe Vector <vector> a un objecte de la subclasse Data vàlid prenent com a referencia l'objecte Protocol <protocol>.

        .. container::

            .. table:: Codis de retorn de la funció ``add_to_frame()``.
                :name: codi-retorn-afegir-dada

                +----------------+--------------------------------------------------------------------------------------------------------+
                | Codi de Retorn | Descripció                                                                                             |
                +----------------+--------------------------------------------------------------------------------------------------------+
                | 0              | Operació completada amb èxit.                                                                          |
                +----------------+--------------------------------------------------------------------------------------------------------+
                | 1              | El paràmetre <vector> no és de tipus Vector.                                                           |
                +----------------+--------------------------------------------------------------------------------------------------------+
                | 2              | El paràmetre <protocol> no és de tipus Protocol.                                                       |
                +----------------+--------------------------------------------------------------------------------------------------------+
                | 3              | No s'ha trobat al protocol <protocol> la referència de l'objecte Vector <vector>.                      |
                +----------------+--------------------------------------------------------------------------------------------------------+
                | 4              | L'objecte Vector <vector> no és vàlid quan la trama és buida.                                          |
                +----------------+--------------------------------------------------------------------------------------------------------+
                | 5              | Conflicte entre màscares a afegir un objecte Vector <vector> de tipus Argument.                        |
                +----------------+--------------------------------------------------------------------------------------------------------+
                | 6              | Error en obtenir l'identificador de la funció associada a l'objecte Vector <vector> de tipus Argument. |
                +----------------+--------------------------------------------------------------------------------------------------------+
                | 7              | L'objecte Vector <vector> no és vàlid quan la trama pertany a una Funció.                              |
                +----------------+--------------------------------------------------------------------------------------------------------+
                | 8              | Possible manipulació de l'objecte trama. Error durant la vinculació de la funció a la trama.           |
                +----------------+--------------------------------------------------------------------------------------------------------+
                | 9              | Conflicte entre màscares a afegir un objecte Vector <vector> de tipus Variables.                       |
                +----------------+--------------------------------------------------------------------------------------------------------+
                | 10             | Conflicte entre les dades de l'objecte Vector <vector> i la informació actual de l'objecte trama.      |
                +----------------+--------------------------------------------------------------------------------------------------------+


        :param vector: Vector que es vol afegir a la trama.
        :type vector: Vector
        :param protocol: Protocol de referència on apunta l'objecte Vector <vector>.
        :type vector: Protocol
        :return: Codi de retorn (consulteu la taula :numref:`codi-retorn-afegir-dada`).
        :rtype: int

        .. note::
            Si un objecte Frame està buit, l'identificador, l'adreça i el tipus de trama CAN s'assignaran a l'objecte Frame buit a partir del primer objecte de dades afegit a ell.
        
        .. warning::
            Si l'identificador de la trama no coincideix amb les dades que vols assignar, aleshores aquestes dades s'eliminen (equivalent a no afegir-les a la trama). El mateix s'aplica a l'adreça de l'objecte de dades que vols afegir a la trama i al contingut de la trama (és a dir, si aquesta trama conté funcions o variables).

            Cal tenir en compte que les variables o funcions repetides dins d'un objecte Frame també seran rebutjades per a la inserció. Les comprovacions en aquest nivell es realitzen a través de la màscara assignada a les dades de la classe Data.
        """
        # Comprovem que els arguments corresponguin amb el tipus correcte.
        if not isinstance(vector, Vector):
            return 1
        if not isinstance(protocol, Protocol):
            return 2
        
        # Cerquem al protocol l'existencia de la informació que conté el vector.
        info = protocol.search(vector)
        if isinstance(info, bool):
            return 3
        
        # Mirem si la trama és buida. Configurem el tipus de trama.
        if len(self._datalist) == 0 and self._is_function != True:
            if vector.datatype in ["T", "R"]:
                self._is_function = False
                self._is_response = True if vector.datatype == "R" else False
                self._can_id = info["msg_id"]
                d = Variable(
                    ids = vector.ids,
                    name = info["name"],
                    mask = info["mask"],
                    value = vector.value,
                    is_signed = True if info["is_signed"] == 1 else False,
                    is_response = self._is_response)
                self._datalist.append(d)
                return 0
            elif vector.datatype == "F":
                self._can_id = info["msg_id"]
                self._is_function = True
                self._is_response = False
                self.__function = Function(
                    ids=vector.ids,
                    name=info["name"]
                )
                return 0
            else:
                return 4
        # Si hi ha elements a la trama, configurem l'afegida comparant el can_id existent amb el que es vol afegir.
        else:
            if self._is_function:
                if isinstance(self.__function,Function):
                    if vector.datatype == "A":
                        if info["f_id"] == self.__function.ids:
                            a = Argument(
                                ids=vector.ids,
                                name=info["name"],
                                mask=info["mask"],
                                value=vector.value,
                                is_signed=info["is_signed"]
                            )
                            for e in self._datalist:
                                if e.get_mask_value() & a.get_mask_value() != 0:
                                    return 5
                            self._datalist.append(a)
                            return 0
                        return 6
                    return 7
                return 8
            else:
                if (self._can_id == info["msg_id"]) and ((vector.datatype == "T" and not self._is_response) or (vector.datatype == "R" and self._is_response)):
                    v = Variable(
                        ids=vector.ids,
                        name=info["name"],
                        mask=info["mask"],
                        value=vector.value,
                        is_signed=info["is_signed"],
                        is_response=self._is_response
                    )
                    for e in self._datalist:
                        if e.get_mask_value() & v.get_mask_value() != 0:
                            return 9
                    self._datalist.append(v)
                    return 0
                return 10
            


    def get_frame(self):
        """
        Retorna una llista amb el contingut de les dades de la trama CAN.

        :return: Dades de la trama CAN.
        :rtype: list
        """
        n = 0
        for e in self._datalist:
            n = n | e.get_frame_value()
        return list(n.to_bytes(8))
    


    def get_can_frame(self):
        """
        Retorna una llista amb el contingut de les dades de la trama CAN en el format de trama CAN (B0,B1,B2,B3,B4,B5,B6,B7) per ser enviada.

        :return: Dades de la trama CAN.
        :rtype: list
        """
        return list(reversed(self.get_frame()))



    def get_can_id(self):
        """
        Retorna el identificador de la trama CAN del objecte Frame.

        :return: L'identificador de la trama.
        :rtype: int
        """
        return int(self._can_id)



    def __len__(self):
        """
        Retorna la quantitat de variables o funcions hi ha a la trama.

        :return: Nombre de variables o funcions en l'objecte trama.
        :rtype: int
        """
        return len(self._datalist)



    def get_datalist(self):
        """
        Retorna una llista amb totes les variables o funcions que conté la trama associada.

        :return: Llista de variables o funcions que té la trama.
        :rtype: list
        """
        return self._datalist



    def get_is_response(self):
        """
        Retorna si la trama és de resposta o no.
        
        :return: True si la trama és de resposta.
        :rtype: bool
        """
        return self._is_response

    

    def get_is_function(self):
        """
        Retorna si la trama conté una funció o no.

        :return: True si la trama conté una o més funcions.
        :rtype: bool
        """
        return self._is_function
    

    def __repr__(self):
        """
        Representa un objecte del tipus Frame.

        :return: Retorna adientment la representació d'un objecte Frame.
        :rtype: str
        """
        return "Frame Object: ("+str(hex(self.get_can_id()))+") have "+str(self.__len__())+" elements."


if __name__ == "__main__":
    a = Data("HOLA", 184, mask=65283, n_bits=10, value=127)
    b = Data("ALOHA", 184, mask=2**16, n_bits=1, value=1)
    c = Data("ADEU", 587, 65283, 10, value=78, is_function=True)
    f = Frame()
    print(f.add_to_frame(a)) # expected 0
    print(f.add_to_frame(b)) # expected 0
    print(f.add_to_frame(c)) # expected 2
    print(f.get_can_id(),f.get_frame())