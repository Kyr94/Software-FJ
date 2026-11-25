"""Demostración de Software FJ: 26 operaciones válidas e inválidas sin detener el programa."""
import sys  # Para ajustar la codificación de la consola

from entidades import Cliente
from servicios import ReservaSala, AlquilerEquipo, AsesoriaEspecializada
from reservas import Reserva
from gestor import GestorSistema
from excepciones import ErrorSistema
from registro import obtener_logger, reiniciar_log, describir_error

logger = obtener_logger()  # Logger compartido (escribe en eventos.log)


def ejecutar_operacion(numero, descripcion, accion):
    """Ejecuta una operación y garantiza que un error NUNCA detenga la demostración."""
    print(f"\nOPERACIÓN {numero}: {descripcion}")
    try:
        resultado = accion()  # Se ejecuta la operación recibida como función
    except ErrorSistema as error:
        # Error controlado de la aplicación: se registra con toda su cadena de causas
        logger.error("Operación %s fallida (%s) | %s", numero, descripcion, describir_error(error))
        print(f"ERROR CONTROLADO: {error}")
        if error.__cause__ is not None:  # Muestra el encadenamiento si existe
            print(f"  Causa original: {error.__cause__}")
    except Exception as error:
        # Error inesperado (no previsto): se registra con traceback y el sistema sigue vivo
        logger.error("Operación %s con ERROR INESPERADO (%s) | %s", numero, descripcion,
                     describir_error(error), exc_info=True)
        print(f"ERROR INESPERADO CONTROLADO ({type(error).__name__}): {error}")
    else:
        # Solo se ejecuta si no hubo excepción
        logger.info("Operación %s exitosa: %s", numero, descripcion)
        print(f"RESULTADO: {resultado}")
    finally:
        # Siempre se ejecuta: marca el final de la operación
        print("Fin de la operación.")


