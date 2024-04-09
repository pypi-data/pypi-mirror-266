import can
import logging

def _get_message(msg):
    """
    Retorna el missatge del bus CAN.

    Aquest mètode és privat i només ha de ser utilitzat per crides estricteament funcionals a la classe Bus.

    :param msg: Missatge a retornar.
    :type msg: can.Message
    :return: Objecte PCANBus que conté informació del missatge.
    :rtype: PCANBus (object)
    """
    return msg


class Bus(object):
    """
    La classe Bus permet establir una connexió en un canal de comunicació CAN assignant un identificador a si mateixa. De moment, aquesta classe només accepta el controlador utilitzat per PEAK Systems. És possible que en futures actualitzacions es puguin acceptar altres interfícies. Si us plau, tingueu-ho en compte abans d'utilitzar l'aplicació.\n\r
    
    .. note::
        Tingueu en compte que actualment només s'accepta el controlador PCAN. Podeu obtenir més informació sobre com instal·lar el controlador PCAN al següent enllaç `<https://www.peak-system.com/Drivers.523.0.html?&L=1>`_.
    """
    def __init__(self, bustype="pcan", channel="1", bitrate=250000, filters=None):
        """
        Crea una nova instància de la classe Bus. La seva inicialització permet modificar el canal, la taxa de dades i afegir filtres al canal de comunicació.

        :param bustype: Estableix el controlador utilitzat per establir la comunicació.
        :type bustype: str
        :param channel: Estableix el número de dispositiu.
        :type channel: str
        :param bitrate: Estableix la velocitat de bauds de la comunicació.
        :type bitrate: int
        :param filters: Estableix els filtres de comunicació sol·licitats.
        :type filters: list (or None)

        .. note::
            Aquesta funció crea per defecte una instància del controlador de comunicacions CAN de PCAN. Actualment, només és compatible amb el controlador PCAN. Per obtenir més informació sobre com instal·lar el controlador PCAN visiteu el següent enllaç:
            `<https://www.peak-system.com/Drivers.523.0.html?&L=1>`_

        .. warning::
            Tingueu en compte que l'ús de canals incorrectes o la configuració inadequada del controlador poden provocar mal funcionament del programa i danys en els dispositius connectats.

        .. seealso::
            * :py:func:`_get_message`: Funció privada que conté les dades del missatge enviat o rebut.
            * :py:class:`can.Bus`: Classe de llibreria ``python-can`` que proporciona una API genèrica per comunicar dispositius amb controladors CAN. Podeu consultar la seva documentació `en aquest enllaç <https://python-can.readthedocs.io/en/stable/>`_.

        """
        logging.info("Initializing CANbus...")
        self.bus = can.Bus(channel="PCAN_USBBUS"+channel, bustype=bustype, bitrate=bitrate)
        self.bus.set_filters(filters)
        logging.info("Creating a buffer reader...")
        self.buffer = can.BufferedReader()
        logging.info("Inizializing notifier...")
        self.notifier = can.Notifier(self.bus, [_get_message, self.buffer])

    def send_message(self, message_id=0x1, mesg=[1,2,3,4,5,6,7,8], extended=False, remote=False):
        """
        Aquest mètode permet transmetre un missatge a través del bus CAN establert.

        :param message_id: Identificador del missatge.
        :type message_id: int
        :param mesg: Conté els valors de tots els bytes (0-255) separats per comes.
        :type mesg: list[int]
        :param extended: Indica si s'utilitza el protocol estès.
        :type extended: bool
        :param remote: Indica si s'està enviant una trama de solicitud de dades.
        :type remote: bool
        :return: True si s'ha transmès correctament el missatge, del contrari retorna False.
        :rtype: bool

        .. note::
            Aquest mètode intenta enviar un missatge CAN amb l'identificador i les dades especificades.
            Si es produeix un error durant l'enviament, s'informa amb un valor False.

        .. warning::
            El valor per defecte de 'message_id' és 0x1. No és recomanable utilitzar-lo a menys que es disposi d'un identificador específic.
        """
        try:
            msg = can.Message(arbitration_id=message_id, data=mesg, is_extended_id=extended, is_remote_frame=remote)
            try:
                self.bus.send(msg)
                return True
            except can.CanError:
                return False
        except:
            return False
        
    def read_input(self, timeout:float = 0.5):
        """
        Aquest mètode permet obtenir un missatge del bus CAN establert, seguint els filtres especificats durant la inicialització del bus.

        .. warning::
            Aquesta funció no és bloquejant. En un futur és possible que aquesta funció esdevingui bloquejant. Si us plau, tingueu en compte això quan realitzeu accions en altres aplicacions.

        :return: Objecte que conté les dades del missatge del frame CAN.
        :rtype: can.Message (object)
        """
        return self.buffer.get_message(timeout)

    def flush_buffer(self):
        """
        Aquest mètode permet netejar el buffer establert del bus CAN.

        :return: None
        """
        msg = self.buffer.get_message()
        while msg is not None:
            msg = self.buffer.get_message()
            
    def cleanup(self):
        """
        Aquest mètode finalitza la comunicació establerta a través de CAN.

        :return: None
        """
        # Atura el notifier que estem usant per llegir dades del bus
        self.notifier.stop()
        # Trenca la connexió del bus
        self.bus.shutdown()
    
        
if __name__ == "__main__":
    #pcan = Bus(filters=[{"can_id": 0x150, "can_mask": 0xFF9, "extended": False},])
    pcan = Bus(bitrate=250000)
    id_msg = 0x100
    payload_msg = [1,2,3,4,5,6,7,8]
    pcan.flush_buffer()
    for e in list(range(0,100)):
        if pcan.send_message(id_msg, payload_msg):
            print("Success!")
        else:
            print("Failed!")
    """
    try:
        pcan.flush_buffer()
        while(True):
            msg_received = pcan.read_input()
            if msg_received != None:
                print(list(msg_received.data))
                print(msg_received)
    except:
        logging.info("Sortint de l'aplicatiu.")
        pcan.cleanup()
    """