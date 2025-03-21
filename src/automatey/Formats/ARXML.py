
# Internal Libraries
import automatey.Formats.XMLParser as XMLParser
import automatey.Utils.StringUtils as StringUtils

# Standard Libraries
import typing

class Model:
    
    pass

class Element:
    
    def __init__(self, xml:XMLParser.XML):
        self.xml = xml
        
        # ? Attributes, defined upon-demand.
        self.packagePath = None
        self.name = None
        self.type = None
        self.modelInstance = None
        
    def getXML(self) -> XMLParser.XML:
        '''
        Returns (raw) XML.
        '''
        return self.xml

    def getPackagePath(self) -> str:
        '''
        Return path of element (excluding name).
        '''
        if self.packagePath is None:
            workingElement = self.xml
            pathList = []
            while True:
                parentElementSearchResult = workingElement.XPath('./parent::*/parent::*')
                if len(parentElementSearchResult) != 1: break
                parentElement = parentElementSearchResult[0]
                if parentElement.getTag() != 'AR-PACKAGE': break
                pathList.append(parentElement.XPath('./SHORT-NAME')[0].getText())
                workingElement = parentElement
            self.packagePath = '/' + '/'.join(reversed(pathList))
        return self.packagePath
    
    def getName(self) -> str:
        '''
        Get element name.
        '''
        if self.name is None:
            self.name = self.xml.XPath('./SHORT-NAME')[0].getText()
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
        if self.type is None:
            self.type = self.xml.getTag()
        return self.type

    def getModel(self):
        '''
        Get model, that corresponds to element type.
        
        If no model is found, `None` is returned.
        '''
        if self.modelInstance is None:
            typeAsStr = StringUtils.Case.Snake2Pascal(self.getType(), character='-')
            if typeAsStr in Model.__dict__:
                self.modelInstance = Model.__dict__[typeAsStr](self)
        return self.modelInstance

class Parser:
    '''
    A parser of ARXML file(s).
    '''
    def __init__(self):
        self.elements = []
    
    def processFile(self, f_arxml):
        '''
        Process a number of ARXML file(s).
        
        Note that,
        - Processing is incremental (i.e., builds on previously processed file(s)).
        '''
        xmlRoot = XMLParser.XML.fromFile(f_arxml)
        xmlElements = xmlRoot.XPath('/descendant::AR-PACKAGE/ELEMENTS/*') + xmlRoot.XPath('/descendant::AUTOSAR/ELEMENTS/*')
        self.elements.extend([Element(xmlElement) for xmlElement in xmlElements])
    
    def getElements(self) -> typing.List[Element]:
        '''
        Access elements.
        '''
        return self.elements
