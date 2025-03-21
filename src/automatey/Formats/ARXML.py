
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
        self.path = None
        
    def getXML(self) -> XMLParser.XML:
        '''
        Returns (raw) XML.
        '''
        return self.xml

    def getPath(self) -> str:
        '''
        Return element path.
        '''
        if self.path is None:
            workingElement = self.xml
            pathList = []
            while (True):
                parentElementSearchResult = workingElement.XPath('./parent::*/parent::*')
                if len(parentElementSearchResult) != 1: break
                parentElement = parentElementSearchResult[0]
                if parentElement.getTag() != 'AR-PACKAGE': break
                pathList.append(parentElement.XPath('./SHORT-NAME')[0].getText())
                workingElement = parentElement
            self.path = '/' + '/'.join(reversed(pathList))
        return self.path
    
    def getName(self) -> str:
        '''
        Get element name.
        '''
        return self.xml.XPath('./SHORT-NAME')[0].getText()

    def getType(self):
        '''
        Get element type (e.g., `ETHERNET-CLUSTER`).
        '''
        modelName = StringUtils.Case.Snake2Pascal(self.xml.getTag(), character='-')
        return modelName

    def getModel(self):
        '''
        Get model, that corresponds to element type.
        
        If no model is found, `None` is returned.
        '''
        modelName = StringUtils.Case.Snake2Pascal(self.xml.getTag(), character='-')

class Parser:
    '''
    A parser of ARXML file(s).
    '''
    def __init__(self):
        self.elements = []
    
    def process(self, f_arxml):
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
