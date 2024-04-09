# from multiprocessing.util import ForkAwareThreadLock
# import sys
import logging
import os.path
import sqlite3 as sql
from collections import defaultdict
import json

def db_sql_instructions():
    """
    Retorna l'estructura SQL de la base de dades interna.

    :return: Estructura SQL.
    :rtype: str
    """
    return """PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- Tabla: Protocol
CREATE TABLE IF NOT EXISTS Protocol (
    p_id          INTEGER       NOT NULL
                                PRIMARY KEY AUTOINCREMENT
                                UNIQUE,
    p_name        VARCHAR (16)  NOT NULL
                                UNIQUE,
    p_description VARCHAR (250) 
);


-- Tabla: Function
CREATE TABLE IF NOT EXISTS Function (
    f_id          INTEGER       NOT NULL
                                PRIMARY KEY AUTOINCREMENT
                                UNIQUE,
    f_name        VARCHAR (16)  NOT NULL,
    f_description VARCHAR (250),
    f_msg_id      VARCHAR (8)   NOT NULL,
    p_id          INTEGER       REFERENCES Protocol (p_id) ON DELETE CASCADE
                                                           ON UPDATE CASCADE
                                NOT NULL,
    FOREIGN KEY (
        p_id
    )
    REFERENCES controladors (p_id) ON DELETE CASCADE
);


-- Tabla: Variable
CREATE TABLE IF NOT EXISTS Variable (
    v_id          INTEGER       NOT NULL
                                PRIMARY KEY AUTOINCREMENT
                                UNIQUE,
    v_name        VARCHAR (32)  NOT NULL,
    v_description VARCHAR (250),
    v_direction   INTEGER       NOT NULL,
    v_msg_id      VARCHAR (8)   NOT NULL,
    v_mask        BLOB,
    v_is_signed   INTEGER       NOT NULL,
    v_default     INTEGER       NOT NULL
                                DEFAULT (0),
    v_offset      INTEGER       NOT NULL
                                DEFAULT (0),
    v_mul         INTEGER       NOT NULL
                                DEFAULT (1),
    v_div         INTEGER       NOT NULL
                                DEFAULT (1),
    p_id          INTEGER       NOT NULL
                                REFERENCES Protocol (p_id)  ON DELETE CASCADE
                                                            ON UPDATE CASCADE,
    FOREIGN KEY (
        p_id
    )
    REFERENCES controladors (p_id) 
);


-- Tabla: Argument
CREATE TABLE IF NOT EXISTS Argument (
    a_id          INTEGER       NOT NULL
                                PRIMARY KEY AUTOINCREMENT
                                UNIQUE,
    a_name        VARCHAR (32)  NOT NULL,
    a_description VARCHAR (250),
    a_is_signed   INTEGER       NOT NULL
                                DEFAULT (0),
    a_mask        BLOB,
    a_offset      INTEGER       NOT NULL
                                DEFAULT (0),
    a_mul         INTEGER       NOT NULL
                                DEFAULT (1),
    a_div         INTEGER       NOT NULL
                                DEFAULT (1),
    f_id          INTEGER       NOT NULL
                                REFERENCES Function (f_id)  ON DELETE CASCADE
                                                            ON UPDATE CASCADE,
    FOREIGN KEY (
        f_id
    )
    REFERENCES Function (f_id) 
);

COMMIT TRANSACTION;
PRAGMA foreign_keys = on;"""

