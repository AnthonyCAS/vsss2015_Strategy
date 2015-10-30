import numpy as np

def velocidad_to_potencias (c):
    m = np.matrix ([
        [0.5,0.5],
        [0.5,-0.5]])
    velocidades = []
    for i in range(3):
        v = m*np.matrix([[c[2*i]],[c[2*i+1]]])
        v[0] = -v[0]
        velocidades.append(v)
    # Tantear. Que porcentaje del rango de potencias es inutil porque el robot no se mueve
    porc_rango_perdidos = [0.4, 0.3, 0.3]


    for i, vel in enumerate(velocidades):
        velocidades[i] = vel*127 + 127

    return [x for vel in velocidades for x in vel]
