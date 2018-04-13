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
import sys

nivel_log = logging.ERROR
# nivel_log = logging.DEBUG
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


matrix_valores_linea = None


def determina_valor_por_lineas(gato, jugador, posicion, calcular_ganador=False):
    pos_i = posicion[0]
    pos_j = posicion[1]
    gato_len = len(gato)
    jugador_opuesto = determina_jugador_opuesto(jugador)
    lineas_peligrosas = 0
    lineas_buenas = 0
    r = 0
    
    gato_tmp = deepcopy(gato)
    gato_tmp[posicion[0]][posicion[1]] = jugador
    
    lineas = []
    
    lineas.append([gato[pos_i][j] for j in range(gato_len)])
    lineas.append([gato[i][pos_j] for i in range(gato_len)])
    
    if determina_posicion_en_diagonal_asc(gato, posicion):
        lineas.append(gato[i][gato_len - i - 1] for i in range(gato_len))
        
    if determina_posicion_en_diagonal_desc(gato, posicion):
        lineas.append(gato[i][i] for i in range(gato_len))
    
    for linea in lineas:
        cnt = Counter(linea)
        rt = matrix_valores_linea[cnt[jugador]][cnt[jugador_opuesto]][cnt[vacio]]
        logger_cagada.debug("cnt {} {} {} valor {}".format(cnt[jugador], cnt[jugador_opuesto], cnt[vacio], rt))
        
        if calcular_ganador and rt == 5:
            r = rt
            break
        
        if cnt[jugador_opuesto] == 1 and cnt[vacio] == 2:
            lineas_peligrosas += 1
        
        if cnt[jugador] == 1 and cnt[vacio] == 2:
            lineas_buenas += 1
            
        if lineas_buenas > 1 and rt < 4:
            rt = 4
        if lineas_peligrosas > 1:
            rt = 6
            
        if rt > r:
            r = rt
        
        if r == 6:
            break
    
    logger_cagada.debug("anal tirada {} el valor es {} jugador {}".format(caca_comun_matrix_a_linea(gato_tmp), r, jugador))
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
    logger_cagada.debug("determinando si es mov ganador {} jugador {}".format(caca_comun_matrix_a_linea(gato), jugador))
    return determina_valor_por_lineas(gato, jugador, posicion, True) == 5


def es_movimiento_bloqueador(gato, jugador, posicion):
    return determina_valor_por_lineas(gato, jugador, posicion) == 6

    
def es_hoja(movimientos_cnt, gato, jugador, posicion_anterior):
    r = not movimientos_cnt or es_movimiento_ganador(gato, jugador, posicion_anterior)
    logger_cagada.debug("determinando si es hoja {} {}".format(caca_comun_matrix_a_linea(gato), r))
    return r


cache = {}


def caca_comun_matrix_a_linea(matrix):
    return "".join(list(map(lambda linea:"".join(linea), matrix)))


def determina_siguiente_movimiento(gato, jugador, jugador_actual, movimientos_cnt, posicion_anterior, alfa, beta):
    mejor_pos = None
    puntaje_anterior = 0
    puntaje_actual = 0
    movimientos_cnt_final = movimientos_cnt
    maximizar = jugador == jugador_actual
    jugador_anterior = determina_jugador_opuesto(jugador_actual)
#    logger_cagada.debug("en gato\n{}".format(caca_comun_imprime_matrix(gato)))
    
    if posicion_anterior:
        puntaje_anterior = determina_valor(gato, jugador_anterior, posicion_anterior)
        if jugador != jugador_anterior:
            puntaje_anterior *= -1
            
    gato_tmp = deepcopy(gato)
    if posicion_anterior:
        gato_tmp[posicion_anterior[0]][posicion_anterior[1]] = jugador_anterior
    
    logger_cagada.debug("\n{} tirado por {}".format(caca_comun_imprime_matrix(gato_tmp), jugador_anterior))
        
    gato_s = caca_comun_matrix_a_linea(gato_tmp)
    if gato_s in cache:
        r = cache[gato_s]
        logger_cagada.debug("el mejor tiro cacheado para estado\n{} jugador {} es\n{} con putaje {}".format(gato_s, jugador_actual, caca_comun_imprime_matrix(gato_tmp), r[0]))   
        return r
    
    if not posicion_anterior or not es_hoja(movimientos_cnt, gato, jugador_anterior, posicion_anterior):
        
