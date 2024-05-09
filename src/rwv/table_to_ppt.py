import pandas as pd
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.shapes import MSO_AUTO_SHAPE_TYPE as MSO_SHAPE

# Create a PowerPoint presentation
presentation = Presentation()

max_rows_per_slide = 15


def generate_powerpoint(selected_query, data, headers):

    data = pd.DataFrame(data=data, columns=headers)

    slide_num = 1
    page_count = 1
    total_number_of_slides = 10

    # TODO: THIS IS GARBAGE, THESE VALUES SHOULD NOT BE HARDCODED TO THE TYPE OF QUERY
    # for query_title in selected_queries:
    #     if query_title == "Athlete Infraction Summary":
    #         total_number_of_slides = total_number_of_slides + 3
    #     else:
    #         total_number_of_slides = total_number_of_slides + 1

    # Determine the number of chunks needed based on the maximum rows per slide
    num_rows = data.shape[0]
    chunks = [
        data.iloc[i : i + max_rows_per_slide]
        for i in range(0, num_rows, max_rows_per_slide)
    ]

    for chunk in chunks:
        slide_layout = presentation.slide_layouts[
            5
        ]  # Use the layout that supports title and content
        slide = presentation.slides.add_slide(slide_layout)
        title = slide.placeholders[0]

        # Set table title
        if len(chunks) > 1:
            title.text = f"{selected_query} Page {slide_num}"
            slide_num += 1
        else:
            title.text = selected_query

        # Add a table to the slide
        rows, cols = chunk.shape
        table = slide.shapes.add_table(
            rows=rows + 1,
            cols=cols,
            left=Inches(0.5),
            top=Inches(2),
            width=Inches(9),
            height=Inches(0.5),
        ).table

        # Set column names as the first row of the table
        for col_num, col_name in enumerate(chunk.columns):
            cell = table.cell(0, col_num)
            cell.text = col_name
            cell.text_frame.paragraphs[0].font.size = Pt(10)

        # Populate the table with data
        for row_num in range(rows):
            for col_num, value in enumerate(chunk.iloc[row_num]):
                cell = table.cell(row_num + 1, col_num)
                cell.text = str(value)
                cell.text_frame.paragraphs[0].font.size = Pt(10)

        # add page number
        page_number_text = slide.shapes.add_textbox(0, 0, Inches(1), Inches(1))
        page_number_text.text_frame.text = str(page_count)

        # add buttons (spacing and number of buttons change depending on the number of slides)
        button_count = 1

        # TODO: THESE SHOULDN'T BE HARDCODED EITHER
        if total_number_of_slides == 10:
            button_spacing = 1.5
        elif total_number_of_slides == 9:
            button_spacing = 2
        elif total_number_of_slides == 8:
            button_spacing = 1.75
        elif total_number_of_slides == 7:
            button_spacing = 1.75
        elif total_number_of_slides == 6:
            button_spacing = 2
        elif total_number_of_slides == 5:
            button_spacing = 2.5
        elif total_number_of_slides == 4:
            button_spacing = 2.6
        elif total_number_of_slides == 3:
            button_spacing = 2.8
        elif total_number_of_slides == 2:
            button_spacing = 3.5

        while button_count <= total_number_of_slides:
            if total_number_of_slides == 1:
                # add "page 1" button when only 1 table is select
                shape = slide.shapes.add_shape(
                    MSO_SHAPE.ROUNDED_RECTANGLE,
                    Inches(4.9),
                    Inches(6.75),
                    Inches(0.35),
                    Inches(0.5),
                )
                shape.text_frame.text = str(button_count)
                button_count = button_count + 1
            else:  # cases for any other amounts of pages
                # TODO: THESE SHOULDN'T BE HARDCODED EITHER
                if total_number_of_slides == 10:
                    shape = slide.shapes.add_shape(
                        MSO_SHAPE.ROUNDED_RECTANGLE,
                        Inches(button_spacing),
                        Inches(6.75),
                        Inches(0.55),
                        Inches(0.5),
                    )
                    shape.text_frame.text = str(button_count)
                    button_spacing = button_spacing + 0.72
                    button_count = button_count + 1

                elif total_number_of_slides == 9:
                    shape = slide.shapes.add_shape(
                        MSO_SHAPE.ROUNDED_RECTANGLE,
                        Inches(button_spacing),
                        Inches(6.75),
                        Inches(0.55),
                        Inches(0.5),
                    )
                    shape.text_frame.text = str(button_count)
                    button_spacing = button_spacing + 0.72
                    button_count = button_count + 1

                elif total_number_of_slides == 8:
                    shape = slide.shapes.add_shape(
                        MSO_SHAPE.ROUNDED_RECTANGLE,
                        Inches(button_spacing),
                        Inches(6.75),
                        Inches(0.55),
                        Inches(0.5),
                    )
                    shape.text_frame.text = str(button_count)
                    button_spacing = button_spacing + 0.85
                    button_count = button_count + 1

                elif total_number_of_slides == 7:
                    shape = slide.shapes.add_shape(
                        MSO_SHAPE.ROUNDED_RECTANGLE,
                        Inches(button_spacing),
                        Inches(6.75),
                        Inches(0.55),
                        Inches(0.5),
                    )
                    shape.text_frame.text = str(button_count)
                    button_spacing = button_spacing + 1
                    button_count = button_count + 1

                elif total_number_of_slides == 6:
                    shape = slide.shapes.add_shape(
                        MSO_SHAPE.ROUNDED_RECTANGLE,
                        Inches(button_spacing),
                        Inches(6.75),
                        Inches(0.55),
                        Inches(0.5),
                    )
                    shape.text_frame.text = str(button_count)
                    button_spacing = button_spacing + 1.15
                    button_count = button_count + 1

                elif total_number_of_slides == 5:
                    shape = slide.shapes.add_shape(
                        MSO_SHAPE.ROUNDED_RECTANGLE,
                        Inches(button_spacing),
                        Inches(6.75),
                        Inches(0.55),
                        Inches(0.5),
                    )
                    shape.text_frame.text = str(button_count)
                    button_spacing = button_spacing + 1.2
                    button_count = button_count + 1

                elif total_number_of_slides == 4:
                    shape = slide.shapes.add_shape(
                        MSO_SHAPE.ROUNDED_RECTANGLE,
                        Inches(button_spacing),
                        Inches(6.75),
                        Inches(0.55),
                        Inches(0.5),
                    )
                    shape.text_frame.text = str(button_count)
                    button_spacing = button_spacing + 1.5
                    button_count = button_count + 1

                elif total_number_of_slides == 3:
                    shape = slide.shapes.add_shape(
                        MSO_SHAPE.ROUNDED_RECTANGLE,
                        Inches(button_spacing),
                        Inches(6.75),
                        Inches(0.55),
                        Inches(0.5),
                    )
                    shape.text_frame.text = str(button_count)
                    button_spacing = button_spacing + 2
                    button_count = button_count + 1

                elif total_number_of_slides == 2:
                    shape = slide.shapes.add_shape(
                        MSO_SHAPE.ROUNDED_RECTANGLE,
                        Inches(button_spacing),
                        Inches(6.75),
                        Inches(0.55),
                        Inches(0.5),
                    )
                    shape.text_frame.text = str(button_count)
                    button_spacing = button_spacing + 2.5
                    button_count = button_count + 1

        # add "Previous Slide" button to each slide
        shape = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE,
            Inches(0.25),
            Inches(6.75),
            Inches(1.0),
            Inches(0.5),
        )
        shape.text_frame.text = "<"
        shape.text_frame.fit_text("Calibri", 12, True, False, None)

        # add "Next Slide" button to each slide
        shape = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE,
            Inches(8.75),
            Inches(6.75),
            Inches(1.0),
            Inches(0.5),
        )
        shape.text_frame.text = ">"
        shape.text_frame.fit_text("Calibri", 12.5, True, False, None)

        page_count = page_count + 1


def add_button_functionality(file_path):
    page_number = 0

    total_number_of_slides = 10

    while page_number < total_number_of_slides:

        # add "next slide and previous slide" button functionality
        this_slide, previous_slide = (
            presentation.slides[page_number],
            presentation.slides[page_number - 1],
        )

        if page_number != total_number_of_slides - 1:
            try:
                next_slide = presentation.slides[page_number + 1]
            except:
                # TODO: Temp fix, needs to be addressed
                next_slide = presentation.slides[0]
                break
        else:  # last slide only
            next_slide = presentation.slides[0]

        next_slide_button = this_slide.shapes[-1]
        next_slide_button.click_action.target_slide = next_slide

        previous_slide_button = this_slide.shapes[-2]
        previous_slide_button.click_action.target_slide = previous_slide

        # add functionality for page number buttons

        button_number = 3
        slide_number = 0

        while button_number <= (total_number_of_slides + 2):
            page_button = this_slide.shapes[button_number]
            page = presentation.slides[slide_number]
            page_button.click_action.target_slide = page

            button_number = button_number + 1
            slide_number = slide_number + 1

        page_number = page_number + 1

    # Save the PowerPoint presentation
    presentation.save(file_path)
