import pandas as pd

#### A small script for taking the coordinate information for USCA312 and converting it to readable coordinate pairs for display on a map

#open city files
city_names_text = open('../OIE project/Data/USCA312_labels.txt', 'r')
city_coordinates_text = open('../OIE project/Data/USCA312_coords.txt', 'r')


#put lines of city_names_Text in a list
city_names_list = [line.strip() for line in city_names_text]
#cut out the filler text at the beginning of the txt file
city_names_list = city_names_list[15:]

#put lines of city_names_Text in a list
city_coord_list = [line.strip() for line in city_coordinates_text]
#cut out the filler text at the beginning of the txt file
city_coord_list = city_coord_list[4:]
#split the individual strings for each line into lists
city_coord_list = [line.split() for line in city_coord_list]

#Keep only the items in index positions 0 and 4 for each sublist
#index 0 is the latidude, index 4 multiplied by -1 is the longitude
city_coord_list = [ [int(sublist[0]), int(sublist[4])*-1] #return elements 0 and 4, append to list
                    for sublist in city_coord_list] #for each sublist

#Create the dataframe
city_coord_df = pd.DataFrame(city_coord_list, #data is the distances list
                            index=city_names_list, #row indices are the city list
                            columns=['Latitude', 'Longitude']) #columns are lat and long

print(city_coord_df.axes)
#city_coord_df.to_csv('../OIE project/Data/USCA312_coords.csv')
