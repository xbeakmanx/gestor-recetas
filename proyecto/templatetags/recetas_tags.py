from django import template

register = template.Library()


@register.filter
def estrellas(puntuacion):
    """Convierte una puntuacion numerica en estrellas."""
    llenas = int(puntuacion)
    vacias = 5 - llenas
    return "★" * llenas + "☆" * vacias


@register.filter
def minutos_a_tiempo(minutos):
    """Convierte minutos a formato legible: 1h 30min."""
    if minutos < 60:
        return f"{minutos} min"
    horas = minutos // 60
    resto = minutos % 60
    if resto == 0:
        return f"{horas}h"
    return f"{horas}h {resto}min"
