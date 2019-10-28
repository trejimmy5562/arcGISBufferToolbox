import arcpy
import os
from arcpy import env
import shutil

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Toolbox"
        self.alias = ""
        # List of tool classes associated with this toolbox
        self.tools = [BuildingProximity]
    
    

class BuildingProximity(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Building Proximity"
        self.description = "Determines which garages on TAMU's campus are near a targeted building"
        self.canRunInBackground = False # Only used in ArcMap
        self.category = "Building Tools"

    

    def getParameterInfo(self):
        """Define parameter definitions"""

        param0 = arcpy.Parameter(
            displayName="Campus Geodatabase",
            name="cgdbpath",
            datatype="DEWorkspace",
            parameterType="Required",
            direction="Input",
        )
        param1 = arcpy.Parameter(
            displayName="ouput Geodatabase folder",
            name="outgdbpath",
            datatype="DEWorkspace",
            parameterType="Required",
            direction="Input",
        )
        param2 = arcpy.Parameter(
            displayName="output Geodatabase name",
            name="gdbname",
            datatype="GPString",
            parameterType="Required",
            direction="Input",
        )
        param3 = arcpy.Parameter(
            displayName="folder containing garages csv",
            name="garagecsv",
            datatype="DEWorkspace",
            parameterType="Required",
            direction="Input",
        )
        param4 = arcpy.Parameter(
            displayName="Garage Name",
            name="buildingNumber",
            datatype="GPString",
            parameterType="Required",
            direction="Input"
        )
        param5 = arcpy.Parameter(
            displayName="Buffer radius",
            name="bufferRadius",
            datatype="GPDouble",
            parameterType="Required",
            direction="Input"
        )
        param5.filter.type = "Range"
        param5.filter.list = [10, 100]

        params = [param0, param1, param2, param3, param4, param5]
        return params
    
    """
    def updateParameters(self, parameters):
        # Set the default distance threshold to 1/100 of the larger of the width
        #  or height of the extent of the input features.  Do not set if there is no 
        #  input dataset yet, or the user has set a specific distance (Altered is true).
        #
        if parameters[0].valueAsText:
            if not parameters[6].altered:
                extent = arcpy.Describe(parameters[0]).extent
            if extent.width > extent.height:
                parameters[6].value = extent.width / 100
            else:
                parameters[6].value = extent.height / 100

        return
    """
    def execute(self, parameters, messages):

        #set your variables
        workspace1 = r"C:\Users\trejimmy5562\Documents\DevSource\GISDev\topic\05"
        workspace2 = parameters[0].valueAsText # campus gdb
        workspace3 = parameters[1].valueAsText # folder to put gdb in
        tempWorkspace = os.path.join(workspace1, 'scratch')
        gdbName_input = parameters[2].valueAsText + '.gdb'
        outLoc = os.path.join(workspace3, gdbName_input) #output gdb 
        garage2 = parameters[3].valueAsText #garages csv file
        file2 = 'garages.csv'
        garage1 = os.path.join(garage2, file2)
        gg = os.path.join(tempWorkspace, 'garages')
        g77 = os.path.join(outLoc, 'garages')
        ss = os.path.join(outLoc, "Structures")

        #set environment
        arcpy.env.workspace = workspace1

        #create Geodatabase
        if arcpy.Exists(outLoc):
            pass
        else:
            arcpy.CreateFileGDB_management(workspace3, gdbName_input)

        #turn the csv into XY feature class
        g1 = arcpy.management.MakeXYEventLayer(file2, 'X', 'Y', 'garages')
        g2 = arcpy.CopyFeatures_management(g1, os.path.join(tempWorkspace, 'garages'))
        #convert table to geodatabase
        arcpy.FeatureClassToGeodatabase_conversion(g2, outLoc)

        #change workspace
        arcpy.env.workspace = workspace2
        #copy the structures feature class to the new database
        arcpy.CopyFeatures_management("Structures", ss)
        #input buffer distance, input garage name
        bldgNum_input = parameters[4].valueAsText
        buffer_dist = int(parameters[5].value)

        # generate where_clause
        where_1 = "Name = '%s'" % bldgNum_input
        #print(where_1)
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

            arcpy.TableToTable_conversion(outLoc + "/clip_%s" % (bldgNum_input), workspace1, 'intersection.csv')
            shutil.rmtree(os.path.join(workspace1, "scratch"))
            os.mkdir(os.path.join(workspace1, "scratch"))
            # os.remove(os.path.join(workspace1, "intersection.csv"))
            # os.remove(os.path.join(workspace1, "intersection.txt.xml"))
            #print("Success!")
        else:
            print("Seems we couldn't find the building you entered")
        return None
    



