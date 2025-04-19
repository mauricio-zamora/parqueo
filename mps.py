import pandas as pd
import math

# ==============================================================================
# --- COPIA AQUÍ TODAS LAS DEFINICIONES DE FUNCIONES DE LA RESPUESTA ANTERIOR ---
# calcular_mps_nivelado
# calcular_mps_perseguidor (o la versión original si prefieres)
# calcular_mps_perseguidor_ss_variable
# calcular_mrp
# calcular_mrp_multinivel (si la necesitas para algún problema específico)
# ==============================================================================

# ==============================================================================
# Función para calcular MPS - Método Nivelado (Level Strategy)
# ==============================================================================
def calcular_mps_nivelado(nombre_producto, demanda, inv_inicial, stock_seguridad_final, scrap_rate, num_periodos):
    """
    Calcula el Plan Maestro de Producción usando una estrategia nivelada.

    Args:
        nombre_producto (str): Nombre del producto para los logs.
        demanda (list or pd.Series): Demanda pronosticada para cada período.
        inv_inicial (float): Inventario inicial al comienzo del período 1.
        stock_seguridad_final (float): Nivel de inventario de seguridad deseado al final del último período.
        scrap_rate (float): Tasa de scrap o desperdicio en producción (e.g., 0.10 para 10%).
        num_periodos (int): Número total de períodos a planificar.

    Returns:
        pd.DataFrame: DataFrame con el MPS calculado.
    """
    print(f"\n--- Calculando MPS Nivelado para: {nombre_producto} ---")
    print(f"Demanda: {demanda}")
    print(f"Inventario Inicial: {inv_inicial}")
    print(f"Stock de Seguridad (objetivo final): {stock_seguridad_final}")
    print(f"Tasa de Scrap: {scrap_rate:.2%}")

    demanda_total = sum(demanda)
    requerimiento_neto_total = demanda_total + stock_seguridad_final - inv_inicial
    requerimiento_neto_total = max(0, requerimiento_neto_total)

    if num_periodos <= 0:
        raise ValueError("El número de períodos debe ser positivo.")
    produccion_necesaria_por_periodo = requerimiento_neto_total / num_periodos

    if 1 - scrap_rate <= 0:
        raise ValueError("La tasa de scrap no puede ser 100% o más.")
    # Redondeo hacia arriba para asegurar que se cumple el objetivo
    produccion_bruta_por_periodo = math.ceil(produccion_necesaria_por_periodo / (1 - scrap_rate))

    print(f"Demanda Total: {demanda_total}")
    print(f"Requerimiento Neto Total (antes de scrap): {requerimiento_neto_total}")
    print(f"Producción Bruta Nivelada por Período (con scrap): {produccion_bruta_por_periodo}")

    periodos = list(range(1, num_periodos + 1))
    mps_df = pd.DataFrame(index=[
        'Inventario Inicial',
        'Producción Bruta Requerida',
        'Inventario Disponible',
        'Demanda',
        'Inventario Final'
    ], columns=periodos).fillna(0.0)

    inv_final_anterior = inv_inicial
    for p in periodos:
        idx_demanda = p - 1
        inv_inicial_periodo = inv_final_anterior
        prod_planificada = produccion_bruta_por_periodo
        inv_disponible = inv_inicial_periodo + prod_planificada
        demanda_actual = demanda[idx_demanda]
        inv_final = inv_disponible - demanda_actual

        mps_df.loc['Inventario Inicial', p] = inv_inicial_periodo
        mps_df.loc['Producción Bruta Requerida', p] = prod_planificada
        mps_df.loc['Inventario Disponible', p] = inv_disponible
        mps_df.loc['Demanda', p] = demanda_actual
        mps_df.loc['Inventario Final', p] = inv_final
        inv_final_anterior = inv_final

    return mps_df

