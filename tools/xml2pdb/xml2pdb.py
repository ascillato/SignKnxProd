import xml.etree.ElementTree as ET
import iso9075

masterTree = ET.parse('knx_master.xml')
masterRoot = masterTree.getroot()
knxns = {'knx': 'http://knx.org/xml/project/11'}

tree = ET.parse('testdev.xml')
root = tree.getroot()
srcDeviceXML = root.find("info")

#manufacturerId = srcDeviceXML.find("manufacturerId").text
manufacturerId = "M-013A"
catalogNumber = srcDeviceXML.find("catalogNumber").text
catalogItemNumber = srcDeviceXML.find("catalogItemNumber").text
serialNumber = srcDeviceXML.find("serialNumber").text
versionNumber = srcDeviceXML.find("versionNumber").text
orderNumber = srcDeviceXML.find("orderNumber").text
applicationNumber = srcDeviceXML.find("applicationNumber").text
applicationVersion = srcDeviceXML.find("applicationVersion").text

catalogSectionId = manufacturerId + "_CS-" + catalogNumber
hardwareId = manufacturerId + "_H-" + serialNumber + "-" + versionNumber
productId= hardwareId + "_P-" + orderNumber
hardware2ProgramId = hardwareId + "_HP-" + "%04X" % int(applicationNumber) + "-" + "%02X" % int(applicationVersion) + "-F00D"
applicationProgramId = manufacturerId + "_A-" + "%04X" % int(applicationNumber) + "-" + "%02X" % int(applicationVersion) + "-F00D"
catalogItemId = hardware2ProgramId + "_CI-" + orderNumber + "-" + catalogItemNumber

def indent(elem, level=0):
	i = "\n" + level*"  "
	if len(elem):
		if not elem.text or not elem.text.strip():
			elem.text = i + "  "
		if not elem.tail or not elem.tail.strip():
			elem.tail = i
		for elem in elem:
			indent(elem, level+1)
		if not elem.tail or not elem.tail.strip():
			elem.tail = i
	else:
		if level and (not elem.tail or not elem.tail.strip()):
			elem.tail = i

def addTranslations(languagesXML, itemsXML, unitId, elementId, tagName):
	for itemXML in itemsXML:
		countryCode = itemXML.get("{http://www.w3.org/XML/1998/namespace}lang")
		
		if countryCode is None:
			continue

		translation = itemXML.text

		languageXML = languagesXML.find("*[@Identifier='" + countryCode + "']")
		
		if languageXML is None:
			languageXML = ET.SubElement(languagesXML, "Language")
			languageXML.set("Identifier", countryCode)

		translationUnitXML = languageXML.find("*[@RefId='" + unitId + "']")
	
		if translationUnitXML is None:
			translationUnitXML = ET.SubElement(languageXML, "TranslationUnit")
			translationUnitXML.set("RefId", unitId)
	
		translationElementXML = translationUnitXML.find("*[@RefId='" + elementId + "']")

		if translationElementXML is None:
			translationElementXML = ET.SubElement(translationUnitXML, "TranslationElement")
			translationElementXML.set("RefId", elementId)
	
		translationXML = ET.SubElement(translationElementXML, "Translation")
		translationXML.set("AttributeName", tagName)
		translationXML.set("Text", translation)

	return

parameterBlockIdx = 0

def addParameterBlock(parentXML, name):
	global parameterBlockIdx

	parameterBlockIdx += 1
	parameterBlockId = applicationProgramId + "_PB-%d" % parameterBlockIdx
	parameterBlockXML = ET.SubElement(parentXML, "ParameterBlock")
	parameterBlockXML.set("Id", parameterBlockId)
	parameterBlockXML.set("Name", name)
	parameterBlockXML.set("Text", name)
	# According to spec: Access. Missing?
	# According to spec: Help Topic ID. Missing?

	return parameterBlockXML

channelIdx = -1

def addChannel(parentXML, name):
	global channelIdx

	channelIdx += 1
	channelId = applicationProgramId + "_CH-%d" % channelIdx
	channelXML = ET.SubElement(parentXML, "Channel")
	channelXML.set("Id", channelId)
	channelXML.set("Name", name)
	channelXML.set("Text", name)
	channelXML.set("Number", str(channelIdx))

	return channelXML

