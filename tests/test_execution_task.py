from centaurus.executor.execution.execution_task import ExecutionTask


def test_execution_task_creation():
    """
    ExecutionTask can be created.
    """

    task = ExecutionTask(plugin_id="whois")

    assert task is not None


def test_execution_task_stores_plugin_id():
    """
    ExecutionTask stores the plugin identifier.
    """

    task = ExecutionTask(plugin_id="whois")

    assert task.plugin_id == "whois"


def test_execution_task_stores_parameters():
    """
    ExecutionTask stores execution parameters.
    """

    params = {"domain": "openai.com"}

    task = ExecutionTask(
        plugin_id="whois",
        parameters=params,
    )

    assert task.parameters == params


def test_execution_task_default_parameters_is_empty_dict():
    """
    ExecutionTask uses an empty parameter dictionary by default.
    """

    task = ExecutionTask(plugin_id="whois")

    assert task.parameters == {}