def main():
    """Define y ejecuta las operaciones de la demostración."""
    reiniciar_log()  # Evidencia limpia en cada ejecución
    sistema = GestorSistema()  # Contenedor de las listas internas

    # ---------------- Clientes ----------------
    def cliente_valido():
        return sistema.registrar_cliente(
            Cliente("C001", "Ana Pérez", "ana@email.com", "300 123 4567")).describir()

    def cliente_invalido():  # Nombre corto, correo y teléfono inválidos
        return Cliente("C002", "Al", "correo-invalido", "123")

    def segundo_cliente():
        return sistema.registrar_cliente(
            Cliente("C003", "Carlos Gómez", "carlos@email.com", "3107654321")).describir()

    def cliente_parametros_faltantes():  # Faltan correo y teléfono
        return sistema.crear_cliente(identificador="C010", nombre="Pedro Ruiz")

    # ---------------- Servicios ----------------
    def sala_valida():
        return sistema.registrar_servicio(
            ReservaSala("SALA", "Sala de reuniones", 50000, capacidad=12)).describir()

    def equipo_valido():
        return sistema.registrar_servicio(
            AlquilerEquipo("EQ", "Alquiler de portátil", 80000)).describir()

    def asesoria_valida():
        return sistema.registrar_servicio(
            AsesoriaEspecializada("ASE", "Asesoría de software", 120000, "Desarrollo")).describir()

    def servicio_tarifa_negativa():
        return ReservaSala("MAL", "Sala inválida", -500)

    def servicio_sin_codigo():
        return AlquilerEquipo("  ", "Equipo sin código", 10000)

    # ---------------- Reservas ----------------
    def reserva_exitosa():  # Crea y procesa con impuesto 19 % y descuento 10 %
        reserva = sistema.crear_reserva("R001", "C001", "SALA", 2)
        total = reserva.procesar(19, 10)
        return f"{reserva.describir()} | Total calculado: ${total:,.2f}"

    def reserva_equipo():
        return f"Reserva creada: {sistema.crear_reserva('R002', 'C003', 'EQ', 3).codigo}"

    def reserva_asesoria():
        return f"Reserva creada: {sistema.crear_reserva('R003', 'C001', 'ASE', 1).codigo}"

    def reserva_sin_cliente():
        return Reserva("R004", None, sistema.buscar_servicio("SALA"), 1)

    def reserva_cliente_inexistente():
        return sistema.crear_reserva("R004", "C999", "SALA", 1)

    def reserva_duracion_invalida():  # 2.5 sesiones no es un entero
        return sistema.crear_reserva("R004", "C001", "ASE", 2.5)

    def confirmar_equipo():  # Variante posicional: solo impuesto
        return sistema.buscar_reserva("R002").confirmar(19)

    def cancelar_asesoria():
        return sistema.buscar_reserva("R003").cancelar()

    def confirmar_cancelada():  # procesar() encadena el error original
        return sistema.buscar_reserva("R003").procesar()

    def cancelar_dos_veces():
        return sistema.buscar_reserva("R003").cancelar()

    def servicio_no_disponible():
        sistema.registrar_servicio(
            ReservaSala("VIP", "Sala VIP", 90000, capacidad=6, disponible=False))
        reserva = sistema.crear_reserva("R005", "C003", "VIP", 1)
        return reserva.procesar()

    # ---------------- Cálculos ----------------
    def calculo_impuesto_invalido():
        return sistema.buscar_servicio("SALA").calcular_costo(2, impuesto=150)

    def variantes_de_calculo():  # Demuestra la sobrecarga simulada
        sala = sistema.buscar_servicio("SALA")
        return (f"base={sala.calcular_costo(2)} | con impuesto={sala.calcular_costo(2, 19)} | "
                f"con descuento={sala.calcular_costo_con_descuento(2, 10)} | "
                f"completo={sala.calcular_costo(2, 19, 10)}")

    def polimorfismo():  # Cada servicio calcula distinto con la misma llamada
        return " | ".join(f"{s.codigo}: {s.calcular_costo(1):,.0f}"
                          for s in sistema.servicios if s.disponible)

    # ---------------- Otros ----------------
    def duplicar_cliente():
        return sistema.registrar_cliente(
            Cliente("C001", "Otra Persona", "otra@email.com", "3001112233"))

    def error_inesperado():  # buscar devuelve None y None no tiene .nombre -> AttributeError
        return sistema.buscar_cliente("NO_EXISTE").nombre

    def reporte():
        return "\n".join(sistema.listar_reservas())

    # (descripción, función) en el orden de ejecución
    operaciones = [
        ("Registrar cliente válido", cliente_valido),
        ("Intentar registrar cliente con datos inválidos", cliente_invalido),
        ("Registrar segundo cliente válido", segundo_cliente),
        ("Intentar crear cliente con parámetros faltantes", cliente_parametros_faltantes),
        ("Crear servicio de reserva de sala", sala_valida),
        ("Crear servicio de alquiler de equipos", equipo_valido),
        ("Crear servicio de asesoría especializada", asesoria_valida),
        ("Intentar crear servicio con tarifa negativa", servicio_tarifa_negativa),
        ("Intentar crear servicio sin código", servicio_sin_codigo),
        ("Crear y procesar reserva de sala con impuesto y descuento", reserva_exitosa),
        ("Crear reserva de alquiler de equipo", reserva_equipo),
        ("Crear reserva de asesoría", reserva_asesoria),
        ("Intentar crear reserva sin cliente", reserva_sin_cliente),
        ("Intentar reservar con un cliente no registrado", reserva_cliente_inexistente),
        ("Intentar reservar con duración inválida", reserva_duracion_invalida),
        ("Confirmar reserva de alquiler de equipo (con impuesto)", confirmar_equipo),
        ("Cancelar reserva de asesoría", cancelar_asesoria),
        ("Intentar procesar una reserva cancelada", confirmar_cancelada),
        ("Intentar cancelar dos veces la misma reserva", cancelar_dos_veces),
        ("Intentar reservar un servicio no disponible", servicio_no_disponible),
        ("Intentar cálculo con impuesto inválido", calculo_impuesto_invalido),
        ("Variantes de cálculo de costo (sobrecarga)", variantes_de_calculo),
        ("Polimorfismo: mismo método, costo distinto por servicio", polimorfismo),
        ("Intentar registrar cliente duplicado", duplicar_cliente),
        ("Provocar un error inesperado (AttributeError)", error_inesperado),
        ("Consultar reporte de reservas", reporte),
    ]

    print("=" * 65)
    print("SISTEMA INTEGRAL DE GESTIÓN - SOFTWARE FJ")
    print("Demostración de operaciones y manejo de excepciones")
    print("=" * 65)
    for numero, (descripcion, accion) in enumerate(operaciones, start=1):
        ejecutar_operacion(numero, descripcion, accion)  # Un fallo no corta el ciclo

    print("\nDemostración finalizada: el sistema siguió activo ante todos los errores.")
    print("Revise el archivo eventos.log.")
    print(f"Clientes registrados: {len(sistema.clientes)}")
    print(f"Servicios registrados: {len(sistema.servicios)}")
    print(f"Reservas registradas: {len(sistema.reservas)}")


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # Evita errores de tildes en consolas Windows
    except (AttributeError, OSError):
        pass  # Si la consola no lo permite, se continúa con la codificación por defecto
    main()
