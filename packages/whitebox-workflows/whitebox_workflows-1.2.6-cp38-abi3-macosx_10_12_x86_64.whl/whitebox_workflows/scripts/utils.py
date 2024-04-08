class LicenseError(Exception):
    def __init__(self, message="This function requires a license for WbW-Pro. Please visit www.whiteboxgeo.com to purchase a license for WbW-Pro."):            
        self.message = message
        super().__init__(self.message)

def print_tool_header(tool_name: str):
    # 44 = length of the 'Powered by' by statement.
    powered_by_statement_length = 44
    welcome_len = max(len(f"* Welcome to {tool_name} *", ), powered_by_statement_length)
    stars = "*" * welcome_len
    print(f"{stars}")
    spaces = " " * (welcome_len - 15 - len(tool_name))
    print(f"* Welcome to {tool_name} {spaces}*")
    spaces = " " * (welcome_len - powered_by_statement_length)
    print(f"* Powered by Whitebox Workflows for Python {spaces}*")
    spaces = " " * (welcome_len - 23)
    print(f"* www.whiteboxgeo.com {spaces}*")
    print(f"{stars}")
