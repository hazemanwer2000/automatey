
# Internal Libraries
import automatey.OS.FileUtils as FileUtils
import automatey.Utils.StringUtils as StringUtils
import automatey.Utils.ExceptionUtils as ExceptionUtils

# External Libraries
import typing
import copy
import lxml.etree
import xml.dom.minidom

class XML:
    
    '''
    XML representation.
    '''
    
    # Loading operation(s).
    
    def __init__(self, root):
        self.root = root
    
    @staticmethod
    def fromFile(f:FileUtils.File) -> "XML":
        '''
        Read from XML file.
        '''
        tree = lxml.etree.parse(str(f))
        return XML(tree.getroot())

    @staticmethod
    def fromString(text:str) -> "XML":
        '''
        Parse XML from string.
        '''
        root = lxml.etree.fromstring(text.encode("utf-8"))
        return XML(root)
    
    @staticmethod
    def fromScratch(tag)-> "XML":
        '''
        Create XML(-element) fom scratch.
        '''
        return XML(lxml.etree.Element(tag))
    
    def saveAs(self, f:FileUtils.File, indent:str='\t'):
        '''
        Save as XML file.
        '''
        if f.isExists():
            raise ExceptionUtils.ValidationError('Destination file must not exist.')

        with f.openFile('wt') as handler:
            handler.writeAny(self.toString(indent=indent))
    
    def toString(self, indent:str='\t'):
        text = lxml.etree.tostring(self.root, pretty_print=True, encoding='unicode')
        dom = xml.dom.minidom.parseString(text)
        return StringUtils.EmptyLine.removeEmptyLines(dom.toprettyxml(indent=indent))
    
    def __str__(self):
        return self.toString()

    def __repr__(self):
        return str(self)
    
    # General operation(s).

    def XPath(self, query) -> typing.List["XML"]:
        '''
        Returns a list, the result of the given XPath query.
        
        Note that,
        - XPath queries must always return an element.
        '''
        result = self.root.xpath(query)
        return [XML(element) for element in result]

    def getTag(self) -> str:
        '''
        Get tag.
        '''
        return self.root.tag
    
    def setTag(self, tag:str):
        '''
        Set tag.
        '''
        self.root.tag = tag
    
    def getAttributes(self) -> dict:
        '''
        Get attributes, as `dict`.
        
        Note,
        - It can be used for reading, and setting attributes.
        '''
        return self.root.attrib
    
    def getText(self) -> str:
        '''
        Get text. Returns `''` if no text is found.
        '''
        text = self.root.text if (self.root.text != None) else ''
        return text.strip()
    
    def setText(self, text:str):
        '''
        Set text.
        '''
        self.root.text = text

    # Formatting-specific operation(s)
    
    def removeElement(self, xml:"XML"):
        '''
        Remove child element.
        '''
        self.root.remove(xml.root)

    def removeElementByIndex(self, idx:int):
        '''
        Remove child element by index.
        '''
        self.root.remove(self.root[idx])

    def insertElement(self, xml:"XML", idx:int=-1):
        '''
        Insert element as child. If index is unspecified, element is appeneded.
        '''
        if idx == -1:
            self.root.append(xml.root)
        else:
            self.root.insert(idx, xml.root)
    
    def copy(self) -> "XML":
        '''
        (Deep-)Copy element.
        '''
        return copy.deepcopy(self)

    # String-Formatting-specific operation(s).
    
    def normalizeAllTextAsSentence(self):
        '''
        Normalize text of element, and all descendant(s), as sentence.
        '''
        result = self.XPath('./descendant-or-self::*')
        for element in result:
            textAsSentence = StringUtils.Normalize.asSentence(element.getText())
            element.setText(textAsSentence)
