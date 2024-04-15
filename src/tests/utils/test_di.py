import abc

from utils.di import DIContainer


class AbstractRepositoryClass(abc.ABC):
    pass


class RepositoryClass(AbstractRepositoryClass):
    pass


class AbstractServiceClass(abc.ABC):
    pass


class ServiceClass(AbstractServiceClass):
    def __init__(self, repo: AbstractRepositoryClass):
        self.repo = repo


class DocumentContainer(DIContainer):
    repo: AbstractRepositoryClass
    service: ServiceClass

    def _get_repo(self) -> AbstractRepositoryClass:
        return RepositoryClass()

    _get_repo.__dict__['singleton'] = True

    def _get_service(self) -> ServiceClass:
        return ServiceClass(self.repo)


def test_singleton() -> None:
    c = DocumentContainer()

    assert c.repo == c.repo


def test_no_singleton() -> None:
    c = DocumentContainer()

    assert c.service != c.service
