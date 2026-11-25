"""Excepciones personalizadas del sistema Software FJ.

Todas heredan de ErrorSistema, de modo que la aplicación puede capturar
cualquier error controlado con un solo bloque ``except ErrorSistema``.
"""


class ErrorSistema(Exception):
    """Excepción base para todos los errores controlados de la aplicación."""


class DatoInvalidoError(ErrorSistema):
    """Se genera cuando un dato no cumple las validaciones (tipo, rango o formato)."""


class ParametroFaltanteError(ErrorSistema):
    """Se genera cuando falta un parámetro obligatorio al crear u operar un objeto."""


class ServicioNoDisponibleError(ErrorSistema):
    """Se genera cuando se intenta usar un servicio marcado como no disponible."""


class ReservaInvalidaError(ErrorSistema):
    """Se genera cuando una reserva no puede crearse o procesarse."""


class OperacionNoPermitidaError(ErrorSistema):
    """Se genera cuando el estado actual de un objeto no permite la operación pedida."""


class CalculoInconsistenteError(ErrorSistema):
    """Se genera cuando un cálculo produce un resultado absurdo (negativo, cero o no finito)."""
