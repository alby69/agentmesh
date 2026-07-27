from econnet.agents.producer import DemandForecaster, HAS_TORCH
from econnet.agents.consumer import QLearner


def test_demand_forecaster():
    forecaster = DemandForecaster()
    if HAS_TORCH:
        pred = forecaster.predict_demand_torch(10.0, 5.0, 0.5)
        assert isinstance(pred, float)
        assert pred >= 0.0

        loss = forecaster.update_torch(10.0, 5.0, 0.5, 6.0)
        assert isinstance(loss, float)
    else:
        pred = forecaster.predict_demand_torch(10.0, 5.0, 0.5)
        assert pred == 0.0


def test_q_learner():
    learner = QLearner(lr=0.1, discount=0.9, epsilon=0.0)

    state1 = [10.0, 100.0, 0.5, 0.2]
    actions = [0, 1, 2]

    action = learner.choose_action(state1, actions)
    assert action in actions

    learner.update(state1, 1, 1.0, [11.0, 90.0, 0.6, 0.1], actions)

    best_action = learner.choose_action(state1, actions)
    assert best_action == 1