# ==============================================================================
# Función para calcular MPS - Método Perseguidor (Chase Strategy - SS Variable)
# ==============================================================================
def calcular_mps_perseguidor_ss_variable(nombre_producto, demanda, inv_inicial, stocks_seguridad_periodo, scrap_rate):
    """
    Calcula el Plan Maestro de Producción usando una estrategia perseguidora
    con stock de seguridad variable por período.

    Args:
        nombre_producto (str): Nombre del producto para los logs.
        demanda (list or pd.Series): Demanda pronosticada para cada período.
        inv_inicial (float): Inventario inicial al comienzo del período 1.
        stocks_seguridad_periodo (list): Nivel de SS deseado al final de CADA período.
        scrap_rate (float): Tasa de scrap o desperdicio en producción (e.g., 0.10 para 10%).

    Returns:
        pd.DataFrame: DataFrame con el MPS calculado.
    """
    print(f"\n--- Calculando MPS Perseguidor (SS Variable) para: {nombre_producto} ---")
    print(f"Demanda: {demanda}")
    print(f"Inventario Inicial: {inv_inicial}")
    print(f"Stock de Seguridad (por período): {stocks_seguridad_periodo}")
    print(f"Tasa de Scrap: {scrap_rate:.2%}")

    num_periodos = len(demanda)
    if len(stocks_seguridad_periodo) != num_periodos:
        raise ValueError("La longitud de stocks_seguridad_periodo debe coincidir con la demanda.")

    periodos = list(range(1, num_periodos + 1))
    mps_df = pd.DataFrame(index=[
        'Inventario Inicial',
        'Stock Seguridad Periodo',
        'Producción Bruta Requerida',
        'Inventario Disponible',
        'Demanda',
        'Inventario Final'
    ], columns=periodos).fillna(0.0)

    inv_final_anterior = inv_inicial
    producciones = []

    for p in periodos:
        idx = p - 1
        inv_inicial_periodo = inv_final_anterior
        demanda_actual = demanda[idx]
        ss_actual = stocks_seguridad_periodo[idx]

        necesidad_total_periodo = demanda_actual + ss_actual
        produccion_necesaria_neta = necesidad_total_periodo - inv_inicial_periodo
        produccion_necesaria_neta = max(0, produccion_necesaria_neta)

        if 1 - scrap_rate <= 0:
             raise ValueError("La tasa de scrap no puede ser 100% o más.")
        # Redondeo hacia arriba
        produccion_bruta_requerida = math.ceil(produccion_necesaria_neta / (1 - scrap_rate))
        producciones.append(produccion_bruta_requerida)

        inv_disponible = inv_inicial_periodo + produccion_bruta_requerida
        inv_final = inv_disponible - demanda_actual

        mps_df.loc['Inventario Inicial', p] = inv_inicial_periodo
        mps_df.loc['Stock Seguridad Periodo', p] = ss_actual # Añadido para claridad
        mps_df.loc['Producción Bruta Requerida', p] = produccion_bruta_requerida
        mps_df.loc['Inventario Disponible', p] = inv_disponible
        mps_df.loc['Demanda', p] = demanda_actual
        mps_df.loc['Inventario Final', p] = inv_final
        inv_final_anterior = inv_final

    print(f"Producción Bruta Requerida por Período: {producciones}")
    return mps_df

