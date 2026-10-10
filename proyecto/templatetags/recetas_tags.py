from django import template

register = template.Library()


#estrellas(puntuación):
#   llenas ← parte entera de la puntuación
#   vacías ← 5 - llenas
#   RETORNAR "★" repetido llenas veces + "☆" repetido vacías veces
@register.filter
def estrellas(puntuacion):
    llenas = int(puntuacion)
    vacias = 5 - llenas
    return "★" * llenas + "☆" * vacias


#minutos_a_tiempo(minutos):
#   SI minutos < 60: RETORNAR "{minutos} min"
#   horas ← minutos / 60 (parte entera)
#   resto ← minutos módulo 60
#   SI resto = 0: RETORNAR "{horas}h"
#   RETORNAR "{horas}h {resto}min"
@register.filter
def minutos_a_tiempo(minutos):
    if minutos < 60:
        return f"{minutos} min"
    horas = minutos // 60
    resto = minutos % 60
    if resto == 0:
        return f"{horas}h"
    return f"{horas}h {resto}min"
