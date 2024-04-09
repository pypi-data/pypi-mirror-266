# SAMBA Copyright (C) 2024 - Closed source

import numpy as np
import subprocess
import pyfiglet
import shutil
import time
import os

version = '1.0.0.1'

print(" ")
print("=============================================================")
print(f'SAMBA v{version} Copyright (C) 2024 ---------------------------')
print("Closed source: Adalberto Fazzio's research group (Ilum|CNPEM)")
print("Author: Augusto de Lelis Araujo -----------------------------")
print("=============================================================")
texto = pyfiglet.figlet_format("SAMBA", font="slant", width=100, justify="left")
print(texto)

#------------------------------------------------
# Checking for updates for VASProcar ------------
#------------------------------------------------
try:
    url = f"https://pypi.org/pypi/{'sampa'}/json"
    response = requests.get(url)
    dados = response.json()
    current_version = dados['info']['version']; current_version = str(current_version)
    if (current_version != version):
       print(" ")
       print("--------------------------------------------------------------")
       print("        !!!!! Your SAMBA version is out of date !!!!!         ")
       print("--------------------------------------------------------------")
       print("    To update, close the SAMBA and enter into the terminal:   ")
       print("                 pip install --upgrade samba                  ")
       print("--------------------------------------------------------------")
       print(" ")
       print(" ")
    ...
except Exception as e:
    print("--------------------------------------------------------------")
    print("    !!!! Unable to verify the current version of SAMBA !!!!   ")
    print("--------------------------------------------------------------") 
    print(" ")



#================================================
tasks = ['relax', 'scf', 'bands', 'dos', 'bader']          # As tarefas são executadas em sequência, logo: 'relax' e 'scf' devem estar na 1º e 2º posições, respectivamentety.
type  = ['sem_SO','com_SO']                                # Define se as tarefas serão realizadas sem e/ou com SO. 'relax' sempre é executados sem SO.
# tasks = ['relax', 'scf', 'bands', 'dos', 'bader']
# type  = ['sem_SO','com_SO']    
#============================
type_k_dens  = 1            # [1] KPOINTS (Monkhorst-Pack);  [2]  KPOINTS (Gamma);  [3] INCAR (KSPACING Monkhorst-Pack);  [4] INCAR (KSPACING Gamma)
k_dens_relax = 12           # Cálculo de relaxação:            nº de pontos-k por Angs^-1
k_dens_scf   = 12           # Cálculo auto-consistente (scf):  nº de pontos-k por Angs^-1
k_dens_dos   = 12           # Cálculo da DOS:                  nº de pontos-k por Angs^-1
k_dens_bader = 12           # Cálculo da Carga de Bader:       nº de pontos-k por Angs^-1
n_kpoints    = 50           # Cálculo das bandas (nscf):       nº de pontos-k em cada trecho do plot da banda
nions_split  = 100          # nº de ions no arquivo POSCAR, para que o cálculo da banda seja executado em etapas (splitado) 



#=======================================================
# !!!!! Verificar diretório abaixo antes de rodar !!!!!!
dir_virtual_python = '/home/dlelis/codes/python_virtual'
# !!!!! Verificar diretório abaixo antes de rodar !!!!!!
#=======================================================

#----------------------
dir_files = os.getcwd()
os.chdir(os.path.dirname(os.path.realpath(__file__)))
#----------------------------------------------------
dir_codes = '/src'
dir_o     = 'WFlow_output'
dir_out   = dir_files + '/' + dir_o
dir_virtual_python += '/bin/activate'
#------------------------------------
task = []
for i in range(len(tasks)):
    if (tasks[i] == 'relax'):  task.append(tasks[i])
    for j in range(len(type)):
        if (type[j] == 'sem_SO'):  rot = '' 
        if (type[j] == 'com_SO'):  rot = '.SO' 
        if (tasks[i] != 'relax'):  task.append(tasks[i] + rot)
#-------------------------------------------------------------

#==============================================
exec(open(dir_codes + '/make_files.py').read())
#==============================================

print(" ")
print("=============")
print("Concluido ===")
print("=============")
print(" ")

