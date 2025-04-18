
# Internal Libraries
import automatey.Formats.XMLParser as XMLParser
import automatey.Utils.StringUtils as StringUtils
import automatey.Utils.MathUtils as MathUtils
import automatey.OS.FileUtils as FileUtils

# Standard Libraries
import typing

class Models:
    '''
    Modelled (i.e., parsable) representation(s) of an element, with a specific type.
    '''
    
    pass

class Element:
    '''
    Representation of an element.
    '''
    
    def __init__(self, xmlElement:XMLParser.XML):

        # ? XML element clean-up.
        self.xmlElement = xmlElement
        # ? ? Remove (useless) attribute(s).
        self.xmlElement.removeAllAttributes(conditional=lambda e, a: a in ['UUID'])
        # ? ? Remove (useless) element(s).
        self.xmlElement.removeAllElements(conditional=lambda e: e.getTag() in ['ADMIN-DATA', 'DESC', 'LONG-NAME'])
        # ? ? Remove all comment(s).
        self.xmlElement.removeAllComments()

        # ? Trace package path.
        xmlWorkingElement = self.xmlElement
        packagePathList = []
        while True:
            xmlParentElementSearchResult = xmlWorkingElement.XPath('./parent::*/parent::*')
            if len(xmlParentElementSearchResult) != 1: break
            xmlParentElement = xmlParentElementSearchResult[0]
            if xmlParentElement.getTag() != 'AR-PACKAGE': break
            packagePathList.append(xmlParentElement.XPath('./SHORT-NAME')[0].getText())
            xmlWorkingElement = xmlParentElement
        self.packagePath = '/' + '/'.join(reversed(packagePathList))
        
        # ? Fetch element name.
        self.name = self.xmlElement.XPath('./SHORT-NAME')[0].getText()
        
        # ? Fetch element type.
        self.type = self.xmlElement.getTag()
        
        # ? Construct model instance, if relevant model is defined.
        self.modelInstance = None
        type_PascalCase = StringUtils.Case.Snake2Pascal(self.type, character='-')
        if type_PascalCase in Models.__dict__:
            self.modelInstance = Models.__dict__[type_PascalCase](self)
        
    def getXML(self) -> XMLParser.XML:
        '''
        Returns (raw) XML.
        '''
        return self.xmlElement

    def getPackagePath(self) -> str:
        '''
        Return path of element (excluding name).
        '''
        return self.packagePath
    
    def getName(self) -> str:
        '''
        Get element name.
        '''
        return self.name
    
    def getPath(self) -> str:
        '''
        Return path of element (including name). 
        '''
        return self.getPackagePath() + '/' + self.getName()

    def getType(self) -> str:
        '''
        Get element type.
        '''
        return self.type

    def getModel(self):
        '''
        Get model, that corresponds to element type.
        
        If no model is found, `None` is returned.
        '''
        return self.modelInstance

    def __str__(self):
        return self.getType() + ': ' + self.getPath()
    
    def __repr__(self):
        return str(self)

class Parser:
    '''
    A parser of ARXML file(s).
    '''
    def __init__(self):
        self.elements:typing.List[Element] = []
    
    def processFile(self, f_arxml:FileUtils.File):
        '''
        Process a number of ARXML file(s).
        
        Note that,
        - Processing is incremental (i.e., builds on previously processed file(s)).
        '''
        # (!) Workaround: Remove AUTOSAR namespace from XML, to ease XML navigation.
        #       Very inefficient for large XML file(s).
        xmlText = f_arxml.quickRead('t')
        xmlText = StringUtils.Regex.replaceAll(r'<AUTOSAR .*?>', r'<AUTOSAR>', xmlText)
        
        xmlRoot = XMLParser.XML.fromString(xmlText)
        xmlElements = xmlRoot.XPath('/descendant::AR-PACKAGE/ELEMENTS/*') + xmlRoot.XPath('/descendant::AUTOSAR/ELEMENTS/*')
        self.elements.extend([Element(xmlElement) for xmlElement in xmlElements])
    
    def getElements(self, conditional=None) -> typing.List[Element]:
        '''
        Access elements.
        '''
        elements = self.elements
        if conditional is not None:
            elements = [element for element in elements if conditional(element)]
        return elements

    def getTypes(self) -> dict:
        '''
        Get dictionary of types, that points to a dictionary of,
        - `count` : Number of elements.
        - `elements` : List of elements.
        '''
        self.elements.sort(key=lambda x: (x.getType(), x.getPath()))
        typeDict = MathUtils.CollectionSpecific.countOccurrences(self.elements, key=lambda x: x.getType())
        for elementType in typeDict:
            occurrenceCount = typeDict[elementType]
            typeDict[elementType] = {
                'count' : occurrenceCount,
                'elements' : []
            }
        for element in self.elements:
            typeDict[element.getType()]['elements'].append(element)
        return typeDict

    def summarize(self, isVerbose:bool=True) -> str:
        '''
        Summarize element(s).
        '''
        writer = StringUtils.Writer()
        typeDict = self.getTypes()
        for elementType in typeDict:
            writer.write(f"{elementType} ({typeDict[elementType]['count']})")
            if isVerbose:
                for element in typeDict[elementType]['elements']:
                    writer.write(f"  {element.getPath()}")
        return str(writer)
    
    def __str__(self):
        return self.summarize()
    
    def __repr__(self):
        return str(self)