# ==============================================================================
# Función para calcular MRP
# ==============================================================================
def calcular_mrp(item_id, requerimientos_brutos, inv_inicial, stock_seguridad, recepciones_programadas, lead_time, lote_minimo=1, politica_lote='LFL'):
    """
    Calcula la Planificación de Requerimientos de Materiales (MRP) para un item.

    Args:
        item_id (str): Identificador del item.
        requerimientos_brutos (list or pd.Series): Necesidades brutas por período.
        inv_inicial (float): Inventario inicial disponible.
        stock_seguridad (float): Stock de seguridad requerido (absoluto).
        recepciones_programadas (list or pd.Series): Cantidades que llegarán por pedidos ya hechos.
                                                     Debe tener la misma longitud que requerimientos_brutos.
        lead_time (int): Tiempo de espera en períodos (Lead Time).
        lote_minimo (int): Tamaño mínimo del lote (LFL) o tamaño fijo (FOQ). Default 1.
        politica_lote (str): Política de lote ('LFL' - Lote por Lote, 'FOQ' - Cantidad Fija). Default 'LFL'.

    Returns:
        pd.DataFrame: DataFrame con la tabla MRP calculada.
        pd.Series: Serie con los Lanzamientos Planificados de Pedidos (para usar en niveles inferiores).
    """
    print(f"\n--- Calculando MRP para Item: {item_id} ---")
    print(f"Req. Brutos: {requerimientos_brutos}")
    print(f"Inv. Inicial: {inv_inicial}, Stock Seg: {stock_seguridad}")
    print(f"Recep. Prog: {recepciones_programadas}")
    print(f"Lead Time: {lead_time}, Política Lote: {politica_lote}, Lote Mín/Fijo: {lote_minimo}")

    # Convertir a lista si es necesario
    if isinstance(requerimientos_brutos, pd.Series):
        requerimientos_brutos = requerimientos_brutos.tolist()
    if isinstance(recepciones_programadas, pd.Series):
        recepciones_programadas = recepciones_programadas.tolist()

    num_periodos = len(requerimientos_brutos)
    periodos = list(range(1, num_periodos + 1))

    if len(recepciones_programadas) != num_periodos:
         # Intentar rellenar con ceros si la longitud no coincide
         print(f"Advertencia: Longitud de Recepciones Programadas ({len(recepciones_programadas)}) no coincide con Num. Periodos ({num_periodos}). Rellenando con ceros.")
         recepciones_programadas = (recepciones_programadas + [0.0] * num_periodos)[:num_periodos]


    mrp_df = pd.DataFrame(index=[
        'Requerimientos Brutos',
        'Recepciones Programadas',
        'Inventario Proyectado Disponible',
        'Requerimientos Netos',
        'Recepción de Pedidos Planificados',
        'Lanzamiento Planificado de Pedidos'
    ], columns=periodos).fillna(0.0)

    pab = [0.0] * (num_periodos + 1) # PAB al *final* del período t
    pab[0] = inv_inicial

    # Lanzamientos planificados indexados por el período de lanzamiento
    lanzamientos_planificados = pd.Series([0.0] * num_periodos, index=periodos)

    for t in periodos:
        idx = t - 1
        pab_inicio_periodo = pab[idx] # PAB al final del período anterior
        rb_t = requerimientos_brutos[idx]
        rp_t = recepciones_programadas[idx]

        mrp_df.loc['Requerimientos Brutos', t] = rb_t
        mrp_df.loc['Recepciones Programadas', t] = rp_t

        # PAB antes de recibir pedidos planificados del periodo actual
        pab_antes_recepcion_planif = pab_inicio_periodo + rp_t

        rn_t = rb_t + stock_seguridad - pab_antes_recepcion_planif
        rn_t = max(0, rn_t)
        mrp_df.loc['Requerimientos Netos', t] = rn_t

        rpp_t = 0.0
        if rn_t > 0:
            if politica_lote == 'LFL':
                rpp_t = max(rn_t, lote_minimo) # Lote por lote, respetando mínimo si aplica
            elif politica_lote == 'FOQ':
                if lote_minimo <= 0: raise ValueError("Lote Fijo (FOQ) debe ser mayor que 0")
                rpp_t = math.ceil(rn_t / lote_minimo) * lote_minimo
            else: # Default LFL
                 rpp_t = max(rn_t, lote_minimo)
        mrp_df.loc['Recepción de Pedidos Planificados', t] = rpp_t

        periodo_lanzamiento = t - lead_time
        if periodo_lanzamiento >= 1:
            # Asegurarse de que el índice existe en la Serie
            if periodo_lanzamiento in lanzamientos_planificados.index:
                 lanzamientos_planificados[periodo_lanzamiento] += rpp_t
            else:
                 # Esto no debería ocurrir con índices de 1 a N, pero por seguridad
                 print(f"Advertencia: Periodo de lanzamiento {periodo_lanzamiento} fuera de rango.")

        # Calcular PAB al final del período t
        pab[t] = pab_antes_recepcion_planif - rb_t + rpp_t
        mrp_df.loc['Inventario Proyectado Disponible', t] = pab[t]

    # Actualizar la fila de lanzamientos en el DataFrame
    mrp_df.loc['Lanzamiento Planificado de Pedidos'] = lanzamientos_planificados

    print(mrp_df) # Imprimir dentro de la función para debug/claridad
    return mrp_df, lanzamientos_planificados


# ==============================================================================
# --- Funciones de Ayuda para los Problemas ---
# ==============================================================================