class Database(object):
    """
    La classe Database permet establir la connexió a una base de dades de manera senzilla. La ruta de la base de dades s'emmagatzema en aquesta classe, permetent afegir mètodes de manera fàcil. La base de dades és tractada com un objecte, i es tanca i obre cada vegada que es fa una consulta o inserció de dades.\n\r
    Aquesta classe permet una major flexibilitat en com es tracta la informació de les variables, funcions i protocols, permetent accedir a la base de dades només quan sigui necessari.
    """
    def __init__(self, db:str):
        """
        Crea una nova instància de la classe Database.

        :param db: Camí de la base de dades a connectar.
        :type db: str
        
        """
        self.db = db

    def loaded_db(self) -> bool:
        """
        Retorna True si la base de dades s'ha carregat correctament, sinó retorna False.\n\r
        :return: Indica si s'ha carregat correctament.
        :rtype: bool
        """
        return os.path.isfile(self.db)
    
    ############################## PROTOCOL FUNCTIONS ##############################
    def add_protocol(self, p_name:str, p_description:str) -> int:
        """
        Afegeix el protocol <p_name> amb descripció <p_description> a la base de dades.

        :param p_name: Nom del nou protocol.
        :type new_protocol: str
        :param p_description: Descripció del protocol.
        :type description: str
        :return: Codi de retorn.
        :rtype: int
        """
        p_name = p_name.replace(" ","").upper()
        if len(p_name) > 2**6 or len(p_name) < 4:
            return 1
        with sql.connect(self.db) as conn:
            conn.row_factory = sql.Row
            c = conn.cursor()
            c.execute("""SELECT COUNT(*) FROM Protocol WHERE p_name = (?);""", (p_name,))
            if c.fetchone()[0] == 0:
                c.execute("""INSERT INTO Protocol (p_name, p_description) VALUES (?, ?)""", (p_name, p_description))
                conn.commit()
                return 0
            else:
                return 2

    def modify_protocol(self, p_id:int, p_name:str, p_description:str) -> int:
        """
        Modifica el nom i descripció del protocol <current_id>.

        :param p_id: L'identificador del protocol associat amb la variable.
        :type p_id: int
        :param p_name: Nom del nou protocol.
        :type p_name: str
        :param p_description: Descripció del protocol.
        :type p_description: str
        :return: Retorna 0 si s'ha realitzat la modificació, 1 o 2 si hi ha hagut algun errors.
        :rtype: int
        """
        p_name = p_name.replace(" ","").upper()
        if len(p_name) > 2**6 or len(p_name) < 4:
            return 1
        with sql.connect(self.db) as conn:
            conn.row_factory = sql.Row
            c = conn.cursor()
            #Comprova que no hi hagui cap protocol amb diferent ID i que ja tingui el nom que volem actualitzar
            c.execute("""SELECT COUNT(*) FROM Protocol WHERE p_name = (?) AND p_id <> (?);""", (p_name, p_id))
            if c.fetchone()[0] == 0:
                c.execute("""UPDATE Protocol SET p_name = (?), p_description = (?) WHERE p_id = (?);""", (p_name, p_description, p_id))
                conn.commit()
                return 0
            else:
                return 2

    def delete_protocol(self,p_id:int) -> int|Exception:
        """
        Elimina un protocol de la base de dades.

        .. warning::

            Aquesta funció elimina també totes les variables i funcions de la base de dades que estiguin associades al protocol especificat.

        :param p_id: L'identificador del protocol (o protocol).
        :type p_id: int
        :return: Retorna 0 si s'ha borrat tot el protocol, variables, funcions i arguments d'aquest o una Excepcio altrament.
        :rtype: int|Exception
        """
        try:
            functions = self.get_all_function_id_from_protocol(p_id)
            for func in functions:
                self.delete_function(func)
            
            variables = self.get_all_variable_id_from_protocol(p_id)
            for variable in variables:
                self.delete_variable(variable)
            with sql.connect(self.db) as conn:
                cursor = conn.cursor()
                cursor.execute("""DELETE FROM Protocol WHERE p_id=?;""", (p_id,))
                conn.commit()
                return 0
        except sql.Error as e:
            logging.error(f"Error eliminant el protocol: {e}")
            raise e

    def update_protocol_name(self, p_id:int, p_name:str) -> int:
        """
        Modifica el nom del protocol <p_name>.

        :param p_id: L'identificador del protocol associat amb la variable.
        :type p_id: int
        :param p_name: Nom del protocol.
        :type p_name: str
        :return: Retorna 0 si s'ha actualitzat correctament, 1 o 2 altrament.
        :rtype: int
        """
        p_name = p_name.replace(" ","").upper()
        if len(p_name) > 2**6 or len(p_name) < 4:
            return 1
        with sql.connect(self.db) as conn:
            conn.row_factory = sql.Row
            c = conn.cursor()
            #Comprova que no hi hagui cap protocol amb diferent ID i que ja tingui el nom que volem actualitzar
            c.execute("""SELECT COUNT(*) FROM Protocol WHERE p_name = (?) AND p_id <> (?);""", (p_name, p_id))
            if c.fetchone()[0] == 0:
                c.execute("""UPDATE Protocol SET p_name = (?) WHERE p_id = (?);""", (p_name, p_id))
                conn.commit()
                return 0
            else:
                return 2
    
    def update_protocol_description(self, p_id:int, p_description:str) -> int|Exception:
        """
        Modifica la descripció del protocol <p_description>.

        :param p_id: L'identificador del protocol.
        :type p_id: int
        :param p_description: Descripció del protocol.
        :type p_description: str
        :return: 0 si s'ha eliminat correctament, Exception altrament.
        :rtype: int|Exception
        """
        try:
            with sql.connect(self.db) as conn:
                conn.row_factory = sql.Row
                c = conn.cursor()
                c.execute("""UPDATE Protocol SET p_description = (?) WHERE p_id = (?);""", (p_description, p_id))
                conn.commit()
                return 0
                    
        except sql.Error as e:
            logging.error(f"Error actualitzant la descripció el protocol: {e}")
            raise e

    def get_variables_from_protocol(self, p_id:int) -> tuple|None:
        """
        Cerca a la base de dades totes les variables assignades a un protocol <p_id>.

        :param p_id: Identificador del protocol.
        :type p_id: int
        :return: Totes les variables disponibles del protocol <p_id>.
        :rtype: tuple (o None)
        """
        if self.loaded_db():
            try:
                conn = sql.connect(self.db)
                cursor = conn.cursor()
                cursor.execute('''SELECT v_name FROM Variable WHERE p_id = (?)''',(p_id,))
                return tuple(e[0] for e in cursor.fetchall())
            finally:
                conn.close()
        else:
            return None

    def get_functions_from_protocol(self, p_id:int) -> tuple|None:
        """
        Cerca a la base de dades totes les funcions assignades a un protocol <p_id>.

        :param p_id: Identificador del protocol.
        :type p_id: int
        :return: Totes les funcions disponibles del protocol <p_id>.
        :rtype: tuple (o None)
        """
        if self.loaded_db():
            try:
                conn = sql.connect(self.db)
                cursor = conn.cursor()
                cursor.execute('''SELECT f_name FROM Function WHERE p_id = (?)''',(p_id,))
                return tuple(e[0] for e in cursor.fetchall())
            finally:
                conn.close()
        else:
            return None
        
    def get_protocol_id(self, p_name:str) -> int|None:
        """
        Cerca a la base de dades el protocol id amb el nom especificat <p_name>. Retorna None si no existeix.

        :param p_name: Nom del protocol.
        :type p_name: str
        :return: L'identificdor del protocol.
        :rtype: int (or None)
        """
        try:
            conn = sql.connect(self.db)
            cursor = conn.cursor()
            cursor.execute('''SELECT p_id FROM Protocol WHERE p_name = (?)''',(p_name,))
            return cursor.fetchone()[0]
        except:
            return None
        finally:
            conn.close()

    def get_protocol_name(self, p_id:int) -> str|None:
        """
        Cerca a la base de dades el nom del protocol amb l'identificador <p_id> especificat.

        :param p_id: L'identificador del protocol.
        :type p_id: int
        :return: El nom del protocol.
        :rtype: str (or None)
        """
        try:
            conn = sql.connect(self.db)
            cursor = conn.cursor()
            cursor.execute('''SELECT p_name FROM Protocol WHERE p_id = (?)''',(p_id,))
            return cursor.fetchone()[0]
        except:
            return None
        finally:
            conn.close()

    def get_protocol_description(self, p_id:int) -> str|None:
        """
        Cerca a la base de dades la descripció del protocol amb l'identificador <p_id> especificat.

        :param p_id: L'identificador del protocol.
        :type p_id: int
        :return: La descripció del protocol.
        :rtype: str (or None)
        """
        try:
            conn = sql.connect(self.db)
            cursor = conn.cursor()
            cursor.execute('''SELECT p_description FROM Protocol WHERE p_id = (?)''',(p_id,))
            return cursor.fetchone()[0]
        except:
            return None
        finally:
            conn.close()
    
    def exist_any_protocol(self) -> bool:
        """
        Retorna si hi ha protocols a la base de dades.

        :return: Retorna True si hi ha protocols a la base de dades, False si no n'hi ha.
        :rtype: bool
        :raises sqlite3.Error: Si es produeix un error amb la base de dades.
        """
        try:
            with sql.connect(self.db) as conn:
                cursor = conn.cursor()
                # Executa la consulta SQL per comptar el nombre de protocols a la base de dades
                cursor.execute('SELECT COUNT(*) FROM Protocol')
                # Retorna True si el nombre de protocols és diferent de 0
                return cursor.fetchone()[0] != 0
        except sql.Error as e:
            print(f'No existeix cap protocol a la BD: {e}')
            return False
    
    def get_info_from_protocol(self, p_id:int) -> dict | bool:
        """
        Obté tota la informació del protocol <p_id> i la retorna ordenada en un parell clau-valor.

        :param p_id: L'identificador del protocol associat amb la variable.
        :type p_id: int
        :return: Diccionari que conté tota la informació del protocol, False sino existeix.
        :rtype: dict | False
        """
        with sql.connect(self.db) as conn:
            conn.row_factory = sql.Row
            c = conn.cursor()
            c.execute("""SELECT p_id, p_name, p_description FROM Protocol WHERE p_id = (?)""", (p_id,))
            existeix = c.fetchone()
            if existeix is not None:
                protocol_info = {}
                protocol_info["protocol_id"] = int(existeix[0])
                protocol_info["protocol_name"] = existeix[1]
                protocol_info["protocol_description"] = existeix[2]
                return protocol_info
            else:
                return False

    def get_all_protocols_names(self) -> list[str] | bool:
        """
        Retorna els noms de tots els protocols.

        :return: Els noms de tots els protocols.
        :rtype: list[str] or bool
        :raises: sqlite3.Error si hi ha algun error amb la connexió a la base de dades.
        """
        try:
            with sql.connect(self.db) as conn:
                conn.row_factory = lambda cursor, row: row[0]
                cursor = conn.cursor()
                cursor.execute('''SELECT p_name FROM Protocol''')
                return [name for name in cursor.fetchall() if isinstance(name, str)]
        except sql.Error as e:
            logging.error(f"Error en obtenir els noms dels protocols. {e}")
            return False

    def get_specific_p_id_from_v_id(self, v_id:int) -> int|Exception:
        """
        Retorna l'identificador de protocol associat a la variable amb identificador <v_id>.

        :param v_id: ID de la variable.
        :type v_id: int
        :return: Identificador del protocol associat. Exception si hi ha hagut algun error en l'execució de la consulta
        :rtype: int (o Exception)
        """
        try:
            with sql.connect(self.db) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT p_id FROM Variable WHERE v_id = ?', (v_id,))
                result = cursor.fetchone()
                if result is not None: 
                    return result[0]
        except Exception as e:
            raise Exception(f"No s'ha pogut obtenir protocol ID de la variable amb ID {v_id}. Error: {e}")

    def get_all_used_msg_id_from_protocol(self, p_id:int) -> list[str] | bool:
        """
        Retorna tots els identificadors de missatge utilitzats per un protocol específic <p_id>.

        :param p_id: L'identificador del protocol.
        :type p_id: int

        :return: Una llista amb tots els identificadors de missatge d'un protocol específic si la consulta és correcta, False si hi ha un error.
        :rtype: list[str] or bool
        """
        try:
            with sql.connect(self.db) as conn:
                conn.row_factory = lambda cursor, row: row[0]
                cursor = conn.cursor()
                sql_query = """SELECT v_msg_id AS msg_id
                            FROM Variable
                            WHERE p_id = ? 

                            UNION ALL

                            SELECT f_msg_id AS msg_id
                            FROM Function
                            WHERE p_id = ?"""
                cursor.execute(sql_query, (p_id,p_id))
                return list(set(cursor.fetchall()))
        except Exception as e:
            logging.error(f'Error getting used msg_ids from protocol: {e}')
            return False

    def get_all_used_msg_id_from_protocol_except_f_id(self, p_id:int, f_id:int) -> list[str] | bool:
        """
        Retorna tots els identificadors de missatge utilitzats per un protocol específic <p_id>, excepte el de l'identificador de la funció <f_id>.

        :param p_id: L'identificador del protocol.
        :type p_id: int
        :param f_id: L'identificador de la funció a excloure.
        :type f_id: int

        :return: Una llista amb tots els identificadors de missatge d'un protocol específic si la consulta és correcta, False si hi ha un error.
        :rtype: list[str] or bool
        """
        try:
            with sql.connect(self.db) as conn:
                conn.row_factory = lambda cursor, row: row[0]
                cursor = conn.cursor()
                sql_query = """SELECT v_msg_id AS msg_id
                            FROM Variable
                            WHERE p_id = ? 

                            UNION ALL

                            SELECT f_msg_id AS msg_id
                            FROM Function
                            WHERE p_id = ?"""
                v = cursor.execute(sql_query, (p_id,p_id))
                data = v.fetchall()
                save = list(set(data))
                save.remove(self.get_function_canid(f_id))
                return save
        except Exception as e:
            logging.error(f'Error getting used msg_ids from protocol except f_id {f_id}: {e}')
            return False    
                           
    ############################## VARIABLE FUNCTIONS ##############################
    def add_variable(self, v_name:str, v_description:str, v_direction:int, v_msg_id:str, v_mask:bytes, v_is_signed:bool, v_default:int, v_offset:int, v_mul:int, v_div:int, p_id:int) -> int|Exception:
        """
        Agrega una variable a la base de dades.

        :param v_name: El nom de la variable.
        :type v_name: str
        :param v_description: La descripció de la variable.
        :type v_description: str
        :param v_direction: El tipus de dades de la variable: (0) com a solicitud, (1) com a resposta.
        :type v_direction: int
        :param v_msg_id: L'identificador del missatge CAN associat amb la variable.
        :type v_msg_id: int
        :param v_mask: La màscara que s'utilitza per filtrar els bits rellevants de la variable.
        :type v_mask: bytes
        :param v_is_signed: Indica si la variable és de tipus signed (1) o no (0).
        :type v_is_signed: int
        :param v_default: El valor predeterminat de la variable.
        :type v_default: int
        :param v_offset: El valor utilitzat com a offset per a la variable.
        :type v_offset: int
        :param v_mul: El valor utilitzat com a multiplicador per a la variable.
        :type v_mul: int
        :param v_div: El valor utilitzat com a divisor per a la variable.
        :type v_div: int
        :param p_id: L'identificador del protocol associat amb la variable.
        :type p_id: int

        :return: 0 si la variable s'ha afegit correctament a la base de dades, altres valors o Exception altrament.
        :rtype: int | Exception
        """
        #1 Verifica que no hi hagi errors en el nom de la variable.
        var_name = ""
        for e in v_name.upper():
            if e == " ":
                pass
            elif e.isalpha() or e.isnumeric():
                var_name += e
            elif e == "_":
                var_name += e
            else:
                return 1
        if len(var_name) == 0:
            return 1
        
        #2 Try to get default value.
        if v_default == "":
            v_default = 0
        else:
            try:
                v_default = int(v_default)
            except:
                return 2

        #3 Count the bits in mask.
        countbits = bin(int.from_bytes(v_mask))[2:].count("1")
        if countbits == 0:
            return 3
        
        #4 Check if default_value is in range.
        if countbits == 1:
            signed = 0
            if v_default >= 2**countbits or v_default < 0:
                return 4
        else:
            if v_is_signed:
                signed = 1
                if v_default >= 2**(countbits-1) or v_default < -(2**(countbits-1)):
                    return 4
            else:
                signed = 0
                if v_default >= 2**countbits or v_default < 0:
                    return 4

        #5 Check is a valid CAN Message
        try:
            can_message = int(v_msg_id,16)
            if can_message > 0x1FFFFFFF or can_message < 0x00000000:
                return 5
        except:
            return 5

        #6 Comprova que no existeix a la base de dades una variable amb el mateix nom associada al protocol.
        othervariablesnames = self.get_all_variables_names_from_protocol(p_id)
        for n in othervariablesnames:
            if n == var_name:
                return 6
        
        #7 Comprova que no entri en conflicte amb altres màscares a la base de dades.
        othermasks = self.get_all_variables_masks_from_protocol(p_id, can_message, v_direction)
        for m in othermasks:
            if (int.from_bytes(m) & int.from_bytes(v_mask)) != 0:
                return 7

        # ADAPTACIO ALS VALORS PER DEFECTE
        if v_offset == "":
            v_offset = 0
        if v_mul == "":
            v_mul = 1
        if v_div == "":
            v_div = 1
        
        # Comprovacio de valors irreals
        if int(v_mul) < 1 or int(v_div) < 1:
            return 9

        try:
            with sql.connect(self.db) as conn:
                cursor = conn.cursor()
                cursor.execute('INSERT INTO Variable(v_name, v_description, v_direction, v_msg_id, v_mask, v_is_signed, v_default, v_offset, v_mul, v_div, p_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (var_name, v_description, v_direction, can_message, v_mask, v_is_signed, v_default, v_offset, v_mul, v_div, p_id,))
                conn.commit()
                return 0
        except ValueError as error:
            logging.error(f'Error adding variable: {error}')
            raise ValueError('El tipus de dades no és vàlid')
        except Exception as error:
            logging.error(f'Error adding variable: {error}')
            return 8

    def modify_variable(self, v_id:int, v_name:str, v_description:str, v_direction:int, v_msg_id:str, v_mask:bytes, v_is_signed:bool, v_default:str, v_offset:int, v_mul:int, v_div:int, p_id:int) -> int|Exception:
        """
        Modifica una variable <v_id> de la base de dades.

        :param v_id: L'identificador de la variable a modificar.
        :type v_id: int
        :param v_name: El nom de la variable.
        :type v_name: str
        :param v_description: La descripció de la variable.
        :type v_description: str
        :param v_direction: El tipus de dades de la variable: (0) com a solicitud, (1) com a resposta.
        :type v_direction: int
        :param v_msg_id: L'identificador del missatge CAN associat amb la variable.
        :type v_msg_id: int
        :param v_mask: La màscara que s'utilitza per filtrar els bits rellevants de la variable.
        :type v_mask: bytes
        :param v_is_signed: Indica si la variable és de tipus signed (1) o no (0).
        :type v_is_signed: int
        :param v_default: El valor predeterminat de la variable.
        :type v_default: int
        :param v_offset: El valor utilitzat com a offset per a la variable.
        :type v_offset: int
        :param v_mul: El valor utilitzat com a multiplicador per a la variable.
        :type v_mul: int
        :param v_div: El valor utilitzat com a divisor per a la variable.
        :type v_div: int
        :param p_id: L'identificador del protocol associat amb la variable.
        :type p_id: int

        :return: 0 si la variable s'ha afegit correctament a la base de dades, altres valors o Exception altrament.
        :rtype: int | Exception
        """
        #1 Verifica que no hi hagi errors en el nom de la variable.
        var_name = ""
        for e in v_name.upper():
            if e == " ":
                pass
            elif e.isalpha() or e.isnumeric():
                var_name += e
            elif e == "_":
                var_name += e
            else:
                return 1
        if len(var_name) == 0:
            return 1
        
        #2 Try to get default value.
        if v_default == "":
            v_default = 0
        else:
            try:
                v_default = int(v_default)
            except:
                return 2

        #3 Count the bits in mask.
        countbits = bin(int.from_bytes(v_mask))[2:].count("1")
        if countbits == 0:
            return 3
        
        #4 Check if default_value is in range.
        if countbits == 1:
            signed = 0
            if v_default >= 2**countbits or v_default < 0:
                return 4
        else:
            if v_is_signed:
                signed = 1
                if v_default >= 2**(countbits-1) or v_default < -(2**(countbits-1)):
                    return 4
            else:
                signed = 0
                if v_default >= 2**countbits or v_default < 0:
                    return 4

        #5 Check is a valid CAN Message
        try:
            can_message = int(v_msg_id,16)
            if can_message > 0x1FFFFFFF or can_message < 0x00000000:
                return 5
        except:
            return 5

        #6 Comprova que no existeix a la base de dades una variable amb el mateix nom associada al protocol.
        othervariablesnames = self.get_all_variables_names_from_protocol_except_v_id(p_id, v_id)
        for n in othervariablesnames:
            if n == var_name:
                return 6
        
        #7 Comprova que no entri en conflicte amb altres màscares a la base de dades.
        othermasks = self.get_all_variables_masks_from_protocol_except_v_id(p_id, v_id)
        for m in othermasks:
            if (int.from_bytes(m) & int.from_bytes(v_mask)) != 0:
                return 7

        # ADAPTACIO ALS VALORS PER DEFECTE
        if v_offset == "":
            v_offset = 0
        if v_mul == "":
            v_mul = 1
        if v_div == "":
            v_div = 1
        
        # Comprovacio de valors irreals
        if int(v_mul) < 1 or int(v_div) < 1:
            return 9

        try:
            with sql.connect(self.db) as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE Variable SET v_name=?, v_description=?, v_direction=?, v_msg_id=?, v_mask=?, v_is_signed=?, v_default=?, v_offset=?, v_mul=?, v_div=? WHERE v_id=?", (var_name, v_description, v_direction, can_message, v_mask, v_is_signed, v_default, v_offset, v_mul, v_div, v_id,))
                conn.commit()
                return 0
        except ValueError as error:
            logging.error(f'Error modifying variable: {error}')
            raise ValueError('El tipus de dades no és vàlid')
        except Exception as error:
            logging.error(f'Error modifying variable: {error}')
            return 8

    def delete_variable(self,v_id:int) -> int|Exception:
        """
        Elimina una variable de la base de dades.

        :param v_id: L'identificador de la variable.
        :type v_id: int
        :return: 0 si s'ha eliminat correctament, Exception altrament.
        """
        try:
            with sql.connect(self.db) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM Variable WHERE v_id=?", (v_id,))
                conn.commit()
                return 0
        except sql.Error as e:
            logging.error(f"Error eliminant la variable: {e}")
            raise e

    def get_nbits_from_variable(self, v_id:int) -> tuple|None:
        """
        Cerca a la base de dades si la variable <v_id> és complement a dos o no, i el nombre de bits que ocupa la variable <v_id>.

        :param v_id: Identificador de la variable.
        :type v_id: int
        :return: La primera posició de la tupla conté si és complement a dos o no, la segona posició conté el nombre de bits.
        :rtype: tuple (or None)
        """
        if self.loaded_db():
            try:
                conn = sql.connect(self.db)
                cursor = conn.cursor()
                cursor.execute('''SELECT v_is_signed, v_mask FROM Variable WHERE v_id = (?)''',(v_id,))
                t = cursor.fetchone()
                bits = bin(int.from_bytes(t[1]))
                n_bits = sum(1 for e in bits if e == "1")
                return (t[0], n_bits)
            finally:
                conn.close()
        else:
            return None

    def get_variable_mask(self, var_id:int) -> bytes | bool:
        """
        Retorna el valor de la màscara de la variable amb l'identificador <var_id> especificat.
        
        :param var_id: Identificador de la variable.
        :type var_id: int
        :return: El valor de la màscara de la variable en bytes.
        :rtype: bytes (o False)
        """
        try:
            conn = sql.connect(self.db)
            cursor = conn.cursor()
            cursor.execute('''SELECT v_mask FROM Variable WHERE v_id = ?''',(var_id,))
            return cursor.fetchone()[0]
        except Exception as e:
            print(e)
            return False
        finally:
            conn.close()

    def get_variable_name(self, v_id:int) -> str|None:
        """
        Cerca a la base de dades el nom de la variable amb l'identificador <v_id> especificat.

        :param v_id: L'identificador de la variable.
        :type v_id: int
        :return: El nom de la variable.
        :rtype: str (or None)
        """
        try:
            conn = sql.connect(self.db)
            cursor = conn.cursor()
            cursor.execute('''SELECT v_name FROM Variable WHERE v_id = (?)''',(v_id,))
            return cursor.fetchone()[0]
        except:
            return None
        finally:
            conn.close()

    def get_variable_id(self, p_id:int, v_name:str) -> int | bool:
        """
        Retorna la identificació de la variable a partir del nom <v_name> i la identificació del protocol <p_id>.
        
        :param p_id: Identificador del protocol.
        :type p_id: int
        :param v_name: Nom de la variable.
        :type v_name: str
        :return: El identificador de la variable.
        :rtype: int (o None)
        :raises Exception: Si es produeix un error en la consulta SQL.
        """
        try:
            conn = sql.connect(self.db)
            cursor = conn.cursor()
            cursor.execute('''SELECT v_id FROM Variable WHERE v_name = ? AND p_id = ?''',(v_name,p_id))
            return cursor.fetchone()[0]
        except Exception as e:
            logging.error(f'Error getting variable id: {e}')
            return False
        finally:
            conn.close()

    def get_variable_description(self, v_id:int) -> str|Exception:
        """
        Retorna la descripcio de la variable amb identificador <v_id>.

        :param v_id: ID de la variable.
        :type v_id: int
        :return: Descripcio de la variable. Exception altrament
        :rtype: str (o Exception)
        :raises Exception: Si hi ha hagut algun error en l'execució de la consulta.
        """
        try:
            with sql.connect(self.db) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT v_description FROM Variable WHERE v_id = ?', (v_id,))
                result = cursor.fetchone()
                if result is not None: 
                    return result[0]
        except Exception as e:
            raise Exception(f"No s'ha pogut obtenir la descripcio de la variable amb ID {v_id}. Error: {e}")
    
    def get_variable_direction(self, v_id:int) -> str|Exception:
        """
        Retorna la direcció de la variable amb identificador <v_id>.

        :param v_id: ID de la variable.
        :type v_id: int
        :return: Direcció de la variable.
        :rtype: int (o None)
        :raises Exception: Si hi ha hagut algun error en l'execució de la consulta.
        """
        try:
            with sql.connect(self.db) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT v_direction FROM Variable WHERE v_id = ?', (v_id,))
                result = cursor.fetchone()
                if result is not None: 
                    return result[0]
        except Exception as e:
            raise Exception(f"No s'ha pogut obtenir la direcció de la variable amb ID {v_id}. Error: {e}") 
        
    def get_variable_canid(self, v_id:int) -> int|Exception:
        """
        Retorna el missatge CAN ID de la variable amb identificador <v_id>.

        :param v_id: ID de la variable.
        :type v_id: int
        :return: Missatge CAN ID de la variable.
        :rtype: int (o Exception)
        :raises Exception: Si hi ha hagut algun error en l'execució de la consulta.
        """
        try:
            with sql.connect(self.db) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT v_msg_id FROM Variable WHERE v_id = ?', (v_id,))
                result = cursor.fetchone()
                if result is not None: 
                    return result[0]
        except Exception as e:
            raise Exception(f"No s'ha pogut obtenir el missatge CAN ID de la variable amb ID {v_id}. Error: {e}") 

    def get_variable_is_signed(self, v_id:int) -> bool|Exception:
        """
        Retorna si la variable amb identificador <v_id> és signada o no.

        :param v_id: ID de la variable.
        :type v_id: int
        :return: True si la variable és signada.
        :rtype: bool (o Exception)
        :raises Exception: Si hi ha hagut algun error en l'execució de la consulta.
        """
        try:
            with sql.connect(self.db) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT v_is_signed FROM Variable WHERE v_id = ?', (v_id,))
                result = cursor.fetchone()
                if result is not None:
                    return int(result[0]) == 1
        except Exception as e:
            raise Exception(f"No s'ha pogut obtenir el signe de la variable amb ID {v_id}. Error: {e}")

    def get_default_variable_value(self, p_id:int, v_name:str) -> int|None:
        """
        Cerca a la base de dades el valor per defecte amb el nom de variable <v_name> especificat del protocol amb el id <p_id> especificat.

        :param p_id: ID del protocol.
        :type p_id: int
        :param v_name: Nom de la variable.
        :type v_name: str
        :return: Valor per defecte de la variable.
        :rtype: int (or None)
        """
        try:
            with sql.connect(self.db) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT v_default FROM Variable WHERE p_id = (?) AND v_name = (?)',(p_id,v_name,))
                return cursor.fetchone()[0]
        except:
            return None
        finally:
            conn.close()

    def get_variable_offset(self, v_id:int) -> int|Exception:
        """
        Retorna l'offset de la variable amb identificador <v_id>.

        :param v_id: ID de la variable.
        :type v_id: int
        :return: L'offset de la variable.
        :rtype: int (o Exception)
        :raises Exception: Si hi ha hagut algun error en l'execució de la consulta.
        """
        try:
            with sql.connect(self.db) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT v_offset FROM Variable WHERE v_id = ?', (v_id,))
                result = cursor.fetchone()
                if result is not None: 
                    return result[0]
        except Exception as e:
            raise Exception(f"No s'ha pogut obtenir el offset de la variable amb ID {v_id}. Error: {e}")
    
    def get_variable_mul(self, v_id:int) -> int|Exception:
        """
        Retorna el valor multiplicador de la variable amb identificador <v_id>.

        :param v_id: ID de la variable.
        :type v_id: int
        :return: El multiplicador de la variable.
        :rtype: int (o Exception)
        :raises Exception: Si hi ha hagut algun error en l'execució de la consulta.
        """
        try:
            with sql.connect(self.db) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT v_mul FROM Variable WHERE v_id = ?', (v_id,))
                result = cursor.fetchone()
                if result is not None: 
                    return result[0]
        except Exception as e:
            raise Exception(f"No s'ha pogut obtenir el multiplicador de la variable amb ID {v_id}. Error: {e}")
    
    def get_variable_div(self, v_id:int) -> int|Exception:
        """
        Retorna el valor divisor de la variable amb identificador <v_id>.

        :param v_id: ID de la variable.
        :type v_id: int
        :return: El divisor de la variable.
        :rtype: int (o Exception)
        :raises Exception: Si hi ha hagut algun error en l'execució de la consulta.
        """
        try:
            with sql.connect(self.db) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT v_div FROM Variable WHERE v_id = ?', (v_id,))
                result = cursor.fetchone()
                if result is not None: 
                    return result[0]
        except Exception as e:
            raise Exception(f"No s'ha pogut obtenir el divisor de la variable amb ID {v_id}. Error: {e}")

    def update_variable_name(self, p_id:int, v_id:int, v_name:str) -> int:
        """
        Modifica el nom de la variable <v_name>.

        :param p_id: L'identificador del protocol associat amb la variable.
        :type p_id: int
        :param v_name: Nom de la variable.
        :type v_name: str
        :return: 0 si s'ha realitzat una modificació, 2 altrament.
        :rtype: int
        """
        
        with sql.connect(self.db) as conn:
            conn.row_factory = sql.Row
            c = conn.cursor()
            c.execute("""SELECT COUNT(*) FROM Variable WHERE v_name = (?) AND p_id <> (?);""", (v_name, p_id))
            if c.fetchone()[0] == 0:
                c.execute("""UPDATE Variable SET v_name = (?) WHERE v_id AND p_id = (?);""", (v_name, v_id, p_id))
                conn.commit()
                return 0
            else:
                return 2
        
    def update_variable_description(self, v_id:int, v_description:str) -> int|Exception:
        """
        Modifica la descripció de la variable <v_description>.

        :param v_id: L'identificador de la variable.
        :type v_id: int
        :param v_description: Descripció de la variable.
        :type v_description: str
        :return: 0 si s'ha realitzat una modificació, Exception altrament.
        :rtype: int|Exception
        """
        try:
            with sql.connect(self.db) as conn:
                conn.row_factory = sql.Row
                c = conn.cursor()
                c.execute("""UPDATE Variable SET v_description = (?) WHERE v_id = (?);""", (v_description, v_id))
                conn.commit()
                return 0
                
        except sql.Error as e:
            logging.error(f"Error actualitzant la descripcio de la variable: {e}")
            raise e
            
    def update_variable_direction(self, v_id:int, v_direction:int) -> int|Exception:
        """
        Modifica la direcció de la variable <v_direction>.

        :param v_id: L'identificador de la variable.
        :type v_id: int
        :param v_direction: Direcció de la variable.
        :type v_direction: str
        :return: 0 si s'ha realitzat una modificació, Exception altrament.
        :rtype: int|Exception
        """
        try:
            with sql.connect(self.db) as conn:
                conn.row_factory = sql.Row
                c = conn.cursor()
                c.execute("""UPDATE Variable SET v_direction = (?) WHERE v_id = (?);""", (v_direction, v_id))
                conn.commit()
                return 0

        except sql.Error as e:
            logging.error(f"Error actualitzant la direcció de la variable: {e}")
            raise e

    def update_variable_msg_id(self, v_id:int, v_msg_id:str) -> int|Exception:
        """
        Modifica el msg id de la variable <v_msg_id>.

        :param v_id: L'identificador de la variable.
        :type v_id: int
        :param v_msg_id: Msg id de la variable.
        :type v_msg_id: str
        :return: 0 si s'ha realitzat una modificació, Exception altrament.
        :rtype: int|Exception
        """
        try:
            with sql.connect(self.db) as conn:
                conn.row_factory = sql.Row
                c = conn.cursor()
                c.execute("""UPDATE Variable SET v_msg_id = (?) WHERE v_id = (?);""", (int(v_msg_id,16), v_id))
                conn.commit()
                return 0
        except sql.Error as e:
            logging.error(f"Error actualitzant el CAN ID de la variable: {e}")
            raise e

    def update_variable_mask(self, v_id:int, mask) -> bool|Exception:
        """
        Actualitza la màscara d'una variable a la base de dades.

        :param v_id: Identificador de la variable que es vol actualitzar.
        :type v_id: int
        :param mask: Màscara que es vol assignar a la variable, en format enter de 8 bytes.
        :type mask: int
        :return: Retorna True si el canvi s'ha fet correctament. Retorna False o Exception si s'ha produït un error.
        :rtype: bool | Exception
        :raises ValueError: Si l'ID de la variable o la màscara no són vàlids.
        :raises sqlite3.Error: Si es produeix un error amb la base de dades.
        """
        if not isinstance(v_id, int) or v_id <= 0:
            raise ValueError('ID de la variable no vàlid')
        if not isinstance(mask, int) or not (0 <= mask < 2**64):
            raise ValueError('Màscara no vàlida')
        try:
            mask_bytes = mask.to_bytes(8, 'big') # Converteix la màscara a 8 bytes
            with sql.connect(self.db) as conn:
                cursor = conn.cursor()
                # Executa la consulta SQL per actualitzar la màscara de la variable especificada
                cursor.execute('UPDATE  Variable SET v_mask = ? WHERE v_id = ?', (mask_bytes, v_id))
                if cursor.rowcount == 0:
                    return False
                conn.commit()
                return True
        except ValueError as ve:
            print(f'Error: {ve}')
            return False
        except sql.Error as e:
            print(f'Error de la base de dades: {e}')
            return False    

    def update_variable_is_signed(self, v_id:int, v_is_signed:int) -> int|Exception:
        """
        Modifica el signe de la variable <v_is_signed>.

        :param v_id: L'identificador de la variable.
        :type v_id: int
        :param v_is_signed: Signe de la variable.
        :type v_is_signed: str
        :return: 0 si s'ha realitzat una modificació, Exception altrament.
        :rtype: int|Exception
        """
        try:
            with sql.connect(self.db) as conn:
                conn.row_factory = sql.Row
                c = conn.cursor()
                c.execute("""UPDATE Variable SET v_is_signed = (?) WHERE v_id = (?);""", (v_is_signed, v_id))
                conn.commit()
                return 0
        except sql.Error as e:
            logging.error(f"Error actualitzant el signe de la variable: {e}")
            raise e
    
    def update_variable_default_value(self, v_id:int, v_default:int) -> int|Exception:
        """
        Modifica el valor per defecte de la variable <v_default>.

        :param p_v_idid: L'identificador de la variable.
        :type v_id: int
        :param v_default: Default value de la variable.
        :type v_default: str
        :return: 0 si s'ha realitzat una modificació, Exception altrament.
        :rtype: int|Exception
        """
        try:
            with sql.connect(self.db) as conn:
                conn.row_factory = sql.Row
                c = conn.cursor()
                c.execute("""UPDATE Variable SET v_default = (?) WHERE v_id = (?);""", (v_default, v_id))
                conn.commit()
                return 0
        except sql.Error as e:
            logging.error(f"Error actualitzant el default value la variable: {e}")
            raise e

    def update_variable_offset(self, v_id:int, v_offset:int) -> int|Exception:
        """
        Modifica el offset de la variable <v_offset>.

        :param v_id: L'identificador de la variable.
        :type v_id: int
        :param v_offset: Offset de la variable.
        :type v_offset: str
        :return: int si s'ha realitzat una modificació, Exception altrament.
        :rtype: int|Exception
        """
        try: 
            with sql.connect(self.db) as conn:
                conn.row_factory = sql.Row
                c = conn.cursor()
                c.execute("""UPDATE Variable SET v_offset = (?) WHERE v_id = (?);""", (v_offset, v_id))
                conn.commit()
                return 0
        except sql.Error as e:
            logging.error(f"Error actualitzant el offset de la variable: {e}")
            raise e
        
    def update_variable_mul(self, v_id:int, v_mul:int) -> int|Exception:
        """
        Modifica el multiplicador de la variable <v_mul>.

        :param v_id: L'identificador de la variable.
        :type v_id: int
        :param v_mul: Multiplicador de la variable.
        :type v_mul: str
        :return: 0 si s'ha realitzat una modificació, Exception altrament.
        :rtype: int|Exception
        """
        try:
            with sql.connect(self.db) as conn:
                conn.row_factory = sql.Row
                c = conn.cursor()
                c.execute("""UPDATE Variable SET v_mul = (?) WHERE v_id = (?);""", (v_mul, v_id))
                conn.commit()
                return 0
        except sql.Error as e:
            logging.error(f"Error actualitzant el multiplicador de la variable: {e}")
            raise e

    def update_variable_div(self, v_id:int, v_div:int) -> int|Exception:
        """
        Modifica el divisor de la variable <v_div>.

        :param v_id: L'identificador de la variable.
        :type v_id: int
        :param v_div: divisor de la variable.
        :type v_div: str
        :return: 0 si s'ha realitzat una modificació, Exception altrament.
        :rtype: int|Exception
        """
        try:
            with sql.connect(self.db) as conn:
                conn.row_factory = sql.Row
                c = conn.cursor()
                c.execute("""UPDATE Variable SET v_div = (?) WHERE v_id = (?);""", (v_div, v_id))
                conn.commit()
                return 0
        except sql.Error as e:
            logging.error(f"Error actualitzant el divisor de la variable: {e}")
            raise e
        
    def get_all_variables_masks_from_protocol(self, p_id:int, v_msg_id:int, direction:int) -> list[bytes] | bool:
        """
        Retorna les màscares de totes les variables de direcció <direction> d'un protocol <p_id> a partir de l'identificador de missatge CAN <v_msg_id> i la direcció <direction>.

        :param p_id: L'identificador del protocol per obtenir les màscares de totes les variables.
        :type p_id: int
        :param v_msg_id: L'identificador de la trama CAN.
        :type v_msg_id: int
        :param direction: Direcció de la màscara.
        :type direction: int
        :return: Les màscares de totes les variables del protocol.
        :rtype: list[bytes] or False
        :raises: False si hi ha algun error amb la connexió a la base de dades.
        """
        try:
            with sql.connect(self.db) as conn:
                conn.row_factory = lambda cursor, row: row[0]
                cursor = conn.cursor()
                cursor.execute('''SELECT v_mask FROM Variable WHERE p_id=(?) and v_direction=(?) and v_msg_id=(?)''',(p_id,direction,v_msg_id))
                return cursor.fetchall()
        except Exception as e:
            logging.error(f"Error en obtenir les màscares de les variables del protocol. {e}")
            return False
        finally:
            conn.close()
  
    def get_all_variables_masks_from_protocol_except_v_id(self, p_id:int, v_id:int) -> list[bytes] | bool:
        """
        Retorna les màscares de totes les variables de direcció <direction> d'un protocol <p_id> a partir de l'ID del protocol.

        :param p_id: L'identificador del protocol per obtenir les màscares de totes les variables.
        :type p_id: int
        :param v_id: L'identificador de la variable que es vol excloure.
        :type v_id: int
        :return: Les màscares de totes les variables del protocol.
        :rtype: list[bytes] or False
        :raises: Exception si hi ha algun error amb la connexió a la base de dades.
        """
        v_msg_id = self.get_variable_canid(v_id)
        direction = self.get_variable_direction(v_id)
        try:
            with sql.connect(self.db) as conn:
                conn.row_factory = lambda cursor, row: row[0]
                cursor = conn.cursor()
                cursor.execute('''SELECT v_mask FROM Variable WHERE p_id=(?) and v_direction=(?) and v_msg_id=(?) and v_id != (?)''',(p_id,direction,v_msg_id,v_id))
                return cursor.fetchall()
        except Exception as e:
            logging.error(f"Error en obtenir les màscares de les variables del protocol excepte {v_id}. {e}")
            return False
        finally:
            conn.close()

    def get_all_variables_masks_from_protocol_except_v_id_2(self, p_id:int, v_id:int, v_msg_id:int, direction:int) -> list[bytes] | bool:
        """
        Retorna les màscares de totes les variables de direcció <direction> d'un protocol <p_id> a partir de l'ID del protocol.

        :param p_id: L'identificador del protocol per obtenir les màscares de totes les variables.
        :type p_id: int
        :param v_id: L'identificador de la variable que es vol excloure.
        :type v_id: int
        :return: Les màscares de totes les variables del protocol.
        :rtype: list[bytes] or False
        :raises: Exception si hi ha algun error amb la connexió a la base de dades.
        """
        #v_msg_id = self.get_variable_canid(v_id)
        #direction = self.get_variable_direction(v_id)
        try:
            with sql.connect(self.db) as conn:
                conn.row_factory = lambda cursor, row: row[0]
                cursor = conn.cursor()
                cursor.execute('''SELECT v_mask FROM Variable WHERE p_id=(?) and v_direction=(?) and v_msg_id=(?) and v_id != (?)''',(p_id,direction,v_msg_id,v_id))
                return cursor.fetchall()
        except Exception as e:
            logging.error(f"Error en obtenir les màscares de les variables del protocol excepte {v_id}. {e}")
            return False
        finally:
            conn.close()    

    def get_all_variables_names_from_protocol_except_v_id(self, p_id:int, v_id:int) -> list[str] | bool:
        """
        Retorna el nom de totes les variables associades a un protocol específic excepte la variable <v_id> especificada.

        :param p_id: L'identificador del protocol associat amb les variables.
        :type p_id: int
        :param v_id: L'identificador de la variable a excluir de la cerca.
        :type v_id: int

        :return: Una llista amb els noms de totes les variables associades a un protocol específic si la consulta és correcta, False si hi ha un error.
        :rtype: list[str] or False
        """
        try:
            with sql.connect(self.db) as conn:
                conn.row_factory = lambda cursor, row: row[0]
                cursor = conn.cursor()
                cursor.execute('SELECT v_name FROM Variable WHERE p_id=(?) and v_id!=(?)', (p_id,v_id))
                return cursor.fetchall()
        except Exception as e:
            logging.error(f'Error getting variable names from protocol excepte {v_id}: {e}')
            return False
    
    def get_all_variables_names_from_protocol(self, p_id:int) -> list[str] | bool:
        """
        Retorna el nom de totes les variables associades a un protocol específic.

        :param p_id: L'identificador del protocol associat amb les variables.
        :type p_id: int

        :return: Una llista amb els noms de totes les variables associades a un protocol específic si la consulta és correcta, False si hi ha un error.
        :rtype: list[str] or False
        """
        try:
            with sql.connect(self.db) as conn:
                conn.row_factory = lambda cursor, row: row[0]
                cursor = conn.cursor()
                cursor.execute('SELECT v_name FROM Variable WHERE p_id=(?)', (p_id,))
                return cursor.fetchall()
        except Exception as e:
            logging.error(f'Error getting variable names from protocol: {e}')
            return False

    def get_all_from_variable(self, v_id:int) -> tuple|Exception:
        """
        Recupera totes les dades associades a un identificador de variable de la taula 'variables'.

        :param v_id: L'identificador de la variable per recuperar les dades associades.
        :type v_id: int
        :returns: Una tupla amb totes les dades associades a l'identificador de variable proporcionat, o Exception si s'ha produït un error.
        :rtype: tuple or Exception
        :raises sqlite3.Error: Si es produeix un error en la connexió o en l'execució de la consulta.
        """
        try:
            with sql.connect(self.db) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM Variable WHERE v_id = ?", (v_id,))
                return cursor.fetchone()
        except sql.Error as e:
            logging.error(f"Error obtenint informació de la variable: {e}")
            raise e

    def get_all_variables(self) -> dict|Exception:
        """
        Recupera totes les variables i les agrupa amb tota la seva informació per nom de protocol en un diccionari.

        :returns: Un diccionari amb totes les variables agrupades per identificador de protocol, o Exception si s'ha produït un error.
        :rtype: dict or Exception
        :raises sqlite3.Error: Si es produeix un error en la connexió o en l'execució de la consulta.
        """
        try:
            with sql.connect(self.db) as conn:
                structure = defaultdict(list)
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM Variable")
                for item in cursor.fetchall():
                    structure[self.get_protocol_name(item[11])].append(item) 
                return dict(structure)
        except sql.Error as e:
            logging.error(f"Error obtenint totes les variables: {e}")
            raise e                    

    def get_info_from_variable(self, v_id:int) -> dict|Exception:
        """
        Recupera totes les dades associades a un identificador de variable de la taula 'variables'.

        :param v_id: L'identificador de la variable per recuperar les dades associades.
        :type v_id: int
        :returns: Un diccionari amb totes les dades associades a l'identificador de variable proporcionat, o Exception si s'ha produït un error.
        :rtype: dict or Exception
        :raises sqlite3.Error: Si es produeix un error en la connexió o en l'execució de la consulta.
        """
        try:
            with sql.connect(self.db) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM Variable WHERE v_id = ?", (v_id,))
                records = cursor.fetchone()
                variable_info = {}
                variable_info["variable_id"] = records[0]
                variable_info["variable_name"] = records[1]
                variable_info["variable_description"] = records[2]
                variable_info["variable_direction"] = records[3]
                variable_info["variable_msg_id"] = records[4]
                mask = bin(int.from_bytes(records[5]))[2:]
                variable_info["variable_mask"] = mask.zfill(64)
                variable_info["variable_is_signed"] = records[6]
                variable_info["variable_default"] = records[7]
                variable_info["variable_offset"] = records[8]
                variable_info["variable_mul"] = records[9]
                variable_info["variable_div"] = records[10]
                variable_info["variable_contained_in_protocol"] = records[11]
                return variable_info
        except sql.Error as e:
            logging.error(f"Error obtenint informació de la variable: {e}")
            raise e

    def get_all_variable_id_from_protocol(self, p_id:int) -> list[str] | bool:
        """
        Retorna totes les variables ids associades a un protocol específic.

        :param p_id: L'identificador del protocol associat amb les variables.
        :type p_id: int

        :return: Una llista amb totes les variables ids associades a un protocol específic si la consulta és correcta, False si hi ha un error.
        :rtype: list[str] or False
        """
        try:
            with sql.connect(self.db) as conn:
                conn.row_factory = lambda cursor, row: row[0]
                cursor = conn.cursor()
                cursor.execute('SELECT v_id FROM Variable WHERE p_id=(?)', (p_id,))
                return cursor.fetchall()
        except Exception as e:
            logging.error(f'Error getting variable ids from protocol: {e}')
            return False 
                    
    ############################## FUNCTION FUNCTIONS ##############################
    def add_function(self, f_name:str, f_description:str, f_msg_id:str, p_id:int ) -> int:
        """
        Agrega una funció a la base de dades.

        :param f_name: El nom de la function.
        :type f_name: str
        :param p_id: L'identificador del protocol associat amb la function.
        :type p_id: int
        :param f_description: La descripció de la function.
        :type f_description: str
        :param f_msg_id: L'identificador del missatge CAN associat amb la function.
        :type f_msg_id: int

        :return: 0 si la function s'ha afegit correctament a la base de dades, altres si ha ocurregut un error.
        :rtype: int
        """
        #1 Verifica que no hi hagi errors en el nom de la function.
        fun_name = ""
        for e in f_name.upper():
            if e == " ":
                pass
            elif e.isalpha() or e.isnumeric():
                fun_name += e
            elif e == "_":
                fun_name += e
            else:
                return 1
        if len(fun_name) == 0:
            return 1
        
        #2 Check is a valid CAN Message
        try:
            can_message = int(f_msg_id,16)
            if can_message > 0x1FFFFFFF or can_message < 0x00000000:
                return 2
        except:
            return 2

        #3 Comprova que no existeix a la base de dades una function amb el mateix nom associada al protocol.
        otherfunctionsnames = self.get_functions_from_protocol(p_id)
        for n in otherfunctionsnames:
            if n == fun_name:
                return 3
        
        #4 Comprova que no entri en conflicte amb altres identificadors de missatge del protocol a la base de dades.
        othermsgids = self.get_all_used_msg_id_from_protocol(p_id)
        for m in othermsgids:
            if int(m) == can_message:
                return 4

        try:
            with sql.connect(self.db) as conn:
                cursor = conn.cursor()
                cursor.execute('INSERT INTO Function(f_name, f_description, f_msg_id, p_id) VALUES (?, ?, ?, ?)', (fun_name, f_description, can_message, p_id))
                conn.commit()
                return 0
        except Exception as error:
            logging.error(f'Error adding function: {error}')
            return 5

    def modify_function(self, function_id:int, f_name:str, f_description:str, f_msg_id:str, p_id:int ) -> int:
        """
        Modifica una funció <f_id> de la base de dades.

        :param function_id: L'identificador de la funció a modificar.
        :type function_id: int
        :param f_name: El nom de la function.
        :type f_name: str
        :param p_id: L'identificador del protocol associat amb la function.
        :type p_id: int
        :param f_description: La descripció de la function.
        :type f_description: str
        :param f_msg_id: L'identificador del missatge CAN associat amb la function.
        :type f_msg_id: int

        :return: 0 si la function s'ha afegit correctament a la base de dades, altres si ha ocorregut un error.
        :rtype: int
        """
        #1 Verifica que no hi hagi errors en el nom de la function.
        var_name = ""
        for e in f_name.upper():
            if e == " ":
                pass
            elif e.isalpha() or e.isnumeric():
                var_name += e
            elif e == "_":
                var_name += e
            else:
                return 1
        if len(var_name) == 0:
            return 1

        #2 Check is a valid CAN Message
        try:
            can_message = int(f_msg_id,16)
            if can_message > 0x1FFFFFFF or can_message < 0x00000000:
                return 2
        except:
            return 2

        #3 Comprova que no existeix a la base de dades una function amb el mateix nom associada al protocol.
        otherfunctionsnames = self.get_all_functions_names_from_protocol_except_f_id(p_id, function_id)
        for n in otherfunctionsnames:
            if n == var_name:
                return 3
        
        #4 Comprova que no entri en conflicte amb altres identificadors a la base de dades.
        othermsg = self.get_all_used_msg_id_from_protocol_except_f_id(p_id, function_id)
        for m in othermsg:
            if int(m) == can_message:
                return 4

        try:
            with sql.connect(self.db) as conn: 
                cursor = conn.cursor()
                cursor.execute("UPDATE Function SET f_name=?, f_description=?, f_msg_id=? WHERE f_id=?", (var_name, f_description, can_message, function_id))
                conn.commit()
                return 0
        except Exception as error:
            logging.error(f'Error editting function: {error}')
            return 5
                         
    def delete_function(self,f_id:int) -> int|Exception:
        """
        Elimina una function de la base de dades.

        :param f_id: L'identificador de la function.
        :type f_id: int
        :return: 0 si s'ha eliminat correctament, Exception altrament.
        """
        try:
            arguments = self.get_all_argument_id_from_function(f_id)

            with sql.connect(self.db) as conn:
                for arg in arguments:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM Argument WHERE a_id=?", (arg,))
                cursor = conn.cursor()
                cursor.execute("DELETE FROM Function WHERE f_id=?", (f_id,))
                conn.commit()
                return 0
        except sql.Error as e:
            logging.error(f"Error eliminant la funcio: {e}")
            raise e

    def get_f_name_from_function(self, f_id:int) -> str|None:
        """
        Cerca a la base de dades el nom de la funció amb l'identificador <f_id> especificat.

        :param f_id: L'identificador de la funcio.
        :type f_id: int
        :return: El nom del protocol.
        :rtype: str (or None)
        """
        try:
            conn = sql.connect(self.db)
            cursor = conn.cursor()
            cursor.execute('''SELECT f_name FROM Function WHERE f_id = (?)''',(f_id,))
            return cursor.fetchone()[0]
        except:
            return None
        finally:
            conn.close()    

    def get_function_id(self, p_id:int, f_name:str) -> int|None:
        """
        Retorna la identificació de la funció a partir del nom de funció <f_name> i la identificació del protocol <p_id>.\n\r
        
        :param p_id: Identificació del protocol.
        :type p_id: int
        :param f_name: Nom de la funció.
        :type f_name: str
        :return: Identificador de la funció (int) o None si no es troba cap funció amb aquesta informació.
        :rtype: int (or None)
        :raises sqlite3.Error: Si hi ha algun problema amb la base de dades.
        """
        try:
            conn = sql.connect(self.db)
            cursor = conn.cursor()
            cursor.execute('''SELECT f_id FROM Function WHERE f_name = ? AND p_id = ?''',(f_name,p_id))
            data = cursor.fetchone()
            if data is not None:
                return data[0]
            return None
        except sql.Error as e:
            print(e)
            return None
        finally:
            conn.close()

    def get_function_name(self, f_id:int) -> str|None:
        """
        Cerca a la base de dades el nom de la funcio amb l'identificador <f_id> especificat.

        :param f_id: L'identificador de la funcio.
        :type f_id: int
        :return: El nom de la funcio.
        :rtype: str (or None)
        """
        try:
            conn = sql.connect(self.db)
            cursor = conn.cursor()
            cursor.execute('''SELECT f_name FROM Function WHERE f_id = (?)''',(f_id,))
            return cursor.fetchone()[0]
        except:
            return None
        finally:
            conn.close()

    def get_function_description(self, f_id:int) -> str|Exception:
        """
        Retorna la descripcio de la funcio amb identificador <f_id>.

        :param v_id: ID de la funcio.
        :type v_id: int
        :return: Descripcio de la funcio.
        :rtype: int (o Exception)
        :raises Exception: Si hi ha hagut algun error en l'execució de la consulta.
        """
        try:
            with sql.connect(self.db) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT f_description FROM Function WHERE f_id = ?', (f_id,))
                result = cursor.fetchone()
                if result is not None: 
                    return result[0]
        except Exception as e:
            raise Exception(f"No s'ha pogut obtenir la descripcio de la funcio amb ID {f_id}. Error: {e}") 

    def get_function_canid(self, f_id:int) -> int|Exception:
        """
        Retorna el missatge CAN ID de la funció amb identificador <f_id>.

        :param f_id: ID de la funció.
        :type f_id: int
        :return: Missatge CAN ID de la funció.
        :rtype: int (o Exception)
        :raises Exception: Si hi ha hagut algun error en l'execució de la consulta.
        """
        try:
            with sql.connect(self.db) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT f_msg_id FROM Function WHERE f_id = ?', (f_id,))
                result = cursor.fetchone()
                if result is not None: 
                    return result[0]
        except Exception as e:
            raise Exception(f"No s'ha pogut obtenir el missatge CAN ID de la funció amb ID {f_id}. Error: {e}")  

    def update_function_name(self, p_id:int, f_id:int, f_name:str) -> int:
        """
        Modifica el nom de la funció <f_name>.

        :param p_id: L'identificador del protocol associat amb la funció.
        :type p_id: int
        :param f_name: Nom de la funció.
        :type f_name: str
        :return: 0 si s'ha realitzat una modificació, 2 altrament.
        :rtype: int
        """
        
        with sql.connect(self.db) as conn:
            conn.row_factory = sql.Row
            c = conn.cursor()
            c.execute("""SELECT COUNT(*) FROM Function WHERE f_name = (?) AND p_id <> (?);""", (f_name, p_id))
            if c.fetchone()[0] == 0:
                c.execute("""UPDATE Function SET f_name = (?) WHERE f_id = (?) and p_id = (?);""", (f_name, f_id, p_id))
                conn.commit()
                return 0
            else:
                return 2
        
    def update_function_description(self, f_id:int, f_description:str) -> int|Exception:
        """
        Modifica la descripció de la funció <f_description>.

        :param f_id: L'identificador de la funció.
        :type f_id: int
        :param f_description: Descripció de la funció.
        :type f_description: str
        :return: int si s'ha realitzat una modificació, Exception altrament.
        :rtype: int|Exception
        """
        try:
            with sql.connect(self.db) as conn:
                conn.row_factory = sql.Row
                c = conn.cursor()
                c.execute("""UPDATE Function SET f_description = (?) WHERE f_id = (?);""", (f_description, f_id))
                conn.commit()
                return 0
        except sql.Error as e:
            logging.error(f"Error actualitzant la funcio de la descripcio: {e}")
            raise e

    def update_function_msg_id(self, f_id:int, f_msg_id:str) -> int|Exception:
        """
        Modifica el msg id de la funcio <f_msg_id>.

        :param f_id: L'identificador de la funcio.
        :type f_id: int
        :param f_msg_id: Msg id de la funcio.
        :type f_msg_id: str
        :return: int si s'ha realitzat una modificació, Exception altrament.
        :rtype: int|Exception
        """
        try:
            with sql.connect(self.db) as conn:
                conn.row_factory = sql.Row
                c = conn.cursor()
                c.execute("""UPDATE Function SET f_msg_id = (?) WHERE f_id = (?);""", (int(f_msg_id,16), f_id))
                conn.commit()
                return 0
        except sql.Error as e:
            logging.error(f"Error actualitzant el CAN ID de la funcio: {e}")
            raise e

    def get_all_from_function(self, f_id:int) -> tuple|Exception:
        """
        Recupera totes les dades associades a un identificador de funcio de la taula 'Function'.

        :param f_id: L'identificador de la funció per recuperar les dades associades.
        :type f_id: int
        :returns: Una tupla amb totes les dades associades a l'identificador de funció proporcionat, o Exception si s'ha produït un error.
        :rtype: tuple or Exception
        :raises sqlite3.Error: Si es produeix un error en la connexió o en l'execució de la consulta.
        """
        try:
            with sql.connect(self.db) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM Function WHERE f_id = ?", (f_id,))
                return cursor.fetchone()
        except sql.Error as e:
            logging.error(f"Error obtenint informació de la funció: {e}")
            raise e

    def get_all_functions(self) -> dict|Exception:
        """
        Recupera totes les funcions i les agrupa amb tota la seva informació per nom de protocol en un diccionari.

        :returns: Un diccionari amb totes les funcions agrupades per identificador de protocol, o Exception si s'ha produït un error.
        :rtype: dict or Exception
        :raises sqlite3.Error: Si es produeix un error en la connexió o en l'execució de la consulta.
        """
        try:
            with sql.connect(self.db) as conn:
                structure = defaultdict(list)
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM Function")
                for item in cursor.fetchall():
                    structure[self.get_protocol_name(item[4])].append(item) 
                return dict(structure)
        except sql.Error as e:
            logging.error(f"Error obtenint totes les funcions: {e}")
            raise e

    def get_specific_p_id_from_f_id(self, f_id:int) -> int|Exception:
            """
            Retorna l'identificador de protocol associat a la funció amb identificador <f_id>.

            :param f_id: ID de la funció.
            :type f_id: int
            :return: Identificador del protocol associat.
            :rtype: int (o Exception)
            :raises Exception: Si hi ha hagut algun error en l'execució de la consulta.
            """
            try:
                with sql.connect(self.db) as conn:
                    cursor = conn.cursor()
                    cursor.execute('SELECT p_id FROM Function WHERE f_id = ?', (f_id,))
                    result = cursor.fetchone()
                    if result is not None: 
                        return result[0]
            except Exception as e:
                raise Exception(f"No s'ha pogut obtenir el missatge CAN ID de la variable amb ID {f_id}. Error: {e}")

    def get_info_from_function(self, f_id:int) -> dict|Exception:
        """
        Recupera totes les dades associades a un identificador de funció de la taula 'funció'.

        :param f_id: L'identificador de la funció per recuperar les dades associades.
        :type f_id: int
        :returns: Un diccionari amb totes les dades associades a l'identificador de funció proporcionat, o Exception si s'ha produït un error.
        :rtype: dict or Exception
        :raises sqlite3.Error: Si es produeix un error en la connexió o en l'execució de la consulta.
        """
        try:
            with sql.connect(self.db) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM Function WHERE f_id = ?", (f_id,))
                records = cursor.fetchone()
                function_info = {}
                function_info["function_id"] = records[0]
                function_info["function_name"] = records[1]
                function_info["function_description"] = records[2]
                function_info["function_contained_in_protocol"] = records[3]
                function_info["function_msg_id"] = records[4]
                return function_info
        except sql.Error as e:
            logging.error(f"Error obtenint informació de la funció: {e}")
            raise e 

    def get_all_functions_names_from_protocol_except_f_id(self, p_id:int, f_id:int) -> list[str] | bool:
        """
        Retorna el nom de totes les funcions associades a un protocol específic excepte la funció <f_id> especificada.

        :param p_id: L'identificador del protocol associat amb les funcions.
        :type p_id: int
        :param f_id: L'identificador de la funció a excluir de la cerca.
        :type f_id: int

        :return: Una llista amb els noms de totes les funcions associades a un protocol específic excepte <f_id> si la consulta és correcta, False si hi ha un error.
        :rtype: list[str] or False
        """
        try:
            with sql.connect(self.db) as conn:
                conn.row_factory = lambda cursor, row: row[0]
                cursor = conn.cursor()
                cursor.execute('SELECT f_name FROM Function WHERE p_id=(?) and f_id!=(?)', (p_id,f_id,))
                return cursor.fetchall()
        except Exception as e:
            logging.error(f'Error getting function names from protocol except {f_id}: {e}')
            return False

    def get_all_function_id_from_protocol(self, p_id:int) -> list[str] | bool:
        """
        Retorna totes les functions ids associades a un protocol específic.

        :param p_id: L'identificador del protocol associat amb les variables.
        :type p_id: int

        :return: Una llista amb totes les functions ids associades a un protocol específic si la consulta és correcta, False si hi ha un error.
        :rtype: list[str] or False
        """
        try:
            with sql.connect(self.db) as conn:
                conn.row_factory = lambda cursor, row: row[0]
                cursor = conn.cursor()
                cursor.execute('SELECT f_id FROM Function WHERE p_id=(?)', (p_id,))
                return cursor.fetchall()
        except Exception as e:
            logging.error(f'Error getting function ids from protocol: {e}')
            return False 

    ############################## ARGUMENT FUNCTIONS ##############################       
    def add_argument(self, a_name:str, a_description:str, a_is_signed:int, a_mask:bytes, a_offset:int, a_mul:int, a_div:int, f_id:int) -> int|Exception:
        """
        Afegeix el argument <a_name> amb descripció <a_description> a la base de dades.

        :param a_name: Nom del nou argument.
        :type a_name: str
        :param a_description: Descripció del protocol.
        :type description: str
        :param a_is_signed: Representa el signe de l'argument.
        :type a_is_signed: int
        :param a_mask: Mascara de l'argument.
        :type a_mask: bytes
        :param a_offset: Representa el offset a aplicar a l'argument.
        :type a_offset: int
        :param a_mult: Representa el valor multiplicador a aplicar a l'argument.
        :type a_mult: int
        :param a_div: Representa el valor divisor a aplicar a l'argument.
        :type a_div: int
        :return: Codi de retorn.
        :rtype: int or Exception
        """
        #1 Verifica que no hi hagi errors en el nom de la variable.
        var_name = ""
        
        for e in a_name.upper():
            if e == " ":
                pass
            elif e.isalpha() or e.isnumeric():
                var_name += e
            elif e == "_":
                var_name += e
            else:
                return 1
        if len(var_name) == 0:
            return 1
        
        #3 Comprova que no existeix a la base de dades un argument amb el mateix nom associada a la funcio.
        otherargumentsnames = self.get_arguments_from_function(f_id)
        for n in otherargumentsnames:
            if n == a_name:
                return 3
        
        # ADAPTACIO ALS VALORS PER DEFECTE
        if a_offset == "":
            a_offset = 0
        if a_mul == "":
            a_mul = 1
        if a_div == "":
            a_div = 1

        # Comprovacio de valors irreals
        if int(a_mul) < 1 or int(a_div) < 1:
            return 9
            
        try:
            with sql.connect(self.db) as conn:
                cursor = conn.cursor()
                cursor.execute("""SELECT COUNT(*) FROM Function WHERE f_id = (?);""", (f_id,))
                if cursor.fetchone()[0] != 0:
                    cursor.execute('INSERT INTO Argument(a_name, a_description, a_is_signed, a_mask, a_offset, a_mul, a_div, f_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', (var_name, a_description, a_is_signed, a_mask, a_offset, a_mul, a_div, f_id,))
                    conn.commit()
                    return 0
        except ValueError as error:
            logging.error(f'Error adding variable: {error}')
            raise ValueError('El tipus de dades no és vàlid')
        except Exception as error:
            logging.error(f'Error adding argument: {error}')
            return 8

    def modify_argument(self, a_id:int, a_name:str, a_description:str, a_is_signed:int, a_mask:bytes, a_offset:int, a_mul:int, a_div:int, f_id:int) -> int|Exception:
        """
        Modifica una variable <v_id> de la base de dades.

        :param a_id: L'identificador de la variable a modificar.
        :type a_id: int
        :param a_name: El nom de la variable.
        :type a_name: str
        :param a_description: La descripció de la variable.
        :type a_description: str
        :param a_is_signed: El tipus de dades de la variable: (0) com a solicitud, (1) com a resposta.
        :type a_is_signed: int
        :param a_mask: La màscara que s'utilitza per filtrar els bits rellevants de la variable.
        :type a_mask: bytes
        :param is_signed: Indica si la variable és de tipus signed (1) o no (0).
        :type is_signed: int
        :param a_offset: El valor utilitzat com a offset per a la variable.
        :type a_offset: int
        :param a_mul: El valor utilitzat com a multiplicador per a la variable.
        :type a_mul: int
        :param a_div: El valor utilitzat com a divisor per a la variable.
        :type a_div: int
        :param f_id: L'identificador del protocol associat amb la variable.
        :type f_id: int

        :return: 0 si la variable s'ha afegit correctament a la base de dades, altres o Exception si ha ocorregut un error.
        :rtype: int|Exception
        :raises ValueError: Si variable_type no és un tipus de dades vàlid.
        """
        #1 Verifica que no hi hagi errors en el nom de la variable.
        var_name = ""
        for e in a_name.upper():
            if e == " ":
                pass
            elif e.isalpha() or e.isnumeric():
                var_name += e
            elif e == "_":
                var_name += e
            else:
                return 1
        if len(var_name) == 0:
            return 1
        
        #3 Count the bits in mask.
        countbits = bin(int.from_bytes(a_mask))[2:].count("1")
        if countbits == 0:
            return 3

        #6 Comprova que no existeix a la base de dades una variable amb el mateix nom associada al protocol.
        othervariablesnames = self.get_all_arguments_names_from_function_except_a_id(f_id, a_id)
        for n in othervariablesnames:
            if n == var_name:
                return 6
        
        #7 Comprova que no entri en conflicte amb altres màscares a la base de dades.
        othermasks = self.get_all_argument_masks_from_function_except_a_id(f_id, a_id)
        for m in othermasks:
            if (int.from_bytes(m) & int.from_bytes(a_mask)) != 0:
                return 7
        
        # ADAPTACIO ALS VALORS PER DEFECTE
        if a_offset == "":
            a_offset = 0
        if a_mul == "":
            a_mul = 1
        if a_div == "":
            a_div = 1

        # Comprovacio de valors irreals
        if int(a_mul) < 1 or int(a_div) < 1:
            return 9

        try:
            with sql.connect(self.db) as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE Argument SET a_name=?, a_description=?, a_is_signed=?, a_mask=?, a_offset=?, a_mul=?, a_div=? WHERE a_id=?", (var_name, a_description, a_is_signed, a_mask, a_offset, a_mul, a_div, a_id,))
                conn.commit()
                return 0
        except ValueError as error:
            logging.error(f'Error editting argument: {error}')
            raise ValueError('El tipus de dades no és vàlid')
        except Exception as error:
            logging.error(f'Error editting argument: {error}')
            return 8
        
    def delete_argument(self,a_id:int) -> int|Exception:
        """
        Elimina un argument de la base de dades.

        :param a_id: L'identificador de l'argument.
        :type a_id: int
        :return: 0 si s'ha eliminat correctament, Exception altrament.
        """
        try:
            with sql.connect(self.db) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM Argument WHERE a_id=?", (a_id,))
                conn.commit()
                return 0
        except sql.Error as e:
            logging.error(f"Error eliminant l'argument': {e}")
            raise e
                
    def get_arguments_from_function(self, f_id:int) -> tuple|None:
        """
        Cerca a la base de dades tots els arguments assignats a una funció <f_id>.

        :param f_id: Identificador de la funció.
        :type f_id: int
        :return: Tots els arguments disponibles de la funció <f_id>.
        :rtype: tuple (o None)
        """
        if self.loaded_db():
            try:
                conn = sql.connect(self.db)
                cursor = conn.cursor()
                cursor.execute('''SELECT a_name FROM Argument WHERE f_id = (?)''',(f_id,))
                return tuple(e[0] for e in cursor.fetchall())
            finally:
                conn.close()
        else:
            return None

    def get_nbits_from_argument(self, a_id:int) -> tuple|None:
        """
        Cerca a la base de dades si el argument <a_id> és complement a dos o no i el nombre de bits que ocupa el argument <a_id>.

        :param a_id: Identificador de l'argument.
        :type a_id: int
        :return: La primera posició de la tupla conté si és complement a dos o no, la segona posició conté el nombre de bits.
        :rtype: tuple (or None)
        """
        if self.loaded_db():
            try:
                conn = sql.connect(self.db)
                cursor = conn.cursor()
                cursor.execute('''SELECT a_is_signed, a_mask FROM Argument WHERE a_id = (?)''',(a_id,))
                t = cursor.fetchone()
                bits = bin(int.from_bytes(t[1]))
                n_bits = sum(1 for e in bits if e == "1")
                return (t[0],n_bits)
            finally:
                conn.close()
        else:
            return None
       
    def get_argument_id(self, f_id:int, a_name:str) -> int|None:
        """
        Retorna la identificació de la funció a partir del nom de l'argument <a_name> i la identificació de la funció <f_id>.\n\r
        
        :param f_id: Identificació de la funció.
        :type f_id: int
        :param a_name: Nom de l'argument.
        :type a_name: str
        :return: Identificador de l'argument (int) o None si no es troba cap funció amb aquesta informació.
        :rtype: int (or None)
        :raises sqlite3.Error: Si hi ha algun problema amb la base de dades.
        """
        try:
            conn = sql.connect(self.db)
            cursor = conn.cursor()
            cursor.execute('''SELECT a_id FROM Argument WHERE a_name = ? AND f_id = ?''',(a_name,f_id))
            return cursor.fetchone()[0]
        except sql.Error as e:
            print(e)
            return None
        finally:
            conn.close()

    def get_argument_name(self, a_id:int) -> str|None:
        """
        Cerca a la base de dades el nom de l'argument amb l'identificador <a_id> especificat.

        :param a_id: L'identificador de l'argument.
        :type a_id: int
        :return: El nom de l'argument.
        :rtype: str (or None)
        """
        try:
            conn = sql.connect(self.db)
            cursor = conn.cursor()
            cursor.execute('''SELECT a_name FROM Argument WHERE a_id = (?)''',(a_id,))
            return cursor.fetchone()[0]
        except:
            return None
        finally:
            conn.close()

    def get_argument_description(self, a_id:int) -> str|Exception:
        """
        Retorna la descripcio de l'argument amb identificador <a_id>.

        :param a_id: ID de l'argument.
        :type a_id: int
        :return: Descripcio de l'argument.
        :rtype: int (o Exception)
        :raises Exception: Si hi ha hagut algun error en l'execució de la consulta.
        """
        try:
            with sql.connect(self.db) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT a_description FROM Argument WHERE a_id = ?', (a_id,))
                result = cursor.fetchone()
                if result is not None: 
                    return result[0]
        except Exception as e:
            raise Exception(f"No s'ha pogut obtenir la descripcio de l'argument amb ID {a_id}. Error: {e}") 

    def get_argument_is_signed(self, a_id:int) -> bool|Exception:
        """
        Retorna si el argument amb identificador <a_id> és signada o no.

        :param a_id: ID de l'argument.
        :type a_id: int
        :return: True si el argument és signat.
        :rtype: bool (o Exception)
        :raises Exception: Si hi ha hagut algun error en l'execució de la consulta.
        """
        try:
            with sql.connect(self.db) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT a_is_signed FROM Argument WHERE a_id = ?', (a_id,))
                result = cursor.fetchone()
                if result is not None:
                    return int(result[0]) == 1
        except Exception as e:
            raise Exception(f"No s'ha pogut obtenir el signe de l'argument amb ID {a_id}. Error: {e}")

    def get_argument_mask(self, a_id:int) -> bytes|None:
        """
        Retorna el valor de màscara de l'argument amb l'identificador <a_id> especificat.\n\r
        
        :param a_id: Identificador de argument.
        :type a_id: int
        :return: El valor de la màscara de l'argument en bytes.
        :rtype: bytes (o None)
        """
        try:
            with sql.connect(self.db) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT a_mask FROM Argument WHERE a_id = ?', (a_id,))
                return cursor.fetchone()[0]
        except Exception as e:
            print(e)
            return None
        finally:
            conn.close()

    def get_argument_offset(self, a_id:int) -> int|Exception:
        """
        Retorna l'offset de l'argument amb identificador <a_id>.

        :param a_id: ID de l'argument.
        :type a_id: int
        :return: L'offset de l'argument.
        :rtype: int (o Exception)
        :raises Exception: Si hi ha hagut algun error en l'execució de la consulta.
        """
        try:
            with sql.connect(self.db) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT a_offset FROM Argument WHERE a_id = ?', (a_id,))
                result = cursor.fetchone()
                if result is not None: 
                    return result[0]
        except Exception as e:
            raise Exception(f"No s'ha pogut obtenir el offset de l'argument amb ID {a_id}. Error: {e}")
    
    def get_argument_mul(self, a_id:int) -> int|Exception:
        """
        Retorna el valor multiplicador de l'argument amb identificador <a_id>.

        :param a_id: ID de l'argument.
        :type a_id: int
        :return: El multiplicador de l'argument.
        :rtype: int (o Exception)
        :raises Exception: Si hi ha hagut algun error en l'execució de la consulta.
        """
        try:
            with sql.connect(self.db) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT a_mul FROM Argument WHERE a_id = ?', (a_id,))
                result = cursor.fetchone()
                if result is not None: 
                    return result[0]
        except Exception as e:
            raise Exception(f"No s'ha pogut obtenir el multiplicador de l'argument amb ID {a_id}. Error: {e}")
    
    def get_argument_div(self, a_id:int) -> int|Exception:
        """
        Retorna el valor divisor de l'argument amb identificador <a_id>.

        :param a_id: ID de l'argument.
        :type a_id: int
        :return: El divisor de l'argument.
        :rtype: int (o Exception)
        :raises Exception: Si hi ha hagut algun error en l'execució de la consulta.
        """
        try:
            with sql.connect(self.db) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT a_div FROM Argument WHERE a_id = ?', (a_id,))
                result = cursor.fetchone()
                if result is not None: 
                    return result[0]
        except Exception as e:
            raise Exception(f"No s'ha pogut obtenir el divisor de l'argument amb ID {a_id}. Error: {e}")

    def update_argument_name(self, f_id:int, a_id:int, a_name:str) -> int:
        """
        Modifica el nom de l'argument <a_name>.

        :param f_id: L'identificador de la funció associada amb l'argument.
        :type f_id: int
        :param a_name: Nom de l'argument.
        :type a_name: str
        :return: 0 si s'ha realitzat una modificació, 2 altrament.
        :rtype: int
        """
        
        with sql.connect(self.db) as conn:
            conn.row_factory = sql.Row
            c = conn.cursor()
            c.execute("""SELECT COUNT(*) FROM Argument WHERE a_name = (?) AND f_id <> (?);""", (a_name, f_id))
            if c.fetchone()[0] == 0:
                c.execute("""UPDATE Argument SET a_name = (?) WHERE a_id = (?) AND f_id = (?);""", (a_name, a_id, f_id))
                conn.commit()
                return 0
            else:
                return 2
        
    def update_argument_description(self, a_id:int, a_description:str) -> int|Exception:
        """
        Modifica la descripció de la funció <v_description>.

        :param a_id: L'identificador de l'argument.
        :type a_id: int
        :param a_description: Descripció de l'argument.
        :type a_description: str
        :return: 0 si s'ha realitzat una modificació, Exception altrament.
        :rtype: int|Exception
        """
        try:
            with sql.connect(self.db) as conn:
                conn.row_factory = sql.Row
                c = conn.cursor()
                c.execute("""UPDATE Argument SET a_description = (?) WHERE a_id = (?);""", (a_description, a_id))
                conn.commit()
                return 0
        except sql.Error as e:
            logging.error(f"Error actualitzant l'argument description: {e}")
            raise e

    def update_argument_is_signed(self, a_id:int, a_is_signed:int) -> int|Exception:
        """
        Modifica el signe de la variable <a_is_signed>.

        :param a_id: L'identificador de l'argument.
        :type a_id: int
        :param a_is_signed: Signe de l'argument'.
        :type a_is_signed: str
        :return: 0 si s'ha realitzat una modificació, Exception altrament.
        :rtype: int|Exception
        """
        try:
            with sql.connect(self.db) as conn:
                conn.row_factory = sql.Row
                c = conn.cursor()
                c.execute("""UPDATE Argument SET a_is_signed = (?) WHERE a_id = (?);""", (a_is_signed, a_id))
                conn.commit()
                return 0
        except sql.Error as e:
            logging.error(f"Error actualitzant el signe de l'argument: {e}")
            raise e
        
    def update_argument_mask(self, id_argument:int, mask) -> bool:
        """
        Permet actualitzar la màscara d'un argument a la base de dades.

        :param id_argument: L'ID de l'argument a actualitzar.
        :type id_argument: int
        :param mask: La màscara de l'argument en format int (8 bytes).
        :type mask: int
        :return: True si la modificació s'ha fet amb èxit, False altrament.
        :rtype: bool
        :raises sqlite3.Error: Si hi ha hagut algun problema en l'execució de la consulta SQL.
        """
        masc_bytes = mask.to_bytes(8, byteorder='big')
        try:
            with sql.connect(self.db) as conn:
                cursor = conn.cursor()
                cursor.execute('UPDATE Argument SET a_mask = ? WHERE a_id = ?', (masc_bytes, id_argument))
                conn.commit()
                return True
        except sql.Error as e:
            print(f"Error actualitzant la mascara de l'argument: {e}")
            return False

    def update_argument_offset(self, a_id:int, a_offset:int) -> int|Exception:
        """
        Modifica el offset de l'argument <a_offset>.

        :param a_id: L'identificador de l'argument.
        :type a_id: int
        :param a_offset: Offset de l'argument.
        :type a_offset: str
        :return: 0 si s'ha realitzat una modificació, Exception altrament.
        :rtype: int|Exception
        """
        try:
            with sql.connect(self.db) as conn:
                conn.row_factory = sql.Row
                c = conn.cursor()
                c.execute("""UPDATE Argument SET a_offset = (?) WHERE a_id = (?);""", (a_offset, a_id))
                conn.commit()
                return 0
        except sql.Error as e:
            logging.error(f"Error actualitzant el offset de l'argument': {e}")
            raise e

    def update_argument_mul(self, a_id:int, a_mul:int) -> int|Exception:
        """
        Modifica el multiplicador de l'argument <a_mul>.

        :param a_id: L'identificador de l'argument.
        :type a_id: int
        :param a_mul: Multiplicador de l'argument.
        :type a_mul: str
        :return: 0 si s'ha realitzat una modificació, Exception altrament.
        :rtype: int|Exception
        """
        try: 
            with sql.connect(self.db) as conn:
                conn.row_factory = sql.Row
                c = conn.cursor()
                c.execute("""UPDATE Argument SET a_mul = (?) WHERE a_id = (?);""", (a_mul, a_id))
                conn.commit()
                return 0
        except sql.Error as e:
            logging.error(f"Error actualitzant el multiplicador de l'argument': {e}")
            raise e

    def update_argument_div(self, a_id:int, a_div:int) -> int|Exception:
        """
        Modifica el divisor de l'argument <a_div>.

        :param a_id: L'identificador del l'argument.
        :type a_id: int
        :param a_div: divisor de l'argument.
        :type a_div: str
        :return: 0 si s'ha realitzat una modificació, Exception altrament.
        :rtype: int|Exception
        """
        try:
            with sql.connect(self.db) as conn:
                conn.row_factory = sql.Row
                c = conn.cursor()
                c.execute("""UPDATE Argument SET a_div = (?) WHERE a_id = (?);""", (a_div, a_id))
                conn.commit()
                return 0
        except sql.Error as e:
            logging.error(f"Error actualitzant el divisor de l'argument': {e}")
            raise e

    def get_all_argument_masks_from_function(self, f_id:int) -> list[bytes]  | bool:
        """
        Retorna les màscares de tots els arguments d'una funció <f_id>.

        :param f_id: L'identificador de la funcio per obtenir les màscares de tots els arguments.
        :type f_id: int
        :return: Les màscares de tots els arguments de la funcio.
        :rtype: list[bytes] or False
        :raises: Exception si hi ha algun error amb la connexió a la base de dades.
        """
        try:
            with sql.connect(self.db) as conn:
                conn.row_factory = lambda cursor, row: row[0]
                cursor = conn.cursor()
                cursor.execute('''SELECT a_mask FROM Argument WHERE f_id=(?)''',(f_id,))
                return cursor.fetchall()
        except Exception as e:
            logging.error(f"Error en obtenir les màscares dels arguments de la funcio. {e}")
            return False
        finally:
            conn.close()

    def get_all_argument_masks_from_function_except_a_id(self, f_id:int, a_id:int) -> list[bytes] | bool:
        """
        Retorna el nom de totes els arguments associats a una funció específica <f_id> excepte el argument <a_id> especificat.

        :param f_id: L'identificador de la funcio  per obtenir les màscares de tots els arguments.
        :type f_id: int
        :param a_id: L'identificador de l'argument que es vol excloure.
        :type a_id: int
        :return: Les màscares de tots els arguments de la funció.
        :rtype: list[bytes] or False
        :raises: Exception si hi ha algun error amb la connexió a la base de dades.
        """
        try:
            with sql.connect(self.db) as conn:
                conn.row_factory = lambda cursor, row: row[0]
                cursor = conn.cursor()
                cursor.execute('''SELECT a_mask FROM Argument WHERE f_id=(?) and a_id != (?)''',(f_id,a_id))
                return cursor.fetchall()
        except Exception as e:
            logging.error(f"Error en obtenir les màscares dels arguments de la funció except {a_id}. {e}")
            return False
        finally:
            conn.close()
    
    def get_all_arguments_names_from_function_except_a_id(self, f_id:int, a_id:int) -> list[str] | bool:
        """
        Retorna el nom de totes les variables associades a una funció específica excepte el argument <a_id> especifit.

        :param f_id: L'identificador de la funció associada amb les variables.
        :type f_id: int
        :param a_id: L'identificador de l'argument a excluir de la cerca.
        :type a_id: int

        :return: Una llista amb els noms de tots els arguments associats a una funció especifica si la consulta és correcta, False si hi ha un error.
        :rtype: list[str] or False
        """
        try:
            with sql.connect(self.db) as conn:
                conn.row_factory = lambda cursor, row: row[0]
                cursor = conn.cursor()
                cursor.execute('SELECT a_name FROM Argument WHERE f_id=(?) and a_id!=(?)', (f_id,a_id))
                return cursor.fetchall()
        except Exception as e:
            logging.error(f'Error getting variable names from Argument excepte {a_id}: {e}')
            return False
        
    def get_all_from_argument(self, a_id:int) -> tuple|Exception:
        """
        Recupera totes les dades associades a un identificador d'argument de la taula 'Argument'.

        :param a_id: L'identificador de l'argument per recuperar les dades associades.
        :type a_id: int
        :returns: Una tupla amb totes les dades associades a l'identificador d'argument proporcionat, o Exception si s'ha produït un error.
        :rtype: tuple or Exception
        :raises sqlite3.Error: Si es produeix un error en la connexió o en l'execució de la consulta.
        """
        try:
            with sql.connect(self.db) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM Argument WHERE a_id = ?", (a_id,))
                return cursor.fetchone()
        except sql.Error as e:
            logging.error(f"Error obtenint informació de l'argument: {e}")
            raise e
     
    def get_all_arguments(self) -> dict|Exception:
        """
        Recupera tots els arguments i els agrupa amb tota la seva informació per nom de funció en un diccionari.

        :returns: Un diccionari amb tots els arguments agrupades per identificador de funció, o Exception si s'ha produït un error.
        :rtype: dict or Exception
        :raises sqlite3.Error: Si es produeix un error en la connexió o en l'execució de la consulta.
        """
        try:
            with sql.connect(self.db) as conn:
                structure = defaultdict(list)
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM Argument")
                for item in cursor.fetchall():
                    structure[self.get_f_name_from_function(item[8])].append(item) 
                return dict(structure)
        except sql.Error as e:
            logging.error(f"Error obtenint tots els arguments: {e}")
            raise e

    def get_all_argument_id_from_function(self, f_id:int) -> list[int] | bool:
        """
        Retorna tots els arguments ids associats a una funció específica.

        :param f_id: L'identificador de la funcio associada als arguments.
        :type f_id: int

        :return: Una llista amb els arguments ids associats a una funció específica si la consulta és correcta, False si hi ha un error.
        :rtype: list[str] or False
        """
        try:
            with sql.connect(self.db) as conn:
                conn.row_factory = lambda cursor, row: row[0]
                cursor = conn.cursor()
                cursor.execute('SELECT a_id FROM Argument WHERE f_id=(?)', (f_id,))
                return cursor.fetchall()
        except Exception as e:
            logging.error(f'Error getting arguments id from function: {e}')
            return False 

    def get_info_from_argument(self, a_id:int) -> dict|Exception:
        """
        Recupera totes les dades associades a un identificador de argument de la taula 'Argument'.

        :param a_id: L'identificador de l'argument per recuperar les dades associades.
        :type a_id: int
        :returns: Un diccionari amb totes les dades associades a l'identificador de argument proporcionat, o Exception si s'ha produït un error.
        :rtype: dict|Exception
        :raises sqlite3.Error: Si es produeix un error en la connexió o en l'execució de la consulta.
        """
        try:
            with sql.connect(self.db) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM Argument WHERE a_id = ?", (a_id,))
                records = cursor.fetchone()
                argument_info = {}
                argument_info["argument_id"] = records[0]
                argument_info["argument_name"] = records[1]
                argument_info["argument_description"] = records[2]
                argument_info["argument_is_signed"] = records[3]
                mask = bin(int.from_bytes(records[4]))[2:]
                argument_info["argument_mask"] = mask.zfill(64)
                argument_info["argument_offset"] = records[5]
                argument_info["argument_mul"] = records[6]
                argument_info["argument_div"] = records[7]
                argument_info["argument_contained_in_function"] = records[8]
                return argument_info
        except sql.Error as e:
            logging.error(f"Error obtenint informació de l'argument: {e}")
            raise e
        
    ############################## GENERIC FUNCTIONS ##############################
    def get_all_structured_by_p_id(self) -> dict:
        """
        (ELIMINAR) Obté una estructura en arbre de tots els protocols juntament amb les seves variables i funcions asociades que existeixen a la base de dades.

        :return: Un arbre estructurat de tot el contingut de la base de dades.
        :rtype: dict
        """
        with sql.connect(self.db) as conn:
            conn.row_factory = sql.Row
            c = conn.cursor()

            # Obtener todos los protocolos
            c.execute("SELECT * FROM Protocol")
            protocols = c.fetchall()

            # Inicializar diccionario de resultados
            resultados = {}

            # Para cada protocolo, obtener las variables y funciones correspondientes
            for protocol in protocols:
                p_id = protocol["p_id"]

                # Obtener todas las variables clasificadas por v_msg_id
                c.execute("SELECT v_msg_id, v_id, v_name, v_default, v_direction, v_is_signed, v_mask, v_offset, v_mul, v_div FROM Variable WHERE p_id = ?", (p_id,))
                variables = c.fetchall()

                # Obtener todas las funciones clasificadas por f_msg_id
                c.execute("SELECT f_msg_id, f_id, f_name, f_description FROM Function WHERE p_id = ?", (p_id,))
                funciones = c.fetchall()

                # Agregar resultados al diccionario
                resultados[p_id] = {
                    "variables": {},
                    "functions": {}
                }

                # Agrupar las variables por v_msg_id
                for variable in variables:
                    v_id = variable["v_id"]
                    #if v_id not in resultados[p_id]["variables"]:
                    #    resultados[p_id]["variables"][v_id] = []
                    #resultados[p_id]["variables"][v_id].append({"ids": variable["v_id"], "name":variable["v_name"], "frame":variable["v_msg_id"], "value": variable["v_value"], "bits": variable["v_bits"], "direction": variable["v_type"], "signed":variable["v_is_signed"], "mask":variable["v_mask"]})
                    resultados[p_id]["variables"][v_id] = {"ids": variable["v_id"], "name":variable["v_name"], "frame":variable["v_msg_id"], "value": variable["v_default"], "direction": variable["v_direction"], "signed":variable["v_is_signed"], "mask":variable["v_mask"], "offset":variable["v_offset"], "mult":variable["v_mul"], "div":variable["v_div"]}

                # Agrupar las funciones por f_msg_id
                for funcion in funciones:
                    f_id = funcion["f_id"]
                    #if f_id not in resultados[p_id]["functions"]:
                    #    resultados[p_id]["functions"][f_id] = []
                    #resultados[p_id]["functions"][f_id].append({"ids": funcion["f_id"], "name":funcion["f_name"], "frame":funcion["f_msg_id"],"direction":"0", "value": funcion["f_value"], "bits": funcion["f_bits"], "signed":funcion["f_is_signed"], "mask":funcion["f_mask"]})
                    resultados[p_id]["functions"][f_id] = {"ids": funcion["f_id"], "name":funcion["f_name"], "description":funcion["f_description"], "frame":funcion["f_msg_id"]}

        return resultados

    def extract_protocol(self, p_id:int) -> tuple|Exception:
            """
            Extreu tot el protocol <p_id>, separant els missatges que contenen variables de transmissió, variables de recepció i funcions.

            :param p_id: ID del protocol
            :type p_id: int
            :return: Una tupla amb 3 diccionaris amb la informació del protocol seleccionat (0->F,1->T,2->R).
            :rtype: tuple (o Exception)
            :raises Exception: Si hi ha hagut algun error en l'execució de la consulta.
            """
            try:
                with sql.connect(self.db) as conn:
                    cursor = conn.cursor()
                    cursor.execute('SELECT * FROM Function WHERE p_id = ?', (p_id,))
                    funcions = cursor.fetchall()
                    cursor.execute('SELECT * FROM Variable WHERE p_id = ? and v_direction = 0', (p_id,))
                    var_tx = cursor.fetchall()
                    cursor.execute('SELECT * FROM Variable WHERE p_id = ? and v_direction = 1', (p_id,))
                    var_rx = cursor.fetchall()
                    fun_dict = {}
                    vartx_dict = {}
                    varrx_dict = {}
                    arg_dict = {}
                    for funcio in funcions:
                        temp_dict = {}
                        temp_dict["name"] = funcio[1]
                        temp_dict["msg_id"] = funcio[3]
                        fun_dict[funcio[0]] = temp_dict

                        cursor.execute('SELECT * FROM ARGUMENT where f_id = ?', (funcio[0],))
                        arguments = cursor.fetchall()
                    
                        for argument in arguments:
                            temp_dict = {}
                            temp_dict["name"] = argument[1]
                            temp_dict["is_signed"] = argument[3]
                            temp_dict["mask"] = argument[4]
                            temp_dict["f_id"] = argument[8]
                            arg_dict[argument[0]] = temp_dict

                    for variable in var_tx:
                        temp_dict = {}
                        temp_dict["name"] = variable[1]
                        temp_dict["msg_id"] = variable[4]
                        temp_dict["mask"] = variable[5]
                        temp_dict["is_signed"] = variable[6]
                        temp_dict["tolerance"] = variable[11]
                        vartx_dict[variable[0]] = temp_dict

                    for variable in var_rx:
                        temp_dict = {}
                        temp_dict["name"] = variable[1]
                        temp_dict["msg_id"] = variable[4]
                        temp_dict["mask"] = variable[5]
                        temp_dict["is_signed"] = variable[6]
                        temp_dict["tolerance"] = variable[11]
                        varrx_dict[variable[0]] = temp_dict

                    return fun_dict, vartx_dict, varrx_dict, arg_dict

            except Exception as e:
                raise Exception(f"No s'ha pogut obtenir la informació del Protocol {p_id}. Error: {e}")

    def export_all_as_json(self):
        """
        Export all protocols, variables and functions from database as JSON format.

        :return: JSON with database content.
        :rtype: json
        """
        try:
            with sql.connect(self.db) as conn:
                cursor = conn.cursor()
                full_db = {}
                cursor.execute('SELECT * FROM Protocol')
                protocols = cursor.fetchall()
                for protocol in protocols:
                    protocol_dic = {}
                    protocol_dic["id"] = protocol[0]
                    protocol_dic["description"] = protocol[2]
                    all_variables = {}
                    cursor.execute('SELECT * FROM Variable WHERE p_id = ?', (protocol_dic["id"],))
                    variables = cursor.fetchall()
                    for variable in variables:
                        variable_dic = {}
                        variable_dic["id"] = variable[0]
                        variable_dic["name"] = variable[1]
                        variable_dic["description"] = variable[2]
                        variable_dic["direction"] = variable[3]
                        variable_dic["msg_id"] = int(variable[4])
                        variable_dic["mask"] = list(variable[5])
                        variable_dic["is_signed"] = variable[6]
                        variable_dic["default_value"] = variable[7]
                        variable_dic["offset"] = variable[8]
                        variable_dic["mul"] = variable[9]
                        variable_dic["div"] = variable[10]
                        variable_dic["tolerance"] = variable[11]
                        variable_dic["p_id"] = variable[12]
                        all_variables[variable[1]] = variable_dic

                    protocol_dic["Variables"] = all_variables

                    all_arguments = {}
                    all_functions = {}
                    cursor.execute('SELECT * FROM Function WHERE p_id = ?', (protocol_dic["id"],))
                    functions = cursor.fetchall()
                    for function in functions:
                        function_dic = {}
                        function_dic["id"] = function[0]
                        function_dic["name"] = function[1]
                        function_dic["description"] = function[2]
                        function_dic["msg_id"] = function[3]
                        function_dic["p_id"] = function[4]
                        all_functions[function[1]] = function_dic
 
                        cursor.execute('SELECT * FROM ARGUMENT where f_id = ?', (function_dic["id"],))
                        arguments = cursor.fetchall()
                    
                        for argument in arguments:
                            argument_dic = {}
                            argument_dic["id"] = argument[0]
                            argument_dic["name"] = argument[1]
                            argument_dic["description"] = argument[2]
                            argument_dic["is_signed"] = argument[3]
                            argument_dic["mask"] = list(argument[4])
                            argument_dic["offset"] = argument[5]
                            argument_dic["mul"] = argument[6]
                            argument_dic["div"] = argument[7]
                            argument_dic["f_id"] = argument[8]
                            all_arguments[argument[1]] = argument_dic

                    protocol_dic["Functions"] = all_functions
                    protocol_dic["Functions"]["Arguments"] = all_arguments
                    full_db[protocol[1]] = protocol_dic
                return json.dumps(full_db)
                
        except Exception as e:
            raise Exception(f"No s'ha pogut exportar la base de dades. Error: {e}")

if __name__ == "__main__":
    #from config_mod import *
    db = Database(r"C:\Development\Akitacan Code\new_proves.db")
    #print(db.db)
    if db.loaded_db():
        #print(db.get_all_used_msg_id_from_protocol_except_f_id(1,3))
        #print(db.modify_function(4, "TEST2", "es un test2", "0x300", 6))
        """
        print("------------------------------------------FIRST TEST------------------------------------------")
        db.add_protocol("T164E","Aquest protocol es per el telescopi electric d'Ausa")
        db.add_variable("BAT_Number_of_Batteries", "", 0, "301", bytes([0,0,0,0,0,0,0,255]), 0, "0", 0, 0, 0, 1)
        db.add_variable("BAT_VIRTUAL_BATTERY_SOC", "", 0, "301", bytes([0,0,0,0,0,0,255,0]), 0, "0", 0, 0, 0, 1)
        db.add_variable("BAT_VIRTUAL_BATTERY_TEMPERATURE", "", 0, "303", bytes([0,0,0,0,0,0,255,255]), 0, "0", 0, 0, 0, 1)
        db.add_function("SDO_TEST", "", "631", 1 )
        db.add_argument("B0", "", 0, bytes([0,0,0,0,0,0,0,255]), 0, 0, 0, 3)
        db.add_argument("B1", "", 0, bytes([0,0,0,0,0,0,255,0]), 0, 0, 0, 3)
        print("------------------------------------------SECOND TEST------------------------------------------")
        print(db.get_variables_from_protocol(1))
        print(db.get_functions_from_protocol(1))
        print(db.get_arguments_from_function(3))
        print("------------------------------------------THIRD TEST------------------------------------------")
        print(db.get_nbits_from_variable(1))
        print(db.get_nbits_from_variable(3))
        print(db.get_nbits_from_argument(3))
        print(db.get_protocol_id("T164E"))
        print(db.get_protocol_name(1))
        print(db.get_default_variable_value(1,"BAT_NUMBER_OF_BATTERIES"))
        print(db.exist_any_protocol())
        print(db.update_variable_mask(1, 0xff0000))
        print(db.update_argument_mask(3, 0xff0000))
        print(db.get_variable_mask(3))
        print(db.get_argument_mask(3))
        print("------------------------------------------FORTH TEST------------------------------------------")
        print(db.get_variable_id(1,"BAT_NUMBER_OF_BATTERIES"))
        print(db.get_function_id(1,"SDO_TEST"))
        print(db.get_argument_id(3,"B1"))
        print(db.get_variable_name(2))
        print(db.get_function_name(3))
        print(db.get_argument_name(3))
        print(db.get_variable_canid(1)) 
        print(db.get_function_canid(3)) 
        print(db.get_variable_is_signed(1)) 
        print(db.get_argument_is_signed(3)) 
        print(db.get_variable_direction(1))
        print(db.get_all_protocols_names())
        print(db.get_all_variables_masks_from_protocol(1,769,0))
        print(db.get_all_variables_masks_from_protocol_except_v_id(1,1,0))
        print(db.get_all_argument_masks_from_function(3))
        print(db.get_all_argument_masks_from_function_except_a_id(3,3))
        print("------------------------------------------FIFTH TEST------------------------------------------")
        print(db.get_all_variables_names_from_protocol(1))
        print(db.get_all_variables_names_from_protocol_except_v_id(1,1))
        print(db.get_all_arguments_names_from_function_except_a_id(3,4))
        print(db.get_all_from_variable(1))
        print(db.get_all_from_function(3))
        print(db.get_all_from_argument(3))
        print(db.get_all_variables())
        print(db.get_all_functions())
        print(db.get_all_arguments())
        print(db.get_all_structured_by_p_id())
        print("------------------------------------------SIXTH TEST------------------------------------------")
        print(db.get_info_from_protocol(1))
        #print(db.modify_protocol(1,"T164E","Aquest protocol es per el telescopi electric d'Ausa")) #FUNCIONA PERO ES COMENTA X EVITAR PROBLEMES
        #print(db.delete_protocol(3)) #FUNCIONA PERO ES COMENTA X EVITAR PROBLEMES
        print(db.get_info_from_variable(1))
        #print(db.modify_variable(1,"BAT_NUMBER_OF_BATTERIES","",0,"301",bytes([0,0,0,0,0,255,0,0]),0,0,0,0,0,1)) #FUNCIONA PERO ES COMENTA X EVITAR PROBLEMES
        print(db.get_specific_p_id_from_v_id(3)) 
        #print(db.delete_variable(6)) #FUNCIONA PERO ES COMENTA X EVITAR PROBLEMES
        print(db.get_info_from_function(3))
        print(db.get_all_used_msg_id_from_protocol(1))
        print(db.get_all_functions_names_from_protocol_except_f_id(1,3))
        #print(db.modify_function(3,"SDO", "", "631", 1)) #FUNCIONA PERO ES COMENTA X EVITAR PROBLEMES
        #print(db.delete_function(4)) #FUNCIONA PERO ES COMENTA X EVITAR PROBLEMES
        #print(db.delete_argument(5)) #FUNCIONA PERO ES COMENTA X EVITAR PROBLEMES
        print(db.get_specific_p_id_from_f_id(3))
        print("------------------------------------------SEVENTH TEST------------------------------------------")
        print(db.extract_protocol(1)) #VA PERO NO SE SI FA EL QUE ES VOLIA A LA IDEA ORIGINAL
        #print(db.export_all_as_json())
        #with open("my_db.json","w") as f:
            #f.write(db.export_all_as_json())
        print("------------------------------------------EIGHT TEST------------------------------------------")
        VALIDAT
        #PROTOCOL FUNCTIONS TO TEST
        print("PROTOCOL TEST")
        print(db.add_protocol("TEST","Aquest protocol es una prova"))
        print(db.update_protocol_name(4,"PROTOCOL_TEST"))
        print(db.update_protocol_description(4,"AIXO ES UN TEST"))
        print(db.get_protocol_id("PROTOCOL_TEST"))
        print(db.get_protocol_name(4))
        print(db.get_protocol_description(4))
        
        #VARIABLE FUNCTIONS TO TEST
        print("VARIABLE TEST")
        #print(db.add_variable("test","",1,"400",bytes([0,0,0,0,0,0,0,1]),0,0,0,0,0,4))
        print(db.get_variable_description(7))
        print(db.get_variable_direction(7))
        print(db.get_variable_offset(7))
        print(db.get_variable_mul(7))
        print(db.get_variable_div(7))
        print(db.update_variable_name(4,"TEST_FINAL"))
        print(db.update_variable_description(7,"UNA DESCRIPCIO"))
        print(db.update_variable_msg_id(7,"500"))
        print(db.update_variable_direction(7,0))
        print(db.update_variable_is_signed(7,1))
        print(db.update_variable_default_value(7,1))
        print(db.update_variable_offset(7,1))
        print(db.update_variable_mul(7,1))
        print(db.update_variable_div(7,1))
        
        #FUNCTION FUNCTIONS TO TEST
        print("FUNCTION TEST")
        #print(db.add_function("TEST", "", "700", 1))
        print(db.update_function_description(5,"DESCRIPCIO DE TEST"))
        print(db.get_function_description(5))
        print(db.update_function_name(1,5,"FUNCIO_TEST"))
        print(db.update_function_name(1,3,"SDO_TEST"))
        print(db.update_function_msg_id(5,"800"))
        
        #ARGUMENT FUNCTIONS TO TEST
        print("ARGUMENT TEST")
        #print(db.add_argument("TEST","",0,bytes([0,0,0,0,0,0,0,255]),0,0,0,3))
        print(db.update_argument_description(6,"descripcio"))
        print(db.update_argument_name(3,6,"arg_test"))
        print(db.update_argument_is_signed(6,1))
        print(db.update_argument_offset(6,1))
        print(db.update_argument_mul(6,1))
        print(db.update_argument_div(6,1))
        print(db.get_argument_description(6))
        print(db.get_argument_offset(6))
        print(db.get_argument_mul(6))
        print(db.get_argument_div(6))
        """
         