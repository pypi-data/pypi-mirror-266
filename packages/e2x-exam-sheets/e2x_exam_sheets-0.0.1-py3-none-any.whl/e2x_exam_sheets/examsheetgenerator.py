import os
from collections import defaultdict
from tempfile import NamedTemporaryFile
from typing import Dict, List, Union

from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML


class ExamSheetGenerator:
    """
    A class for generating exam sheets.
    """

    def __init__(
        self,
        date: str,
        semester: str,
        exam_name: str,
        examiners: List[str],
        university_name: str,
        department_name: str,
        degree_program: str,
        language="en",
        hashcode_num_blocks: int = 3,
        hashcode_block_size: int = 4,
    ) -> None:
        """
        Initializes an instance of the ExamSheetGenerator class.

        Args:
            date (str): The date of the exam.
            semester (str): The semester in which the exam is being conducted.
            exam_name (str): The name of the exam.
            examiner_1 (str): The name of the first examiner.
            examiner_2 (str): The name of the second examiner.
            university_name (str): The name of the university.
            department_name (str): The name of the department.
            degree_program (str): The degree program.
            language (str, optional): The language of the exam sheet. Defaults to "en".
            hashcode_num_blocks (int, optional): The number of blocks in the hashcode.
                Defaults to 3.
            hashcode_block_size (int, optional): The size of each block in the hashcode.
                Defaults to 4.
        """
        HERE = os.path.dirname(os.path.abspath(__file__))
        self.env = Environment(loader=FileSystemLoader(os.path.join(HERE, "templates")))
        self.template = self.env.get_template("exam_sheet.html")
        self.exam_info = dict(
            date=date,
            semester=semester,
            exam_name=exam_name,
            examiners=examiners,
            degree_program=degree_program,
            university_name=university_name,
            department_name=department_name,
            hashcode_num_blocks=hashcode_num_blocks,
            hashcode_block_size=hashcode_block_size,
        )
        self.language = language

    def generate_html(
        self,
        students: List[Dict[str, str]],
        output_file: str = None,
    ) -> Union[str, None]:
        """
        Generates an HTML exam sheet for the given students.

        Args:
            students (List[Dict[str, str]]): A list of dictionaries containing the
                student information.
            output_file (str, optional): The path to the output file. If not provided,
                the HTML content is returned. Defaults to None.

        Returns:
            Union[str, None]: The HTML content if no output file is provided, otherwise None.
        """
        student_groups = defaultdict(list)
        for student in students:
            student_groups[student["room"]].append(student)
        html = self.template.render(
            exam_info=self.exam_info,
            language=self.language,
            student_groups=student_groups,
        )
        if output_file:
            with open(output_file, "w") as f:
                f.write(html)
        else:
            return html

    def generate_pdf(
        self,
        students: List[Dict[str, str]],
        output_file: str,
    ) -> None:
        """
        Generates a PDF exam sheet for the given students.

        Args:
            students (List[Dict[str, str]]): A list of dictionaries containing the
                student information.
            output_file (str): The path to the output PDF file.

        Returns:
            None
        """
        with NamedTemporaryFile(suffix=".html") as f:
            html_file = f.name
            self.generate_html(students, html_file)
            HTML(html_file).write_pdf(output_file)