def calcular_stock_seguridad_porcentaje(demanda, porcentaje, tipo='periodo'):
    """Calcula el stock de seguridad basado en porcentaje."""
    if not 0 <= porcentaje <= 1:
        raise ValueError("El porcentaje debe estar entre 0 y 1.")

    if tipo == 'periodo':
        # 10% de la demanda de cada período (para Perseguidor)
        return [math.ceil(d * porcentaje) for d in demanda]
    elif tipo == 'final':
        # 10% de la demanda del último período (para Nivelado - fin horizonte)
        if not demanda: return 0
        return math.ceil(demanda[-1] * porcentaje)
    elif tipo == 'promedio':
         # 10% de la demanda promedio (otra opción para Nivelado)
         if not demanda: return 0
         promedio = sum(demanda) / len(demanda)
         return math.ceil(promedio * porcentaje)
    else:
        raise ValueError("Tipo de cálculo de SS no reconocido ('periodo', 'final', 'promedio')")

# ==============================================================================
# --- Solución Problema 1 ---
# ==============================================================================
def solve_problem_1():
    print("\n" + "="*60)
    print(" RESOLVIENDO PROBLEMA 1")
    print("="*60)

    # --- Datos ---
    num_periodos = 4
    periodos_idx = list(range(1, num_periodos + 1))

    # Producto A (Perseguidor)
    demanda_a = [300, 500, 900, 1500]
    inv_inicial_a = 400
    ss_porcentaje_a = 0.10 # 10% de la demanda del período
    scrap_a = 0.15
    capacidad_a = 500
    ss_a_periodo = calcular_stock_seguridad_porcentaje(demanda_a, ss_porcentaje_a, tipo='periodo')

    # Producto B (Nivelador)
    demanda_b = [800, 1000, 700, 700]
    inv_inicial_b = 0
    ss_fijo_b = 50 # Fijo
    scrap_b = 0.05
    capacidad_b = 1000

    # Producto C (Nivelador)
    demanda_c = [1500, 750, 800, 900]
    inv_inicial_c = 300
    ss_porcentaje_c = 0.15 # 15% (¿De qué? Asumiremos final, como es nivelador)
    scrap_c = 0.10
    capacidad_c = 1500
    ss_c_final = calcular_stock_seguridad_porcentaje(demanda_c, ss_porcentaje_c, tipo='final')

    # --- Cálculos MPS ---
    mps_a = calcular_mps_perseguidor_ss_variable(
        nombre_producto="A",
        demanda=demanda_a,
        inv_inicial=inv_inicial_a,
        stocks_seguridad_periodo=ss_a_periodo,
        scrap_rate=scrap_a
    )

    mps_b = calcular_mps_nivelado(
        nombre_producto="B",
        demanda=demanda_b,
        inv_inicial=inv_inicial_b,
        stock_seguridad_final=ss_fijo_b, # Usamos el SS fijo como objetivo final
        scrap_rate=scrap_b,
        num_periodos=num_periodos
    )

    mps_c = calcular_mps_nivelado(
        nombre_producto="C",
        demanda=demanda_c,
        inv_inicial=inv_inicial_c,
        stock_seguridad_final=ss_c_final, # Usamos el % de la última demanda
        scrap_rate=scrap_c,
        num_periodos=num_periodos
    )

    print("\n--- Resultados MPS Problema 1 ---")
    print("\nMPS Producto A (Perseguidor):")
    print(mps_a)
    print("\nMPS Producto B (Nivelador):")
    print(mps_b)
    print("\nMPS Producto C (Nivelador):")
    print(mps_c)

    # --- Chequeo de Capacidad ---
    print("\n--- Chequeo de Capacidad Consumida (Problema 1) ---")
    # Capacidad Total por producto (puede variar por período si se indica)
    capacidades = {'A': capacidad_a, 'B': capacidad_b, 'C': capacidad_c}
    # Producción requerida por período para cada producto
    prod_req_a = mps_a.loc['Producción Bruta Requerida']
    prod_req_b = mps_b.loc['Producción Bruta Requerida']
    prod_req_c = mps_c.loc['Producción Bruta Requerida']

    # Crear DataFrame para el análisis de capacidad
    capacidad_df = pd.DataFrame(index=periodos_idx)
    capacidad_df['Prod. Req. A'] = prod_req_a
    capacidad_df['Prod. Req. B'] = prod_req_b
    capacidad_df['Prod. Req. C'] = prod_req_c
    capacidad_df['Capacidad Disp. A'] = capacidad_a
    capacidad_df['Capacidad Disp. B'] = capacidad_b
    capacidad_df['Capacidad Disp. C'] = capacidad_c

    # Calcular Déficit/Superávit por producto
    capacidad_df['Balance Cap. A'] = capacidad_df['Capacidad Disp. A'] - capacidad_df['Prod. Req. A']
    capacidad_df['Balance Cap. B'] = capacidad_df['Capacidad Disp. B'] - capacidad_df['Prod. Req. B']
    capacidad_df['Balance Cap. C'] = capacidad_df['Capacidad Disp. C'] - capacidad_df['Prod. Req. C']

    print(capacidad_df)

    print("\nAnálisis de capacidad:")
    for p in periodos_idx:
        print(f"Periodo {p}:")
        deficit_a = capacidad_df.loc[p, 'Balance Cap. A'] < 0
        deficit_b = capacidad_df.loc[p, 'Balance Cap. B'] < 0
        deficit_c = capacidad_df.loc[p, 'Balance Cap. C'] < 0
        if deficit_a: print(f"  - Déficit Capacidad Producto A: {abs(capacidad_df.loc[p, 'Balance Cap. A']):.0f} unidades")
        if deficit_b: print(f"  - Déficit Capacidad Producto B: {abs(capacidad_df.loc[p, 'Balance Cap. B']):.0f} unidades")
        if deficit_c: print(f"  - Déficit Capacidad Producto C: {abs(capacidad_df.loc[p, 'Balance Cap. C']):.0f} unidades")
        if not deficit_a and not deficit_b and not deficit_c:
            print("  - Capacidad suficiente para todos los productos.")

    # Pregunta 2: Si la secuencia es B-C-A...
    # Esto implica que la capacidad es COMPARTIDA y se consume secuencialmente.
    # La capacidad total de la línea no está clara en el enunciado (¿es la suma?, ¿es otra?).
    # ASUMIENDO que hay una capacidad TOTAL de línea por periodo y estos productos la comparten.
    # El enunciado dice "comparten la misma línea", pero luego da capacidades individuales.
    # Esto puede significar que *esas* son las capacidades máximas *si solo se produce ese item*.
    # Interpretación más probable: La capacidad dada es POR PRODUCTO en esa línea. El chequeo anterior es válido.
    # La pregunta de la secuencia podría referirse a si hay cuellos de botella si se prioriza.
    # Con los chequeos individuales ya vemos si hay problemas. Si B, C, A se hacen en secuencia DENTRO
    # de un período, el análisis de capacidad total consumida vs disponible sigue siendo el mismo.
    # La pregunta sobre "horas extras" se responde calculando el total de unidades en déficit.

    unidades_deficit_total = abs(capacidad_df[capacidad_df < 0].sum().sum()) # Suma de todos los balances negativos
    if unidades_deficit_total > 0:
         print(f"\nSe requerirían horas extras o ajustes para cubrir un déficit total de {unidades_deficit_total:.0f} unidades a lo largo del horizonte.")
         print("(Asumiendo que la capacidad indicada es el límite por producto en la línea compartida)")
    else:
         print("\nBajo la secuencia B-C-A (o cualquier otra), el MPS calculado parece factible según las capacidades individuales indicadas.")


