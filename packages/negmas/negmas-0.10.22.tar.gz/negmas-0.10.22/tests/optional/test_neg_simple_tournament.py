from __future__ import annotations
from time import sleep
from negmas.gb.common import ResponseType
from negmas.inout import Scenario
from negmas.outcomes import make_issue
from negmas.outcomes.outcome_space import make_os
from negmas.preferences import LinearAdditiveUtilityFunction as U
from negmas.sao import AspirationNegotiator, RandomNegotiator
from negmas.sao.common import SAOResponse
from negmas.sao.mechanism import SAOMechanism
from negmas.sao.negotiators.base import SAONegotiator
from negmas.tournaments.neg import cartesian_tournament
import pytest


class TimeWaster(SAONegotiator):
    def __call__(self, state) -> SAOResponse:
        sleep(10000 * 60 * 60)
        return SAOResponse(ResponseType.REJECT_OFFER, self.nmi.random_outcome())


@pytest.mark.skip(
    "Can be used in the future to test breaking negotiations with infinite loops. Currently it will hang at the end"
)
def test_can_run_cartesian_simple_tournament_with_no_infinities():
    n = 1
    rotate_ufuns = True
    n_repetitions = 1
    issues = (
        make_issue([f"q{i}" for i in range(10)], "quantity"),
        make_issue([f"p{i}" for i in range(5)], "price"),
    )
    ufuns = [
        (
            U.random(issues=issues, reserved_value=(0.0, 0.2), normalized=False),
            U.random(issues=issues, reserved_value=(0.0, 0.2), normalized=False),
        )
        for _ in range(n)
    ]
    scenarios = [
        Scenario(
            outcome_space=make_os(issues, name=f"S{i}"),
            ufuns=u,
            mechanism_type=SAOMechanism,  # type: ignore
            mechanism_params=dict(),
        )
        for i, u in enumerate(ufuns)
    ]
    competitors = [RandomNegotiator, TimeWaster]
    results = cartesian_tournament(
        competitors=competitors,
        scenarios=scenarios,
        mechanism_params=dict(n_steps=10000000, hidden_time_limit=3),
        n_repetitions=n_repetitions,
        verbosity=4,
        rotate_ufuns=rotate_ufuns,
        # plot_fraction=0.5,
        path=None,
    )
    scores = results.scores
    assert (
        len(scores)
        == len(scenarios)
        * (int(rotate_ufuns) + 1)  # two variations if rotate_ufuns else one
        * len(competitors)
        * len(competitors)
        * n_repetitions
        * 2  # two scores per run
    )

    assert (
        len(results.details)
        == len(scenarios)
        * (int(rotate_ufuns) + 1)  # two variations if rotate_ufuns else one
        * len(competitors)
        * len(competitors)
        * n_repetitions
    )
    assert len(results.final_scores) == len(competitors)


def test_can_run_cartesian_simple_tournament_n_reps():
    n = 2
    rotate_ufuns = True
    n_repetitions = 4
    issues = (
        make_issue([f"q{i}" for i in range(10)], "quantity"),
        make_issue([f"p{i}" for i in range(5)], "price"),
    )
    ufuns = [
        (
            U.random(issues=issues, reserved_value=(0.0, 0.2), normalized=False),
            U.random(issues=issues, reserved_value=(0.0, 0.2), normalized=False),
        )
        for _ in range(n)
    ]
    scenarios = [
        Scenario(
            outcome_space=make_os(issues, name=f"S{i}"),
            ufuns=u,
            mechanism_type=SAOMechanism,  # type: ignore
            mechanism_params=dict(),
        )
        for i, u in enumerate(ufuns)
    ]
    competitors = [RandomNegotiator, AspirationNegotiator]
    results = cartesian_tournament(
        competitors=competitors,
        scenarios=scenarios,
        mechanism_params=dict(n_steps=10),
        n_repetitions=n_repetitions,
        verbosity=0,
        rotate_ufuns=rotate_ufuns,
        # plot_fraction=0.5,
        path=None,
    )
    scores = results.scores
    assert (
        len(scores)
        == len(scenarios)
        * (int(rotate_ufuns) + 1)  # two variations if rotate_ufuns else one
        * len(competitors)
        * len(competitors)
        * n_repetitions
        * 2  # two scores per run
    )

    assert (
        len(results.details)
        == len(scenarios)
        * (int(rotate_ufuns) + 1)  # two variations if rotate_ufuns else one
        * len(competitors)
        * len(competitors)
        * n_repetitions
    )
    assert len(results.final_scores) == len(competitors)
