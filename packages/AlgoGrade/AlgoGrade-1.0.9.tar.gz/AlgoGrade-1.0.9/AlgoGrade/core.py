from collections import Counter
from typing import Iterable, Callable, Type, Any
from pydantic import BaseModel
from .adapters import pycga_to_pydantic, pydantic_to_pycga


class Answers(BaseModel):
    @classmethod
    def from_iterable(cls, iterable):
        raise NotImplementedError
    
    def to_pydantic_list(self):
        raise NotImplementedError
    
    def to_pycga_list(self):
        return pydantic_to_pycga(self.to_pydantic_list())


class Mistake:
    def __init__(self, scorings, description=""):
        self.scorings = scorings
        self.description = description
    
    @property
    def is_repeated(self):
        return self.scorings.repeat_fine > 0
    
    def __eq__(self, other):
        return (
            isinstance(other, self.__class__) and
            self.scorings == other.scorings
        )
    
    def __hash__(self):
        return hash((self.__class__, self.scorings))


class Scoring(BaseModel, frozen=True):
    min_grade: float = -1000.0
    max_grade: float = 0.0
    fine: float = 0.0
    repeat_fine: float = 0.0


class Grader:
    @classmethod
    def grade_pycga(cls, answers, correct_answers, scorings):
        """
            Compare answers to correct_answers (both in PyCGA format) an return a tuple
            `(total_grade, answers_grades)`, where answers_grades is a list of tuples--grades for each answer `(answer, grade)` in PyCGA format.
        """
        mistake_lists = [
            grading_method(answer, correct_answer, scorings)
            for grading_method, answer, correct_answer, scorings
            in zip(cls.grade_methods(), answers, correct_answers, scorings)
        ]
        mistake_counters = [Counter(mistakes) for mistakes in mistake_lists]
        mistake_fines_dicts = [
            {
                mistake: mistake.scorings.repeat_fine if mistake.is_repeated and count > 1 else mistake.scorings.fine
                for mistake, count in mistake_counter.items()
            }
            for mistake_counter in mistake_counters
        ]

        answers_grades = [
            (answer, max(scorings.min_grade, scorings.max_grade-sum(mistake_fine_dict.values())))
            for answer, scorings, mistake_fine_dict
            in zip(answers, scorings, mistake_fines_dicts)
        ]
        total_grade = sum(grade for answer, grade in answers_grades)
        
        return total_grade, answers_grades
    
    @classmethod
    def grade_pydantic(cls, answers, correct_answers, scorings):
        """
            Compare answers to correct_answers (both in PydanticAdapter format) an return a tuple
            `(total_grade, answers_grades)`, where answers_grades is a list of tuples--grades for each answer `(answer, grade)` in PydanticAdapter format.
        """
        total_grade, answers_grades = cls.grade_pycga(pydantic_to_pycga(answers), pydantic_to_pycga(correct_answers), scorings)
        return total_grade, [(pycga_to_pydantic(answer), grade) for answer, grade in answers_grades]
    
    @classmethod
    def grade_answers_wrapper(cls, answers: Answers, correct_answers: Answers, scorings):
        """
            Compare answers to correct_answers (both in Answers format) an return a tuple
            `(total_grade, answers_grades)`, where answers_grades is a list of tuples--grades for each answer `(answer, grade)` in PydanticAdapter format.
        """
        return cls.grade_pydantic(answers.to_pydantic_list(), correct_answers.to_pydantic_list(), scorings)
    
    @classmethod
    def grade_default(cls, answer, correct_answer, scorings, item_mistake_text=""):
        return [] if answer == correct_answer else [Mistake(scorings, description=item_mistake_text)]
    
    @classmethod
    def grade_iterable(cls, answer, correct_answer, scorings, grade_item_method=None, item_mistake_text=""):
        if grade_item_method is None:
            grade_item_method = cls.grade_default
        if callable(grade_item_method):
            grade_item_method = [grade_item_method] * len(correct_answer)
        elif not isinstance(grade_item_method, Iterable):
            raise TypeError(f"grade_item_method should be either a grading method, or an iterable of grading methods for each item, or None (defaults to default_grading)")

        len_diff = len(correct_answer) - len(answer)
        if len_diff == 0:
            return flatten([
                g(a, c, scorings, item_mistake_text=item_mistake_text)
                for g, a, c in zip(grade_item_method, answer, correct_answer)
            ])

        return [Mistake(scorings, description=f"Too {'few' if len_diff < 0 else 'many'} items")] * abs(len_diff)

    @classmethod
    def grade_bin_tree(cls, answer, correct_answer, scorings, grade_item_method=None, item_mistake_text=""):
        if grade_item_method is None:
            grade_item_method = cls.grade_default
        
        return cls._find_mistakes_in_bin_tree(answer.root, correct_answer.root, scorings, grade_item_method, item_mistake_text)

    @classmethod
    def _find_mistakes_in_bin_tree(
        cls, node, correct_node, scorings,
        grade_item_method=None, item_mistake_text="", mistakes=None, extra=None, missing=None
    ):
        if mistakes is None:
            mistakes = []
        if extra is None:
            extra = []
        if missing is None:
            missing = []
        
        mistakes.extend(grade_item_method(node, correct_node, scorings))
        
        if node.left and correct_node.left:
            cls._find_mistakes_in_bin_tree(node.left, correct_node.left, scorings, grade_item_method, item_mistake_text, mistakes, extra, missing)
        if node.left and not correct_node.left:
            extra.extend(Mistake(scorings, "Extra item") for _ in node.left.traverse_preorder()[1:])
        if not node.left and correct_node.left:
            missing.extend(Mistake(scorings, "Missing item") for _ in correct_node.left.traverse_preorder()[1:])

        if node.right and correct_node.right:
            cls._find_mistakes_in_bin_tree(node.right, correct_node.right, scorings, grade_item_method, item_mistake_text, mistakes, extra, missing)
        if node.right and not correct_node.right:
            extra.extend(Mistake(scorings, "Extra item") for _ in node.right.traverse_preorder()[1:])
        if not node.right and correct_node.right:
            missing.extend(Mistake(scorings, "Missing item") for _ in correct_node.right.traverse_preorder()[1:])
        
        return mistakes + extra + missing

    @classmethod
    def grade_methods(cls):
        raise NotImplementedError


