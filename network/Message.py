"""
Message consists of code + instructions (ex. 100 HELLO)
There are two ways for making Massage
1. With constructer  
    Message(102, {"NAME", "hogehoge"})
2. With "convertToMessage" method
    convertToMessage("102 NAME hogehoge")
"""
class Message:
    def __init__(self, code, instructions):
        self.code = code
        self.instructions = instructions
    def __str__(self):
        return str(self.code)+" "+' '.join(self.instructions) + "\n"
    @staticmethod
    def createFromRawMessage(raw_message):
        vector = raw_message.split()
        code = int(vector[0])
        instructions = vector[1:]
        return Message(code, instructions)

