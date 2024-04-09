# SAMBA Copyright (C) 2024 - Closed source


#----------------------------------------------------------------------------
# Função para simular a digitação de comandos no terminal Linux -------------
#----------------------------------------------------------------------------
def command_terminal(command):
    command = command.split()
    vector_command = []
    for i in range(len(command)):  vector_command.append(command[i])
    subprocess.run(vector_command)

#----------------------------------------------------------------------------
# Função para listar todas os arquivos dentro de um dado diretório ----------
#----------------------------------------------------------------------------
def list_files(dir):
   l_files = [name for name in os.listdir(dir) if os.path.isfile(os.path.join(dir, name))]
   return l_files

#----------------------------------------------------------------------------
# Função para listar todas as pastas dentro de um dado diretório ------------
#----------------------------------------------------------------------------
def list_folders(dir):
   l_folders = [name for name in os.listdir(dir) if os.path.isdir(os.path.join(dir, name))]
   return l_folders

#----------------------------------------------------------------------------
# Resetando o diretório 'output' --------------------------------------------
#----------------------------------------------------------------------------
if os.path.isdir(dir_out):
   shutil.rmtree(dir_out)
   os.mkdir(dir_out)
else: os.mkdir(dir_out)
#----------------------



print(" ")
print("-------------------------------------------------------------------------")
print("Criando diretórios e copiando arquivos POSCAR e de input do VASProcar ---")
print("-------------------------------------------------------------------------")

files = list_files('Structures')
#------------------------------------------
t = 1.0; number = -1; n_passos = len(files)
#------------------------------------------

for i in range(len(files)):
    #----------------------
    number += 1
    porc = (number/n_passos)*100        
    #---------------------------
    if (porc >= t and porc <= 100):
       print(f'Progresso  {porc:>3,.0f}%')                 
       number += 1
       if (number == 1): t = 1
       if (number == 2): t = 1
       if (number >= 3): t = t + 1
       #--------------------------
              
    #---------------------------------
    os.mkdir(dir_out + '/' + files[i])
    #---------------------------------
    for j in range(len(task)):
        #==================================================
        dir_task = dir_out + '/' + files[i] + '/' + task[j]
        dir_inputs = dir_codes + '/INPUTS/inputs_VASProcar'
        #==================================================
        os.mkdir(dir_task)
        shutil.copyfile('Structures' + '/' + files[i], dir_task + '/POSCAR')
        #===================================================================
        if (task[j] == 'relax'):
           shutil.copyfile(dir_codes + '/contcar_update.py', dir_task + '/contcar_update.py')
        #====================================================================================
        if (task[j][:3] == 'dos'):
           os.mkdir(dir_out + '/' + files[i] + '/' + task[j] + '/inputs') 
           shutil.copyfile(dir_inputs + '/input.vasprocar.dos', dir_task + '/inputs/input.vasprocar.dos')
        #================================================================================================
        if (task[j][:3] == 'scf'):
           os.mkdir(dir_out + '/' + files[i] + '/' + task[j] + '/inputs')
           shutil.copyfile(dir_inputs + '/input.vasprocar.locpot', dir_task + '/inputs/input.vasprocar.locpot')
        #======================================================================================================
        if (task[j][:5] == 'bands'):
           os.mkdir(dir_out + '/' + files[i] + '/' + task[j] + '/inputs')
           shutil.copyfile(dir_inputs + '/input.vasprocar.orbitals', dir_task + '/inputs/input.vasprocar.orbitals')
           shutil.copyfile(dir_inputs + '/input.vasprocar.locpot', dir_task + '/inputs/input.vasprocar.locpot') 
           shutil.copyfile(dir_inputs + '/input.vasprocar.bands', dir_task + '/inputs/input.vasprocar.bands')
           if (task[j][-3:] == '.SO'):
              shutil.copyfile(dir_inputs + '/input.vasprocar.spin', dir_task + '/inputs/input.vasprocar.spin') 
           #---------------------------------------
           poscar = open(dir_task + '/POSCAR', 'r')
           VTemp1 = poscar.readline().split();  poscar.close()
           #--------------------------------------------------           
           if (len(VTemp1) >= 3):
              #------------------
              shutil.copyfile(dir_inputs + '/input.vasprocar.location', dir_task + '/inputs/input.vasprocar.location')
              #-------------------------------------------------------------------------------------------------------
              label_materials = VTemp1[0].replace('+', ' ').split()
              range_ion_Lattice = []; nion = 0
              #------------------------------------
              for m in range(len(label_materials)):
                  range_ion_Lattice.append( str(1 + nion) + ':')
                  nion += int(VTemp1[m+1])
                  range_ion_Lattice[m] += str(nion) 
              #--------------------------------------------------------------------------------------------
              # Atualizando o arquivo input.vasprocar.location --------------------------------------------
              #--------------------------------------------------------------------------------------------
              with open(dir_task + '/inputs/input.vasprocar.location', "r") as file:  content = file.read()
              content = content.replace('replace_n_reg', str(len(label_materials)))
              for m in range(len(label_materials)):
                  content = content.replace('replace_label_Lattice' + str(m+1), str(label_materials[m].replace('_', '')))
                  content = content.replace('replace_nion_Lattice' + str(m+1), str(range_ion_Lattice[m]))
              with open(dir_task + '/inputs/input.vasprocar.location', "w") as file: file.write(content)
        #===============================================================================================
        if (task[j][:5] == 'bader'):
           #-----------------------------------------------------------------------------------
           shutil.copyfile(dir_codes + '/charge_transfer.py', dir_task + '/charge_transfer.py')
           shutil.copyfile(dir_codes + '/bader_update.py', dir_task + '/bader_update.py')
           dir_poscar = dir_out + '/' + files[i] + '/' + task[j]
           exec(open(dir_codes + '/bader_poscar.py').read())
           #------------------------------------------------