class GivenJSONParser:
    """Parses a JSON-represented (list) givens as a tuple of arguments to be fed into the respective PyCGA task solving method."""
    @classmethod
    def parse(cls, data) -> list[Any]:
        """Parses a JSON-represented (list) givens as a tuple of arguments to be fed into the respective PyCGA task solving method."""
        raise NotImplementedError


class Task:
    algorithm: Callable = None
    grader_class: Type[Grader] = None
    answers_class: Type[Answers] = None
    given_parser_class: Type[GivenJSONParser] = None
    
    @classmethod
    def solve_as_pycga_list(cls, givens: Iterable):
        """Solves a task with the givens provided in PyCGA format and returns a list of answers in PyCGA format."""
        return list(cls.algorithm(*givens))
    
    @classmethod
    def solve_as_pydantic_list(cls, givens: Iterable):
        """Solves a task with the givens provided in PyCGA format and returns a list of answers in PydanticAdapter format."""
        pycga_answers = list(cls.solve_as_pycga_list(givens))
        return pycga_to_pydantic(pycga_answers)
    
    @classmethod
    def solve_as_answers_wrapper(cls, givens: Iterable):
        """Solves a task with the givens provided in PyCGA format and returns answers in form of the respective Answers wrapper."""
        pydantic_answers = cls.solve_as_pydantic_list(givens)
        return cls.answers_class.from_iterable(pydantic_answers)


def flatten(iterable):
    return list(_flatten(iterable))


def _flatten(iterable):
    for item in iterable:
        if isinstance(item, Iterable) and not isinstance(item, str):
            for inner_item in flatten(item):
                yield inner_item
        else:
            yield item
