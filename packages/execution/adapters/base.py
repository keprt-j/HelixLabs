from typing import Protocol as TypingProtocol


class ExecutionAdapter(TypingProtocol):
    def validate_task(self, task: object) -> bool:
        ...

    def execute_task(self, task: object) -> object:
        ...

    def get_status(self, execution_id: str) -> str:
        ...

    def recover_from_error(self, task: object, error: Exception) -> object:
        ...

