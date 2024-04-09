from convictquandary import Tournament
from convictquandary.strategy_filter import strategy_filter


def test_tournament_player_rounds():
    players = strategy_filter(filters={"strategy_set": "axelrod1984"})
    tournament = Tournament(players, 200)
    tournament.play_tournament()
    assert all([len(i.player1.actions) == 200 for i in tournament.matches.values()])
