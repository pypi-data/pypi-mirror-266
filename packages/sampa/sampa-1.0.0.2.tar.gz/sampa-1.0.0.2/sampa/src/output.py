# SAMBA Copyright (C) 2024 - Closed source


import os
import shutil


#------------------------
current_dir = os.getcwd()
folders = folders = [name for name in os.listdir(current_dir) if os.path.isdir(os.path.join(current_dir, name))]
#---------------------------------------------------------------------------------------------------------------
if os.path.isdir('output'):
   0 == 0
else:
   os.mkdir('output')
#--------------------


for i in range(len(folders)):
    #-----------------------------------
    dir_folders = folders[i] + '/output'
    #-----------------------------------
    if (folders[i] == 'scf'):
       if os.path.isdir(dir_folders + '/Potencial'):  shutil.copytree(dir_folders + '/Potencial',  'output/Potencial_scf')
       if os.path.isdir(dir_folders):                 shutil.rmtree(dir_folders)
    #--------------------------------
    if (folders[i] == 'scf.SO'):
       if os.path.isdir(dir_folders + '/Potencial'):  shutil.copytree(dir_folders + '/Potencial',  'output/Potencial_scf_SO')
       if os.path.isdir(dir_folders):                 shutil.rmtree(dir_folders)
    #--------------------------------
    if (folders[i] == 'dos'):
       if os.path.isdir(dir_folders + '/DOS'):  shutil.copytree(dir_folders + '/DOS',  'output/DOS')
       if os.path.isdir(dir_folders):           shutil.rmtree(dir_folders)
    #--------------------------------
    if (folders[i] == 'dos.SO'):
       if os.path.isdir(dir_folders + '/DOS'):  shutil.copytree(dir_folders + '/DOS',  'output/DOS_SO')
       if os.path.isdir(dir_folders):           shutil.rmtree(dir_folders)
    #--------------------------------
    if (folders[i] == 'bands'):
       if os.path.isdir(dir_folders + '/Bandas'):       shutil.copytree(dir_folders + '/Bandas',  'output/Bandas')
       if os.path.isdir(dir_folders + '/Orbitais'):     shutil.copytree(dir_folders + '/Orbitais',  'output/Orbitais')
       if os.path.isdir(dir_folders + '/Localizacao'):  shutil.copytree(dir_folders + '/Localizacao',  'output/Localizacao')
       if os.path.isdir(dir_folders + '/Potencial'):    shutil.copytree(dir_folders + '/Potencial',  'output/Potencial_bands')
       if os.path.isdir(dir_folders):                   shutil.copyfile(dir_folders + '/informacoes.txt',  'output/informacoes.txt')
       if os.path.isdir(dir_folders):                   shutil.rmtree(dir_folders)
    #--------------------------------
    if (folders[i] == 'bands.SO'):
       if os.path.isdir(dir_folders + '/Spin'):         shutil.copytree(dir_folders + '/Spin',  'output/Spin')
       if os.path.isdir(dir_folders + '/Bandas'):       shutil.copytree(dir_folders + '/Bandas',  'output/Bandas_SO')
       if os.path.isdir(dir_folders + '/Orbitais'):     shutil.copytree(dir_folders + '/Orbitais',  'output/Orbitais_SO')
       if os.path.isdir(dir_folders + '/Localizacao'):  shutil.copytree(dir_folders + '/Localizacao',  'output/Localizacao_SO')
       if os.path.isdir(dir_folders + '/Potencial'):    shutil.copytree(dir_folders + '/Potencial',  'output/Potencial_bands_SO')
       if os.path.isdir(dir_folders):                   shutil.copyfile(dir_folders + '/informacoes.txt',  'output/informacoes_SO.txt')
       if os.path.isdir(dir_folders):                   shutil.rmtree(dir_folders)
    #--------------------------------
    if (folders[i] == 'bader'):
       if os.path.isdir(folders[i] + '/Charge_transfer'):  shutil.copytree(folders[i] + '/Charge_transfer',  'output/Charge_transfer')
       if os.path.isdir(folders[i] + '/Charge_transfer'):  shutil.rmtree(folders[i] + '/Charge_transfer')
    #--------------------------------
    if (folders[i] == 'bader.SO'):
       if os.path.isdir(folders[i] + '/Charge_transfer'):  shutil.copytree(folders[i] + '/Charge_transfer',  'output/Charge_transfer_SO')
       if os.path.isdir(folders[i] + '/Charge_transfer'):  shutil.rmtree(folders[i] + '/Charge_transfer')
    #--------------------------------












