"""Clase Reserva y procesamiento de sus estados."""
from datetime import datetime  # Para registrar la fecha de creación

from excepciones import (
    ErrorSistema, ReservaInvalidaError, OperacionNoPermitidaError, DatoInvalidoError,
)
from entidades import Cliente, Entidad
from servicios import Servicio
from registro import obtener_logger, describir_error

logger = obtener_logger()  # Logger compartido del sistema


class Reserva(Entidad):
    """Integra cliente, servicio, duración y estado."""

    ESTADOS = ("PENDIENTE", "CONFIRMADA", "CANCELADA")  # Estados posibles

    def __init__(self, codigo, cliente, servicio, duracion):
        super().__init__(codigo)  # Valida el código de la reserva
        if cliente is None or servicio is None:  # Parámetros obligatorios
            raise ReservaInvalidaError("La reserva requiere cliente y servicio.")
        if not isinstance(cliente, Cliente) or not isinstance(servicio, Servicio):
            raise ReservaInvalidaError("El cliente o el servicio no son objetos válidos.")
        try:
            servicio.validar_parametros(duracion)  # La duración depende del tipo de servicio
        except DatoInvalidoError as error:
            # Encadenamiento: se conserva el error original como causa (raise ... from ...)
            raise ReservaInvalidaError(
                f"Duración inválida para la reserva {self.identificador}.") from error
        self._cliente = cliente          # Cliente que reserva
        self._servicio = servicio        # Servicio reservado
        self._duracion = duracion        # Horas, días o sesiones según el servicio
        self._estado = "PENDIENTE"       # Toda reserva nace pendiente
        self._total = None               # Se calcula al confirmar
        self.fecha_creacion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ----- Propiedades de solo lectura -----
    @property
    def codigo(self):
        return self.identificador

    @property
    def cliente(self):
        return self._cliente

    @property
    def servicio(self):
        return self._servicio

    @property
    def duracion(self):
        return self._duracion

    @property
    def estado(self):
        return self._estado

    @property
    def total(self):
        return self._total

    # ----- Operaciones sobre el estado -----
    def confirmar(self, impuesto=0, descuento=0):
        """Confirma la reserva y calcula su total. Solo desde el estado PENDIENTE."""
        if self._estado != "PENDIENTE":
            raise OperacionNoPermitidaError("Solo se pueden confirmar reservas pendientes.")
        self._servicio.validar_disponibilidad()  # Puede lanzar ServicioNoDisponibleError
        # Se calcula ANTES de cambiar el estado: si falla, la reserva queda intacta
        total = self._servicio.calcular_costo(self._duracion, impuesto, descuento)
        self._total = total        # Guarda el total calculado
        self._estado = "CONFIRMADA"  # Solo ahora cambia el estado
        logger.info("Reserva confirmada: %s | total %s", self.codigo, total)
        return total

    def cancelar(self):
        """Cancela la reserva (desde PENDIENTE o CONFIRMADA)."""
        if self._estado == "CANCELADA":
            raise OperacionNoPermitidaError("La reserva ya está cancelada.")
        self._estado = "CANCELADA"
        logger.info("Reserva cancelada: %s", self.codigo)
        return self._estado

    def procesar(self, impuesto=0, descuento=0):
        """Procesa la reserva usando try/except/else/finally y encadenamiento de errores."""
        try:
            total = self.confirmar(impuesto, descuento)  # Intento principal
        except ErrorSistema as error:
            # Error controlado: se registra y se relanza con contexto (from error)
            logger.error("Fallo al procesar %s | %s", self.codigo, describir_error(error))
            raise ReservaInvalidaError(
                f"No fue posible procesar la reserva {self.codigo}.") from error
        except Exception as error:
            # Error inesperado: se registra con traceback completo y se encapsula
            logger.error("Error inesperado al procesar %s | %s", self.codigo,
                         describir_error(error), exc_info=True)
            raise ReservaInvalidaError(
                f"Error inesperado al procesar la reserva {self.codigo}.") from error
        else:
            # Se ejecuta solo si NO hubo excepción
            logger.info("Procesamiento exitoso de %s", self.codigo)
            return total
        finally:
            # Se ejecuta SIEMPRE (con o sin error): deja constancia del cierre del intento
            logger.info("Intento de procesamiento finalizado: %s (estado %s)",
                        self.codigo, self._estado)

    def describir(self):
        return (f"Reserva {self.codigo} | {self._cliente.nombre} | "
                f"{self._servicio.nombre} | {self._estado} | Total: {self._total}")
