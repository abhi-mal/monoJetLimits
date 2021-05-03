from __future__ import division

def get_transpose(my_grid):
    return [list(x) for x in zip(*my_grid)] 

def identify_blocks(row):
    print(row)
    row_ones = []
    for j in range(len(row)):
        if(row[j]==1): row_ones.append(j) # row_ones has the indices where the row elements are 1 i.e has base limits
    row_block= regions(row_ones,row)
    return(row_block)

def regions(list_1,row):
    num_ones = len(list_1)
    num_regions = num_ones+1 # but if one of these ones is in the edge of list then num of regions changes, so use flags
    flag_1=0
    flag_2=0
    if(list_1[0]==0): 
        flag_1 =1 # row starts with 1
        num_regions -=1
    if(list_1[-1]==(len(row)-1)): 
        flag_2 =1 # row ends with 1
        num_regions -=1
    start_indices = [] #*  num_regions # as each region has a start index   
    end_indices = [] #*  num_regions # as each region has a end index 
    if flag_1 == 0 : 
            start_indices.append(0)
            end_indices.append(list_1[0])
    for i in range(num_ones-1):
        start_indices.append(list_1[i]) 
        end_indices.append(list_1[i+1])
    if flag_2 == 0:
            start_indices.append(list_1[-1]) 
            end_indices.append(len(row)-1) 
   # print(list_1)        
   # print(flag_1)
   # print(flag_2)
   # print(start_indices)
   # print(end_indices)
   # print(num_regions)
 
   # return(blocks)
    Block = merge_regions(start_indices,end_indices,flag_1,flag_2,len(row))
    return(Block)

def merge_regions(list_a,list_b,flag_a,flag_b,total):
    block = []  
    list_c = []
    for j in range(len(list_a)):
         list_c.append([list_a[j],list_b[j]])
   # print(list_c) 
    trimmed_c = []
    for k in list_c:
     #   print(k)
    #if start and end index for a given region differ only by 1 then we can ignore such regions because no 0 between those two 1s 
        if ((k[0]+1)!=k[1]) or (flag_a==0 and k[0]==0) or (flag_b==0 and k[1]==(total-1)):  
          #  print("hi")
            trimmed_c.append(k)
   # print(trimmed_c)  
    return(trimmed_c)
    #for j in range(len(list_c)):
    #    if (flag_a ==0 and j ==0): block.append([list_a[j],list_b[j]])
    #    elif((list_b[j]-list_a[j])==1):
    #        block.append([list_a[j],list_b[j+1]])
    #    print(block)    

def get_interp_blocks(a,a_trans):
    inter_block_x = [0]*len(a)
    inter_block_y = [0]*len(a_trans)
    for j in range(len(a)):
        inter_block_x[j] = identify_blocks(a[j])
      #  raw_input("Press Enter to continue...")
    for x in inter_block_x:
        print x
    for j in range(len(a_trans)):
        inter_block_y[j] = identify_blocks(a_trans[j])
      #  raw_input("Press Enter to continue...")
    for x in inter_block_y:
        print x  
    return  inter_block_x,inter_block_y  

def my_interpolate(X1,Y1,X2,Y2,flag,X0): # Linear inperpolation
    if (X1==X2): # means only one point in a given row
        Y0 = Y1  # because anyways Y1==Y2
    else:     
        slope = (Y2-Y1)/(X2-X1)
        Y0 = Y1 + slope*(X0-X1)
    #print(Y0)    
    return Y0

def block_identify(element_index,chain,chain_number):
    to_return = -1
    for subchain_number,subchain in enumerate(chain[chain_number]):
        if (subchain[0] <= element_index <= subchain[1]):
            to_return = subchain_number
            break
    return to_return      

