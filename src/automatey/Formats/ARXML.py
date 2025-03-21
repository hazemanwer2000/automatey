
# Internal Libraries
import automatey.Formats.XMLParser as XMLParser
import automatey.Utils.StringUtils as StringUtils

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
        # ? ? Remove 'UUID' attribute.
        xmlElementsWithUUID = xmlElement.XPath('./descendant-or-self::*[@UUID]')
        for xmlElementWithUUID in xmlElementsWithUUID:
            del xmlElementWithUUID.getAttributes()['UUID']
        # ? ? Remove 'ADMIN-DATA' element.
        xmlAllElements = xmlElement.XPath('./descendant-or-self::*')
        for xmlWorkingElement in xmlAllElements:
            xmlAdminDataSearchResult = xmlWorkingElement.XPath('./ADMIN-DATA')
            if len(xmlAdminDataSearchResult) == 1:
                xmlAdminData = xmlAdminDataSearchResult[0]
                xmlWorkingElement.removeElement(xmlAdminData)
        self.xmlElement = xmlElement
        
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
    
    def getElements(self, conditional=None) -> typing.List[Element]:
        '''
        Access elements.
        '''
        elements = self.elements
        if conditional is not None:
            elements = [element for element in elements if conditional(element)]
        return elements