def createRootNode():
	rootXML = ET.Element("KNX")

	rootXML.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
	rootXML.set("xmlns:xsd", "http://www.w3.org/2001/XMLSchema")
	rootXML.set("CreatedBy", "knxconv")
	rootXML.set("ToolVersion", "4.0.1907.45562")
	rootXML.set("xmlns", "http://knx.org/xml/project/11")

	return rootXML

def createCatalog(srcRootXML):
	languagesXML = ET.Element("Languages")
	srcDeviceXML = srcRootXML.find("info")
	dstRootXML = createRootNode()

	manufacturerDataXML = ET.SubElement(dstRootXML, "ManufacturerData")

	manufacturerXML = ET.SubElement(manufacturerDataXML, "Manufacturer")
	manufacturerXML.set("RefId", manufacturerId)

	catalogXML = ET.SubElement(manufacturerXML, "Catalog")

	catalogSectionXML = ET.SubElement(catalogXML, "CatalogSection")
	catalogSectionXML.set("Id", catalogSectionId)
	catalogSectionXML.set("Name", srcDeviceXML.find("category").text)
	addTranslations(languagesXML, srcDeviceXML.findall("category"), catalogSectionId, catalogSectionId, "Name")
	catalogSectionXML.set("Number", catalogNumber)
	catalogSectionXML.set("VisibleDescription", "")
	catalogSectionXML.set("DefaultLanguage", "de-DE")
	catalogSectionXML.set("NonRegRelevantDataVersion", "0")

	catalogItemXML = ET.SubElement(catalogSectionXML, "CatalogItem")
	catalogItemXML.set("Id", catalogItemId)
	catalogItemXML.set("Name", srcDeviceXML.find("name").text)
	addTranslations(languagesXML, srcDeviceXML.findall("name"), catalogItemId, catalogItemId, "Name")
	catalogItemXML.set("Number", catalogItemNumber)
	# According to spec: VisibleDescription. Missing?
	catalogItemXML.set("ProductRefId", productId)
	catalogItemXML.set("Hardware2ProgramRefId", hardware2ProgramId)
	catalogItemXML.set("DefaultLanguage", "de-DE")
	catalogItemXML.set("NonRegRelevantDataVersion", "0")

	manufacturerXML.append(languagesXML)

	return dstRootXML

