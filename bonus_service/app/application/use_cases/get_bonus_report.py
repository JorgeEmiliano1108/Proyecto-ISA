from typing import List

from app.application.ports.input import GetBonusReportInputPort
from app.application.ports.output import BonusRepositoryPort


class GetBonusReportUseCase(GetBonusReportInputPort):
    """Genera el consolidado financiero de bonos para un periodo dado."""

    def __init__(self, bonus_repo: BonusRepositoryPort):
        self._bonus_repo = bonus_repo

    async def execute(self, periodo_id: int) -> List[dict]:
        bonuses = await self._bonus_repo.find_by_periodo(periodo_id)
        return [b.to_dict() for b in bonuses]
