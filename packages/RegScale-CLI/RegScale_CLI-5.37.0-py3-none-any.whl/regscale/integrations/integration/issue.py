from abc import ABC, abstractmethod
from regscale.models import Issue


class IntegrationIssue(ABC):
    def __init__(
        self,
        **kwargs,
    ):
        for key, value in kwargs.items():
            setattr(self, key, value)

    @abstractmethod
    def pull(self):
        """
        Pull inventory from an Integration platform into RegScale
        """
        pass

    def create_issues(
        self,
        issues: list[Issue],
    ):
        """
        Create issues in RegScale
        """
        Issue.batch_create(items=issues)
