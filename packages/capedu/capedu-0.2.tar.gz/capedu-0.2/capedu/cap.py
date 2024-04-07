
class Calculo:
    def __init__(self, estimacion):
        self.estimacion = estimacion

    def calcular_cap(self, capital10_porciento, capital20_porciento, capital50_porciento, capital75_porciento,
                     capital100porciento, capitalprimario, capitalsecundario, inversionseguros, inversionempresas):
        # Calcular los porcentajes de capital
        capital10 = capital10_porciento * 0.10
        capital20 = capital20_porciento * 0.20
        capital50 = capital50_porciento * 0.50
        capital75 = capital75_porciento * 0.75

        # Calcular el coeficiente de adecuación patrimonial
        cap = ((capitalprimario + capitalsecundario - inversionempresas - inversionseguros) / (
                capital10 + capital20 + capital50 + capital75 + capital100porciento)) * 100
        return round(cap, 2)


# Solicitar datos
capital10porciento = float(input(f"Ingrese el Capital Categoria II Riesgo 10%: "))
capital20porciento = float(input(f"Ingrese el Capital Categoria III Riesgo 20%: "))
capital50porciento = float(input(f"Ingrese el Capital Categoria IV Riesgo 50%: "))
capital75porciento = float(input(f"Ingrese el Capital Categoria V Riesgo 75%: "))
capital100porciento = float(input(f"Ingrese el Capital Categoria VI Riesgo 100%: "))
capitalprimario = float(input(f"Ingrese el Capital Primario Despúes de Ajustes: "))
capitalsecundario = float(input(f"Ingrese el Capital Secundario Despúes de Ajustes: "))
inversionseguros = float(input(f"Ingrese las Inversiones en Sociedades Anonimas de Seguros: "))
inversionempresas = float(input(f"Ingrese las Inversiones en otras Empresas No Consolidadas: "))

# Instancia de Evaluacion
calculo = Calculo("Estimacion")

# Calcular Coeficiente de Adecuación Patrimonial
cap = calculo.calcular_cap(capital10porciento, capital20porciento, capital50porciento, capital75porciento,
                            capital100porciento, capitalprimario, capitalsecundario, inversionseguros,
                            inversionempresas)

# Imprimir Coeficiente de Adecuación Patrimonial
print(f"El Coeficiente de Adecuación Patrimonial es: {cap:.2f}%".replace('.', ','))
