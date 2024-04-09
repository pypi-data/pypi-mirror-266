# SAMBA Copyright (C) 2024 - Closed source


#---------------------------
poscar = open('POSCAR', 'r')
VTemp = poscar.readline();  VTemp = str(VTemp)
poscar.close()
#-------------

with open('CONTCAR', 'r') as file: line = file.readlines()
line[0] = VTemp
with open('CONTCAR', 'w') as file: file.writelines(line)
