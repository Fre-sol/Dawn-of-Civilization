from Core import *
from RFCUtils import *
# Fresol: getSettlerValue / exportCore use this and it lives in Resources
from Resources import dConquerorPlotTypesDict

import BugPath as path

import Setup
from Files import FileMap, getPath
import os

EXPORT_MAPS_PATH = "Assets/Maps"

IMAGE_LOCATION = os.getcwd() + "\Mods\\RFC Dawn of Civilization\\Export"
iLongestName = len("Netherlands") #Netherlands currently has the longest civ name

gc = CyGlobalContext()

def getTLBR(lPlots):
	lPlotX = [plot.getX() for plot in plots.of(lPlots)]
	lPlotY = [plot.getY() for plot in plots.of(lPlots)]
	TL = (min(lPlotX), min(lPlotY))
	BR = (max(lPlotX), max(lPlotY))
	return TL, BR

def getCivName(iPlayer):
	if civ(player(iPlayer)) == iHolyRome:
		return "HolyRome"
	elif civ(player(iPlayer)) == iTurks:
		return "Turks"
	elif civ(player(iPlayer)) == iOttomans:
		return "Ottomans"
	return name(iPlayer)

def exportFlip(iPlayer, (lHumanFlipPlot, lAIFlipPlots)):
	sLocation = "FlipZones"
	sName = getCivName(iPlayer)
	sDictName = "dBirthArea"
	
	BL, TR = getTLBR(lHumanFlipPlot)
	lExtended = lHumanFlipPlot + lAIFlipPlots
	BLai, TRai = getTLBR(lExtended)
	
	tExceptions = None
	lExceptions = plots.rectangle(BLai, TRai).without(lExtended)
	if lExceptions:
		tExceptions = ("dBirthAreaExceptions", lExceptions)
	
	lExtraDictList = None
	if lAIFlipPlots:
		lExtraDictList = [("dExtendedBirthArea", (BLai, TRai))]
		
	writeTRBLDictFile(sLocation, sName, (BL, TR), sDictName, tExceptions, lExtraDictList = lExtraDictList)
	
	show("Flipzone of %s exported" % sName) 

def exportCore(iPlayer):
	sLocation = "Cores"
	sName = getCivName(iPlayer)
	sDictName = "dCoreArea"
	
	lCorePlots = plots.core(iPlayer)
	BL, TR = getTLBR(lCorePlots)

	tExceptions = None
	lExceptions = plots.rectangle(BL, TR).land().where(lambda p: (not p.isPeak() or location(p) in dConquerorPlotTypesDict) and not p.isPlayerCore(iPlayer))
	if lExceptions:
		tExceptions = ("dCoreAreaExceptions", lExceptions)
	
	writeTRBLDictFile(sLocation, sName, (BL, TR), sDictName, tExceptions)
	
	show("Core of %s exported" % sName) 

def exportSettlerMap(iPlayer):
	sLocation = "SettlerValues"
	sName = getCivName(iPlayer)
	valueFunction = getSettlerValue
	sPath = writeMapCsv(sLocation, sName, valueFunction, iPlayer = iPlayer)
	
	show("Settlermap of %s exported to %s" % (sName, sPath))
	
def getSettlerValue(plot, *args, **kwargs):
	iPlayer = kwargs.get('iPlayer', None)
	
	if plot.isWater():
		return 0
	elif plot.isPeak() and location(plot) in dConquerorPlotTypesDict:
		return 0
		
	if iPlayer is not None:
		return plot.getPlayerSettlerValue(iPlayer)
		
	return 0

def exportWarMap(iPlayer):
	sLocation = "WarMaps"
	sName = getCivName(iPlayer)
	valueFunction = getWarValue
	sPath = writeMapCsv(sLocation, sName, valueFunction, iPlayer = iPlayer)
	
	show("Warmap of %s exported to %s" % (sName, sPath))
	
def getWarValue(plot, *args, **kwargs):
	iPlayer = kwargs.get('iPlayer', None)
	if iPlayer is not None:
		return plot.getPlayerWarValue(iPlayer)
	return 0


## Fresol - start: write Assets/Maps/Regions.csv, the file RegionMap.py loads.
# The old version wrote Export/other/RegionMap.txt, a python literal nothing
# reads any more, so the button was a dead end (the TODO it replaced said as
# much).  Size comes from the map itself, so it cannot drift from Consts.py.
def exportRegionMap():
	iW = CyMap().getGridWidth()
	iH = CyMap().getGridHeight()
	
	rows = []
	for y in range(iH):
		rows.append([str(plot_(x, y).getRegionID()) for x in range(iW)])
	
	# Fresol: export *beside* the loaded file -- renaming it over
	# Regions.csv stays a deliberate step (same rule as the settler and
	# war exporters, 2026-10-13)
	FileMap.write(rows, "Regions_export.csv")
	
	show("Regionmap exported to %s" % getPath("Regions_export.csv"))
## Fresol - end
	
def getRegionValue(plot, *args, **kwargs):

	#TODO: bAutoWater should be removed if water features get their own region ID
	bAutoWater = True
	if plot.isWater() and bAutoWater:
		return -1
		
	return plot.getRegionID()


