======================
Generating Exam Sheets
======================

What is an exam sheet?
-----------------------

An exam sheet is a sheet of paper that contains the login information for a student to take an exam. 
The sheet contains the student's name, student ID, and a unique exam ID. The student uses this information to log in to the exam system and take the exam.
There is space for the student to write the hashcode of the exam, which is used to verify the integrity of the exam.

This package generates exam sheets in HTML and PDF format. It consist of an overview page that lists all students, and individual pages for each student.

How to generate exam sheets?
-----------------------------

1. Create the student information.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

First, you need to create a list of dictionaries, where each dictionary contains the information of a student.
The dictionary should contain the following entries:

* first_name: The student's first name
* last_name: The student's last name
* room: The room where the student will take the exam
* seat: The seat number of the student
* username: The student's username
* password: The student's password

Optionally you can add the following entries:

* is_backup: If True, the student is a backup student. These will not be included in the overview page.


Here is an example of a student list:

.. code-block:: python

    students = [
        dict(
            first_name='John',
            last_name='Doe',
            room='A101',
            seat=1,
            username='johndoe',
            password='password',
            is_backup=False # Optional
        ),
        dict(
            first_name='Jane',
            last_name='Doe',
            room='A101',
            seat=2,
            username='janedoe',
            password='password',
            is_backup=False # Optional
        ),
        dict(
            first_name="Backup",
            last_name="Student",
            room="A101",
            seat=3,
            username="backupstudent",
            password="password",
            is_backup=True # Optional
        )
    ]


2. Generate the exam sheets.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To generate the exam sheets, you can use the class :class:`ExamSheetGenerator`.

First you need to create an instance of the class:

.. code-block:: python

    from e2x_exam_sheets import ExamSheetGenerator

    generator = ExamSheetGenerator(        
        university_name='University of Example', # The name of the university
        department_name='Department of Example', # The name of the department
        degree_program='Bachelor of Example', # The name of the degree program
        exam_name='Example Exam', # The name of the exam
        examiners=['Prof. Dr. John Doe', 'Prof. Dr. Jane Doe'], # The examiners of the exam
        date='01.01.2024', # The date of the exam
        semester='Winter Semester 2023/2024', # The semester of the exam
        language='en', # The language of the exam sheet. Can be 'en' or 'de'. Default is 'en'
        hashcode_num_blocks=3, # Optional. The number of blocks in the hashcode
        hashcode_block_size=4, # Optional. The number of characters in each block of the hashcode        
    )

Then you can generate the exam sheets by calling the method :meth:`ExamSheetGenerator.generate_html` or :meth:`ExamSheetGenerator.generate_pdf`:

.. code-block:: python

    generator.generate_html(students, output_file='exam_sheets.html')
    generator.generate_pdf(students, output_file='exam_sheets.pdf')

Here is the output in `PDF Format <../_static/example_sheet.pdf>`_ or `HTML Format <../_static/example_sheet.html>`_.


.. note::

    The overview page will be sorted by last_name. The student sheets will be sorted by seat number.
    The generator will generate an overview page for each room.

