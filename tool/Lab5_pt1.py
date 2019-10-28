import arcpy
import os
from arcpy import env

#set your variables
workspace1 = r"C:\Users\trejimmy5562\Documents\DevSource\GISDev\topic\05"
workspace2 = os.path.join(workspace1, 'Campus.gdb')
tempWorkspace = os.path.join(workspace1, 'scratch')
file2 = 'garages.csv'
outLoc = os.path.join(workspace1, 'Lab5.gdb')
gg = os.path.join(tempWorkspace, 'garages')
g77 = os.path.join(outLoc, 'garages')
ss = os.path.join(outLoc, "Structures")

#set environment
arcpy.env.workspace = workspace1

#create Geodatabase
if arcpy.Exists(outLoc):
    pass
else:
    arcpy.CreateFileGDB_management(workspace1, 'Lab5.gdb')


#turn the csv into XY feature class
g1 = arcpy.management.MakeXYEventLayer(file2, 'X', 'Y', 'garages')
g2 = arcpy.CopyFeatures_management(g1, os.path.join(tempWorkspace, 'garages'))
#convert table to geodatabase
arcpy.FeatureClassToGeodatabase_conversion(g2, outLoc)

#change workspace
arcpy.env.workspace = workspace2

#copy the structures feature class to the lab5 database
arcpy.CopyFeatures_management("Structures", ss)
#input buffer distance, input garage name
bldgNum_input = input("Please enter a garage name: ")
buffer_dist = int(input("input buffer distance in Meters: "))

# generate where_clause
where_1 = "Name = '%s'" % bldgNum_input
print(where_1)
# check if building exists
cursor = arcpy.SearchCursor(g77, where_clause=where_1)
proceed = False
#iterate through rows to find the bldg # equal to our input, go on if found
for row in cursor:
    if row.getValue("Name") == bldgNum_input:
        proceed = True

# check if we should proceed, do buffer if yes
if proceed:
    #perform buffer analysis
    arcpy.env.workspace = outLoc
    # generate the name for buffer layer
    buildingBuff = "building_%s_buffed_%s" % (bldgNum_input, buffer_dist)
    buffer12 = os.path.join(outLoc, buildingBuff)
    # Get reference to building
    buildingFeature = arcpy.Select_analysis(g77, outLoc + "/building_%s" % (bldgNum_input), where_1)
    

    arcpy.Buffer_analysis(g77, buffer12, buffer_dist)
    #find intersections with buffer
    # Clip the structures to our buffered feature
    #in2 = arcpy.Intersect_analysis([buffer12, ss], os.path.join(outLoc, 'intersection'), 'ALL')
    in3 = arcpy.Clip_analysis(ss, outLoc + '\\' + buildingBuff, outLoc + "/clip_%s" % (bldgNum_input))
    # Remove the feature class we just created
    arcpy.Delete_management(outLoc + "/building_%s" % (bldgNum_input))

    arcpy.TableToTable_conversion (in3, workspace1, 'intersection.csv')
    print("Success!")
else:
    print("Seems we couldn't find the garage you entered")

