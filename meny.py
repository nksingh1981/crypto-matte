#add this file in .nuke folder

import extract_cryptomatte

# add menu entry in top menu Bar
menubar = nuke.menu("Nuke")
m = menubar.addMenu("PythonScript Tool")
m.addCommand("Advance Cryptomatte Extract", "extract_cryptomatte.crypto_tool()")