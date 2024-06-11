import openpyxl
from pptx import Presentation
from pptx.util import Inches

# Open the Excel file
wb = openpyxl.load_workbook('Client Use Cases.xlsx')
sheet = wb.active

# Load the sample PowerPoint to use its theme
prs = Presentation('DATAASTRAA_SAMPLE_PPTX.pptx')

current_project = ''

# Loop through the data
for row in sheet.iter_rows(min_row=2, values_only=True):  # Assuming data starts from the second row
    project, project_description, module, module_description = row
    print(project, project_description, module, module_description)

    if project == 'Done':
        break

    if project:
        current_project = project
        # Create a main heading slide for the project
        slide_layout = prs.slide_layouts[1]  # Assuming 1 is the Title and Content layout
        slide = prs.slides.add_slide(slide_layout)
        title = slide.shapes.title
        content = slide.placeholders[1]
        title.text = project
        content.text = project_description

    # Create a subsequent slide for each module
    module_slide_layout = prs.slide_layouts[1]  # Assuming 1 is the Title and Content layout
    module_slide = prs.slides.add_slide(module_slide_layout)
    title = module_slide.shapes.title
    content = module_slide.placeholders[1]
    title.text = module
    content.text = module_description

print('for loop done')
# Save the presentation
output_pptx_path = 'project_modules_presentation.pptx'
prs.save(output_pptx_path)

print(f"Presentation saved as '{output_pptx_path}'")
