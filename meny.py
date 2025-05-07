import extract_cryptomatte

# add menu entry in toop menu Bar
menubar = nuke.menu("Nuke")
m = menubar.addMenu("PythonScript Tool")
m.addCommand("Advance Cryptomatte Extract", "extract_cryptomatte.crypto_tool()")