# Sistema Integral de Gestión de Clientes, Servicios y Reservas - Software FJ

Proyecto académico del curso Programación (213023), UNAD. Actividad 4 (Fase 4):
estabilidad, robustez y manejo de errores en una aplicación orientada a objetos.

## Requisitos
- Python 3.10 o superior (probado en 3.12).
- Sin librerías externas y **sin bases de datos**: todo se maneja con objetos y listas.
- Los archivos se usan **solo** para el registro de eventos y errores (`eventos.log`).

## Estructura
| Archivo | Contenido |
|---|---|
| `main.py` | Demostración de 26 operaciones (válidas e inválidas). |
| `entidades.py` | Clase abstracta `Entidad` y clase `Cliente`. |
| `servicios.py` | Clase abstracta `Servicio` y `ReservaSala`, `AlquilerEquipo`, `AsesoriaEspecializada`. |
| `reservas.py` | Clase `Reserva`: confirmar, cancelar y procesar. |
| `gestor.py` | `GestorSistema`: listas internas de clientes, servicios y reservas. |
| `excepciones.py` | Jerarquía de excepciones personalizadas. |
| `registro.py` | Configuración del archivo de logs. |
| `pruebas.py` | Pruebas automáticas con `unittest`. |
| `salida_prueba.txt` | Salida de consola de una ejecución completa (evidencia). |
| `eventos.log` | Log generado por la ejecución (evidencia). |

## Ejecución
```bash
python main.py                    # demostración (en Windows también: py main.py)
python -m unittest pruebas -v     # pruebas automáticas
```

## Cumplimiento de los requisitos del Anexo 3
| Requisito | Dónde se cumple |
|---|---|
| Clase abstracta de entidades generales | `Entidad` (`entidades.py`) |
| `Cliente` con validaciones y encapsulación | `Cliente`: atributos protegidos + propiedades con *setters* validados |
| `Servicio` abstracto + 3 servicios especializados | `Servicio`, `ReservaSala`, `AlquilerEquipo`, `AsesoriaEspecializada` |
| Polimorfismo y métodos sobrescritos | `validar_parametros`, `calcular_costo_base` y `describir` se sobrescriben en cada servicio con reglas propias |
| `Reserva` (cliente, servicio, duración, estado) | `Reserva` con `confirmar()`, `cancelar()` y `procesar()` |
| Métodos sobrecargados | `calcular_costo(cantidad, impuesto, descuento)` admite varias firmas (posicionales o con nombre) más `calcular_costo_con_impuesto` y `calcular_costo_con_descuento` |
| Excepciones personalizadas | 7 clases en `excepciones.py`, todas hijas de `ErrorSistema` |
| `try/except`, `try/except/else`, `try/except/finally` | `Reserva.procesar()` usa los cuatro bloques; `ejecutar_operacion()` en `main.py` también |
| Encadenamiento de excepciones | `raise ... from error` en `Reserva.__init__` y `Reserva.procesar()`; el log muestra la cadena de causas |
| Archivo de logs | `eventos.log` (errores con su causa, eventos y tracebacks de errores inesperados) |
| Al menos 10 operaciones simuladas | 26 operaciones en `main.py` |
| Sin base de datos | Listas en `GestorSistema`; archivos solo para logs |

## Nota sobre la sobrecarga
Python no admite sobrecarga de métodos por firma como Java o C#. Se simula con parámetros
opcionales, así que estas llamadas son todas válidas:

```python
sala.calcular_costo(2)                       # sin ajustes
sala.calcular_costo(2, 19)                   # con impuesto
sala.calcular_costo(2, 19, 10)               # con impuesto y descuento
sala.calcular_costo(2, descuento=10)         # solo descuento
```

## Errores controlados
Datos inválidos, parámetros faltantes, operaciones no permitidas, reservas incorrectas,
servicios no disponibles, cálculos inconsistentes y errores inesperados. Ninguno detiene la
aplicación; todos quedan registrados en `eventos.log`.