def interpolator(interp_block,axis,value_matrix,mass_matrix,my_grid,fill_value,border_dist,only_border=1):   
    if   axis ==0: 
        index_to_get = 0 # mphi--because interpolating along x now
    elif axis ==1: 
        index_to_get = 1 # mchi--because interpolating along y now    
    for index,blocks in enumerate(interp_block):
        for block in blocks:
            y1 = value_matrix[index][block[0]]
            y2 = value_matrix[index][block[1]]
            x1 = mass_matrix[index][block[0]][index_to_get] 
            x2 = mass_matrix[index][block[1]][index_to_get]  
            extend = 0
            # flags can be 0 only for block[j] referring to first or last columns only
            flag_1 = my_grid[index][block[0]]
            flag_2 = my_grid[index][block[1]]
            if (block[0]==0): # means the block start at first column
                if(flag_1==0):# first column value of this should be determined
                    if(flag_2 != 0): # the only time both flag_1 and flag_2(inside this loop) are zero means row empty
                            x1,y1 = x2,y2
                            next_1 = block[1] # default value, if nothing to the right of block[1] is 1, then this used
                            for j in range(block[1]+1,len(my_grid[index])):
                                 if(my_grid[index][j]==1):
                                        next_1 = j
                                        break
                            x2,y2 = mass_matrix[index][next_1][index_to_get],value_matrix[index][next_1] # if default value is used then both represent the same point now
                            extend = -1            

                    else : 
                            print("row empty")                            
                elif(flag_1==1):
                    pass
            if(block[1]==(len(my_grid[index])-1)):  # means the block ends at last column    
                if(flag_2==0): # last column value should be determined
                    if(flag_1 != 0):  # the only time both flag_1 and flag_2 (inside this loop)are zero means row empty
                        x2,y2 = x1,y1
                        count = 0
                        next_1 = block[0] # default value, if nothing to the left of block[0]is 1, then this used
                        for i,j in enumerate(my_grid[index][::-1]):
                                if(j==1):
                                    count +=1
                                    if(count==2): # because the first 1 coming from right will already be block[0]
                                        next_1 = (len(my_grid[index])-1)-i# we want the corresponding index in unreversed array
                                        break
                        x1,y1 = mass_matrix[index][next_1][index_to_get],value_matrix[index][next_1] # if default value is used then both represent the same point now
                        extend = 1
                    else:
                        print("row empty")
                elif(my_grid[index][block[1]]==1):  
                        pass
            for subindex in range(block[0],block[1]+1):
                     if(my_grid[index][subindex] ==0): 
                            x0 =  mass_matrix[index][subindex][index_to_get] # mphi mass
                            #print("x1:%f| y1:%f| x2:%f| y2:%f| x0:%f|"%(x1,y1,x2,y2,x0))
                            #raw_input("Press Enter to continue...")
                            if(only_border==1):
                                fill_value[index][subindex] = my_interpolate(x1,y1,x2,y2,extend,x0)
                                if((index==0) or (index==len(interp_block)-1) or ((subindex==0) or (subindex==len(my_grid[index])-1))):                                    
                                    if axis ==0:  border_dist[index][subindex][index_to_get] = abs(x2-x0)+abs(x1-x0) # along hor dir(w.r.t original  binary_grid)
                                    elif axis ==1:border_dist[subindex][index][index_to_get] = abs(x2-x0)+abs(x1-x0) # along ver dir(w.r.t original  binary_grid)
#    for x in border_dist:
#           print(x)                                         
                            elif(only_border==0):
                                if axis ==0: fill_value[index][subindex] = my_interpolate(x1,y1,x2,y2,extend,x0)
                                elif axis ==1: fill_value[index][subindex] = my_interpolate(x1,y1,x2,y2,extend,x0) 
    if(only_border==1):   return   fill_value,border_dist                 
    elif(only_border==0): return fill_value
            
def border_interp_opt2(val_x,val_y,dx,dy,power):
    w1= 1/(dx**power)
    w2= 1/(dy**power)
    #print("w1=%f w2=%f"%(w1,w2))
    fin_total = (val_x*w1+val_y*w2)/(w1+w2)
    print(fin_total)
    return fin_total

def border_interp_opt3(val_x,val_y,dx,dy,power):
    if(dx<dy): w2 = 0; w1 =1
    elif(dx>dy): w1 = 0; w2 =1
    else: # if dx == dy    
        w1= 1/(dx**power)
        w2= 1/(dy**power)
    #print("w1=%f w2=%f"%(w1,w2))
    fin_total = (val_x*w1+val_y*w2)/(w1+w2)
    print(fin_total)
    return fin_total