# ==============================================================================
# --- Solución Problema 2 ---
# ==============================================================================
def solve_problem_2():
    print("\n" + "="*60)
    print(" RESOLVIENDO PROBLEMA 2")
    print("="*60)

    # --- Datos ---
    num_periodos = 3

    # Producto A (Nivelador)
    demanda_a = [7500, 9000, 11500]
    inv_inicial_a = 200
    ss_porcentaje_a = 0.10 # 10% (Asumir final para nivelador)
    scrap_a = 0.08
    ss_a_final = calcular_stock_seguridad_porcentaje(demanda_a, ss_porcentaje_a, tipo='final')

    # Producto B (Perseguidor)
    demanda_b = [8000, 7500, 10000]
    inv_inicial_b = 500
    ss_porcentaje_b = 0.10 # 10% (Asumir por periodo para perseguidor)
    scrap_b = 0.05
    ss_b_periodo = calcular_stock_seguridad_porcentaje(demanda_b, ss_porcentaje_b, tipo='periodo')

    # --- Cálculos MPS ---
    mps_a = calcular_mps_nivelado(
        nombre_producto="A",
        demanda=demanda_a,
        inv_inicial=inv_inicial_a,
        stock_seguridad_final=ss_a_final,
        scrap_rate=scrap_a,
        num_periodos=num_periodos
    )

    mps_b = calcular_mps_perseguidor_ss_variable(
        nombre_producto="B",
        demanda=demanda_b,
        inv_inicial=inv_inicial_b,
        stocks_seguridad_periodo=ss_b_periodo,
        scrap_rate=scrap_b
    )

    print("\n--- Resultados MPS Problema 2 ---")
    print("\nMPS Producto A (Nivelador):")
    print(mps_a)
    print("\nMPS Producto B (Perseguidor):")
    print(mps_b)