def createHardware(srcRootXML):
	languagesXML = ET.Element("Languages")
	srcDeviceXML = srcRootXML.find("info")
	dstRootXML = createRootNode()
	
	manufacturerDataXML = ET.SubElement(dstRootXML, "ManufacturerData")
	
	manufacturerXML = ET.SubElement(manufacturerDataXML, "Manufacturer")
	manufacturerXML.set("RefId", manufacturerId)

	hardwaresXML = ET.SubElement(manufacturerXML, "Hardware")

	hardwareXML = ET.SubElement(hardwaresXML, "Hardware")
	hardwareXML.set("Id", hardwareId)
	hardwareXML.set("Name", srcDeviceXML.find("name").text)
	hardwareXML.set("SerialNumber", serialNumber)
	hardwareXML.set("VersionNumber", versionNumber)
	hardwareXML.set("BusCurrent", "12")
	hardwareXML.set("IsAccessory", "0")
	hardwareXML.set("HasIndividualAddress", "1")
	hardwareXML.set("HasApplicationProgram", "1")
	# According to spec: Download Application Program. Missing?
	hardwareXML.set("HasApplicationProgram2", "0")
	# According to spec: Download Application Program2. Missing?
	hardwareXML.set("IsPowerSupply", "0")
	hardwareXML.set("IsChoke", "0")
	hardwareXML.set("IsCoupler", "0")
	hardwareXML.set("IsPowerLineRepeater", "0")
	hardwareXML.set("IsPowerLineSignalFilter", "0")
	hardwareXML.set("IsCable", "0")
	hardwareXML.set("NonRegRelevantDataVersion", "0")
	hardwareXML.set("IsIPEnabled", "0")

	productsXML = ET.SubElement(hardwareXML, "Products")

	productXML = ET.SubElement(productsXML, "Product")
	productXML.set("Id", productId)
	productXML.set("Text", srcDeviceXML.find("name").text)
	addTranslations(languagesXML, srcDeviceXML.findall("name"), productId, productId, "Name")
	productXML.set("OrderNumber", orderNumber)
	productXML.set("IsRailMounted", "1")
	productXML.set("WidthInMillimeter", "1.0500000e+002")
	productXML.set("VisibleDescription", srcDeviceXML.find("name").text)
	addTranslations(languagesXML, srcDeviceXML.findall("name"), productId, productId, "VisibleDescription")
	productXML.set("DefaultLanguage", "de-DE")
	productXML.set("Hash", "")
	productXML.set("NonRegRelevantDataVersion", "0")

	registrationInfoXML = ET.SubElement(productXML, "RegistrationInfo")
	registrationInfoXML.set("RegistrationStatus", "Registered")
	registrationInfoXML.set("RegistrationSignature", "")
		
	hardware2ProgramsXML = ET.SubElement(hardwareXML, "Hardware2Programs")

	hardware2ProgramXML = ET.SubElement(hardware2ProgramsXML, "Hardware2Program")
	hardware2ProgramXML.set("Id", hardware2ProgramId)
	hardware2ProgramXML.set("MediumTypes", "MT-0")
	hardware2ProgramXML.set("Hash", "")

	applicationProgramRefXML = ET.SubElement(hardware2ProgramXML, "ApplicationProgramRef")
	applicationProgramRefXML.set("RefId", applicationProgramId)

	# According to spec: Application Program 2 Ref. Missing?

	registrationInfoXML = ET.SubElement(hardware2ProgramXML, "RegistrationInfo")
	registrationInfoXML.set("RegistrationStatus", "Registered")
	registrationInfoXML.set("RegistrationSignature", "")

	manufacturerXML.append(languagesXML)

	return dstRootXML

