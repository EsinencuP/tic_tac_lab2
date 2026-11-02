"""Консольные крестики-нолики: человек против полного Minimax."""

from dataclasses import dataclass
from typing import Optional, Tuple

EMPTY = " "
DRAW = "draw"
WIN_LINES = (
    (0, 1, 2), (3, 4, 5), (6, 7, 8),
    (0, 3, 6), (1, 4, 7), (2, 5, 8),
    (0, 4, 8), (2, 4, 6),
)


@dataclass(frozen=True)
class GameState:
    board: Tuple[str, ...] = (EMPTY,) * 9
    current_player: str = "X"
    ai: str = "O"


def terminal_result(state: GameState) -> Optional[str]:
    """X/O — победитель, draw — ничья, None — игра продолжается."""
    for a, b, c in WIN_LINES:
        if state.board[a] != EMPTY and state.board[a] == state.board[b] == state.board[c]:
            return state.board[a]
    if EMPTY not in state.board:
        return DRAW
    return None


def get_legal_moves(state: GameState):
    """Индексы свободных клеток; после конца игры ходов нет."""
    if terminal_result(state) is not None:
        return []
    return [i for i, cell in enumerate(state.board) if cell == EMPTY]


def apply_move(state: GameState, move: int) -> GameState:
    """Создаёт новое состояние, не изменяя исходное."""
    if move not in get_legal_moves(state):
        raise ValueError("Недопустимый ход")
    board = list(state.board)
    board[move] = state.current_player
    next_player = "O" if state.current_player == "X" else "X"
    return GameState(tuple(board), next_player, state.ai)


def evaluate(state: GameState) -> int:
    result = terminal_result(state)
    if result == state.ai:
        return 10
    if result in ("X", "O"):
        return -10
    return 0


def minimax(state: GameState, depth: int, is_maximizing: bool) -> int:
    """Полный обход дерева: ИИ максимизирует, человек минимизирует."""
    if terminal_result(state) is not None:
        return evaluate(state)

    # depth считает глубину, но не ограничивает поиск: идём до конца партии.
    scores = []
    for move in get_legal_moves(state):
        child = apply_move(state, move)
        scores.append(minimax(child, depth + 1, not is_maximizing))
    return max(scores) if is_maximizing else min(scores)


def choose_best_move(state: GameState) -> int:
    if state.current_player != state.ai:
        raise ValueError("Сейчас очередь человека")
    moves = get_legal_moves(state)
    if not moves:
        raise ValueError("Игра уже завершена")

    best_move = moves[0]
    best_score = -float("inf")
    for move in moves:
        child = apply_move(state, move)
        score = minimax(child, 1, False)
        if score > best_score:
            best_score = score
            best_move = move
    return best_move


def print_board(state: GameState):
    cells = [cell if cell != EMPTY else str(i + 1)
             for i, cell in enumerate(state.board)]
    print()
    for row in range(3):
        print(" " + " | ".join(cells[row * 3:row * 3 + 3]))
        if row < 2:
            print("---+---+---")
    print()


def read_human_move(state: GameState) -> int:
    while True:
        text = input("Ваш ход (1–9, q — выход): ").strip().lower()
        if text in ("q", "й", "exit"):
            raise EOFError
        try:
            move = int(text) - 1
        except ValueError:
            print("Введите целое число от 1 до 9.")
            continue
        if move in get_legal_moves(state):
            return move
        print("Эта клетка занята или номер вне диапазона 1–9.")


def play():
    print("Крестики-нолики 3×3. X ходит первым. Для выхода введите q.")
    while True:
        human = input("Выберите X или O: ").strip().upper()
        if human == "Q":
            return
        if human in ("X", "O"):
            break
        print("Введите X или O латинскими буквами.")

    state = GameState(ai="O" if human == "X" else "X")
    print_board(state)
    while terminal_result(state) is None:
        if state.current_player == state.ai:
            print("ИИ просчитывает ходы...")
            move = choose_best_move(state)
            print(f"ИИ выбирает клетку {move + 1}.")
        else:
            move = read_human_move(state)
        state = apply_move(state, move)
        print_board(state)

    result = terminal_result(state)
    if result == DRAW:
        print("Ничья!")
    elif result == state.ai:
        print("Победил ИИ!")
    else:
        print("Вы победили!")


if __name__ == "__main__":
    try:
        play()
    except (EOFError, KeyboardInterrupt):
        print("\nИгра завершена.")
