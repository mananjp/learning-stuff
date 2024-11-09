#include <stdio.h>
#include <stdlib.h>  // For malloc and free functions

// Function to swap the values of two integers
void swap(int* x, int* y) {
    int temp = *x;
    *x = *y;
    *y = temp;
}

// Function to calculate points based on position and kills
int calculate_points(int position, int kills) {
    int total_points = 0;
    int kill_bonus = 2 * kills;  // Each kill gives 2 extra points

    // Award points based on position
    switch (position) {
        case 1: total_points = kill_bonus + 5; break;
        case 2: total_points = kill_bonus + 4; break;
        case 3: total_points = kill_bonus + 3; break;
        case 4: total_points = kill_bonus + 2; break;
        case 5: total_points = kill_bonus + 1; break;
        default: total_points = 0;  // Invalid position, should not happen if input is valid
    }

    return total_points;
}

int main() {
    int number_of_teams;

    // Ask the user for the number of teams
    printf("Welcome to the Team Ranking System!\n");
    printf("How many teams do you want to rank?: ");
    scanf("%d", &number_of_teams);

    // Dynamically allocate memory for the teams' position, kills, and points
    int (*team_data)[2] = malloc(number_of_teams * sizeof(int[2]));  // Stores position and kills for each team
    int *team_points = malloc(number_of_teams * sizeof(int));  // Stores points for each team
    int *team_numbers = malloc(number_of_teams * sizeof(int));  // Stores team numbers (1, 2, 3, etc.)

    // Array to track taken positions, initialized to 0 (not taken)
    // The positions are between 1 and `number_of_teams`
    int *position_taken = calloc(number_of_teams + 1, sizeof(int));  // +1 to use positions 1 to number_of_teams

    // Collect input from the user for each team's position and kills
    for (int team_index = 0; team_index < number_of_teams; team_index++) {
        int team_number = team_index + 1;

        // Store the team number for later reference
        team_numbers[team_index] = team_number;

        // Ask for team position and kills, with input validation
        while (1) {
            printf("\nEnter the position and kills for Team %d : ", team_number, number_of_teams);
            scanf("%d %d", &team_data[team_index][0], &team_data[team_index][1]);

            // Validate the position (must be between 1 and number_of_teams)
            if (team_data[team_index][0] < 1 || team_data[team_index][0] > number_of_teams) {
                printf("Invalid position! Please choose a position between 1 and %d.\n", number_of_teams);
            }
            // Check if the position is already taken
            else if (position_taken[team_data[team_index][0]] == 1) {
                printf("Position %d is already taken! Please choose another position.\n", team_data[team_index][0]);
            }
            // If position is valid and not taken, break the loop
            else {
                position_taken[team_data[team_index][0]] = 1;
                break;
            }
        }
    }

    // Calculate points for each team based on their position and kills
    for (int i = 0; i < number_of_teams; i++) {
        team_points[i] = calculate_points(team_data[i][0], team_data[i][1]);
    }

    // Sorting teams based on points in descending order using bubble sort
    for (int i = 0; i < number_of_teams - 1; i++) {
        for (int j = 0; j < number_of_teams - i - 1; j++) {
            if (team_points[j] < team_points[j + 1]) {
                // Swap the points if the next team has more points
                swap(&team_points[j], &team_points[j + 1]);
                // Swap position and kills for the corresponding teams
                swap(&team_data[j][0], &team_data[j + 1][0]);
                swap(&team_data[j][1], &team_data[j + 1][1]);
                // Swap the team numbers to maintain correct association
                swap(&team_numbers[j], &team_numbers[j + 1]);
            }
        }
    }

    // Output the sorted results (highest points first)
    printf("\n\n---- Final Rankings ----\n");
    printf("Teams sorted by points (highest to lowest):\n");

    for (int i = 0; i < number_of_teams; i++) {
        // Print team number, position, kills, and points in a readable format
        printf("Team %d  - Points: %d\n",
               team_numbers[i], team_points[i]);
    }

    // Free dynamically allocated memory to prevent memory leaks
    free(team_data);
    free(team_points);
    free(team_numbers);
    free(position_taken);

    return 0;
}
