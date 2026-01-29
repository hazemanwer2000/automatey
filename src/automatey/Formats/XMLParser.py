
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
    
    def saveAs(self, f:FileUtils.File, indent:str='  '):
        '''
        Save as XML file.
        '''
        if f.isExists():
            raise ExceptionUtils.ValidationError('Destination file must not exist.')

        with f.openFile('wt') as handler:
            handler.writeAny(self.toString(indent=indent))
    
    def toString(self, indent:str='  '):
        text = lxml.etree.tostring(self.root, pretty_print=True, encoding="utf-8", xml_declaration=True)
        dom = xml.dom.minidom.parseString(text)
        return StringUtils.EmptyLine.removeEmptyLines(dom.toprettyxml(indent=indent))
    
    def __str__(self):
        return self.toString()

    def __repr__(self):
        return str(self)
    
    # General operation(s).

    def XPath(self, query, namespaces=None) -> typing.List["XML"]:
        '''
        Returns a list, the result of the given XPath query.
        
        Note that,
        - XPath queries the search for non-elements are prohibited.
        - `namespaces` is a `dict`, mapping prefix to namespace URI.
            - For example, `{'ns':'http://example.com/ns'}`.
        '''
        kwargs = {}
        if namespaces is not None:
            kwargs['namespaces'] = namespaces

        result = self.root.xpath(query, **kwargs)
        return [XML(element) for element in result]

    def getTag(self) -> str:
        '''
        Get tag.
        '''
        tag = self.root.tag

        # ? Search for namespace.
        result = StringUtils.Regex.findAll(r'\{.+\}(.+)', tag)
        if len(result) > 0:
            tag = result[0]
            
        return tag
    
    def getNamespace(self) -> str:
        '''
        Get namespace. If undefined, `None` is returned.
        '''
        ns = None

        # ? Search for namespace.
        result = StringUtils.Regex.findAll(r'\{(.+)\}.+', self.root.tag)
        if len(result) > 0:
            ns = result[0]
            
        return ns
    
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

    def getChildren(self) -> typing.List["XML"]:
        '''
        Get list of children.
        '''
        return [XML(x) for x in self.root.iterchildren()]

    def getParent(self) -> "XML":
        '''
        Get parent. If not applicable, `None` is returned.
        '''
        parentNode = self.root.getparent()
        return XML(parentNode) if (parentNode is not None) else None

    # Formatting-specific operation(s)

    def removeAllAttributes(self, conditional):
        '''
        Remove all attributes that satisfy a conditional.

        Conditional must accept `element, attribute-name`.
        '''
        descendantsOrSelf = self.XPath(query='./descendant-or-self::*')
        for element in descendantsOrSelf:
            for attrib_name in element.getAttributes():
                if conditional(element, attrib_name):
                    del element.getAttributes()[attrib_name]
    
    def removeAllComments(self):
        '''
        Remove all comment(s).
        '''
        comments = self.XPath(query='./descendant::comment()')
        for comment in comments:
            comment.getParent().removeElement(comment)
    
    def removeAllElements(self, conditional):
        '''
        Remove all descendant element(s) that satisfy a conditional.
        '''
        descendants = self.XPath(query='./descendant::*')
        for descendant in descendants:
            if conditional(descendant):
                descendant.getParent().removeElement(descendant)

    def removeElement(self, xml:"XML"):
        '''
        Remove child element.
        '''
        if xml.root in self.root.iterchildren():
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
