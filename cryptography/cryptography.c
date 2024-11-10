#include <stdio.h>
#include <string.h>
#include <stdlib.h>

void encrypt_string(char *str, int length) {
    for (int i = 0; i < length; i++) {
        if (str[i] >= 'a' && str[i] <= 'z') {
            str[i] = 'a' + (str[i] - 'a' + i) % 26; // Encrypt lowercase letters
        }
        else if (str[i] >= 'A' && str[i] <= 'Z') {
            str[i] = 'A' + (str[i] - 'A' + i) % 26; // Encrypt uppercase letters
        }
        else if (str[i] >= '0' && str[i] <= '9') {
            str[i] = '0' + (str[i] - '0' + i) % 10; // Encrypt digits
        }
    }
    printf("Encrypted string: %s\n", str);
}

void decrypt_string(char *str, int length) {
    for (int i = 0; i < length; i++) {
        if (str[i] >= 'a' && str[i] <= 'z') {
            str[i] = 'a' + (str[i] - 'a' - i + 26) % 26; // Decrypt lowercase letters
        }
        else if (str[i] >= 'A' && str[i] <= 'Z') {
            str[i] = 'A' + (str[i] - 'A' - i + 26) % 26; // Decrypt uppercase letters
        }
        else if (str[i] >= '0' && str[i] <= '9') {
            str[i] = '0' + (str[i] - '0' - i + 10) % 10; // Decrypt digits
        }
    }
    printf("Decrypted string: %s\n", str);
}

int main() {
    char *input_string = (char*)malloc(50 * sizeof(char));

    if (input_string == NULL) {
        printf("Memory allocation failed.\n");
        return 1;
    }

    printf("Enter a string: ");
    if (fgets(input_string, 50, stdin) == NULL) {
        printf("Error reading input.\n");
        free(input_string);
        return 1;
    }

    size_t input_length = strlen(input_string);

    // Remove the newline character if present
    if (input_length > 0 && input_string[input_length - 1] == '\n') {
        input_string[input_length - 1] = '\0';
        input_length--;
    }

    printf("Original string: %s\n", input_string);

    encrypt_string(input_string, input_length);
    decrypt_string(input_string, input_length);

    free(input_string);

    return 0;
}
