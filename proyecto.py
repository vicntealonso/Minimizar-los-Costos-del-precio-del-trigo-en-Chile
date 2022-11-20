import datos
from gurobipy import Model, GRB, quicksum 
import pandas as pd
from random import random, seed

seed(10)

model = Model()
# ------------ SUBÍNDICES ------------ #


# Tipos de trigo
J = range(3)

# Meses
T = range(18)

# Regiones
R = range(16)

# Regiones que importan trigo: I, V, VIII, XV
R_i = [0, 4, 7, 14]

# Regiones que producen trigo: VI, VII, VIII, X, XIII, XIV, XVI
R_p = [5, 6, 7, 9, 12, 13, 15]


# ------------ PARÁMETROS ------------ #


# Costo en pesos de transportar una tonelada de trigo desde la región r a la región i en el mes t
c = [[[0 for t in T] for r_ll in R] for r_s in R]

for r_s in R:
    for r_ll in R:
        c[r_s][r_ll][0] = datos.c_inicial[r_s][r_ll]
        for t in T[1:]:
            c[r_s][r_ll][t] = c[r_s][r_ll][0] * (0.95 + (0.1 + 0.005 * t)*random())

# Máxima cantidad de trigo en toneladas que se puede transportar desde la región r en el mes t
m_c = [[0 for t in T] for r in R]
for r in R:
    m_c[r][0] = datos.m_c_inicial[r]
    for t in T[1:]:
        m_c[r][t] = m_c[r][0] * (0.95 + (0.1 + 0.005 * t)*random())

# Costo en pesos de importar una tonelada de trigo del tipo j a la región r en el mes t
i = [[[datos.i_inicial[j] * (0.95 + (0.1 + 0.005 * t)*random()) for t in T] for r in R] for j in J]

# Costo fijo en pesos de importar trigo del tipo j a la región r en el mes t
i_f = [[[datos.i_f_inicial[j] * (0.95 + (0.1 + 0.005 * t)*random()) for t in T] for r in R] for j in J]

# Máxima cantidad de trigo en toneladas que se puede importar a la región r en el mes t
m_i = [[datos.m_i * (0.95 + (0.1 + 0.005 * t)*random()) for t in T] for r in R]

# Costo en pesos de producir una tonelada de trigo del tipo j en la región r en el mes t
p = [[[datos.p_inicial[j] * (0.95 + (0.1 + 0.005 * t)*random()) for t in T] for r in R] for j in J]

# Costo fijo en pesos de producir trigo del tipo j en la región r en el mes t
p_f = [[[datos.p_f_inicial[j] * (0.95 + (0.1 + 0.005 * t)*random()) for t in T] for r in R] for j in J]

# Máxima cantidad en toneladas que se puede producir de trigo en la región r en el mes t
m_p = [[datos.m_p * (0.95 + (0.1 + 0.005 * t)*random()) for t in T] for r in R]

# Demanda en toneladas de trigo del tipo j en la región r en el mes t
d = [[[0 for t in T] for r in R] for j in J]
for j in J:
    for r in R:
        d[j][r][0] = datos.demanda_inicial[j][r]
        for t in T[1:]:
            d[j][r][t] = datos.demanda_inicial[j][r] * (0.95 + (0.1 + 0.005 * t)*random())



# Costo en pesos de almacenar una tonelada de trigo en la región r en el mes t
c_a = [[datos.c_a * (0.95 + (0.1 + 0.005 * t)*random()) for t in T] for r in R]

# Máxima cantidad de toneladas de trigo que se puede almacenar en la región r en el mes t
m_a = [
    [
        datos.m_a[r] * (0.95 + (0.1 + 0.005 * t)*random() * 13)
        for t in T
    ]
    for r in R
]

# Cantidad almacenada al inicio del modelo en toneladad de trigo del tipo j en la región r
a_0 = datos.a_0


# Big N
n = datos.n


# ------------ VARIABLES ------------ #


# Toneladas de trigo del tipo j producidas en la región r en el mes t.
x = model.addVars(J, R, T, vtype=GRB.CONTINUOUS)

# Si se produce o no trigo del tipo j en la región r en el mes t
w = model.addVars(J, R, T, vtype=GRB.BINARY)

# Toneladas de trigo del tipo j importadas en la región r en el mes t.
y = model.addVars(J, R, T, vtype=GRB.CONTINUOUS)

# Si se importa o no trigo del tipo j en la región r en el mes t
b = model.addVars(J, R, T, vtype=GRB.BINARY)

# Toneladas de trigo del tipo j transportadas desde la región r a la región i en el mes t.
z = model.addVars(J, R, R, T, vtype=GRB.CONTINUOUS)

# Toneladas de trigo del tipo j almacenadas en la región r en el mes t.
a = model.addVars(J, R, T, vtype=GRB.CONTINUOUS)

# Toneladas de trigo del tipo j utilizadas en la región r en el mes t.
g = model.addVars(J, R, T, vtype=GRB.CONTINUOUS)

model.update()
# ----------- RESTRICCIONES ----------- #


# R1: No se puede superar la cantidad máxima de producción
model.addConstrs(
    quicksum(
        x[j, r, t] 
        for j in J
    ) 
    <= m_p[r][t] 
    for r in R 
    for t in T
)

# R2: No se puede superar la cantidad máxima de importación
model.addConstrs(
    quicksum(
        y[j, r, t] 
        for j in J
    ) 
    <= m_i[r] [t] 
    for r in R 
    for t in T
)