def do_interpolation(value,mchi,mphi,method=2):
    mchi = [int(i) for i in mchi] # making sure input is int and not unicode
    mphi = [int(i) for i in mphi]
    mass = [[0 for p in range(len(mphi))] for q in range(len(mchi))]
    binary_grid = [[0 for p in range(len(mphi))] for q in range(len(mchi))]
    for q in range(len(mass)):
           for p in range(len(mass[q])):
                   mass[q][p] = [mphi[p],mchi[q]] 
                   if(value[q][p]!=0): binary_grid[q][p]=1
    mass_trans =  get_transpose(mass)  
    value_trans =  get_transpose(value)
    binary_grid_trans = get_transpose(binary_grid)              
    inter_block_x,inter_block_y = get_interp_blocks(binary_grid,binary_grid_trans)
    block_matrix = [[[[],[]] for p in range(len(mphi))] for q in range(len(mchi))]
    for index,elem in enumerate(binary_grid):
            for subindex, elem1 in enumerate(elem):
                        if((index==0) or (index==(len(binary_grid)-1)) or ((subindex==0) or subindex==(len(elem)-1))): # (top row) or (bottom row) or (first or last column)
                                   if(elem1==0):
                                            block_matrix[index][subindex][0] = [index,block_identify(subindex,inter_block_x,index)]
    for index,elem in enumerate(binary_grid_trans): 
            for subindex, elem1 in enumerate(elem):
                        if((index==0) or (index==(len(binary_grid_trans)-1)) or ((subindex==0) or subindex==(len(elem)-1))): # (top row) or (bottom row) or (first or last column)
                                   if(elem1==0):
                                            block_matrix[subindex][index][-1] = [index,block_identify(subindex,inter_block_y,index)]
    for x in block_matrix:                
            print(x)   
    border_value_x = [[0 for p in range(len(mphi))] for q in range(len(mchi))]
    border_value_y = [[0 for q in range(len(mchi))] for p in range(len(mphi))]
    border_dist = [[[-1,-1] for p in range(len(mphi))] for q in range(len(mchi))] 
    new_value_x = [[0 for p in range(len(mphi))] for q in range(len(mchi))]
    new_value_y = [[0 for q in range(len(mchi))] for p in range(len(mphi))]
    border_value_x, border_dist = interpolator(inter_block_x,0,value,mass,binary_grid,border_value_x,border_dist,only_border=1)
    border_value_y, border_dist = interpolator(inter_block_y,1,value_trans,mass_trans,binary_grid_trans,border_value_y,border_dist,only_border=1) 
    border_filled_value = [[0 for p in range(len(mphi))] for q in range(len(mchi))]                
    for q in range(len(mass)):
        for p in range(len(mass[q])):
            if((q==0) or (q==len(mass)-1) or ((p==0) or (p==len(mass[q])-1))):
                if(binary_grid[q][p]==0):
                    if method==2 : border_filled_value[q][p] = border_interp_opt2(border_value_x[q][p],border_value_y[p][q],border_dist[q][p][0],border_dist[q][p][1],3)
                    elif method==3: border_filled_value[q][p] = border_interp_opt3(border_value_x[q][p],border_value_y[p][q],border_dist[q][p][0],border_dist[q][p][1],3)
#Update the value and my_grid matrices to reflect that the borders are filled
    for q in range(len(mass)):
        for p in range(len(mass[q])):
            if(binary_grid[q][p]==0):
                value[q][p] = border_filled_value[q][p]    
            if(((q==0) or (q==len(mass)-1) or ((p==0) or (p==len(mass[q])-1))) and (value[q][p]!=0)):
                binary_grid[q][p]=1        
            
    value_trans =  get_transpose(value)
    binary_grid_trans =  get_transpose(binary_grid)

# get new interp blocks
    inter_block_x,inter_block_y = get_interp_blocks(binary_grid,binary_grid_trans)    
# get the interpolation values for all other mass points
    new_value_x = interpolator(inter_block_x,0,value,mass,binary_grid,new_value_x,border_dist,only_border=0) # border_dist argument not used when only_border==0
    new_value_y = interpolator(inter_block_y,1,value_trans,mass_trans,binary_grid_trans,new_value_y,border_dist,only_border=0) 
    print(new_value_x)
    print(new_value_y)      
#Take the average of the 2 new_value_x and new_value_y
    new_value_y_trans = get_transpose(new_value_y) 
    new_value = [[0 for p in range(len(mphi))] for q in range(len(mchi))]
    for q in range(len(mass)):
        for p in range(len(mass[q])):
            new_value[q][p] = (new_value_x[q][p]+new_value_y_trans[q][p])/2 
    print(new_value)      
    final_value = [[0 for p in range(len(mphi))] for q in range(len(mchi))]
    for q in range(len(mass)):
        for p in range(len(mass[q])):
            if(binary_grid[q][p]==0):
                final_value[q][p] = new_value[q][p]
            else:
                final_value[q][p] = value[q][p]

    final_value_trans =get_transpose(final_value)# transposing it so that we can Fill TH2 using mphi along x and mchi along y
    return final_value_trans 
