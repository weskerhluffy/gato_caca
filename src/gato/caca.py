'''
Created on 17/03/2018

@author: 

XXX:
'''

import logging
from sys import stdin
from collections import Counter
from operator import gt, lt
from copy import copy, deepcopy

nivel_log = logging.ERROR
nivel_log = logging.DEBUG
logger_cagada = None

def determina_jugador_opuesto(jugador):
    if jugador == 'X':
        return 'O'
    else:
        assert jugador == 'O'
        return 'X'

esquinas = None
vacio = '_'

def determina_posicion_en_diagonal_asc(gato, posicion):
    return sum(posicion) == len(gato) - 1
def determina_posicion_en_diagonal_desc(gato, posicion):
    return posicion[0] == posicion[1]

def determina_valor_por_lineas(gato, jugador, posicion):
    pos_i = posicion[0]
    pos_j = posicion[1]
    gato_len = len(gato)
    r = 0
    
    lineas = []
    
    lineas.append([gato[pos_i][j] for j in range(gato_len)])
    lineas.append([gato[i][pos_j] for i in range(gato_len)])
    
    if determina_posicion_en_diagonal_asc(gato, posicion):
        lineas.append(gato[i][gato_len - i - 1] for i in range(gato_len))
        
    if determina_posicion_en_diagonal_desc(gato, posicion):
        lineas.append(gato[i][i] for i in range(gato_len))
    
    lineas_gane = list(filter(lambda linea:Counter(linea)[jugador] == 2, lineas))
    lineas_bloqueo = list(filter(lambda linea:Counter(linea)[determina_jugador_opuesto(jugador)] == 2, lineas))
    lineas_parciales = list(filter(lambda linea:Counter(linea)[jugador] == 1 and Counter(linea)[vacio] == 2, lineas))
    
#    logger_cagada.debug("lineas gane {}".format(lineas_gane))
#    logger_cagada.debug("lineas blokeo {}".format(lineas_bloqueo))
#    logger_cagada.debug("lineas parciales {}".format(lineas_parciales))
    
    if lineas_parciales:
        r = 3
    if lineas_gane:
        r = 4
    if lineas_bloqueo:
        r = 5
    
    gato_tmp = deepcopy(gato)
    gato_tmp[posicion[0]][posicion[1]] = jugador
#    logger_cagada.debug("el valor de \n{} es {}".format(caca_comun_imprime_matrix(gato_tmp), r))
    return r

def determina_valor_posicion(posicion):
    r = 0
    if posicion in esquinas:
        r = 2
    else:
        r = 1
    return r

def determina_valor(gato, jugador, posicion):
    r = max(determina_valor_posicion(posicion), determina_valor_por_lineas(gato, jugador, posicion))
    gato_tmp = deepcopy(gato)
    gato_tmp[posicion[0]][posicion[1]] = jugador
#    logger_cagada.debug("el valor de \n{} es {}".format(caca_comun_imprime_matrix(gato_tmp), r))
    return r

def determina_posiciones_libres(gato):
    return [(i, j) for i in range(len(gato)) for j in range(len(gato)) if gato[i][j] == vacio]

def es_movimiento_ganador(gato, jugador, posicion):
    return determina_valor_por_lineas(gato, jugador, posicion) == 4

def es_movimiento_bloqueador(gato, jugador, posicion):
    return determina_valor_por_lineas(gato, jugador, posicion) == 5
    
def es_hoja(movimientos_cnt, gato, jugador, posicion_anterior):
    return not movimientos_cnt or es_movimiento_ganador(gato, jugador, posicion_anterior)

def determina_siguiente_movimiento(gato, jugador, jugador_actual, movimientos_cnt, posicion_anterior):
    mejor_pos = None
    puntaje_anterior = 0
    puntaje_actual = 0
    movimientos_cnt_final = movimientos_cnt
    jugador_anterior = determina_jugador_opuesto(jugador_actual)
    logger_cagada.debug("en gato\n{}".format(caca_comun_imprime_matrix(gato)))
    
    if posicion_anterior:
        puntaje_anterior = determina_valor(gato, jugador_anterior, posicion_anterior)
        if jugador != jugador_anterior:
            puntaje_anterior *= -1
    
    if not posicion_anterior or not es_hoja(movimientos_cnt, gato, jugador_anterior, posicion_anterior):
        gato_tmp = deepcopy(gato)
        if posicion_anterior:
            gato_tmp[posicion_anterior[0]][posicion_anterior[1]] = jugador_anterior
        
        logger_cagada.debug("gato orig \n{}\nact\n{} valor {}".format(caca_comun_imprime_matrix(gato), caca_comun_imprime_matrix(gato_tmp), puntaje_anterior))
        
        libres = determina_posiciones_libres(gato_tmp)
    
        if jugador == jugador_actual:
            funcion_comparacion = gt
        else:
            funcion_comparacion = lt
            
        for libre in libres:
            puntaje_actual_tmp, movimientos_cnt_tmp, _ = determina_siguiente_movimiento(gato_tmp, jugador, jugador_anterior, movimientos_cnt - 1, libre)
            if funcion_comparacion(puntaje_actual_tmp, puntaje_actual) or (puntaje_actual_tmp == puntaje_actual and movimientos_cnt_tmp > movimientos_cnt_final):
                puntaje_actual = puntaje_actual_tmp
                mejor_pos = libre
                movimientos_cnt_final = movimientos_cnt_tmp
    else:
        gato_tmp = deepcopy(gato)
        gato_tmp[posicion_anterior[0]][posicion_anterior[1]] = jugador_anterior
        if es_movimiento_bloqueador(gato, jugador, posicion_anterior):
            logger_cagada.debug("se blokea con\n{}".format(caca_comun_imprime_matrix(gato_tmp)))
        if es_movimiento_ganador(gato, jugador, posicion_anterior):
            logger_cagada.debug("se gana con\n{}".format(caca_comun_imprime_matrix(gato_tmp)))
        if not movimientos_cnt:
            logger_cagada.debug("no hay mas con\n{}".format(caca_comun_imprime_matrix(gato_tmp)))
    return puntaje_anterior + puntaje_actual, movimientos_cnt_final, mejor_pos

def core(gato, jugador):
    _, _, posi = determina_siguiente_movimiento(gato, jugador, jugador, len(determina_posiciones_libres(gato)), None)
    return posi
    
def caca_comun_imprime_matrix(matrix):
    return "\n".join(map(lambda linea:"".join(linea), matrix))

def main():
    jugador = input()
    gato = []
    for _ in range(3):
        gato.append(list(input()))
    
    llena_esquinas(gato)
    
    logger_cagada.debug("{}".format(gato))
    logger_cagada.debug("\n{}".format(caca_comun_imprime_matrix(gato)))
    pos = core(gato, jugador)
    print("{} {}".format(pos[0], pos[1]))

def llena_esquinas(gato):
    gato_len = len(gato)
    global esquinas
    esquinas = set([(0, 0), (0, gato_len - 1), (gato_len - 1, 0), (gato_len - 1, gato_len - 1)])

if __name__ == '__main__':
        FORMAT = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
        logging.basicConfig(level=nivel_log, format=FORMAT)
        logger_cagada = logging.getLogger("asa")
        logger_cagada.setLevel(nivel_log)
        main()