def exportAreaExport(lPlots, bWaterException, bPeakException):
	if not lPlots:
		show("No area selected")
		return
	
	x_coords, y_coords = zip(*lPlots)
	tTL = (min(x_coords), min(y_coords))
	tBR = (max(x_coords), max(y_coords))
	
	exceptions = [location(p) for p in plots.rectangle(tTL, tBR) if location(p) not in lPlots and not p.isWater()]

	# Fresol: normpath so the path shown and used has one kind of separator
	file_path = os.path.normpath("%s/%s/%s" % (path.getModDir(), EXPORT_MAPS_PATH, "Export/Area.txt"))
	file = open(file_path, "w")
	
	try:
		content = "rectangle = (%s,\t%s)\nexceptions = %s\nlist = %s" % (tTL, tBR, exceptions, lPlots)
		file.write(content)
		show("Area exported")
	finally:
		file.close()
		
	"""
	if lPlots:
		sLocation = "other"
		sName = "NewArea"
		sDictName = "NewArea"
	
		BL, TR = getTLBR(lPlots)
		
		tExceptions = None
		lExceptions = plots.start(BL).end(TR).where(lambda p: location(p) not in lPlots)
		
		if bWaterException:
			lExceptions = plots.start(BL).end(TR).where(lambda p: p.isWater() or p in lExceptions)
		if bPeakException:
			lExceptions = plots.start(BL).end(TR).where(lambda p: p.isPeak() or p in lExceptions)
			
		if lExceptions:
			tExceptions = ("Exceptions", lExceptions)
			
		writeTRBLDictFile(sLocation, sName, (BL, TR), sDictName, tExceptions, False)
		
		show("Area exported")
	else:
		show("No area selected")
	"""


## Fresol - start: write the csv the game loads, not the old tuple dump
#
# The settler and war exporters below wrote a python literal into
# Export/<dir>/<name>.txt, which nothing reads any more: Rise.py loads
# Assets/Maps/<dir>/<name>.csv.  So write that file directly, with water plots
# left blank the way the shipped files have them.
dCsvFolders = {'SettlerValues': 'Settler', 'WarMaps': 'War'}

def writeMapCsv(sFileLocation, sName, valueFunction, *args, **kwargs):
	sFolder = os.path.normpath(os.path.join(os.getcwd(), 'Mods', 'RFC Dawn of Civilization',
		EXPORT_MAPS_PATH, dCsvFolders.get(sFileLocation, sFileLocation)))
	if not os.path.isdir(sFolder):
		os.makedirs(sFolder)

	# Fresol: export beside the original rather than over it - replacing the shipped
	# map stays a deliberate step the player takes.
	sPath = os.path.join(sFolder, sName + '_export.csv')
	file = open(sPath, 'wb')

	try:
		iW = globals().get('iWorldX', 150)
		iH = globals().get('iWorldY', 80)

		for y in reversed(range(iH)):
			lCells = []
			for x in range(iW):
				p = plot_(x, y)
				if p.isWater():
					lCells.append('')
				else:
					lCells.append('%d' % valueFunction(p, *args, **kwargs))
			file.write(','.join(lCells) + '\r\n')
	finally:
		file.close()

	return sPath
## Fresol - end


## Fresol - start: the exporters wrote into Export/<dir>/ which does not exist
def ensureFolder(sFile):
	sFolder = os.path.dirname(sFile)
	if sFolder and not os.path.isdir(sFolder):
		os.makedirs(sFolder)
## Fresol - end


def writeMapFile(sFileLocaton, sName, valueFunction, *args, **kwargs):
	sMapName = kwargs.get('sMapName', None)
	bDictStyle = kwargs.get('bDictStyle', False)
	
	sFile = IMAGE_LOCATION + "\\" + sFileLocaton + "\\" + sName + ".txt"
	ensureFolder(sFile)
	file = open(sFile, 'wt')

	try:
		if sMapName:
			file.write(sMapName + " = ( \n")
		else:
			file.write("(")
		for y in reversed(range(iWorldY)):
			sLine = "(\t"
			for x in range(iWorldX):
				plot = plot_(x, y)
				iValue = valueFunction(plot, *args, **kwargs)
				sLine += "%d,\t" % iValue
			if y == 0 and bDictStyle:
				sLine += ")),"
			else:
				sLine += "),\n"
			file.write(sLine)
		if not bDictStyle:
			file.write(")")
	finally:
		file.close()

def writeTRBLDictFile(sFileLocaton, sName, tSquare, sDictName, tExceptions = None, bIsDictionary = True, lExtraDictList = None):
	BL, TR = tSquare
	
	sIdentifierText = ""
	if bIsDictionary:
		sIdentifier = "i" + sName
		# allign tabs
		iTabs = (iLongestName - len(sName) - 1) // 4 + 1
		sIdentifierText = sIdentifier + " :" + iTabs*"\t"
	
	sFile = IMAGE_LOCATION + "\\" + sFileLocaton + "\\" + sName + ".txt"
	ensureFolder(sFile)
	file = open(sFile, 'wt')
	try:
		file.write("# " + sDictName + "\n")
		file.write(sIdentifierText + "("+ str(BL) + ",\t" + str(TR) + ")")
		if bIsDictionary:
			file.write(",")
			
		if tExceptions:
			sExceptionName, lExceptions = tExceptions
			file.write("\n\n# " + sExceptionName + "\n")
			file.write(sIdentifierText + str(lExceptions))
			if bIsDictionary:
				file.write(",")
				
		if lExtraDictList:
			for sListName, lList in lExtraDictList:
				file.write("\n\n# " + sListName + "\n")
				file.write(sIdentifierText + str(lList))
				if bIsDictionary:
					file.write(",")
	finally:
		file.close()