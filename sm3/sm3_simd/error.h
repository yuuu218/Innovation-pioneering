#pragma once
#include <stdio.h>
#include <stdarg.h>
#include <string.h>
#include <stdint.h>
#define GMSSL_FMT_BIN 1
#define GMSSL_FMT_HEX 2
#define GMSSL_FMT_DER 4
#define GMSSL_FMT_PEM 8
#define DEBUG 1
#define error_print()                                                       \
    do                                                                      \
    {                                                                       \
        if (DEBUG)                                                          \
            fprintf(stderr, "%s:%d:%s():\n", __FILE__, __LINE__, __func__); \
    } while (0)

#define error_print_msg(fmt, ...)                                                           \
    do                                                                                      \
    {                                                                                       \
        if (DEBUG)                                                                          \
            fprintf(stderr, "%s:%d:%s(): " fmt, __FILE__, __LINE__, __func__, __VA_ARGS__); \
    } while (0)

#define error_puts(str)                                                           \
    do                                                                            \
    {                                                                             \
        if (DEBUG)                                                                \
            fprintf(stderr, "%s: %d: %s: %s", __FILE__, __LINE__, __func__, str); \
    } while (0)