# R3: No se puede superar la cantidad máxima de transporte. 
# Comentario: r_s == región de salida, r_ll == región de llegada
model.addConstrs(
    quicksum(
        quicksum(
            z[j, r_s, r_ll, t] 
            for r_ll in R
        ) 
        for j in J
    ) 
    <= m_c[r_s] [t] 
    for r_s in R 
    for t in T
)

# R4: No se puede superar la cantidad máxima de almacenamiento
model.addConstrs(
    quicksum(
        a[j, r, t]
        for j in J
    )
    <= m_a[r][t]
    for r in R
    for t in T
)

# R5: Se debe cumplir con la demanda
model.addConstrs(
    g[j, r, t] 
    >= d[j] [r] [t] 
    for j in J 
    for r in R 
    for t in T
)

# R6: El almacenamiento de cada mes debe ser igual al del mes anterior, más el trigo producido e importado, 
# menos el trigo utilizado y exportado.
model.addConstrs(
    a[j, r, t-1] 
    + x[j, r, t] 
    + y[j, r, t] 
    + quicksum(
        z[j, r_s, r, t] 
        for r_s in R
    ) 
    - quicksum(
        z[j, r, r_ll, t] 
        for r_ll in R
    ) 
    - g[j, r, t] 
    == a[j, r, t]
    for j in J 
    for r in R 
    for t in T[1:]
)
model.addConstrs(
    a_0[j] [r] 
    + x[j, r, 1] 
    + y[j, r, 1] 
    + quicksum(
        z[j, r_s, r, 1] 
        for r_s in R
    ) 
    - quicksum(
        z[j, r, r_ll, 1] 
        for r_ll in R
    ) 
    - g[j, r, 1] 
    == a[j, r, 1] 
    for j in J 
    for r in R 
)

# R7: No se considera el costo fijo de producción si no se produce
model.addConstrs(
    x[j, r, t]
    <= n*w[j, r, t]
    for j in J
    for r in R
    for t in T
)

# R8: No se considera el costo fijo de importación si no se importa
model.addConstrs(
    y[j, r, t]
    <= n*b[j, r, t]
    for j in J
    for r in R
    for t in T
)

# R9: No se puede producir en las regiones que no son aptas para producir
model.addConstrs(
    x[j, r, t]
    == 0
    for j in J
    for r in R if r not in R_p
    for t in T
)

# R10: No se puede importar a las regiones que no son aptas para importar
model.addConstrs(
    y[j, r, t]
    == 0
    for j in J
    for r in R if r not in R_i
    for t in T
)

# R11: Se debe gastar el trigo como máximo al noveno mes contando desde su producción e importación 
# (se incluye el caso del primer mes, en donde se debe gastar el trigo que ya estaba
# almacenado)
model.addConstrs(
    quicksum(
        x[j, r, t]
        for r in R
    )
    + quicksum(
        y[j, r, t]
        for r in R
    )
    <= quicksum(
        quicksum(
            g[j, r, t]
            for t in range(m, m+9)
        )
        for r in R
    )
    for j in J
    for m in range(2, len(T) - 8)
    for t in T
)
model.addConstrs(
    quicksum(
        x[j, r, 1]
        for r in R
    )
    + quicksum(
        y[j, r, 1]
        for r in R
    )
    <= quicksum(
        quicksum(
            g[j, r, 1]
            for t in range(m, m+9)
        )
        for r in R
    )
    for j in J
    for m in range(2, len(T) - 7)
)

# --------- FUNCIÓN OBJETIVO --------- #


objetivo = quicksum(
    quicksum(
        quicksum(
            quicksum(
                z[j, r_s, r_ll, t]
                for j in J
            )
            *c[r_s][r_ll][t]
            for t in T
        )
        for r_ll in R
    )
    for r_s in R
) + quicksum(
    quicksum(
        quicksum(
            x[j, r, t]
            * p[j][r][t]

            + w[j, r, t]
            * p_f[j][r][t]
            for t in T
        )
        for r in R
    )
    for j in J
) + quicksum(
    quicksum(
        quicksum(
            y[j, r, t]
            * i[j][r][t]

            + b[j, r, t]
            * i_f[j][r][t]
            for t in T
        )
        for r in R
    )
    for j in J
) + quicksum(
    quicksum(
        quicksum(
            a[j, r, t]
            for j in J
        )
        * c_a[r][t]
        for t in T
    )
    for r in R
)

model.setObjective(objetivo, GRB.MINIMIZE)
model.Params.MIPGap = 0.005
model.optimize()


# ----- ANÁLISIS DE LA SOLUCIÓN Y VALOR OBJETIVO ----- #

for j in J:
    for t in T:
        opt = [[x[j, r, t].x, w[j, r, t].x, y[j, r, t].x, b[j, r, t].x, a[j, r, t], g[j, r, t]] for r in R]
        opt = pd.DataFrame(opt, columns=["Producción", "Se produce", "Importación", "Se importa", "Almacenamiento", "Utilización"])
        opt.to_excel(f"Trigo_{j+1}_Mes_{t+1}.xlsx")


for r_ll in R:
    for r_s in R:
        for t in T:
            if z[0, r_s, r_ll, t].x != 0:
                print(
                    f"Región {r_s+1} envía {z[0, r_s, r_ll, t]} toneladas de trigo a región {r_ll+1} en el mes {t+1}"
                )
