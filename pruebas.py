"""Pruebas automáticas (unittest) de las reglas principales de Software FJ.

Ejecutar con:  python -m unittest pruebas -v
"""
import unittest  # Framework de pruebas incluido en Python

from entidades import Entidad, Cliente
from servicios import Servicio, ReservaSala, AlquilerEquipo, AsesoriaEspecializada
from reservas import Reserva
from gestor import GestorSistema
from excepciones import (
    DatoInvalidoError, ParametroFaltanteError, ServicioNoDisponibleError,
    ReservaInvalidaError, OperacionNoPermitidaError, CalculoInconsistenteError,
)


class PruebasSistema(unittest.TestCase):
    def setUp(self):  # Se ejecuta antes de cada prueba
        self.cliente = Cliente("C1", "ana pérez", " ANA@Email.com ", "300-123-4567")
        self.sala = ReservaSala("sala", "Sala de reuniones", 50000)
        self.equipo = AlquilerEquipo("eq", "Portátil", 80000)
        self.asesoria = AsesoriaEspecializada("ase", "Asesoría", 120000)

    def test_clases_abstractas_no_se_instancian(self):
        with self.assertRaises(TypeError):
            Entidad("X")
        with self.assertRaises(TypeError):
            Servicio("X", "Algo", 10)

    def test_cliente_normaliza_y_valida(self):
        self.assertEqual(self.cliente.nombre, "Ana Pérez")
        self.assertEqual(self.cliente.correo, "ana@email.com")
        self.assertEqual(self.cliente.telefono, "3001234567")
        for datos in [("C2", "Al", "a@b.co", "3001234567"),
                      ("C2", "Ana", "malcorreo", "3001234567"),
                      ("C2", "Ana", "a@b.co", "12"),
                      ("C2", "Ana", "a@b.co", "abc1234567"),
                      ("", "Ana", "a@b.co", "3001234567"),
                      (True, "Ana", "a@b.co", "3001234567")]:
            with self.assertRaises(DatoInvalidoError):
                Cliente(*datos)

    def test_servicios_rechazan_datos_invalidos(self):
        for args in [("A", "Sala", -1), ("A", "Sala", 0), ("A", "Sala", True),
                     ("A", "Sala", float("nan")), ("A", "  ", 100), ("", "Sala", 100)]:
            with self.assertRaises(DatoInvalidoError):
                ReservaSala(*args)

    def test_polimorfismo_costos_distintos(self):
        self.assertEqual(self.sala.calcular_costo(2), 100000)
        self.assertEqual(self.equipo.calcular_costo(2), 168000)   # incluye seguro 5 %
        self.assertEqual(self.asesoria.calcular_costo(2), 240000)

    def test_sobrecarga_de_calculo(self):
        self.assertEqual(self.sala.calcular_costo(2, 19, 10), 107100)
        self.assertEqual(self.sala.calcular_costo(2, impuesto=19, descuento=10), 107100)
        self.assertEqual(self.sala.calcular_costo_con_impuesto(2, 19), 119000)
        self.assertEqual(self.sala.calcular_costo_con_descuento(2, 10), 90000)
        with self.assertRaises(DatoInvalidoError):
            self.sala.calcular_costo(2, 19, 10, 5)          # demasiados argumentos
        with self.assertRaises(DatoInvalidoError):
            self.sala.calcular_costo(2, 19, impuesto=19)    # impuesto duplicado

    def test_calculos_invalidos(self):
        with self.assertRaises(DatoInvalidoError):
            self.sala.calcular_costo(2, impuesto=150)
        with self.assertRaises(DatoInvalidoError):
            self.sala.calcular_costo(0)
        with self.assertRaises(DatoInvalidoError):
            self.equipo.calcular_costo(2.5)
        with self.assertRaises(CalculoInconsistenteError):
            self.sala.calcular_costo(2, descuento=100)       # total 0 = inconsistente

    def test_reserva_ciclo_de_estados(self):
        r = Reserva("R1", self.cliente, self.sala, 2)
        self.assertEqual(r.estado, "PENDIENTE")
        self.assertEqual(r.confirmar(19, 10), 107100)
        self.assertEqual(r.estado, "CONFIRMADA")
        with self.assertRaises(OperacionNoPermitidaError):
            r.confirmar()
        r.cancelar()
        with self.assertRaises(OperacionNoPermitidaError):
            r.cancelar()

    def test_reserva_invalida_y_encadenamiento(self):
        with self.assertRaises(ReservaInvalidaError):
            Reserva("R1", None, self.sala, 1)
        with self.assertRaises(ReservaInvalidaError) as ctx:
            Reserva("R1", self.cliente, self.asesoria, 2.5)
        self.assertIsInstance(ctx.exception.__cause__, DatoInvalidoError)

    def test_servicio_no_disponible_no_cambia_estado(self):
        self.sala.desactivar()
        r = Reserva("R1", self.cliente, self.sala, 1)
        with self.assertRaises(ReservaInvalidaError) as ctx:
            r.procesar()
        self.assertIsInstance(ctx.exception.__cause__, ServicioNoDisponibleError)
        self.assertEqual(r.estado, "PENDIENTE")  # el fallo no altera la reserva

    def test_gestor(self):
        g = GestorSistema()
        g.registrar_cliente(self.cliente)
        g.registrar_servicio(self.sala)
        with self.assertRaises(DatoInvalidoError):
            g.registrar_cliente(self.cliente)             # duplicado
        with self.assertRaises(ParametroFaltanteError):
            g.crear_cliente(identificador="C9", nombre="Pedro")
        with self.assertRaises(ReservaInvalidaError):
            g.crear_reserva("R1", "NOEXISTE", "SALA", 1)
        reserva = g.crear_reserva("R1", "C1", "sala", 1)  # el código se normaliza
        self.assertIs(g.buscar_reserva("R1"), reserva)


if __name__ == "__main__":
    unittest.main()
