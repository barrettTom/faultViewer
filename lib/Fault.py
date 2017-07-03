import lxml.etree as ET

class Fault(object):
    def __init__(self, program, rung=None):
        self.program = program
        self.rung = rung
        try:
            textElement = str(rung.findall("Text")[0].text)
            f = textElement.find("AOI_Fault_Set_Reset")
            if f == -1:
                self.valid = False
                return

            textElement = textElement[f:]
            p = textElement.find(')')
            textElement = textElement[:p].split(',')[2:4]

            self.number = int(textElement[0])
            self.catagory = textElement[1]

            self.literal = self.getFaultLiteral()
            self.text = self.getFaultText(self.literal)
            self.element = self.getFaultElement()

            self.valid = True
        except:
            self.number = program
            self.catagory = ""
            self.text = ""
            self.literal = ""
            self.valid = False

    def getFaultText(self, literal):
        if len(literal.split(':')) == 2:
            comment = literal.split(':')[1]
        elif len(literal.split(':')) == 3:
            comment = literal.split(':')[1] + literal.split(':')[2]

        name = self.program.attrib['Name'].split("_")[1]
        mtn = name[:3]
        stn = name[3:]
        if stn == "":
            stn = "G3"
        if mtn[0] == '5':
            loop = "07"
        elif mtn[0] == '6':
            loop = "08"
        elif mtn[0] == '7':
            loop = "09"
        else:
            loop = "10"

        try:
            f = comment[1:].find(" ") + 1

            sensor = comment[1:f]

            comment = comment[f:]

            comment = loop + mtn + "_" + stn + "_" + sensor + ":" + comment
        except:
            comment = "ERROR: NOT CORRECT FORMAT"

        return comment

    def getFaultLiteral(self):
        literal = self.rung.findall("Comment")
        if literal:
            literal = literal[0].text
            literal = literal.split('\n')[2]
            return literal
        else:
            return False

    def getFaultElement(self):
        element = self.rung.findall("Comment")[0]
        return element

    def fix(self):
        self.catagoryFix()
        self.numberFix()

    def catagoryFix(self):
        if self.catagory.find("Warning") != -1:
            self.catagory = "M"
        elif self.catagory.find("Stop") != -1:
            self.catagory = "C"
        elif self.catagory.find("Abort") != -1:
            self.catagory = "I"
        return self

    def numberFix(self):
        n = str(self.number)
        if len(n) == 1:
            self.number = "Fault_00" + n
        if len(n) == 2:
            self.number = "Fault_0" + n
        if len(n) == 3:
            self.number = "Fault_" + n
        if self.text == "":
            self.text = self.number

    def giveLiteral(self, value):
        self.literal = value

        f = ">"*75
        value = '\n' + f + '\n' + value + '\n' + f + '\n'
        self.element.text = ET.CDATA(value)
