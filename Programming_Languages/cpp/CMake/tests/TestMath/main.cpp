#include <iostream>

#ifdef USE_MATHLIB
    #include <MathLib.h>
    using namespace MathLib;
#endif

using namespace std;

int main(int argc, char *argv[]) {
	int result;

    #ifdef USE_MATHLIB
        printf("Using MathLib\n");
        result = add(1, 2);
    #else
        result = 1 + 2;
    #endif

	printf("a + b = %d\n", result);

	return 0;
}

