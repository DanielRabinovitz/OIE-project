#### Not actually used because Gurobi is *stupid* ####

from fileinput import close
from numpy import random
import pandas as pd
import gurobipy as gp
from gurobipy import GRB
from itertools import combinations

## This script is the version of the project with the basic TSP, mapless. Do not change it! ##

#### Make Data ####

##
import os

#open city files
city_names_text = open(r'../OIE project/Data/USCA312_labels.txt', 'r')
city_distances_text = open(r'../OIE project/Data/USCA312_distances.txt', 'r')


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
city_dist_list = [element #return element, append to list
                    for sublist in city_dist_list #for each sublist
                        for element in sublist] #for each element in each sublist
#split the main list back up into chunks for each city
city_dist_list = [city_dist_list[city_index*len(city_names_list)
                                 :
                                 (city_index+1)*len(city_names_list)] #return a range that is a block of 312 cities
                        for city_index in range(len(city_names_list))] #for each city in city_names_list

#Create the dataframe
city_dist_df = pd.DataFrame(city_dist_list, #data is the distances list
                            index=city_names_list, #row and column indices are the city list
                            columns=city_names_list)

#Gurobi tutorial works with combinations instead so mild conversion
def distance(city1, city2):
    return int(city_dist_df[city1][city2])

    
city_dist_combinations = {(c1, c2): distance(c1, c2) for c1, c2 in combinations(city_names_list, 2)}

#makes a gurobi model to solve a TSP for a given list of cities
def make_gurobi_model(list_of_cities):
    #swap city_dist_combinations for chosen set of cities later

    #### Model Creation ####

    ## Base model ##

    m = gp.Model()

    #mpg = 9 #mpg of vehicle
    #tank_cap = 200 #gas tank capacity

    # Variables: is city 'i' adjacent to city 'j' on the tour?
    vars = m.addVars(city_dist_combinations.keys(), obj=city_dist_combinations, vtype=GRB.BINARY, name='x')

    # Symmetric direction: Copy the object
    for i, j in vars.keys():
        vars[j, i] = vars[i, j]  # edge in opposite direction

    ## Constraints ## 

    # two edges incident to each city
    cons = m.addConstrs(vars.sum(c, '*') == 2 for c in list_of_cities)

    #Lazy subtour constraints
    def subtourelim(model, where):
        if where == GRB.Callback.MIPSOL:
            # make a list of edges selected in the solution
            vals = model.cbGetSolution(model._vars)
            selected = gp.tuplelist((i, j) for i, j in model._vars.keys()
                                if vals[i, j] > 0.5)
            # find the shortest cycle in the selected edge list
            tour = subtour(selected)
            print(tour)
            if len(tour) < len(list_of_cities):
                # add subtour elimination constr. for every pair of cities in subtour
                model.cbLazy(gp.quicksum(model._vars[i, j] for i, j in combinations(tour, 2))
                            <= len(tour)-1)

    # Given a tuplelist of edges, find the shortest subtour
    def subtour(edges):
        unvisited = list_of_cities[:]
        cycle = list_of_cities[:] # Dummy - guaranteed to be replaced
        while unvisited:  # true if list is non-empty
            thiscycle = []
            neighbors = unvisited
            while neighbors:
                current = neighbors[0]
                thiscycle.append(current)
                unvisited.remove(current)
                neighbors = [j for i, j in edges.select(current, '*')
                            if j in unvisited]
            if len(thiscycle) <= len(cycle):
                cycle = thiscycle # New shortest subtour
        return cycle

    #### Solving the model ####

    #solve
    m.setParam('SolutionCount',1) 
    m._vars = vars
    m.Params.lazyConstraints = 1
    m.optimize(subtourelim)

    #retrieve solution
    vals = m.getAttr('x', vars)
    selected = gp.tuplelist((i, j) for i, j in vals.keys() if vals[i, j] > 0.5)

    #check if it worked 
    tour = subtour(selected)
    #assert len(tour) == len(list_of_cities)

    return {'model':m, 'vars':vars}

#so I'm not gonna lie I have no clue why Gurobi has two solutions
#Gurobi's "optimal" solution is often shorter than a single edge in the mandatory tour
#The hueristic solution is way too high though. So I'm grabbing both.
def get_gurobi_tour_length(model):
    return model.ObjVal

#stupid gurobi nonsense :)
def get_gurobi_tour(vars):
    edge_list = vars.select('*', '*')
    route = []
    for edge in edge_list:
        if edge.x > 0.5:
            edge_name = edge.VarName
            edge_name = edge_name[edge_name.find('[')+1 : edge_name.find(']')]
            split_point = edge_name.find(',')+4
            start_node = edge_name[0:split_point]
            end_node = edge_name[split_point+1:]
            route.append((start_node, end_node))
    
    return route


