from time import time
from time import sleep
from cv2 import cv2
from os import listdir
import sys
import numpy as np
import mss
import pyautogui
import yaml


abrir_config = open("config.yaml", "r")
carregar_config = yaml.safe_load(abrir_config)
pyautogui.PAUSE = carregar_config["tempo_clique"]
pyautogui.FAILSAFE = False


def remover_prefixo(string, prefixo):
    if prefixo and string.startswith(prefixo):
        return string[len(prefixo):]
    return string


def remover_sufixo(string, sufixo):
    if sufixo and string.endswith(sufixo):
        return string[:-len(sufixo)]
    return string


def carregar_imagens(dir_path='./alvos/'):
    arquivos = listdir(dir_path)
    alvos = {}
    for arquivo in arquivos:
        path = remover_prefixo(dir_path, './') + arquivo
        alvos[remover_sufixo(arquivo, '.PNG')] = cv2.imread(path)
    return alvos


def print_screen():
    with mss.mss() as sct:
        monitor = sct.monitors[0]
        sct_img = np.array(sct.grab(monitor))

    return sct_img[:, :, :3]


def posicoes(imagem, confianca=0.7, screenshot=None):
    if screenshot is None:
        screenshot = print_screen()

    resultado = cv2.matchTemplate(screenshot, imagem, cv2.TM_CCOEFF_NORMED)
    l = imagem.shape[1]
    a = imagem.shape[0]

    yloc, xloc = np.where(resultado >= confianca)

    retangulos = []

    for (x, y) in zip(xloc, yloc):
        retangulos.append([int(x), int(y), int(l), int(a)])
        retangulos.append([int(x), int(y), int(l), int(a)])

    retangulos, larguras = cv2.groupRectangles(retangulos, 1, 0.2)

    return retangulos


def mover(x, y):
    pyautogui.moveTo(x, y, 1)


def clicar(img, timeout=3, confianca=0.7):
    inicio = time()
    expirou = False
    while(not expirou):
        encontrou = posicoes(img, confianca=confianca)

        if(len(encontrou) == 0):
            expirou = time() - inicio > timeout
            continue

        x, y, l, a = encontrou[0]

        clicar_x = x+l/2
        clicar_y = y+a/2

        mover(clicar_x, clicar_y)
        pyautogui.click()

        return True

    return False


def login():
    clicar(imagens['conectar_metamask'], timeout=10)

    clicar(imagens['assinar'], timeout=8)

    sleep(carregar_config["tempo_fases"])
    clicar(imagens['cacar'], timeout=15)

    sleep(carregar_config["tempo_boss"])
    clicar(imagens['boss1'], timeout=10)

    return


def jogar():

    timeout = 5
    inicio = time()
    expirou = False
    while(not expirou):
        encontrou = posicoes(imagens["raio2"])

        if(len(encontrou) == 0):
            expirou = time() - inicio > timeout
            continue
        else:
            clicar(imagens["cacar_chefe"])
            sleep(carregar_config["tempo_comecar_jogo"])
            pyautogui.click()
            expirou = True

    return


def final():
    if(clicar(imagens["toque"])):

        sleep(carregar_config["tempo_abrir_bau"])

        pyautogui.click()

    clicar(imagens["derrotado"])
    return


def main():
    global imagens
    imagens = carregar_imagens()

    sleep(carregar_config["tempo_comecar_programa"])

    ultimo = {
        "login": 0,
        "jogar": 0,
        "final": 0,
        "atualizar": 0
    }

    while True:
        agora = time()

        if agora - ultimo["atualizar"] > 5400:
            ultimo["atualizar"] = agora
            pyautogui.hotkey('ctrl', 'f5')
            sleep(carregar_config["tempo_login"])

        if agora - ultimo["login"] > 60:
            ultimo["login"] = agora
            login()

        if agora - ultimo["jogar"] > 60:
            ultimo["jogar"] = agora
            jogar()

        if agora - ultimo["final"] > 60:
            ultimo["final"] = agora
            final()

        sys.stdout.flush()


if __name__ == '__main__':

    main()
