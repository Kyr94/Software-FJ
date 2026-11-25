"""Servicios abstractos y especializados de Software FJ."""
from abc import ABC, abstractmethod  # Soporte de clases abstractas
import math                          # math.isfinite descarta NaN e infinito

from excepciones import (
    DatoInvalidoError, ServicioNoDisponibleError, CalculoInconsistenteError,
)
from entidades import Entidad  # Servicio también es una entidad identificable


def _es_numero(valor):
    """True si el valor es int o float real (excluye bool, NaN e infinito)."""
    return (isinstance(valor, (int, float)) and not isinstance(valor, bool)
            and math.isfinite(valor))


def _aplicar_ajustes(subtotal, impuesto, descuento):
    """Aplica descuento y luego impuesto (ambos en porcentaje) con validación estricta."""
    if not _es_numero(impuesto) or not 0 <= impuesto <= 100:  # Impuesto: 0 a 100 %
        raise DatoInvalidoError("El impuesto debe ser un número entre 0 y 100.")
    if not _es_numero(descuento) or not 0 <= descuento <= 100:  # Descuento: 0 a 100 %
        raise DatoInvalidoError("El descuento debe ser un número entre 0 y 100.")
    total = subtotal * (1 - descuento / 100) * (1 + impuesto / 100)  # Fórmula del total
    if not math.isfinite(total) or total <= 0:  # Un total <= 0 no tiene sentido comercial
        raise CalculoInconsistenteError(f"El cálculo produjo un valor inconsistente: {total}.")
    return round(total, 2)  # Se redondea a dos decimales


class Servicio(Entidad, ABC):
    """Clase abstracta base para los servicios (hereda de Entidad)."""

    def __init__(self, codigo, nombre, tarifa_base, disponible=True):
        super().__init__(codigo)  # El código es el identificador (validado en Entidad)
        self._identificador = self._identificador.upper()  # Los códigos se guardan en mayúscula
        if not isinstance(nombre, str) or len(nombre.strip()) < 3:  # Nombre estricto
            raise DatoInvalidoError("El nombre del servicio debe tener al menos 3 caracteres.")
        if not _es_numero(tarifa_base) or tarifa_base <= 0:  # Tarifa positiva
            raise DatoInvalidoError("La tarifa base debe ser un número positivo.")
        self._nombre = nombre.strip()        # Nombre normalizado
        self._tarifa_base = float(tarifa_base)  # Tarifa por unidad (hora, día o sesión)
        self._disponible = bool(disponible)  # Estado de disponibilidad

    # ----- Propiedades de solo lectura (encapsulación) -----
    @property
    def codigo(self):
        """Alias de identificador: el código del servicio."""
        return self.identificador

    @property
    def nombre(self):
        return self._nombre

    @property
    def tarifa_base(self):
        return self._tarifa_base

    @property
    def disponible(self):
        return self._disponible

    # ----- Gestión de disponibilidad -----
    def activar(self):
        """Marca el servicio como disponible."""
        self._disponible = True

    def desactivar(self):
        """Marca el servicio como no disponible."""
        self._disponible = False

    def validar_disponibilidad(self):
        """Lanza ServicioNoDisponibleError si el servicio está desactivado."""
        if not self._disponible:
            raise ServicioNoDisponibleError(f"El servicio {self.nombre} no está disponible.")

    # ----- Métodos que cada servicio especializado DEBE sobrescribir (polimorfismo) -----
    @abstractmethod
    def validar_parametros(self, cantidad):
        """Valida la cantidad/duración según las reglas propias del servicio."""

    @abstractmethod
    def calcular_costo_base(self, cantidad):
        """Devuelve el subtotal (sin impuesto ni descuento) según el tipo de servicio."""

    @abstractmethod
    def describir(self):
        """Describe el servicio."""

    # ----- Cálculo con sobrecarga simulada -----
    def calcular_costo(self, cantidad, *args, impuesto=None, descuento=None):
        """Calcula el costo total. Python no tiene sobrecarga por firma, por lo que
        se simulan las variantes con parámetros opcionales (posicionales o con nombre):

            calcular_costo(2)                      -> sin impuesto ni descuento
            calcular_costo(2, 19)                  -> con impuesto del 19 %
            calcular_costo(2, 19, 10)              -> con impuesto 19 % y descuento 10 %
            calcular_costo(2, descuento=10)        -> solo descuento
            calcular_costo(2, impuesto=19, descuento=10)
        """
        if len(args) > 2:  # Solo se admiten (impuesto, descuento) como posicionales
            raise DatoInvalidoError("Se admiten como máximo impuesto y descuento.")
        if len(args) >= 1:  # Primer posicional = impuesto
            if impuesto is not None:  # No se puede dar dos veces
                raise DatoInvalidoError("El impuesto fue indicado dos veces.")
            impuesto = args[0]
        if len(args) == 2:  # Segundo posicional = descuento
            if descuento is not None:
                raise DatoInvalidoError("El descuento fue indicado dos veces.")
            descuento = args[1]
        impuesto = 0.0 if impuesto is None else impuesto      # Valor por defecto
        descuento = 0.0 if descuento is None else descuento   # Valor por defecto
        self.validar_parametros(cantidad)                      # Regla propia del servicio
        subtotal = self.calcular_costo_base(cantidad)          # Cálculo polimórfico
        return _aplicar_ajustes(subtotal, impuesto, descuento)  # Ajustes comunes

    def calcular_costo_con_impuesto(self, cantidad, impuesto):
        """Variante explícita: costo con impuesto."""
        return self.calcular_costo(cantidad, impuesto=impuesto)

    def calcular_costo_con_descuento(self, cantidad, descuento):
        """Variante explícita: costo con descuento."""
        return self.calcular_costo(cantidad, descuento=descuento)


