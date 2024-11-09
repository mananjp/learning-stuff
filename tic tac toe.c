#include <stdio.h>

void printBoard(char arr[3][3]) {
    for(int i = 0; i < 3; i++) {
        for(int j = 0; j < 3; j++) {
            printf("%c ", arr[i][j]);
        }
        printf("\n");
    }
}

void initializeBoard(char arr[3][3]) {
    for(int i = 0; i < 3; i++) {
        for(int j = 0; j < 3; j++) {
            arr[i][j] = '_';
        }
    }
}

int checkWin(char arr[3][3], char player) {
    for(int i = 0; i < 3; i++) {
        if((arr[i][0] == player && arr[i][1] == player && arr[i][2] == player) ||
           (arr[0][i] == player && arr[1][i] == player && arr[2][i] == player)) {
            return 1;
        }
    }

    if((arr[0][0] == player && arr[1][1] == player && arr[2][2] == player) ||
       (arr[0][2] == player && arr[1][1] == player && arr[2][0] == player)) {
        return 1;
    }

    return 0;
}

int isBoardFull(char arr[3][3]) {
    for(int i = 0; i < 3; i++) {
        for(int j = 0; j < 3; j++) {
            if(arr[i][j] == '_') {
                return 0;
            }
        }
    }
    return 1;
}

int main() {
    int x, y;
    char arr[3][3];
    int turn = 0;
    char players[2] = {'O', 'X'};

    initializeBoard(arr);

    while(1) {
        printBoard(arr);
        printf("Player %d (%c's turn). Enter row and column (0, 1, or 2): ", turn + 1, players[turn]);
        if (scanf("%d %d", &x, &y) != 2) {
            printf("Invalid input. Please enter two integers.\n");
            while(getchar() != '\n'); // Clear invalid input
            continue;
        }

        if(x < 0 || x >= 3 || y < 0 || y >= 3 || arr[x][y] != '_') {
            printf("Invalid move. Try again.\n");
            continue;
        }

        arr[x][y] = players[turn];

        if(checkWin(arr, players[turn])) {
            printBoard(arr);
            printf("Player %d wins!\n", turn + 1);
            break;
        }

        if(isBoardFull(arr)) {
            printBoard(arr);
            printf("It's a draw!\n");
            break;
        }

        turn = 1 - turn;
    }

    return 0;
}
