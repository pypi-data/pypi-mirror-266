# https://community.bistudio.com/wiki/Arma_3:_Server_Config_File


def is_quoted(arg) -> bool:
    quoted = True
    if arg == "integer" or arg == "float":
        quoted = False
    return quoted


class BaseLineType(object):

    @staticmethod
    def generate(name, value, arg):
        pass


class SimpleType(BaseLineType):

    @staticmethod
    def generate(name, value, arg):
        quoted = is_quoted(arg)
        if quoted:
            return f'{name} = "{value}";'
        else:
            return f"{name} = {value};"


class ListType(BaseLineType):

    @staticmethod
    def generate(name, value, arg):
        quoted = is_quoted(arg)
        product = []
        newline = "\n"
        if quoted:
            quote = '"'
        else:
            quote = ""

        product.append(f"{name}[] = {{{newline}")
        for item in value:
            product.append(f"  {quote}{item}{quote},{newline}")
        product.append(f"}};{newline}")

        return "".join(product)


class MissionType(BaseLineType):
    pass


class MPMissionType(BaseLineType):
    pass


class Generator(object):

    def __init__(self, data):
        self.data = data

    # # hostname = "Fun and Test Server";
    # # motdInterval = 5;
    # def simple_lineitem(self, key, value, quoted=False):
    #     if quoted:
    #         return f'{key} = "{value}";'
    #     else:
    #         return f'{key} = {value};'

    # # missionWhitelist[] = {
    # #   "direct_action_dev.Altis",
    # # };
    # # list_items('missionWhiteList', 'direct_action_dev.Altis', true, false)
    # def list_items(self, key, values, quoted=False, newlines=True):

    #     product = []
    #     if newlines:
    #         newline = ""
    #     else:
    #         newline = "\n"
    #     if quoted:
    #         quote = '"'
    #     else:
    #         quote = ''

    #     product.append(f'{key}[] = {{{newline}')
    #     for item in values:
    #         product.append(f'  {quote}{item}{quote},{newline}')
    #     product.append(f'}};{newline}')

    #     return "".join(product)

    # def generate(self):
    #     for