class ReservaSala(Servicio):
    """Reserva de salas por horas (admite medias horas, de 0.5 a 12 h)."""

    def __init__(self, codigo, nombre, tarifa_base, capacidad=10, disponible=True):
        super().__init__(codigo, nombre, tarifa_base, disponible)  # Datos comunes
        if isinstance(capacidad, bool) or not isinstance(capacidad, int) or capacidad <= 0:
            raise DatoInvalidoError("La capacidad de la sala debe ser un entero positivo.")
        self._capacidad = capacidad  # Personas que caben en la sala

    def validar_parametros(self, horas):
        if not _es_numero(horas) or not 0.5 <= horas <= 12 or (horas * 2) % 1 != 0:
            raise DatoInvalidoError(
                "Las horas de sala deben estar entre 0.5 y 12, en pasos de media hora.")

    def calcular_costo_base(self, horas):
        return self._tarifa_base * horas  # Tarifa por hora x horas

    def describir(self):
        return (f"Reserva de sala por hora (capacidad {self._capacidad}). "
                f"Tarifa: ${self.tarifa_base:,.0f}")


class AlquilerEquipo(Servicio):
    """Alquiler de equipos por día (1 a 30 días) con seguro obligatorio."""

    def __init__(self, codigo, nombre, tarifa_base, porcentaje_seguro=5, disponible=True):
        super().__init__(codigo, nombre, tarifa_base, disponible)
        if not _es_numero(porcentaje_seguro) or not 0 <= porcentaje_seguro <= 50:
            raise DatoInvalidoError("El seguro debe ser un porcentaje entre 0 y 50.")
        self._porcentaje_seguro = porcentaje_seguro  # Recargo propio de este servicio

    def validar_parametros(self, dias):
        if isinstance(dias, bool) or not isinstance(dias, int) or not 1 <= dias <= 30:
            raise DatoInvalidoError("Los días de alquiler deben ser un entero entre 1 y 30.")

    def calcular_costo_base(self, dias):
        # Tarifa diaria x días + recargo de seguro (regla distinta a la de las otras clases)
        return self._tarifa_base * dias * (1 + self._porcentaje_seguro / 100)

    def describir(self):
        return (f"Alquiler de equipos por día (seguro {self._porcentaje_seguro}%). "
                f"Tarifa: ${self.tarifa_base:,.0f}")


class AsesoriaEspecializada(Servicio):
    """Asesoría especializada por sesión (1 a 10 sesiones)."""

    def __init__(self, codigo, nombre, tarifa_base, especialidad="General", disponible=True):
        super().__init__(codigo, nombre, tarifa_base, disponible)
        if not isinstance(especialidad, str) or not especialidad.strip():
            raise DatoInvalidoError("La especialidad es obligatoria.")
        self._especialidad = especialidad.strip()  # Área de la asesoría

    def validar_parametros(self, sesiones):
        if isinstance(sesiones, bool) or not isinstance(sesiones, int) or not 1 <= sesiones <= 10:
            raise DatoInvalidoError("El número de sesiones debe ser un entero entre 1 y 10.")

    def calcular_costo_base(self, sesiones):
        return self._tarifa_base * sesiones  # Tarifa por sesión x sesiones

    def describir(self):
        return (f"Asesoría especializada en {self._especialidad} por sesión. "
                f"Tarifa: ${self.tarifa_base:,.0f}")
