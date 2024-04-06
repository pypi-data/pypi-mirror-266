# VASProcar Copyright (C) 2023
# GNU GPL-3.0 license

#===============================================================================
# Copying the image containing the Greek Alphabet list to the output folder ====
#===============================================================================

if (dest_k == 2):
   source = main_dir + '/etc/Greek_alphabet.jpg'
   destination = dir_files + '/output/Greek_alphabet.jpg'
   shutil.copyfile(source, destination)


#==============================================================================
# Getting the position of the k-points in the plot of the bands/projections ===
#==============================================================================

nk_total = n_procar*nk
separacao = [0.0]*(nk_total +1)

#--------------------------------------------------------
inform = open(dir_files + '/output/informacoes.txt', "r")
#--------------------------------------------------------
                    
palavra = 'k-points |'

for line in inform:   
    if palavra in line: 
       break

VTemp = inform.readline()
VTemp = inform.readline()
       
for i in range (1,(nk_total+1)):
    VTemp = inform.readline().split()
    r1 = int(VTemp[0]); r2 = float(VTemp[1]); r3 = float(VTemp[2]); r4 = float(VTemp[3])
    #-------------------------------
    if (len(VTemp) == 5):
       comprimento = float(VTemp[4])
    if (len(VTemp) == 8):
       comprimento = float(VTemp[7])
    #-------------------------------
    separacao[i] = comprimento

#-------------
inform.close()
#-------------


#======================================================================
# Warning message for user to edit KPOINTS file (n_procar = 1) ========
#======================================================================

if (dest_k == 2 and n_procar == 1):
   #----------------------------
   number = 0;     k_point = 0
   dest_pk  = [];  label_pk = []
   #----------------------------

   if (len(inputs) == 0):
      print("")
      print ("=============================================================================================")
      print ("Attention: Edit the KPOINTS file, inserting the desired label in the k-points of the file.   ")
      print ("               !!!! All k-points present in the KPOINTS file, must be labeled !!!!           ") 
      print ("=============================================================================================")
      print ("Example:                                                                                     ")
      print ("         0.0 0.0 0.0 #1 (Gamma)                                                              ")
      print ("         0.5 0.5 0.0 M                                                                       ")
      print ("                                                                                             ")
      print ("         0.5 0.5 0.0 M                                                                       ")
      print ("         0.5 0.0 0.0 X                                                                       ")
      print ("=============================================================================================")
      print ("Use the following codes (#number) for using Greek symbols as labels:                         ") 
      print ("                                                                                             ")
      print ("#1  = Gamma       |  #2  = gamma        |  #3  = Delta     |  #4  = delta       |               ")
      print ("#5  = Lambda      |  #6  = lambda       |  #7  = Sigma     |  #8  = sigma       |               ")
      print ("#9  = Theta       |  #10 = tetha        |  #11 = Omega     |  #12 = omega       |               ")
      print ("#13 = Psi         |  #14 = psi          |  #15 = Phi       |  #16 = phi         |  #17 = varphi ")
      print ("#18 = alfa        |  #19 = beta         |  #20 = pi        |  #21 = rho         |               ")
      print ("#22 = tau         |  #23 = upsilon      |  #24 = mu        |  #25 = nu          |               ")
      print ("#26 = epsilon     |  #27 = eta          |  #28 = kappa     |  #29 = xi          |  #30 = zeta   ")
      print ("#31 = left_arrow  |  #32 = right_arrow  |  #33 = up_arrow  |  #34 = down_arrow  |               ")
      print ("=============================================================================================")
      print ("After editing the KPOINTS file, press [ENTER] to continue                                    ")
      print ("=============================================================================================")
      confirmacao = input (" "); confirmacao = str(confirmacao) 


   #------------
   n_kpoints = 0
   #------------
   try:
       f = open(dir_files + '/KPOINTS')
       f.close()
       n_kpoints = 1
   except:
       print("")
       print("... Missing KPOINTS file ...") 
       print("")
       print("--------------------------------------------------------------------------")
       print("After inserting the KPOINTS file in the directory, press ENTER to continue")
       print("--------------------------------------------------------------------------")
       confirmacao = input (" "); confirmacao = str(confirmacao)       


   #============================================================================
   # Getting the number of k-points to be highlighted in the Bands structure ===
   #============================================================================    

   #------------------------------------------
   kpoints = open(dir_files + '/KPOINTS', "r")
   #------------------------------------------
   VTemp = kpoints.readline()
   VTemp = kpoints.readline();  points_path = int(VTemp)

   for i in range (100):
       VTemp = kpoints.readline().split()
       if (len(VTemp) >= 4):
          #----------
          number += 1 
          resto = (number % 2)
          #-------------------
          if (resto == 1):  k_point = k_point + 1
          if (resto == 0):  k_point = k_point + (points_path - 1)
          #--------------------------------
          if (resto == 1 or k_point == nk):
             dest_pk.append(separacao[k_point])
             label_pk.append(str(VTemp[3]))

   #------------------------
   contador2 = len(label_pk)
   #--------------
   kpoints.close()
   #--------------


