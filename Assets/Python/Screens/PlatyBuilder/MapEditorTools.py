from Core import *
from RFCUtils import *
# Fresol: getSettlerValue / exportCore use this and it lives in Resources
from Resources import dConquerorPlotTypesDict
from Periods import dPeriodNames

import BugPath as path

import Setup
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
	
	sPath = os.path.normpath(IMAGE_LOCATION + "\\FlipZones\\" + sName + ".txt")
	show("Flip zone of %s exported to:\n%s\n\nTo make it take effect, paste the lines into Assets/Python/Areas.py: dBirthArea / dBirthAreaExceptions (and dExtendedBirthArea), then restart the game." % (sName, sPath))

def exportCore(iPlayer):
	sLocation = "Cores"
	sName = getCivName(iPlayer)
	iPeriod = period(civ(iPlayer))

	# Fresol: the edited flags, not the defined area - plots.core() on the factory
	# answers with dCoreArea, so the bounding box would ignore new plots outside it.
	lCorePlots = plots.all().core(iPlayer)
	if not lCorePlots:
		show("No core plots for %s" % sName)
		return

	BL, TR = getTLBR(lCorePlots)

	# Fresol: a civilisation in a special period exports into the period dictionaries;
	# every other core exports into the base ones.
	if iPeriod in dPeriodCoreArea:
		sFile = dPeriodNames[iPeriod]
		sIdentifier = "Period" + sFile.replace("_", "")
		sDictName = "dPeriodCoreArea"
		sExceptionName = "dPeriodCoreAreaExceptions"
	else:
		sFile = sName
		sIdentifier = sName
		sDictName = "dCoreArea"
		sExceptionName = "dCoreAreaExceptions"

	tExceptions = None
	lExceptions = plots.rectangle(BL, TR).land().where(lambda p: (not p.isPeak() or location(p) in dConquerorPlotTypesDict) and not p.isPlayerCore(iPlayer))
	if lExceptions:
		tExceptions = (sExceptionName, lExceptions)

	writeTRBLDictFile(sLocation, sFile, (BL, TR), sDictName, tExceptions, sIdentifierName = sIdentifier)

	sPath = os.path.normpath(IMAGE_LOCATION + "\\Cores\\" + sFile + ".txt")
	sKey = "i" + sIdentifier
	show("Core of %s exported to:\n%s\n\nThe current game already uses your edits. To make them permanent for future games, paste the two lines into Assets/Python/Areas.py:\n%s  (key %s)\n%s  (key %s)\nthen restart the game.\n\nA period change reloads this civilisation's core from the definitions." % (sFile, sPath, sDictName, sKey, sExceptionName, sKey))

def exportSettlerMap(iPlayer):
	sLocation = "SettlerValues"
	sName = getCivName(iPlayer)
	sLoadedName = civ_name(civ(iPlayer))
	valueFunction = getSettlerValue
	sPath = writeMapCsv(sLocation, sName, valueFunction, iPlayer = iPlayer)

	show("Settler map of %s exported to:\n%s\n\nThe current game already uses your edits: the AI reads the live plot values.\nFor all future games, review the file, then rename or copy it over Assets/Maps/Settler/%s.csv (the game does not load the _export file), and start a new game.\n\nA period change or this civilisation's activation reloads its map from that CSV." % (sName, sPath, sLoadedName))
	
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
	sLoadedName = civ_name(civ(iPlayer))
	valueFunction = getWarValue
	sPath = writeMapCsv(sLocation, sName, valueFunction, iPlayer = iPlayer)

	show("War map of %s exported to:\n%s\n\nThe current game already uses your edits: the AI reads the live plot values.\nFor all future games, review the file, then rename or copy it over Assets/Maps/War/%s.csv (the game does not load the _export file), and start a new game.\n\nA period change or this civilisation's activation reloads its map from that CSV." % (sName, sPath, sLoadedName))
	
def getWarValue(plot, *args, **kwargs):
	iPlayer = kwargs.get('iPlayer', None)
	if iPlayer is not None:
		return plot.getPlayerWarValue(iPlayer)
	return 0


#TODO: use export to csv function in map branch when merged
def exportRegionMap():
	sLocation = "other"
	sName = "RegionMap"
	valueFunction = getRegionValue
	writeMapFile(sLocation, sName, valueFunction, sMapName = "tRegionMap")
	
	sPath = os.path.normpath(IMAGE_LOCATION + "\\other\\RegionMap.txt")
	show("Region map exported to:\n%s\n\nThe game loads Assets/Maps/Regions.csv; this export is a tuple map, so convert or copy the data into that file, then restart the game." % sPath)
	
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
		show("Area exported to:\n%s\n\nUse the rectangle/exceptions where the new area is defined (Areas.py), then restart the game." % file_path)
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

def writeTRBLDictFile(sFileLocaton, sName, tSquare, sDictName, tExceptions = None, bIsDictionary = True, lExtraDictList = None, sIdentifierName = None):
	BL, TR = tSquare

	# Fresol: the dictionary key is not always the file name - a period core is filed
	# under the period name but keyed by its iPeriod constant.
	if sIdentifierName is None:
		sIdentifierName = sName

	sIdentifierText = ""
	if bIsDictionary:
		sIdentifier = "i" + sIdentifierName
		# allign tabs
		iTabs = max(1, (iLongestName - len(sIdentifierName) - 1) // 4 + 1)
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