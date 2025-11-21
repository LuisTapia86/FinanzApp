# services/__init__.py
from .proyeccion import calcular_proyeccion_meses, calcular_proyeccion_quincenal, calcular_quincenas_a_proyectar
from .alertas import obtener_proximas_alertas
from .simulador import simular_compra

__all__ = ['calcular_proyeccion_meses', 'calcular_proyeccion_quincenal', 'calcular_quincenas_a_proyectar', 'obtener_proximas_alertas', 'simular_compra']
