
import automatey.StringUtils as StringUtils

class Utils:
    
    class Command:
        
        @staticmethod
        def normalize(inputCommand:str):
            strippedCommand = inputCommand.strip()
            normalizedCommand = StringUtils.Regex.replaceAll(r'\s+', ' ', strippedCommand)
            print(normalizedCommand)
            return normalizedCommand

class CommandTemplate:
    '''
    A command template.
    
    May include:
    - Section(s), represented as `{{{SECTION-NAME: ... :}}}`
    - Parameter(s), represented as `{{{PARAMETER-NAME}}}`
    
    Note that,
    - All name(s) must be upper-case.
    - Section name(s) must be unique (or, repeated, but identical in content).
    '''
    
    def __init__(self, *args):
        self.template = ' '.join(args)
        
    def assertSection(self, sectionName:str, params:dict):
        '''
        Assert a section, asserting contained parameter value(s).
        '''
        self.template = CommandTemplate.INTERNAL_Utils.Regex.assertSection(sectionName, params, self.template)
    
    def assertParameter(self, paramName:str, paramValue:str):
        '''
        Assert parameter value.
        '''
        self.template = CommandTemplate.INTERNAL_Utils.Regex.assertParameter(paramName, paramValue, self.template)
    
    def removeSection(self, sectionName:str):
        '''
        Remove a section.
        '''
        self.template = CommandTemplate.INTERNAL_Utils.Regex.removeSection(sectionName, self.template)
    
    def __str__(self):
        return Utils.Command.normalize(self.template)
    
    def __repr__(self):
        return str(self)
    
    class INTERNAL_Utils:
        
        class Regex:
            
            @staticmethod
            def formatSectionExpression(sectionName:str):
                '''
                Format a section Regex match expression.
                '''
                return r'{{{' + sectionName.upper() + ':' + r'(.*)' + r':}}}'
            
            @staticmethod
            def formatParameterExpression(paramName:str):
                '''
                Format a parameter Regex match expression.
                '''
                return r'{{{' + paramName.upper() + r'}}}'
            
            @staticmethod
            def assertParameter(paramName:str, paramValue:str, txt):
                '''
                Assert parameter value.
                '''
                paramExpr = CommandTemplate.INTERNAL_Utils.Regex.formatParameterExpression(paramName)
                txt = StringUtils.Regex.replaceAll(paramExpr, paramValue, txt)
                return txt

            @staticmethod
            def assertSection(sectionName:str, params:dict, txt):
                '''
                Assert a section, asserting contained parameter value(s).
                '''
                sectionExpr = CommandTemplate.INTERNAL_Utils.Regex.formatSectionExpression(sectionName)
                sectionContent = StringUtils.Regex.findAll(sectionExpr, txt)[0]
                for paramName in params:
                    sectionContent = CommandTemplate.INTERNAL_Utils.Regex.assertParameter(paramName, params[paramName])
                txt = StringUtils.Regex.replaceAll(sectionExpr, sectionContent, txt)
                return txt
            
            @staticmethod
            def removeSection(sectionName:str, txt):
                '''
                Remove a section.
                '''
                sectionExpr = CommandTemplate.INTERNAL_Utils.Regex.formatSectionExpression(sectionName)
                txt = StringUtils.Regex.replaceAll(sectionExpr, '', txt)
                return txt
