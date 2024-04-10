from dataclasses import dataclass
from typing import List

import pytest

from tecton.cli.environment import DEFAULT_UPLOAD_PART_SIZE_MB
from tecton.cli.environment import UploadPart
from tecton.cli.environment import get_upload_parts
from tecton.cli.environment_utils import is_requirement_present
from tecton.cli.environment_utils import is_valid_environment_name


@dataclass
class FileSplit__TestCase:
    name: str
    file_size: int
    expected_parts: List[UploadPart]


FILE_SPLIT_TEST_CASES = [
    FileSplit__TestCase(
        name="single_file",
        file_size=DEFAULT_UPLOAD_PART_SIZE_MB * 1024 * 1024 - 1,
        expected_parts=[UploadPart(part_number=1, offset=0, part_size=DEFAULT_UPLOAD_PART_SIZE_MB * 1024 * 1024 - 1)],
    ),
    FileSplit__TestCase(
        name="exact_multiple_parts",
        file_size=DEFAULT_UPLOAD_PART_SIZE_MB * 1024 * 1024 * 5,
        expected_parts=[
            UploadPart(
                part_number=i,
                offset=(i - 1) * DEFAULT_UPLOAD_PART_SIZE_MB * 1024 * 1024,
                part_size=DEFAULT_UPLOAD_PART_SIZE_MB * 1024 * 1024,
            )
            for i in range(1, 6)
        ],
    ),
    FileSplit__TestCase(
        name="multiple_parts_with_last_part_smaller",
        file_size=(DEFAULT_UPLOAD_PART_SIZE_MB * 1024 * 1024 * 2) + (DEFAULT_UPLOAD_PART_SIZE_MB * 1024 * 1024 // 2),
        expected_parts=[
            UploadPart(part_number=1, offset=0, part_size=DEFAULT_UPLOAD_PART_SIZE_MB * 1024 * 1024),
            UploadPart(
                part_number=2,
                offset=DEFAULT_UPLOAD_PART_SIZE_MB * 1024 * 1024,
                part_size=DEFAULT_UPLOAD_PART_SIZE_MB * 1024 * 1024,
            ),
            UploadPart(
                part_number=3,
                offset=2 * DEFAULT_UPLOAD_PART_SIZE_MB * 1024 * 1024,
                part_size=DEFAULT_UPLOAD_PART_SIZE_MB * 1024 * 1024 // 2,
            ),
        ],
    ),
    FileSplit__TestCase(
        name="zero_size_file",
        file_size=0,
        expected_parts=[],
    ),
]


@pytest.fixture
def temporary_requirements_file(tmp_path):
    requirements_text = "package1\n# package2\npackage3\n"
    requirements_path = tmp_path / "requirements.txt"
    requirements_path.write_text(requirements_text)
    return requirements_path


@pytest.mark.parametrize(
    "package_name, expected_result",
    [
        ("package2", False),  # package2 is commented
        ("non_existent_package", False),
        ("package1", True),
    ],
)
def test_is_requirement_present(temporary_requirements_file, package_name, expected_result):
    requirements_path = temporary_requirements_file
    assert is_requirement_present(requirements_path, package_name) == expected_result


@pytest.mark.parametrize("test_case", FILE_SPLIT_TEST_CASES, ids=[tc.name for tc in FILE_SPLIT_TEST_CASES])
def test_get_upload_parts(test_case):
    parts = get_upload_parts(test_case.file_size)
    assert len(parts) == len(test_case.expected_parts)
    for part, expected_part in zip(parts, test_case.expected_parts):
        assert part.part_size == expected_part.part_size
        assert part.part_number == expected_part.part_number
        assert part.offset == expected_part.offset


@pytest.mark.parametrize(
    "name, expected",
    [
        ("env123", True),
        ("env_123", True),
        ("ENV-123", True),
        ("env*123", False),
        ("env?123", False),
        ("env!123", False),
        ("", False),
        ("env 123", False),
    ],
)
def test_environments(name, expected):
    assert is_valid_environment_name(name) == expected