print(" ")
print("-------------------------------------------------------------------------")
print("Criando arquivos POTCAR para cada material ------------------------------")
print("-------------------------------------------------------------------------")

files0 = list_folders(dir_out)
#-------------------------------------------
t = 1.0; number = -1; n_passos = len(files0)
#-------------------------------------------

for i in range(len(files0)):
    #-----------------------
    number += 1
    porc = (number/n_passos)*100        
    #-----------------------------
    if (porc >= t and porc <= 100):
       print(f'Progresso  {porc:>3,.0f}%')                 
       number += 1
       if (number == 1): t = 1
       if (number == 2): t = 1
       if (number >= 3): t = t + 1
       #--------------------------

    for j in range(len(task)):
        #---------------------------
        if (task[j][:5] != 'bader'):
           dir_poscar = dir_out + '/' + files0[i] + '/' + task[j] + '/POSCAR'
           dir_potcar = dir_out + '/' + files0[i] + '/' + task[j] + '/POTCAR'
           exec(open(dir_codes + '/potcar.py').read())
           #------------------------------------------
        if (task[j][:5] == 'bader'):
           #---------------------------------------------------------------
           files1 = list_folders(dir_out + '/' + files0[i] + '/' + task[j])
           #---------------------------------------------------------------
           for k in range(len(files1)):
               if (files1[k] != 'Charge_transfer'):
                  dir_poscar = dir_out + '/' + files0[i] + '/' + task[j] + '/' + files1[k] + '/POSCAR'
                  dir_potcar = dir_out + '/' + files0[i] + '/' + task[j] + '/' + files1[k] + '/POTCAR'
                  exec(open(dir_codes + '/potcar.py').read())



print(" ")
print("-------------------------------------------------------------------------")
print("Criando arquivo KPOINT para cada material -------------------------------")
print("-------------------------------------------------------------------------")

#----------------------------------------------------------------
exec(open(dir_codes + '/INPUTS/POTCAR/cut_off_energy.py').read())
#----------------------------------------------------------------

files = list_folders(dir_out)
#------------------------------------------
t = 1.0; number = -1; n_passos = len(files)
#------------------------------------------

for i in range(len(files)):
    #---------------------------
    number += 1
    porc = (number/n_passos)*100        
    #---------------------------
    if (porc >= t and porc <= 100):
       print(f'Progresso  {porc:>3,.0f}%')                 
       number += 1
       if (number == 1): t = 1
       if (number == 2): t = 1
       if (number >= 3): t = t + 1
       #--------------------------

    for m in range(len(task)):
        #--------------------------------------------------
        if (task[m][:5] == 'relax'):  k_dens = k_dens_relax
        if (task[m][:5] == 'bader'):  k_dens = k_dens_bader
        if (task[m][:3] == 'scf'):    k_dens = k_dens_scf
        if (task[m][:3] == 'dos'):    k_dens = k_dens_dos
        #--------------------------------------------------
        if (task[m][:5] != 'bader'):
           #----------------------------------------------------
           path_vaspkit = dir_o + '/' + files[i] + '/' + task[m]
           exec(open(dir_codes + '/kpoints.py').read())
           #------------------------
        if (task[m][:5] == 'bader'):
           files1 = list_folders(dir_out + '/' + files0[i] + '/' + task[m])
           for k in range(len(files1)):
               if (files1[k] != 'Charge_transfer'):
                  #----------------------------------------------------------------------
                  path_vaspkit = dir_o + '/' + files[i] + '/' + task[m] + '/' + files1[k]
                  exec(open(dir_codes + '/kpoints.py').read())
                  #-------------------------------------------



print(" ")
print("-------------------------------------------------------------------------")
print("Criando arquivo INCAR para cada material -------------------------------")
print("-------------------------------------------------------------------------")

#------------------------------------------
t = 1.0; number = -1; n_passos = len(files)
#------------------------------------------

