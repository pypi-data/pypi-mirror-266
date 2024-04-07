from typing import List, Union

import yaml
from pydantic import BaseModel


class Case(BaseModel):
    test_name: str
    steps: List[dict]
    mark: List[Union[str, dict]] = []

    @classmethod
    def from_case_dict(cls, case_dict: dict):
        """

        :param case_dict: {'test_name': 'test a add b',
                            'steps': [
                                        {'a': 1, 'b': 2, 'assert': 3},
                                        {'a': 2, 'b': 3, 'assert': 4}
                                    ]
                            }

        :return:
        """
        # print(case_dict)

        return cls(**case_dict)

    def to_yaml(self):
        return yaml.dump(self.model_dump(), allow_unicode=True, sort_keys=False)

    @classmethod
    def from_yaml(cls, yaml_str):
        data = yaml.safe_load(yaml_str)
        return cls(**data)
