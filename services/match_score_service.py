from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from models.match import Match
    from models.player import Player


from exceptions.validation_exceptions import PlayerNotInMatchError


class MatchScoreService:
    """Сервис начисления очка игроку согласно правилам тенниса."""

    def play_match(self, match: Match, player: Player) -> Player | None:
        """Начисляет очко выбранному игроку и возвращает победителя, если матч завершён."""

        winner = self.check_match_winner(match)
        if winner is not None:
            return winner
        self.award_point(match, player)
        if self.is_tie_break(match):
            tie_break_winner = self.check_tie_break_winner(match)
            if tie_break_winner:
                self.award_game(match, tie_break_winner)
                set_winner = self.check_set_winner(match)
                if set_winner:
                    self.award_set(match, winner_player=set_winner)
                    self.reset_points(match)
                    self.reset_games(match)
                    return self.check_match_winner(match)
        else:
            game_winner = self.check_game_winner(match)
            if game_winner:
                self.award_game(match, winner_player=game_winner)
                self.reset_points(match)
                set_winner = self.check_set_winner(match)
                if set_winner:
                    self.award_set(match, winner_player=set_winner)
                    self.reset_points(match)
                    self.reset_games(match)
        return self.check_match_winner(match)


    def award_point(self, match: Match, player: Player) -> None:
        if player.id == match.player_1.id:
            match.player_1_score.points += 1
        elif player.id == match.player_2.id:
            match.player_2_score.points += 1
        else:
            raise PlayerNotInMatchError("Данный игрок в этом матче не учавствует")


    def check_game_winner(self, match: Match) -> Player | None:
        points_1 = match.player_1_score.points
        points_2 = match.player_2_score.points
        if max(points_1, points_2) >= 4 and abs(points_1 - points_2) >= 2:
            if points_1 > points_2:
                return match.player_1
            else:
                return match.player_2
        return None

    def award_game(self, match: Match, winner_player: Player | None) -> None:
        if winner_player:
            if winner_player.id == match.player_1.id:
                match.player_1_score.games += 1
            else:
                match.player_2_score.games += 1


    def reset_points(self, match: Match) -> None:
        match.player_1_score.points = 0
        match.player_2_score.points = 0


    def is_tie_break(self, match: Match) -> bool:
        if match.player_1_score.games == 6 and match.player_2_score.games == 6:
            return True
        return False

    def check_tie_break_winner(self, match: Match) -> Player | None:
        points_1 = match.player_1_score.points
        points_2 = match.player_2_score.points
        if max(points_1, points_2) >= 7 and abs(points_1 - points_2) >= 2:
            if points_1 > points_2:
                return match.player_1
            else:
                return match.player_2
        return None


    def check_set_winner(self, match: Match) -> Player | None:
        games_1 = match.player_1_score.games
        games_2 = match.player_2_score.games
        if games_1 == 7 and games_2 == 6:
            return match.player_1
        elif games_2 == 7 and games_1 == 6:
            return match.player_2
        elif max(games_1, games_2) >= 6 and abs(games_1 - games_2) >= 2:
            if games_1 > games_2:
                return match.player_1
            else:
                return match.player_2
        return None


    def award_set(self, match: Match, winner_player: Player | None) -> None:
        if winner_player:
            if winner_player.id == match.player_1.id:
                match.player_1_score.sets += 1
            else:
                match.player_2_score.sets += 1


    def reset_games(self, match: Match) -> None:
        match.player_1_score.games = 0
        match.player_2_score.games = 0


    def reset_sets(self, match: Match) -> None:
        match.player_1_score.sets = 0
        match.player_2_score.sets = 0


    def check_match_winner(self, match: Match) -> Player | None:
        points_1 = match.player_1_score.sets
        points_2 = match.player_2_score.sets
        if max(points_1, points_2) >= 2:
            if points_1 > points_2:
                return match.player_1
            else:
                return match.player_2
        return None

