for i in range(len(files)):
    #---------------------------
    number += 1
    porc = (number/n_passos)*100        
    #---------------------------
    if (porc >= t and porc <= 100):
       print(f'Progresso  {porc:>3,.0f}%')                 
       number += 1
       if (number == 1): t = 1
       if (number == 2): t = 1
       if (number >= 3): t = t + 1
       #--------------------------

    #--------------
    ENCUT = -1000.0
    #-----------------------------------------------------------------------
    poscar = open(dir_out + '/' + files[i] + '/' + task[0] + '/POSCAR', 'r')
    #-----------------------------------------------------------------------
    for j in range(6):  VTemp1 = poscar.readline().split()
    poscar.close()
    #---------------------------
    for j in range(len(VTemp1)):
        temp = globals()['ENCUT_' + str(VTemp1[j])]   # Obtendo o valor da varíavel ENCUT para o correspondente átomo.
        if (ENCUT <= temp):  ENCUT = temp
    ENCUT = ENCUT*(1.3); ENCUT = float(int(ENCUT) +1)


    for j in range(len(task)):
        #--------------------------------------------
        if (task[m][:5] == 'bands'): type_kpoints = 0
        if (task[m][:5] == 'relax'):
           k_dens = 1/k_dens_relax;  type_kpoints = 1
        if (task[m][:5] == 'bader'):
           k_dens = 1/k_dens_bader;  type_kpoints = 1
        if (task[m][:3] == 'scf'):
           k_dens = 1/k_dens_scf;    type_kpoints = 1
        if (task[m][:3] == 'dos'):
           k_dens = 1/k_dens_dos;    type_kpoints = 1
        #--------------------------------------------


        if (task[j][:5] != 'bader'):
           #-------------------------------------------------------
           dir_incar = dir_codes + '/INPUTS/' + 'INCAR_' + task[j]
           dir_output = dir_out + '/' + files[i] + '/' + task[j] + '/INCAR'
           #----------------------------------------------------------------
           shutil.copyfile(dir_incar, dir_output)
           #---------------------------------------------------------------
           # Inserindo o valor de ENCUT em cada arquivo INCAR -------------
           #---------------------------------------------------------------
           with open(dir_output, "r") as file:  content = file.read()
           content = content.replace('replace_encut', str(ENCUT))
           if (type_kpoints == 1):
              if (type_k_dens == 3):
                 content = content.replace('# KSPACING', 'KSPACING = ' + str(k_dens))
                 content = content.replace('# KGAMMA',   'KGAMMA = ' + 'False')
              if (type_k_dens == 4):
                 content = content.replace('# KSPACING', 'KSPACING = ' + str(k_dens))
                 content = content.replace('# KGAMMA',   'KGAMMA = ' + 'True')
           with open(dir_output, "w") as file: file.write(content)


        if (task[j][:5] == 'bader'):
           #--------------------------------------------------------------
           files2 = list_folders(dir_out + '/' + files[i] + '/' + task[j])
           for k in range(len(files2)):
              if (files2[k] != 'Charge_transfer'):
                 #-------------------------------------------------------
                 dir_incar = dir_codes + '/INPUTS/' + 'INCAR_' + task[j]
                 dir_output = dir_out + '/' + files[i] + '/' + task[j] + '/' + files2[k] + '/INCAR'
                 #-----------------------------------------------------------------------------------------------------------
                 shutil.copyfile(dir_codes + '/bader', dir_out + '/' + files[i] + '/' + task[j] + '/' + files2[k] + '/bader')
                 shutil.copyfile(dir_codes + '/chgsum.pl', dir_out + '/' + files[i] + '/' + task[j] + '/' + files2[k] + '/chgsum.pl')
                 shutil.copyfile(dir_incar, dir_output)
                 #---------------------------------------------------------------------------------
                 # Inserindo o valor de ENCUT em cada arquivo INCAR -------------------------------
                 #---------------------------------------------------------------------------------
                 with open(dir_output, "r") as file:  content = file.read()
                 content = content.replace('replace_encut', str(ENCUT))
                 if (type_kpoints == 1):
                    if (type_k_dens == 3):
                       content = content.replace('# KSPACING', 'KSPACING = ' + str(k_dens))
                       content = content.replace('# KGAMMA',   'KGAMMA = ' + 'False')
                    if (type_k_dens == 4):
                       content = content.replace('# KSPACING', 'KSPACING = ' + str(k_dens))
                       content = content.replace('# KGAMMA',   'KGAMMA = ' + 'True')
                 with open(dir_output, "w") as file: file.write(content)
           #--------------------------------------------------------------
           os.remove(dir_out + '/' + files[i] + '/' + task[j] + '/POSCAR')
           #--------------------------------------------------------------


    #---------------------------------------------------------------------------------
    # Criando o arquivo output.py para o diretorio principal -------------------------
    #---------------------------------------------------------------------------------
    shutil.copyfile(dir_codes + '/output.py', dir_out + '/' + files[i] + '/output.py')
    #---------------------------------------------------------------------------------


###################################################################
# Escrevendo o arquivo de job para execução dos cálculos de DFT ###
###################################################################
exec(open(dir_codes + '/job.py').read())
#---------------------------------------
