"""Entidades generales y clientes del sistema."""
from abc import ABC, abstractmethod  # ABC y abstractmethod permiten definir clases abstractas
import re                            # Expresiones regulares para validar texto

from excepciones import DatoInvalidoError  # Error propio para datos que no cumplen reglas


class Entidad(ABC):
    """Clase abstracta que representa cualquier entidad identificable del sistema."""

    def __init__(self, identificador):
        # bool es subclase de int en Python; se rechaza explícitamente (True no es un ID válido)
        if isinstance(identificador, bool) or identificador is None:
            raise DatoInvalidoError("El identificador es obligatorio y no puede ser booleano.")
        texto = str(identificador).strip()  # Normaliza a texto sin espacios laterales
        if not texto:  # Cadena vacía o solo espacios
            raise DatoInvalidoError("El identificador es obligatorio.")
        self._identificador = texto  # Atributo protegido: solo se lee mediante la propiedad

    @property
    def identificador(self):
        """Identificador de solo lectura (no tiene setter, no se puede modificar)."""
        return self._identificador

    @abstractmethod
    def describir(self):
        """Devuelve una descripción de la entidad (cada subclase la implementa)."""

    def __str__(self):
        return self.describir()  # str(objeto) reutiliza el método polimórfico describir()


class Cliente(Entidad):
    """Cliente con datos personales encapsulados y validados."""

    # Letras (con tildes y ñ), espacios, apóstrofes, puntos y guiones
    _PATRON_NOMBRE = re.compile(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ' .\-]+")
    # Formato básico de correo: algo@dominio.extensión, sin espacios
    _PATRON_CORREO = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")
    # Caracteres permitidos en un teléfono (dígitos, espacios, +, -, paréntesis)
    _PATRON_TELEFONO = re.compile(r"[\d\s+\-()]+")

    def __init__(self, identificador, nombre, correo, telefono):
        super().__init__(identificador)  # Valida y guarda el identificador en Entidad
        self.nombre = nombre      # Pasa por el setter: se valida automáticamente
        self.correo = correo      # Pasa por el setter: se valida automáticamente
        self.telefono = telefono  # Pasa por el setter: se valida automáticamente

    @property
    def nombre(self):
        """Nombre del cliente (lectura)."""
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        # Debe ser texto, tener al menos 3 caracteres útiles y solo caracteres de nombre
        if (not isinstance(valor, str) or len(valor.strip()) < 3
                or not self._PATRON_NOMBRE.fullmatch(valor.strip())):
            raise DatoInvalidoError(
                "El nombre debe ser texto de al menos 3 caracteres y solo contener letras.")
        self._nombre = valor.strip().title()  # Se guarda normalizado: "ana pérez" -> "Ana Pérez"

    @property
    def correo(self):
        """Correo electrónico del cliente (lectura)."""
        return self._correo

    @correo.setter
    def correo(self, valor):
        # Se limpia primero y luego se valida el formato con la expresión regular
        if not isinstance(valor, str) or not self._PATRON_CORREO.fullmatch(valor.strip()):
            raise DatoInvalidoError("El correo electrónico no tiene un formato válido.")
        self._correo = valor.strip().lower()  # Los correos se almacenan en minúscula

    @property
    def telefono(self):
        """Teléfono del cliente, solo dígitos (lectura)."""
        return self._telefono

    @telefono.setter
    def telefono(self, valor):
        if isinstance(valor, bool) or not isinstance(valor, (str, int)):
            raise DatoInvalidoError("El teléfono debe ser texto o número.")
        texto = str(valor).strip()  # Se trabaja siempre con texto
        if not self._PATRON_TELEFONO.fullmatch(texto):  # Rechaza letras u otros símbolos
            raise DatoInvalidoError("El teléfono solo puede contener dígitos, espacios, + - ( ).")
        digitos = re.sub(r"\D", "", texto)  # Elimina todo lo que no sea dígito
        if not 7 <= len(digitos) <= 15:  # Longitud razonable según estándares telefónicos
            raise DatoInvalidoError("El teléfono debe contener entre 7 y 15 dígitos.")
        self._telefono = digitos  # Se guarda solo con dígitos

    def describir(self):
        """Implementación polimórfica de Entidad.describir()."""
        return f"Cliente {self.identificador}: {self.nombre} ({self.correo})"
