from pydantic import BaseModel, Field

class getBackupStep(BaseModel):
    steps: int = Field(title="Иногда для прыжка вперёд требуется отступить на два шага назад. — А иногда надо лишь иметь желание прыгнуть.")
