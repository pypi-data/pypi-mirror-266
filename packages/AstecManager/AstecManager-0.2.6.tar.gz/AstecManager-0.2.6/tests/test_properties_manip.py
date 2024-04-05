from AstecManager.libs.XMLPropertiesLib import LoadCellPropertyFromFile,LoadPropertyFromFile,LoadCellToCellPropertyFromFile,LoadXMLTree,LoadCellListFromFile,SaveDictToXML,LoadCellToCellPropertyFromFileForCell


lineage = "/Users/bgallean/Projects/Github/astecmanagerelease/AstecManager/atlas/pm1.xml"

"""
property_volume = LoadPropertyFromFile(lineage,"cell_volume")
for cellkey in property_volume:
    print(cellkey + " -> "+str(property_volume[cellkey]))

contact_surface = LoadCellToCellPropertyFromFile(lineage,"cell_contact_surface")
for cellkey in contact_surface:
    print(cellkey + " : ")
    for childtuple in contact_surface[cellkey]:
        print("      "+str(childtuple[0])+" -> "+str(childtuple[1]))
"""

cellproperty = LoadCellPropertyFromFile("1920798",lineage,"cell_volume")
print(cellproperty)
contact_surface_specificcell = LoadCellToCellPropertyFromFileForCell("1920798",lineage,"cell_contact_surface")
print(contact_surface_specificcell)