#======================================================================
# Warning message for user to edit KPOINTS file (n_procar > 1) ========
#======================================================================

if (dest_k == 2 and n_procar > 1):
   #------------------------------------------
   k_point = 0;  dest_pk  = [];  label_pk = []
   #------------------------------------------
   for i in range (n_procar):


       if (len(inputs) == 0 and i == 0):
          print("")
          print ("=============================================================================================")
          print ("Attention: Edit the KPOINTS file, inserting the desired label in the k-points of the file.   ")
          print ("               !!!! All k-points present in the KPOINTS file, must be labeled !!!!           ") 
          print ("=============================================================================================")
          print ("Example:                                                                                     ")
          print ("         0.0 0.0 0.0 #1 (Gamma)                                                              ")
          print ("         0.5 0.5 0.0 M                                                                       ")
          print ("                                                                                             ")
          print ("         0.5 0.5 0.0 M                                                                       ")
          print ("         0.5 0.0 0.0 X                                                                       ")
          print ("=============================================================================================")
          print ("Use the following codes (#number) for using Greek symbols as labels:                         ") 
          print ("                                                                                             ")
          print ("#1  = Gamma       |  #2  = gamma        |  #3  = Delta     |  #4  = delta       |               ")
          print ("#5  = Lambda      |  #6  = lambda       |  #7  = Sigma     |  #8  = sigma       |               ")
          print ("#9  = Theta       |  #10 = tetha        |  #11 = Omega     |  #12 = omega       |               ")
          print ("#13 = Psi         |  #14 = psi          |  #15 = Phi       |  #16 = phi         |  #17 = varphi ")
          print ("#18 = alfa        |  #19 = beta         |  #20 = pi        |  #21 = rho         |               ")
          print ("#22 = tau         |  #23 = upsilon      |  #24 = mu        |  #25 = nu          |               ")
          print ("#26 = epsilon     |  #27 = eta          |  #28 = kappa     |  #29 = xi          |  #30 = zeta   ")
          print ("#31 = left_arrow  |  #32 = right_arrow  |  #33 = up_arrow  |  #34 = down_arrow  |               ")
          print ("=============================================================================================")
          print ("After editing the KPOINTS file, press [ENTER] to continue                                    ")
          print ("=============================================================================================")
          confirmacao = input (" "); confirmacao = str(confirmacao) 


       #------------
       n_kpoints = 0
       #------------
       try:
           f = open(dir_files + '/KPOINTS.' + str(i+1))
           f.close()
           n_kpoints = 1
       except:
           print("")
           print(f'... Missing KPOINTS.{str(i+1)} file ...') 
           print("")
           print("----------------------------------------------------------------------------")
           print(f'After inserting the KPOINTS.{str(i+1)} file in the directory, press ENTER to continue')
           print("----------------------------------------------------------------------------")
           confirmacao = input (" "); confirmacao = str(confirmacao)       


       #============================================================================
       # Getting the number of k-points to be highlighted in the Bands structure ===
       #============================================================================

       #------------------------------------------------------
       kpoints = open(dir_files + '/KPOINTS.' + str(i+1), "r")
       #------------------------------------------------------
       VTemp = kpoints.readline()
       VTemp = kpoints.readline();  points_path = int(VTemp)
       for j in range (2): VTemp = kpoints.readline()
       #---------------------------------------------
       number = 0
       for j in range(2):
           VTemp = kpoints.readline().split()
           if (len(VTemp) >= 4):
              #----------
              number += 1 
              resto = (number % 2)
              #-------------------
              if (resto == 1):  k_point = k_point + 1
              if (resto == 0):  k_point = k_point + (points_path - 1)
              #--------------------------------
              if (resto == 1 or k_point == nk):
                 dest_pk.append(separacao[k_point])
                 label_pk.append(str(VTemp[3]))     

       #--------------
       kpoints.close()
   #------------------------
   contador2 = len(label_pk)
   #------------------------


#======================================================================
#======================================================================
#======================================================================