# ==============================================================================
# --- Solución Problema 3 ---
# ==============================================================================
def solve_problem_3():
    print("\n" + "="*60)
    print(" RESOLVIENDO PROBLEMA 3")
    print("="*60)

    # --- Datos ---
    num_periodos = 3

    # Producto A (Ambos métodos)
    demanda_a = [8000, 10000, 21000]
    inv_inicial_a = 1000
    ss_porcentaje_a = 0.10 # 10%
    scrap_a = 0.12

    # Para Nivelador (SS final)
    ss_a_final_nivelado = calcular_stock_seguridad_porcentaje(demanda_a, ss_porcentaje_a, tipo='final')
    # Para Perseguidor (SS por periodo)
    ss_a_periodo_perseguidor = calcular_stock_seguridad_porcentaje(demanda_a, ss_porcentaje_a, tipo='periodo')


    # --- Cálculos MPS ---
    print("\n--- Método Nivelador ---")
    mps_a_nivelado = calcular_mps_nivelado(
        nombre_producto="A",
        demanda=demanda_a,
        inv_inicial=inv_inicial_a,
        stock_seguridad_final=ss_a_final_nivelado,
        scrap_rate=scrap_a,
        num_periodos=num_periodos
    )

    print("\n--- Método Perseguidor ---")
    mps_a_perseguidor = calcular_mps_perseguidor_ss_variable(
        nombre_producto="A",
        demanda=demanda_a,
        inv_inicial=inv_inicial_a,
        stocks_seguridad_periodo=ss_a_periodo_perseguidor,
        scrap_rate=scrap_a
    )

    print("\n--- Resultados MPS Problema 3 ---")
    print("\nMPS Producto A (Nivelador):")
    print(mps_a_nivelado)
    print("\nMPS Producto A (Perseguidor):")
    print(mps_a_perseguidor)

