import gurobipy as gp
import numpy as np
import matplotlib.pyplot as plt
import pprint

## Not an important file but it's trapp's example ##

#open city files
city_names_text = open('../OIE project/Data/USCA312_labels.txt', 'r')
city_distances_text = open('../OIE project/Data/USCA312_distances.txt', 'r')

#put lines of city_names_Text in a list
city_names_list = [line.strip() for line in city_names_text]
#cut out the filler text at the beginning of the txt file
city_names_list = city_names_list[15:]

#put lines of city_names_Text in a list
city_dist_list = [line.strip() for line in city_distances_text]
#cut out the filler text at the beginning of the txt file
city_dist_list = city_dist_list[7:]
#split the individual numbers into their own elements, but they're split into sublists by line
city_dist_list = [line.split() for line in city_dist_list]
#merge all the sublists
city_dist_list = [int(element) #return element, append to list
                    for sublist in city_dist_list #for each sublist
                        for element in sublist] #for each element in each sublist
#split the main list back up into chunks for each city
city_dist_list = [city_dist_list[city_index*len(city_names_list)
                                 :
                                 (city_index+1)*len(city_names_list)] #return a range that is a block of 312 cities
                        for city_index in range(len(city_names_list))] #for each city in city_names_list

n = len(city_dist_list)

#Model
m = gp.Model("TSP")

z = {}
for i in range(n):
  for j in range(n):
    z[i,j] = m.addVar(obj=city_dist_list[i][j], vtype=gp.GRB.BINARY, name='z('+str(i)+')('+str(j)+')' )
m.update()

#u decision variables: continuous variables used in indexing for MTZ formulation
u = {}
for i in range(n):
  if (i > 0):
    u[i] = m.addVar(vtype=gp.GRB.CONTINUOUS, lb=1.0, ub=n-1, obj=0.0, name='u('+str(i)+')' )
  else:
    u[i] = m.addVar(vtype=gp.GRB.CONTINUOUS, lb=0, ub=0, obj=0.0, name='u('+str(i)+')' )
    #The above assigns u[0] to zero via its lb and ub

m.update()

#Constraints
#1: Each job has an arriving arc
for j in range(n):
  m.addConstr(gp.quicksum(z[i,j] for i in range(n)) == 1)

#2: Each job has a departing arc
for i in range(n):
  m.addConstr(gp.quicksum(z[i,j] for j in range(n)) == 1)
  z[i,i].ub = 0

#3: Use MTZ constraints to forbid subtours
for i in range(n-1):
  for j in range(n-1):
    if (i != j):
      m.addConstr(u[j+1] >= u[i+1] + 1 - (n-1)*(1-z[i+1,j+1]))

m.modelSense = gp.GRB.MINIMIZE

m.update()

m.write("MTZ.lp")

#solve
m.optimize()


# Print optimal sequence of TSP nodes (these are stored in the u variables)
print('The optimal sequence is:')
for i in range(n):
  print(u[i].x) #uses 1-based indexing (instead of 0-based)

#########################################################################################
#Extra: This code also plots the (x,y) pairs, as well as the optimal sequence, in Python
#########################################################################################

#Define plot sequence q[]
u1 = []
for i in range(n):
  u1.append(int(round(u[i].x,2)))

m = []
q = []

for i in range (n):
  m.append(i)

for i in range (n):
  q.append(i)

for i in range (n):
  q[(u1[i]-1)]=int(m[i])


def plotTSP(path1, points, num_iters=1):
  """
  path: List of lists with the different orders in which the nodes are visited
  points: coordinates for the different nodes
  num_iters: number of paths that are in the path list
  """

  # Unpack the primary TSP path and transform it into a list of ordered coordinates

  x = []
  y = []
  for i in path1:
    x.append(points[i][0])
    y.append(points[i][1])

  plt.plot(x, y, 'co')

  # Set a scale for the arrow heads 
  x_scale = float(max(x)) / float(50)


  # Draw the primary path for the TSP problem
  plt.arrow(x[-1], y[-1], (x[0] - x[-1]), (y[0] - y[-1]), head_width=x_scale, color='r', length_includes_head=True)
  for i in range(0, len(x) - 1):
    plt.arrow(x[i], y[i], (x[i + 1] - x[i]), (y[i + 1] - y[i]), head_width=x_scale, color='r', length_includes_head=True)

  # Set axis too slitghtly larger than the set of x and y
  plt.xlim(0, max(x) * 1.1)
  plt.ylim(0, max(y) * 1.1)
  plt.show()

# For Python to read a source file
if __name__ == '__main__':

#Pend coordinates to points 
  points = []
  for i in range(0, len(x_coordinates)):
    points.append((x_coordinates[i], y_coordinates[i]))
      
#Create path order from u[i]    
# Local Search operation
  path1 = []
  for i in range(n):
    path1.append(int(q[i]))

  # Run the function
  plotTSP(path1, points,1)