def createProduct(srcRootXML):
	languagesXML = ET.Element("Languages")
	srcDeviceXML = srcRootXML.find("info")
	dstRootXML = createRootNode()
	
	manufacturerDataXML = ET.SubElement(dstRootXML, "ManufacturerData")
	
	manufacturerXML = ET.SubElement(manufacturerDataXML, "Manufacturer")
	manufacturerXML.set("RefId", manufacturerId)
	
	applicationProgramsXML = ET.SubElement(manufacturerXML, "ApplicationPrograms")

	applicationProgramXML = ET.SubElement(applicationProgramsXML, "ApplicationProgram")
	applicationProgramXML.set("Id", applicationProgramId)
	applicationProgramXML.set("ApplicationNumber", applicationNumber)
	applicationProgramXML.set("ApplicationVersion", applicationVersion)
	applicationProgramXML.set("ProgramType", "ApplicationProgram")
	applicationProgramXML.set("MaskVersion", "MV-0705")
	# According to spec: Visible Description. Missing?
	applicationProgramXML.set("Name", srcDeviceXML.find("name").text)
	addTranslations(languagesXML, srcDeviceXML.findall("name"), applicationProgramId, applicationProgramId, "Name")
	applicationProgramXML.set("LoadProcedureStyle", "DefaultProcedure")
	applicationProgramXML.set("PeiType", "0")
	# According to spec: Serial Number. Missing?
	# According to spec: Help Topic ID. Missing?
	applicationProgramXML.set("HelpFile", "")
	applicationProgramXML.set("DefaultLanguage", "de-DE")
	applicationProgramXML.set("DynamicTableManagement", "0")
	applicationProgramXML.set("Linkable", "0")
	applicationProgramXML.set("MinEtsVersion", "4.0")
	applicationProgramXML.set("PreEts4Style", "0")
	applicationProgramXML.set("NonRegRelevantDataVersion", "0")
	# According to spec: Replaces Versions. Missing?
	applicationProgramXML.set("Hash", "")
	# Not in spec. Obsolete? applicationProgramXML.set("ConvertedFromPreEts4Data", "1")
	# Not in spec. Obsolete? applicationProgramXML.set("Broken", "0")
	applicationProgramXML.set("IPConfig", "Tool")
	applicationProgramXML.set("AdditionalAddressesCount", "0")
	# Not in spec. Obsolete? applicationProgramXML.set("DownloadInfoIncomplete", "0")
	# Not in spec. Obsolete? applicationProgramXML.set("CreatedFromLegacySchemaVersion", "0")

	staticXML = ET.SubElement(applicationProgramXML, "Static")

	codeXML = ET.SubElement(staticXML, "Code")
	parameterTypesXML = ET.SubElement(staticXML, "ParameterTypes")
	parametersXML = ET.SubElement(staticXML, "Parameters")
	parameterRefsXML = ET.SubElement(staticXML, "ParameterRefs")
	comObjectTableXML = ET.SubElement(staticXML, "ComObjectTable")
	comObjectRefsXML = ET.SubElement(staticXML, "ComObjectRefs")
	addressTableXML = ET.SubElement(staticXML, "AddressTable")
	associationTableXML = ET.SubElement(staticXML, "AssociationTable")
	loadProceduresXML = ET.SubElement(staticXML, "LoadProcedures")
	extensionXML = ET.SubElement(staticXML, "Extension")
	optionsXML = ET.SubElement(staticXML, "Options")

	dynamicXML = ET.SubElement(applicationProgramXML, "Dynamic")

	absoluteSegmentAddr = "16384"
	absoluteSegmentId = applicationProgramId + "_AS-" + "%04X" % int(absoluteSegmentAddr)
	absoluteSegmentXML = ET.SubElement(codeXML, "AbsoluteSegment")
	absoluteSegmentXML.set("Id", absoluteSegmentId)
	absoluteSegmentXML.set("Address", absoluteSegmentAddr)
	absoluteSegmentXML.set("Size", "403")
	absoluteSegmentXML.set("UserMemory", "0")

	absoluteSegmentAddr = "16787"
	absoluteSegmentId = applicationProgramId + "_AS-" + "%04X" % int(absoluteSegmentAddr)
	absoluteSegmentXML = ET.SubElement(codeXML, "AbsoluteSegment")
	absoluteSegmentXML.set("Id", absoluteSegmentId)
	absoluteSegmentXML.set("Address", absoluteSegmentAddr)
	absoluteSegmentXML.set("Size", "401")
	absoluteSegmentXML.set("UserMemory", "0")

	absoluteSegmentAddr = "17188"
	absoluteSegmentId = applicationProgramId + "_AS-" + "%04X" % int(absoluteSegmentAddr)
	absoluteSegmentXML = ET.SubElement(codeXML, "AbsoluteSegment")
	absoluteSegmentXML.set("Id", absoluteSegmentId)
	absoluteSegmentXML.set("Address", absoluteSegmentAddr)
	absoluteSegmentXML.set("Size", "360")
	absoluteSegmentXML.set("UserMemory", "0")

	#dataXML = ET.SubElement(absoluteSegmentXML, "Data")
	#dataXML.text = ""

	#maskXML = ET.SubElement(absoluteSegmentXML, "Mask")
	#maskXML.text = ""

	comObjectTableXML.set("CodeSegment", absoluteSegmentId)
	comObjectTableXML.set("Offset", "0")

	srcChannelsXML = srcRootXML.find("channels")
	parameterIdx = 0
	parameterSeparatorIdx = 0

	for srcChannelXML in srcChannelsXML:
		channelXML = addChannel(dynamicXML, srcChannelXML.find("name").text)
		addTranslations(languagesXML, srcChannelXML.findall("name"), applicationProgramId, channelXML.get("Id"), "Text")

		srcParameterBlocksXML = srcChannelXML.find("parameterBlocks")

		for srcParameterBlockXML in srcParameterBlocksXML:

			parameterBlockXML = addParameterBlock(channelXML, srcParameterBlockXML.find("name").text)
			addTranslations(languagesXML, srcParameterBlockXML.findall("name"), applicationProgramId, parameterBlockXML.get("Id"), "Text")
		
			srcParametersXML = srcParameterBlockXML.find("parameters")

			for srcEntryXML in srcParametersXML:
				if srcEntryXML.tag == "parameter":
					parameterTypeName = srcEntryXML.find("name").text
					parameterTypeId = applicationProgramId + "_PT-" + parameterTypeName.encode('iso9075')
					parameterTypeXML = ET.SubElement(parameterTypesXML, "ParameterType")
					parameterTypeXML.set("Id", parameterTypeId)
					parameterTypeXML.set("Name", parameterTypeName)
					parameterTypeXML.set("Plugin", "")
					
					type = srcEntryXML.get("type")
						
					if (type == "unsignedInt") | (type == "signedInt"):
						sizeInBit = srcEntryXML.get("sizeInBit")

						typeNumberXML = ET.SubElement(parameterTypeXML, "TypeNumber")
						typeNumberXML.set("SizeInBit", sizeInBit)
						
						minInclusive = srcEntryXML.get("minInclusive")
						maxInclusive = srcEntryXML.get("maxInclusive")

						if (type == "unsignedInt"):
							if minInclusive is None:
								minInclusive = "0"

							if maxInclusive is None:
								maxInclusive = str((1 << int(sizeInBit)) - 1)

							typeNumberXML.set("Type", "unsignedInt")
						else:
							if minInclusive is None:
								minInclusive = "-" + str(1 << (int(sizeInBit) - 1))

							if maxInclusive is None:
								maxInclusive = str((1 << (int(sizeInBit) - 1)) - 1)

							typeNumberXML.set("Type", "signedInt")

						typeNumberXML.set("minInclusive", minInclusive)
						typeNumberXML.set("maxInclusive", maxInclusive)
						
						if srcEntryXML.get("uiHint") is not None:
							typeNumberXML.set("UIHint", srcEntryXML.get("uiHint"))
					elif type == "float":
						typeFloatXML = ET.SubElement(parameterTypeXML, "TypeFloat")

						sizeInBit = srcEntryXML.get("sizeInBit");
						minInclusive = srcEntryXML.get("minInclusive")
						maxInclusive = srcEntryXML.get("maxInclusive")

						if sizeInBit == "16":
							encoding = "DPT 9"

							if minInclusive is None:
								minInclusive = "-671088.64"
		
							if maxInclusive is None:
								maxInclusive = "670760.96"

						elif sizeInBit == "32":
							encoding = "IEEE-754 Single"

							if minInclusive is None:
								minInclusive = "1.175e-38"

							if maxInclusive is None:
								maxInclusive = "3.4028235e+38"

						elif sizeInBit == "64":
							encoding = "IEEE-754 Double"

							if minInclusive is None:
								minInclusive = "2.2251e-308"
							
							if maxInclusive is None:
								maxInclusive = "1.798e308"
						else:
							print "Unkown sizeInBit: " + sizeInBit
								
						typeFloatXML.set("Encoding", encoding)
						typeFloatXML.set("minInclusive", minInclusive)
						typeFloatXML.set("maxInclusive", maxInclusive)

						if srcEntryXML.get("uiHint") is not None:
							typeFloatXML.set("UIHint", srcEntryXML.get("uiHint"))
					elif type == "text":
						typeTextXML = ET.SubElement(parameterTypeXML, "TypeText")
						typeTextXML.set("SizeInBit", srcEntryXML.get("sizeInBit"))

						if srcEntryXML.get("pattern") is not None:
							typeTextXML.set("Pattern", srcEntryXML.get("pattern"))
					elif type == "enumeration":
						typeRestrictionXML = ET.SubElement(parameterTypeXML, "TypeRestriction")
						typeRestrictionXML.set("Base", "Value")
						typeRestrictionXML.set("SizeInBit", srcEntryXML.get("sizeInBit"))
							
						srcEntriesXML = srcEntryXML.find("entries")
							
						for srcListEntryXML in srcEntriesXML:
							enumerationValue = srcListEntryXML.get("value")
							enumerationId = parameterTypeId + "_EN-%s" % enumerationValue
							enumerationXML = ET.SubElement(typeRestrictionXML, "Enumeration")
							enumerationXML.set("Id", enumerationId)
							# Obsolete! enumerationXML.set("DisplayOrder", "")
							enumerationXML.set("Text", srcListEntryXML.find("name").text)
							addTranslations(languagesXML, srcListEntryXML.findall("name"), applicationProgramId, enumerationId, "Text")
							enumerationXML.set("Value", enumerationValue)
					else:
						print type


					parameterIdx = parameterIdx + 1
					parameterId = applicationProgramId + "_P-%d" % parameterIdx
					parameterXML = ET.SubElement(parametersXML, "Parameter")
					parameterXML.set("Id", parameterId)
					parameterXML.set("Name", srcEntryXML.find("name").text)
					parameterXML.set("ParameterType", parameterTypeId)
					parameterXML.set("Text", srcEntryXML.find("name").text)
					addTranslations(languagesXML, srcEntryXML.findall("name"), applicationProgramId, parameterId, "Text")
					# According to spec: SuffixText. Missing?
					parameterXML.set("Access", "ReadWrite")
					parameterXML.set("Value", srcEntryXML.get("default"))
					# According to spec: Patch Always. Missing?
					# According to spec: Unique Number. Missing?
					
					#memoryXML = ET.SubElement(parameterXML, "Memory")
					#memoryXML.set("CodeSegment", "")
					#memoryXML.set("Offset", "0")
					#memoryXML.set("BitOffset", "0")
					
					#propertyXML = ET.SubElement(parameterXML, "Property")
					#propertyXML.set("ObjectIndex", "0")
					#propertyXML.set("PropertyId", "0")
					#propertyXML.set("Offset", "0")
					#propertyXML.set("BitOffset", "0")
					
					parameterRefId = parameterId + "_R-1"
					parameterRefXML = ET.SubElement(parameterRefsXML, "ParameterRef")
					parameterRefXML.set("Id", parameterRefId)
					parameterRefXML.set("RefId", parameterId)
					# According to spec: Text. Missing?
					# According to spec: SuffixText. Missing?
					# Obsolete! parameterRefXML.set("DisplayOrder", "1")
					# According to spec: Access. Missing?
					# According to spec: Default Value. Missing?
					parameterRefXML.set("Tag", "1")
				
					parameterRefRefXML = ET.SubElement(parameterBlockXML, "ParameterRefRef")
					parameterRefRefXML.set("RefId", parameterRefId)

				elif srcEntryXML.tag == "parameterSeparator":
					parameterSeparatorIdx += + 1
					parameterSeparatorId = applicationProgramId + "_PS-%d" % parameterSeparatorIdx
					parameterSeparatorXML = ET.SubElement(parameterBlockXML, "ParameterSeparator")
					parameterSeparatorXML.set("Id", parameterSeparatorId)
					parameterSeparatorText = srcEntryXML.find("text")
					if parameterSeparatorText is None:
						parameterSeparatorXML.set("Text", "")
					else:
						parameterSeparatorXML.set("Text", srcEntryXML.find("text").text)
						addTranslations(languagesXML, srcEntryXML.findall("text"), applicationProgramId, parameterSeparatorId, "Text")
					# According to spec: Access. Missing?

				else:
					print "Unknown tag: " + srcEntryXML.tag

	srcParametersXML = srcRootXML.find("comObjects")
	comObjectIdx = -1
	comObjectRefIdx = 0

	channelIndependentBlockXML = ET.SubElement(dynamicXML, "ChannelIndependentBlock")

	for srcEntryXML in srcParametersXML:
		if srcEntryXML.tag == "comObject":

			datapointTypeXML = masterRoot.find(".//knx:DatapointSubtype[@Id='" + srcEntryXML.find("datapointType").text + "']/../..", knxns)
			datapointSubtypeXML = masterRoot.find(".//knx:DatapointSubtype[@Id='" + srcEntryXML.find("datapointType").text + "']", knxns)
			bitSize = int(datapointTypeXML.get("SizeInBit"))
			
			if bitSize < 8:
				objectSize = "%d Bit" % bitSize
			elif bitSize == 8:
				objectSize = "1 Byte"
			elif (bitSize % 8) == 0:
				objectSize = "%d Bytes" % (bitSize / 8)
			else:
				print "Unknown bitsize: %d bits" % bitSize
			
			comObjectIdx += + 1
			comObjectId = applicationProgramId + "_O-%d" % comObjectIdx
			comObjectXML = ET.SubElement(comObjectTableXML, "ComObject")
			comObjectXML.set("Id", comObjectId)
			comObjectXML.set("Name", srcEntryXML.find("name").text)
			comObjectXML.set("Text", srcEntryXML.find("name").text)
			addTranslations(languagesXML, srcEntryXML.findall("name"), applicationProgramId, comObjectId, "Text")
			comObjectXML.set("Number", str(comObjectIdx))
			comObjectXML.set("FunctionText", srcEntryXML.find("function").text)
			addTranslations(languagesXML, srcEntryXML.findall("function"), applicationProgramId, comObjectId, "FunctionText")
			comObjectXML.set("Priority", "Low")
			comObjectXML.set("ObjectSize", objectSize)

			if srcEntryXML.find("readFlag") is None:
				comObjectXML.set("ReadFlag", "Disabled")
			else:
				comObjectXML.set("ReadFlag", "Enabled")

			if srcEntryXML.find("writeFlag") is None:
				comObjectXML.set("WriteFlag", "Disabled")
			else:
				comObjectXML.set("WriteFlag", "Enabled")

			comObjectXML.set("CommunicationFlag", "Enabled")

			if srcEntryXML.find("transmitFlag") is None:
				comObjectXML.set("TransmitFlag", "Disabled")
			else:
				comObjectXML.set("TransmitFlag", "Enabled")

			comObjectXML.set("UpdateFlag", "Enabled")
			comObjectXML.set("ReadOnInitFlag", "Disabled")
			comObjectXML.set("DatapointType", srcEntryXML.find("datapointType").text)
			# Not in spec. Obsolete? comObjectXML.set("VisibleDescription", "")
			
			comObjectRefIdx += 1
			comObjectRefId = comObjectId + "_R-%d" % comObjectRefIdx
			comObjectRefXML = ET.SubElement(comObjectRefsXML, "ComObjectRef")
			comObjectRefXML.set("Id", comObjectRefId)
			comObjectRefXML.set("RefId", comObjectId)
			# According to spec: Name. Missing?
			# According to spec: Text. Missing?
			# According to spec: Function Text. Missing?
			# According to spec: Priority. Missing?
			# According to spec: Object Size. Missing?
			# According to spec: Read Flag. Missing?
			# According to spec: Write Flag. Missing?
			# According to spec: Communication Flag. Missing?
			# According to spec: Transmit Flag. Missing?
			# According to spec: Update Flag. Missing?
			# According to spec: ReadOnInit Flag. Missing?
			#comObjectRefXML.set("DatapointType", "DPST-10-1")
			comObjectRefXML.set("Tag", str(comObjectRefIdx))

			comObjectRefRefXML = ET.SubElement(channelIndependentBlockXML, "ComObjectRefRef")
			comObjectRefRefXML.set("RefId", comObjectRefId)

	addressTableXML.set("CodeSegment", applicationProgramId + "_AS-4000")
	addressTableXML.set("Offset", "0")
	addressTableXML.set("MaxEntries", "200")

	associationTableXML.set("CodeSegment", applicationProgramId + "_AS-4193")
	associationTableXML.set("Offset", "0")
	associationTableXML.set("MaxEntries", "200")

	optionsXML.set("TextParameterEncodingSelector", "UseTextParameterEncodingCodePage")
	optionsXML.set("TextParameterEncoding", "utf-8")

	#chooseXML = ET.SubElement(parameterBlockXML, "choose")
	#chooseXML.set("ParamRefId", parameterRefId)

	#whenXML = ET.SubElement(chooseXML, "when")
	#whenXML.set("test", "1")

	manufacturerXML.append(languagesXML)

	return dstRootXML

catalogXML = createCatalog(root)

indent(catalogXML)
#ET.dump(catalogXML)
catalogTree = ET.ElementTree(catalogXML)
catalogTree.write("Catalog.xml", "utf-8", True)

hardwareXML = createHardware(root)

indent(hardwareXML)
#ET.dump(hardwareXML)
hardwareTree = ET.ElementTree(hardwareXML)
hardwareTree.write("Hardware.xml", "utf-8", True)

productXML = createProduct(root)

indent(productXML)
#ET.dump(productXML)
productTree = ET.ElementTree(productXML)
productTree.write(applicationProgramId + ".xml", "utf-8", True)