# ==============================================================================
# --- Solución Problema 4 ---
# ==============================================================================
def solve_problem_4():
    print("\n" + "="*60)
    print(" RESOLVIENDO PROBLEMA 4 (MRP para Componentes A, B, C)")
    print("="*60)
    # NOTA: Como se discutió, calcularemos MRP para cada componente individualmente
    #       usando los datos provistos para cada uno. La demanda de C se toma
    #       del "MPS de C" dado (asumido), y las de A y B no se especifican
    #       (se usarán ceros a menos que se deriven de P/Q, cuyo MPS no tenemos).

    num_periodos = 8 # Basado en el MPS de ejemplo para C

    # --- Datos Componente C ---
    item_c_id = 'C'
    # MPS de C (usado como Req. Brutos para su propio MRP) - ¡VERIFICAR ESTOS VALORES!
    req_brutos_c = [800, 1200, 900, 1100, 1000, 1300, 700, 1000] # Ejemplo del código anterior
    inv_inicial_c = 300
    stock_seguridad_c = 100 # Fijo
    recepciones_c = [0.0] * num_periodos
    recepciones_c[1-1] = 500 # Semana 1
    recepciones_c[4-1] = 250 # Semana 4
    lead_time_c = 1
    politica_lote_c = 'LFL'
    lote_minimo_c = 1

    # --- Datos Componente A ---
    item_a_id = 'A'
    # Req. Brutos de A - NO DADOS. Dependerían del MPS de P y Q. Asumiremos 0 por ahora.
    req_brutos_a = [0] * num_periodos
    inv_inicial_a = 150
    stock_seguridad_a = 20 # Fijo
    recepciones_a = [0.0] * num_periodos
    recepciones_a[2-1] = 300 # Semana 2
    lead_time_a = 1
    politica_lote_a = 'LFL'
    lote_minimo_a = 1

    # --- Datos Componente B ---
    item_b_id = 'B'
    # Req. Brutos de B - NO DADOS. Dependerían del MPS de P y Q. Asumiremos 0 por ahora.
    req_brutos_b = [0] * num_periodos
    inv_inicial_b = 80
    stock_seguridad_b = 10 # Fijo
    recepciones_b = [0.0] * num_periodos # Ninguna
    lead_time_b = 2
    politica_lote_b = 'FOQ' # Múltiplos de 400
    lote_minimo_b = 400 # Lote fijo

    # --- Cálculos MRP ---
    print("\n--- MRP Componente C ---")
    mrp_c_df, lanzamientos_c = calcular_mrp(
        item_id=item_c_id,
        requerimientos_brutos=req_brutos_c,
        inv_inicial=inv_inicial_c,
        stock_seguridad=stock_seguridad_c,
        recepciones_programadas=recepciones_c,
        lead_time=lead_time_c,
        lote_minimo=lote_minimo_c,
        politica_lote=politica_lote_c
    )

    print("\n--- MRP Componente A ---")
    # Nota: Con Req. Brutos = 0, el MRP será trivial a menos que SS > InvInicial+Recep.
    mrp_a_df, lanzamientos_a = calcular_mrp(
        item_id=item_a_id,
        requerimientos_brutos=req_brutos_a,
        inv_inicial=inv_inicial_a,
        stock_seguridad=stock_seguridad_a,
        recepciones_programadas=recepciones_a,
        lead_time=lead_time_a,
        lote_minimo=lote_minimo_a,
        politica_lote=politica_lote_a
    )

    print("\n--- MRP Componente B ---")
    # Nota: Con Req. Brutos = 0, el MRP será trivial a menos que SS > InvInicial+Recep.
    mrp_b_df, lanzamientos_b = calcular_mrp(
        item_id=item_b_id,
        requerimientos_brutos=req_brutos_b,
        inv_inicial=inv_inicial_b,
        stock_seguridad=stock_seguridad_b,
        recepciones_programadas=recepciones_b,
        lead_time=lead_time_b,
        lote_minimo=lote_minimo_b, # Lote Fijo
        politica_lote=politica_lote_b
    )

    print("\n--- Resultados MRP Problema 4 ---")
    print(f"\nMRP Calculado para {item_c_id}:")
    # print(mrp_c_df) # Ya se imprime dentro de la función
    print(f"\nLanzamientos Planificados para {item_c_id}:")
    print(lanzamientos_c)

    print(f"\nMRP Calculado para {item_a_id}:")
    # print(mrp_a_df)
    print(f"\nLanzamientos Planificados para {item_a_id}:")
    print(lanzamientos_a)

    print(f"\nMRP Calculado para {item_b_id}:")
    # print(mrp_b_df)
    print(f"\nLanzamientos Planificados para {item_b_id}:")
    print(lanzamientos_b)

    # Si tuviéramos el MPS de P y Q, y el BOM correcto, usaríamos calcular_mrp_multinivel.
    # Ejemplo rápido de cómo se haría (requiere MPS de P y Q):
    # mps_P = [...]
    # mps_Q = [...]
    # req_brutos_A = (mps_P * 2) + (mps_Q * 2) # Asumiendo que P y Q tienen el mismo horizonte
    # req_brutos_B = (mps_P * 5) + (mps_Q * 5)
    # Y luego se calcularía el MRP de A y B con estos req. brutos.


# ==============================================================================
# --- Punto de Entrada Principal ---
# ==============================================================================
if __name__ == "__main__":
    print("Iniciando Cálculos MPS y MRP...")

    # Ejecutar solución para cada problema
    solve_problem_1()
    solve_problem_2()
    solve_problem_3()
    solve_problem_4() # Ejecutando solo el problema 4 como ejemplo

    print("\n" + "="*60)
    print("Cálculos Finalizados.")
    print("="*60)