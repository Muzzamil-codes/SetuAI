import os
import sys

os.system(
    f'"{sys.executable}" input_builder.py'
)

os.system(
    f'"{sys.executable}" chart_generator.py'
)

os.system(
    f'"{sys.executable}" docx_builder.py'
)

os.system(
    f'"{sys.executable}" xlsx_builder.py'
)

os.system(
    f'"{sys.executable}" pptx_builder.py'
)

print(
    "\nAll Artifacts Generated Successfully!"
)