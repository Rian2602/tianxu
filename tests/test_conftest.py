def test_dummy_session_fixture(dummy_session):
    assert dummy_session is not None
    assert dummy_session.state is not None
    assert dummy_session.state.player.name == "Chen Xu"
    assert dummy_session.state.location == "loc_gerbang_akademi"


def test_mock_god_mode_fixture(mock_god_mode):
    import src.engine.battle as battle
    assert mock_god_mode is True
    assert battle.random.uniform(0.8, 1.2) == 1.0
    assert battle.random.random() == 1.0