if (n_procar > 1 or (n_procar == 1 and dest_k < 2)):

   nk_total = nk*n_procar              # Total number of k-points for the band
   contador2 = 0
   n_pk = []                           # Vector formed by the indices of the selected k-points
   dest_pk = []                        # Vector formed by the coordinates on the x-axis of the plot of the selected k-points
   k1_pk = []; k2_pk = []; k3_pk = []  # Direct coordinates (k1, k2, k3) of selected k-points 

   #--------------------------------------------------------
   inform = open(dir_files + '/output/informacoes.txt', "r")
   #--------------------------------------------------------

   palavra = 'k-points |'                          

   for line in inform:   
       if palavra in line: 
          break

   VTemp = inform.readline()
   VTemp = inform.readline()
       
   for i in range (nk_total):
       VTemp = inform.readline().split()
       r1 = int(VTemp[0]); r2 = float(VTemp[1]); r3 = float(VTemp[2]); r4 = float(VTemp[3])
       if (len(VTemp) == 5):
          comprimento = float(VTemp[4])
       if (len(VTemp) == 8):
          comprimento = float(VTemp[7])
       if (i == 0):
          n_pk.append(1)
          dest_pk.append(0.0)
          k1_pk.append(r2); k2_pk.append(r3); k3_pk.append(r4)         
       if (i != 0) and (i != (nk_total - 1)):  
          dif = comprimento - comprimento_old     
          if(dif == 0.0):
             contador2 += 1
             k1_pk.append(r2)
             k2_pk.append(r3)
             k3_pk.append(r4)
             dest_pk.append(comprimento)
             n_pk.append(i+1)
       comprimento_old = comprimento

   n_pk.append(nk_total)
   dest_pk.append(comprimento)
   k1_pk.append(r2); k2_pk.append(r3); k3_pk.append(r4)
   
   contador2 = contador2 + 2

   #-------------
   inform.close()
   #-------------


#======================================================================
# Defining the corresponding nomenclatures for GRACE and Matplotlib ===
#======================================================================

if (dest_k == 2):

   r_grace = []

   r_grace.append('\\f{Symbol}G');     r_grace.append('\\f{Symbol}g');     r_grace.append('\\f{Symbol}D')
   r_grace.append('\\f{Symbol}d');     r_grace.append('\\f{Symbol}L');     r_grace.append('\\f{Symbol}l')
   r_grace.append('\\f{Symbol}S');     r_grace.append('\\f{Symbol}s');     r_grace.append('\\f{Symbol}Q')
   r_grace.append('\\f{Symbol}q');     r_grace.append('\\f{Symbol}W');     r_grace.append('\\f{Symbol}w') 
   r_grace.append('\\f{Symbol}Y');     r_grace.append('\\f{Symbol}y');     r_grace.append('\\f{Symbol}F')
   r_grace.append('\\f{Symbol}f');     r_grace.append('\\f{Symbol}j');     r_grace.append('\\f{Symbol}a')
   r_grace.append('\\f{Symbol}b');     r_grace.append('\\f{Symbol}p');     r_grace.append('\\f{Symbol}r') 
   r_grace.append('\\f{Symbol}t');     r_grace.append('\\f{Symbol}u');     r_grace.append('\\f{Symbol}m')
   r_grace.append('\\f{Symbol}n');     r_grace.append('\\f{Symbol}e');     r_grace.append('\\f{Symbol}h')
   r_grace.append('\\f{Symbol}k');     r_grace.append('\\f{Symbol}x');     r_grace.append('\\f{Symbol}z')
   r_grace.append('\\f{Symbol}\c,\C'); r_grace.append('\\f{Symbol}\c.\C'); r_grace.append('\\f{Symbol}\c-\C');  r_grace.append('\\f{Symbol}\c/\C')

   #======================================================================

   r_matplot = []

   r_matplot.append('${\\Gamma}$');     r_matplot.append('${\\gamma}$');      r_matplot.append('${\\Delta}$')
   r_matplot.append('${\\delta}$');     r_matplot.append('${\\Lambda}$');     r_matplot.append('${\\lambda}$')
   r_matplot.append('${\\Sigma}$');     r_matplot.append('${\\sigma}$');      r_matplot.append('${\\Theta}$')
   r_matplot.append('${\\theta}$');     r_matplot.append('${\\Omega}$');      r_matplot.append('${\\omega}$') 
   r_matplot.append('${\\Psi}$');       r_matplot.append('${\\psi}$');        r_matplot.append('${\\Phi}$')
   r_matplot.append('${\\phi}$');       r_matplot.append('${\\varphi}$');     r_matplot.append('${\\alpha}$')
   r_matplot.append('${\\beta}$');      r_matplot.append('${\\pi}$');         r_matplot.append('${\\rho}$') 
   r_matplot.append('${\\tau}$');       r_matplot.append('${\\upsilon}$');    r_matplot.append('${\\mu}$')
   r_matplot.append('${\\nu}$');        r_matplot.append('${\\epsilon}$');    r_matplot.append('${\\eta}$')
   r_matplot.append('${\\kappa}$');     r_matplot.append('${\\xi}$');         r_matplot.append('${\\zeta}$')
   r_matplot.append('${\\leftarrow}$'); r_matplot.append('${\\rightarrow}$'); r_matplot.append('${\\uparrow}$');  r_matplot.append('${\\downarrow}$')

   #======================================================================
   