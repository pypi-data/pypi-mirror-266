class State(object):
    """
    Representa la classe Estat de Línia. Permet crear diferents estats en funció de la línia del document específica. D'aquesta manera, es permet l'abstracció de la màquina d'estats durant la sintaxi d'una línia.
    """

    def __init__(self, id:int, required:bool=True, strict:bool=True, command:str|None=None, allow_reserved_words=False, error_msg:str="Undefined error."):
        """
        Crea una instància de la classe State.
        """
        self._id:int = id
        self._required = required
        self._origin:bool = (command == None and strict == True and required==True)
        self._strict:bool = strict
        self._command:str|None = command
        self._next:list[State] = []
        self._error = False
        self._error_command = None
        self._error_msg = error_msg
        self._use_reserved_word = False
        self._reserved_words=["create","enviroment","situation","var", "fn", "end", "import", "protocol","for","do","each","case"]
        if allow_reserved_words:
            self._reserved_words=[]


    def set_next(self,child) -> bool:
        """
        Afegeix un fill sota aquest estat.
        """
        if isinstance(child,State):
            if self._id != child._id:
                self._next.append(child)
                return True
            else:
                return False
        else:
            return False


    def is_next(self, command:str|None) -> bool:
        """
        Retorna True si la comanda <command> existeix en qualsevol dels estats fills de l'estat actual.
        """
        if command is not None:
            for state in self._next:
                if not state._required:
                    if not state._strict and command != state._command and command not in self._reserved_words:
                        return True
                    elif not state._strict and command != state._command and command in self._reserved_words:
                        self._error = True
                        self._use_reserved_word = True
                        self._error_command = command
                        return False
                    elif state._strict and command == state._command:
                        return True
                
        for state in self._next:
            if state._required:
                if not state._strict and command != state._command and command not in self._reserved_words:
                    return True
                elif not state._strict and command != state._command and command in self._reserved_words:
                    self._error = True
                    self._use_reserved_word = True
                    self._error_command = command
                    return False
                elif state._strict and command == state._command:
                    return True
        self._error = True
        self._error_command = command
        return False
        

    def get_next(self, command:str|None):
        """
        Retorna l'estat següent si la comanda <command> existeix en qualsevol dels estats fills de l'estat actual.
        """
        if command is not None:
            for state in self._next:
                if not state._required:
                    if not state._strict and command != state._command:
                        return state
                    elif state._strict and command == state._command:
                        return state
                
        for state in self._next:
            if state._required:
                if not state._strict and command != state._command:
                    return state
                elif state._strict and command == state._command:
                    return state
        self._error = True
        self._error_command = command
        return None
        

    def get_error(self) -> str:
        """
        Retorna el missatge d'error per a l'estat actual.
        """
        if self._use_reserved_word:
            return "Used a reserved word ''{}'' after ''{}'' statement.".format(str(self._error_command),self._command)
        return self._error_msg.format(str(self._error_command)) if self._error_command is not None else self._error_msg.format("<empty>")
    

    def used_reserved_word(self) -> bool:
        return self._use_reserved_word

    def __str__(self) -> str:
        return str(self._id)
    

    def __repr__(self) -> str:
        return repr(self._id)


    


if __name__ == "__main__":
    root = State(0)
    import_instance = State(1000,command="import",strict=True)
    import_protocol = State(1001,command="protocol")
    import_name_protocol = State(1002,command="<name>", strict=False)
    import_end_instance = State(1003,command="end",required=False)
    comment = State(999990, required=False, command="//")
    comment_msg = State(999991, required=False, strict=False, command="<msg>")
    comment_msg2 = State(999992, required=False, strict=False, command="<msg>")

    root.set_next(import_instance)
    root.set_next(comment)
    import_instance.set_next(import_protocol)
    import_protocol.set_next(import_name_protocol)
    import_protocol.set_next(import_end_instance)
    import_end_instance.set_next(root)
    import_name_protocol.set_next(root)
    
    # Per agregar infinits estats d'espera d'arguments.
    comment_msg.set_next(root)
    comment_msg2.set_next(root)
    comment_msg.set_next(comment_msg2)
    comment_msg2.set_next(comment_msg)
    comment.set_next(comment_msg)
    # ############################################### #

    root.is_next("import")
    import_instance.is_next("protocol")
    import_protocol.is_next("jsakldjklsjld")
    import_protocol.is_next("end")
    import_protocol.is_next("2376237")
    import_name_protocol.is_next(None)
    import_end_instance.is_next(None)
    print("-------------------------------------------------")
    print(id(comment_msg))
    print(id(comment_msg._next[1]._next[1]))
    print(comment._next)
    print(comment_msg._next[1]._next)
    print(comment_msg2._next[1]._next[1]._next[1]._next[1]._next[1]._next[1]._next[1]._next[1]._next)
    root.is_next("//")
    a = comment.get_next("asasa")
    print(a)
    a2 = a.get_next("yayayaya")
    print(a2)
    a = a2.get_next("atatatata")
    print(a)
    a2 = a.get_next("soajalsjlc")
    print(a2)
    print(a2.get_next(None))
    print(a.get_next(None))


    a = root.get_next("import")
    # print(a._id)
    b = import_instance.get_next("protocol")
    # print(b._id)
    c = import_protocol.get_next("jsakldjklsjld")
    # print(c._id)
    d = import_protocol.get_next("end")
    # print(d._id)
    e = import_protocol.get_next("2376237")
    # print(e._id)
    f = import_name_protocol.get_next(None)
    # print(f._id)
    g = import_end_instance.get_next(None)
    # print(g._id)
    g = g.get_next("import")
    # print(g._id)
    g = g.get_next("protocol")
    # print(g._id)
    g = g.get_next("T164E")
    # print(g._id)
    g = g.get_next(None)
    # print(g._id)
    # Causar un error! Cal que retornem l'estat actual o mostrem error? Valorar!!!
    # g = g.get_next("middleware")
    # print(g._id)