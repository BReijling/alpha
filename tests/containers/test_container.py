from dependency_injector.containers import DynamicContainer


def test_container_initialization(container):

    assert isinstance(container, DynamicContainer)
    assert hasattr(container, 'api_gen_command')
    assert hasattr(container, 'api_run_command')
    assert hasattr(container, 'api_section')
    assert hasattr(container, 'sections')
