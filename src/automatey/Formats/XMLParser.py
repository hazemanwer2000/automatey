
# Internal Libraries
import automatey.OS.FileUtils as FileUtils
import automatey.Utils.StringUtils as StringUtils

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
    def fromScratch(tag)-> "XML":
        '''
        Create XML(-element) fom scratch.
        '''
        return XML(lxml.etree.Element(tag))
    
    def saveAs(self, f:FileUtils.File):
        '''
        Save as XML file.
        '''
        with f.openFile('wt') as handler:
            handler.writeAny(str(self))
    
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
    
    def attributes(self) -> dict:
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
    
    def __str__(self):
        text = lxml.etree.tostring(self.root, pretty_print=True, encoding='unicode')
        dom = xml.dom.minidom.parseString(text)
        return StringUtils.Normalize.asParagraph(dom.toprettyxml())

    def __repr__(self):
        return str(self)
    
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
            print(element.getTag())
            textAsSentence = StringUtils.Normalize.asSentence(element.getText())
            element.setText(textAsSentence)
            