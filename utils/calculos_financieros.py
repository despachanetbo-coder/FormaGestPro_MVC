# utils/calculos_financieros.py
import math

def calcular_descuento_exacto(monto_base, porcentaje):
    """
    Calcula el descuento y el monto final con redondeo apropiado.
    Devuelve: (descuento, monto_final)
    """
    if porcentaje < 0 or porcentaje > 100:
        raise ValueError("El porcentaje debe estar entre 0 y 100")
    
    # Calcular el descuento exacto
    descuento_exacto = monto_base * (porcentaje / 100)
    
    # Redondear a 2 decimales (centavos) usando round half up
    descuento_redondeado = round(descuento_exacto + 1e-10, 2)
    
    # Calcular monto final
    monto_final = monto_base - descuento_redondeado
    
    # Asegurar que el monto final tenga exactamente 2 decimales
    monto_final = round(monto_final + 1e-10, 2)
    
    # Verificar que la suma sea consistente
    if abs((descuento_redondeado + monto_final) - monto_base) > 0.01:
        # Ajustar para que sumen exactamente
        diferencia = monto_base - (descuento_redondeado + monto_final)
        monto_final += diferencia
        monto_final = round(monto_final, 2)
    
    return descuento_redondeado, monto_final

def calcular_porcentaje_para_monto_final(monto_base, monto_final_deseado):
    """
    Calcula el porcentaje necesario para llegar a un monto final específico.
    Útil cuando se quiere un monto exacto (ej: 3520 de 3800)
    """
    if monto_base <= 0:
        return 0
    
    if monto_final_deseado > monto_base:
        raise ValueError("El monto final no puede ser mayor al monto base")
    
    if monto_final_deseado <= 0:
        raise ValueError("El monto final debe ser positivo")
    
    descuento_necesario = monto_base - monto_final_deseado
    porcentaje = (descuento_necesario / monto_base) * 100
    
    return porcentaje

def formatear_moneda(monto):
    """Formatea un monto a string con 2 decimales y separadores de miles"""
    return f"{monto:,.2f}"

def redondear_a_entero_cercano(monto):
    """Redondea al entero más cercano (para mostrar montos sin decimales)"""
    return round(monto + 1e-10)

def calcular_monto_cuota(monto_total, numero_cuotas):
    """
    Calcula el monto de cada cuota con redondeo apropiado.
    Asegura que la suma de las cuotas sea igual al monto total.
    """
    if numero_cuotas <= 0:
        raise ValueError("El número de cuotas debe ser mayor a 0")
    
    # Calcular cuota exacta
    cuota_exacta = monto_total / numero_cuotas
    
    # Redondear a 2 decimales
    cuota_redondeada = round(cuota_exacta + 1e-10, 2)
    
    # Calcular diferencia por redondeo
    total_redondeado = cuota_redondeada * numero_cuotas
    diferencia = monto_total - total_redondeado
    
    # Ajustar la última cuota si hay diferencia
    if abs(diferencia) > 0.01:
        cuota_redondeada = monto_total / numero_cuotas
        # Distribuir la diferencia en la última cuota
        cuotas = [round(cuota_redondeada, 2)] * (numero_cuotas - 1)
        ultima_cuota = monto_total - sum(cuotas)
        cuotas.append(round(ultima_cuota, 2))
        return cuotas
    else:
        return [cuota_redondeada] * numero_cuotas

def verificar_suma_correcta(monto_base, descuento, monto_final):
    """Verifica que el descuento + monto final sumen el monto base"""
    return abs((descuento + monto_final) - monto_base) < 0.01