#        logger_cagada.debug("gato orig \n{}\nact\n{} valor {}".format(caca_comun_imprime_matrix(gato), caca_comun_imprime_matrix(gato_tmp), puntaje_anterior))
        
        libres = determina_posiciones_libres(gato_tmp)
    
        if maximizar:
            funcion_comparacion = gt
        else:
            funcion_comparacion = lt
            
        for libre in libres:
            puntaje_actual_tmp, movimientos_cnt_tmp, _ , alfa, beta = determina_siguiente_movimiento(gato_tmp, jugador, jugador_anterior, movimientos_cnt - 1, libre, alfa, beta)
            gato_tmp_x = deepcopy(gato_tmp)
            gato_tmp_x[libre[0]][libre[1]] = jugador_actual
            logger_cagada.debug("valor de {} es {} {} el original era {} jugador actual {}".format(caca_comun_matrix_a_linea(gato_tmp_x), puntaje_actual_tmp, movimientos_cnt_tmp, caca_comun_matrix_a_linea(gato_tmp), jugador_actual))
            if not mejor_pos or funcion_comparacion(puntaje_actual_tmp, puntaje_actual) or (puntaje_actual_tmp == puntaje_actual and movimientos_cnt_tmp > movimientos_cnt_final):
                puntaje_actual = puntaje_actual_tmp
                mejor_pos = libre
                movimientos_cnt_final = movimientos_cnt_tmp
            if maximizar:
                alfa = max(alfa, puntaje_actual_tmp)
            else:
                beta = min(beta, puntaje_actual_tmp)
            if beta <= alfa:
                break
    else:
        if es_movimiento_bloqueador(gato, jugador_anterior, posicion_anterior):
            pass
            logger_cagada.debug("se blokea con\n{}".format(caca_comun_imprime_matrix(gato_tmp)))
        if es_movimiento_ganador(gato, jugador_anterior, posicion_anterior):
            pass
            logger_cagada.debug("se gana con\n{} putaje {}".format(caca_comun_imprime_matrix(gato_tmp), puntaje_anterior))
        if not movimientos_cnt:
            pass
            logger_cagada.debug("no hay mas con\n{} jugador {} putaje {}".format(caca_comun_imprime_matrix(gato_tmp), jugador_anterior, puntaje_anterior))
    cache[gato_s] = puntaje_anterior + puntaje_actual, movimientos_cnt_final, mejor_pos, alfa, beta
    gato_tmp_1 = deepcopy(gato)
    if posicion_anterior:
        gato_tmp_1[posicion_anterior[0]][posicion_anterior[1]] = jugador_anterior
    gato_tmp_2 = deepcopy(gato_tmp)
    if mejor_pos:
        gato_tmp_2[mejor_pos[0]][mejor_pos[1]] = jugador_actual
#    logger_cagada.debug("el mejor tiro para estado\n{} jugador {} es\n{} con putaje {}".format(caca_comun_matrix_a_linea(gato_tmp_1), jugador_actual, caca_comun_imprime_matrix(gato_tmp_2), puntaje_actual))   
    logger_cagada.debug("el mejor tiro para estado\n{} jugador {} es\n{} con putaje {}".format(caca_comun_imprime_matrix(gato_tmp_1), jugador_actual, caca_comun_imprime_matrix(gato_tmp_2), puntaje_actual))   
    return puntaje_anterior + puntaje_actual, movimientos_cnt_final, mejor_pos, alfa, beta


def core(gato, jugador):
    _, _, posi, _, _ = determina_siguiente_movimiento(gato, jugador, jugador, len(determina_posiciones_libres(gato)), None, -sys.maxsize, sys.maxsize)
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
    global matrix_valores_linea
    esquinas = set([(0, 0), (0, gato_len - 1), (gato_len - 1, 0), (gato_len - 1, gato_len - 1)])
    matrix_valores_linea = []
    for _ in range(4):
        m = []
        for _ in range(4):
            m.append([0] * 4)
        matrix_valores_linea.append(m)
    matrix_valores_linea[1][0][2] = 3
    matrix_valores_linea[2][0][1] = 5
    matrix_valores_linea[0][2][1] = 6
#    matrix_valores_linea[3][0][0] = 4


if __name__ == '__main__':
        FORMAT = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
        logging.basicConfig(level=nivel_log, format=FORMAT)
        logger_cagada = logging.getLogger("asa")
        logger_cagada.setLevel(nivel_log)
        main()

