from .frame import Frame
from .protocol import Vector, Protocol


class Situation(object):
    """
    La classe "Situation" crea un entorn virtual de situació (VSE - Virtual Situation Environment) que ens permet emmagatzemar objectes "Frame" i identificar aquests frames amb un nom de situació.
    """
    def __init__(self, name, time) -> None:
        """
        Inicialitza una VSE.

        :param name: Nom de la VSE.
        :type name: str
        """
        self.name:str = name
        self.time:int = time
        self._frames:list[Frame] = []



    def add_to_situation(self, vector:Vector, protocol:Protocol) -> int:
        """
        Aquest mètode permet afegir un objecte "Data" a una situació. 

        .. seealso::

            Aquesta funció retorna els mateixos codi d'error que la funció ``add_to_frame()``, ja que aquesta és la que executa la inserció de la dada.

            
        :param f: Objecte Trama que es vol afegir a la situació.
        :type f: Frame
        :param d: Objecte Dada que es vol afegir a la situació.
        :type d: Data
        :return: Codi de retorn (consulteu la taula :numref:`codi-retorn-afegir-dada`)
        :rtype: int
        """
        info = protocol.search(vector)
        if vector.datatype != "F":
            for e in self._frames:
                if info["msg_id"] == e.get_can_id():
                    return e.add_to_frame(vector,protocol)
            f=Frame()
            f.add_to_frame(vector,protocol)
            self._frames+=[f]
        else:
            f=Frame()
            f.add_to_frame(vector,protocol)
            self._frames+=[f]
        return 0



    def get_name(self) -> str:
        """
        Retorna el nom de la VSE.

        :return: Nom de la VSE.
        :rtype: str
        """
        return self.name



    def get_framelist(self) -> list[Frame]:
        """
        Retorna una llista que conté totes les trames de la situació.

        :return: Lista que conté totes les trames de la situació.
        :rtype: list
        """
        return self._frames



    def get_functions_frames(self) -> list[Frame]:
        """
        Retorna una llista que conté totes les trames que contenen funcions.

        :return: Lista que conté trames que contenen funcions. 
        :rtype: list
        """
        functionframes = []
        for frame in self._frames:
            if frame.get_is_function():
                functionframes += [frame]
        return functionframes



    def get_rx_frames(self) -> list[Frame]:
        """
        Retorna una llista amb totes les trames de resposta que conté la situació.

        :return: Llista que conté les trames de resposta de la situació. 
        :rtype: list
        """
        rxframes = []
        for frame in self._frames:
            if frame.get_is_response():
                rxframes += [frame]
        return rxframes



    def get_tx_frames(self) -> list[Frame]:
        """
        Retorna una llista amb totes les trames que contenen variables per a ser tramesses.

        :return: Llista que conté totes les trames on hi ha variables per a ser enviades.
        :rtype: list
        """
        txframes = []
        for frame in self._frames:
            if not frame.get_is_response():
                if not frame.get_is_function():
                    txframes += [frame]
        return txframes



if __name__ == "__main__":
    pass
    # s = Situation("ExampleA")
    # a = Data("HOLA", 184, mask=65283, n_bits=10, value=127)
    # b = Data("ALOHA", 184, mask=2**16, n_bits=1, value=1)
    # c = Data("ADEU", 587, 65283, 10, value=78, is_function=True)
    # f = Frame()
    # g = Frame()
    # print(f.add_to_frame(a))
    # print(f.add_to_frame(b))
    # print(g.add_to_frame(c))
    # print(s.add_to_situation(a))
    # print(s.add_to_situation(b))
    # print(s.add_to_situation(b))
    # print(s._frames[0])
    # print(s._frames[0].get_datalist())