"""Configuración centralizada del archivo de logs (eventos y errores)."""
import logging  # Módulo estándar de Python para registrar eventos
import os       # Para construir rutas independientes del sistema operativo

# La ruta se calcula a partir de la ubicación de este archivo, no de la carpeta
# desde la que se ejecuta el programa; así eventos.log siempre queda junto al código.
RUTA_LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "eventos.log")


def obtener_logger():
    """Devuelve el logger del sistema, creándolo una sola vez."""
    logger = logging.getLogger("software_fj")  # Logger con nombre propio
    if not logger.handlers:  # Evita duplicar manejadores si se llama varias veces
        logger.setLevel(logging.INFO)  # Se registran eventos INFO, WARNING y ERROR
        manejador = logging.FileHandler(RUTA_LOG, mode="a", encoding="utf-8")  # Escribe en el archivo
        manejador.setFormatter(
            logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")  # Fecha | nivel | mensaje
        )
        logger.addHandler(manejador)  # Conecta el manejador al logger
        logger.propagate = False  # No imprime en consola: la consola es solo para la demostración
    return logger


def reiniciar_log():
    """Vacía el archivo de logs (se usa al iniciar la demostración para tener evidencia limpia)."""
    open(RUTA_LOG, "w", encoding="utf-8").close()  # Abrir en modo "w" trunca el archivo


def describir_error(error):
    """Devuelve el error y toda su cadena de causas (encadenamiento de excepciones)."""
    partes = [f"{type(error).__name__}: {error}"]  # Primer eslabón: el error actual
    causa = error.__cause__  # __cause__ se llena con 'raise ... from ...'
    while causa is not None:  # Recorre la cadena hasta el error original
        partes.append(f"causa -> {type(causa).__name__}: {causa}")
        causa = causa.__cause__
    return " | ".join(partes)  # Una sola línea legible para el log
