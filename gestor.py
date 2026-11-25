"""Gestor principal: listas internas (sin base de datos) y registro de eventos."""
from excepciones import (
    DatoInvalidoError, ParametroFaltanteError, ReservaInvalidaError,
)
from entidades import Cliente
from reservas import Reserva
from registro import obtener_logger

logger = obtener_logger()  # Logger compartido


class GestorSistema:
    """Administra clientes, servicios y reservas en listas internas."""

    def __init__(self):
        self.clientes = []   # Lista de objetos Cliente
        self.servicios = []  # Lista de objetos Servicio
        self.reservas = []   # Lista de objetos Reserva

    # ----- Creación con verificación de parámetros obligatorios -----
    def crear_cliente(self, **datos):
        """Crea y registra un cliente; avisa qué parámetros faltan."""
        requeridos = ("identificador", "nombre", "correo", "telefono")
        faltantes = [campo for campo in requeridos if campo not in datos]  # Campos ausentes
        if faltantes:
            raise ParametroFaltanteError(f"Faltan parámetros del cliente: {', '.join(faltantes)}.")
        return self.registrar_cliente(Cliente(**datos))  # Crea y registra

    # ----- Registro en las listas internas -----
    def registrar_cliente(self, cliente):
        if self.buscar_cliente(cliente.identificador) is not None:  # Evita duplicados
            raise DatoInvalidoError("Ya existe un cliente con ese identificador.")
        self.clientes.append(cliente)
        logger.info("Cliente registrado: %s", cliente.identificador)
        return cliente

    def registrar_servicio(self, servicio):
        if self.buscar_servicio(servicio.codigo) is not None:
            raise DatoInvalidoError("Ya existe un servicio con ese código.")
        self.servicios.append(servicio)
        logger.info("Servicio registrado: %s", servicio.codigo)
        return servicio

    def registrar_reserva(self, reserva):
        if self.buscar_reserva(reserva.codigo) is not None:
            raise DatoInvalidoError("Ya existe una reserva con ese código.")
        self.reservas.append(reserva)
        logger.info("Reserva creada: %s", reserva.codigo)
        return reserva

    def crear_reserva(self, codigo, id_cliente, codigo_servicio, duracion):
        """Busca cliente y servicio registrados y crea la reserva."""
        cliente = self.buscar_cliente(id_cliente)
        if cliente is None:  # El cliente debe existir en el sistema
            raise ReservaInvalidaError(f"El cliente {id_cliente} no está registrado.")
        servicio = self.buscar_servicio(codigo_servicio)
        if servicio is None:  # El servicio debe existir en el sistema
            raise ReservaInvalidaError(f"El servicio {codigo_servicio} no está registrado.")
        return self.registrar_reserva(Reserva(codigo, cliente, servicio, duracion))

    # ----- Búsquedas (devuelven None si no existe) -----
    def buscar_cliente(self, identificador):
        return next((c for c in self.clientes if c.identificador == str(identificador).strip()), None)

    def buscar_servicio(self, codigo):
        return next((s for s in self.servicios if s.codigo == str(codigo).strip().upper()), None)

    def buscar_reserva(self, codigo):
        return next((r for r in self.reservas if r.codigo == str(codigo).strip()), None)

    # ----- Reportes -----
    def listar_reservas(self):
        return [r.describir() for r in self.reservas]
