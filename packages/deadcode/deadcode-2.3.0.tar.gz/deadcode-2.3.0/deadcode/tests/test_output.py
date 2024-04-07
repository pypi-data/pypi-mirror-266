from deadcode.cli import main
from deadcode.tests.base import BaseTestCase


class TestCountOptionOutput(BaseTestCase):
    def test_count_several_classes(self):
        # Having
        self.files = {
            "ignore_names_by_pattern.py": """
                class MyModel:
                    pass

                class MyUserModel:
                    pass

                class Unused:
                    pass

                class ThisClassShouldBeIgnored:
                    pass
                """
        }

        # When
        unused_name_count = main(["ignore_names_by_pattern.py", "--no-color", "--count"])

        # Then
        self.assertEqual(unused_name_count, "4")

    def test_count_variables_function_and_class(self):
        # Having
        self.files = {
            "ignore_names_by_pattern.py": """
                first_variable = 0
                def this_is_a_function():
                    pass
                class MyModel:
                    def __init__(self):
                        pass
                """
        }

        # When
        unused_name_count = main(["ignore_names_by_pattern.py", "--no-color", "--count"])

        # Then
        self.assertEqual(unused_name_count, "3")


class TestQuietOptionOutput(BaseTestCase):
    def test_count_several_classes(self):
        # Having
        self.files = {
            "ignore_names_by_pattern.py": """
                class MyModel:
                    pass

                class MyUserModel:
                    pass

                class Unused:
                    pass

                class ThisClassShouldBeIgnored:
                    pass
                """
        }

        # When
        unused_name_count = main(["ignore_names_by_pattern.py", "--no-color", "--quiet"])

        # Then
        self.assertEqual(unused_name_count, "")

    def test_count_variables_function_and_class(self):
        # Having
        self.files = {
            "ignore_names_by_pattern.py": """
                first_variable = 0
                def this_is_a_function():
                    pass
                class MyModel:
                    def __init__(self):
                        pass
                """
        }

        # When
        unused_name_count = main(["ignore_names_by_pattern.py", "--no-color", "--quiet"])

        # Then
        self.assertEqual(unused_name_count, "")


class TestVerboseOutput(BaseTestCase):
    def test_colorful_output(self):
        self.files = {
            "tests/files/variables.py": """
                unused_global_variable = True
                ANOTHER_GLOBAL_VARIABLE = "This variable is unused"
                third_global_varialbe3 = 12 * 25
                THIS_ONE_IS_USED = "World"
                print(THIS_ONE_IS_USED)"""
        }
        unused_names = main(["tests/files/variables.py"])

        self.assertEqual(
            unused_names,
            (
                "tests/files/variables.py:1:0: \x1b[91mDC01\x1b[0m Variable "
                "`\x1b[1munused_global_variable\x1b[0m` is never used\n"
                "tests/files/variables.py:2:0: \x1b[91mDC01\x1b[0m Variable "
                "`\x1b[1mANOTHER_GLOBAL_VARIABLE\x1b[0m` is never used\n"
                "tests/files/variables.py:3:0: \x1b[91mDC01\x1b[0m Variable "
                "`\x1b[1mthird_global_varialbe3\x1b[0m` is never used"
            ),
        )

    def test_no_color_option(self):
        self.files = {
            "tests/files/variables.py": """
                unused_global_variable = True
                ANOTHER_GLOBAL_VARIABLE = "This variable is unused"
                third_global_varialbe3 = 12 * 25
                THIS_ONE_IS_USED = "World"
                print(THIS_ONE_IS_USED)"""
        }
        unused_names = main(["tests/files/variables.py", "--no-color"])

        self.assertEqual(
            unused_names,
            (
                "tests/files/variables.py:1:0: DC01 Variable `unused_global_variable` is never used\n"
                "tests/files/variables.py:2:0: DC01 Variable `ANOTHER_GLOBAL_VARIABLE` is never used\n"
                "tests/files/variables.py:3:0: DC01 Variable `third_global_varialbe3` is never used"
            ),
        )
