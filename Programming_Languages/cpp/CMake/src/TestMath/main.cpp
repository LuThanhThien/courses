#include <iostream>
#include <GLFW/glfw3.h>
#include <TestMathConfig.h>

#ifdef USE_MATHLIB
    #include <MathLib.h>
    using namespace MathLib;
#endif

// https://askubuntu.com/questions/306703/compile-opengl-program-missing-gl-gl-h
// https://scicomp.aalto.fi/triton/quickstart/installxonwindows/
// https://www.shogan.co.uk/how-tos/wsl2-gui-x-server-using-vcxsrv/#:~:text=With%20the%20black%20X-server%20%2F%20display%20window%20from,1%20nameserver%20%2Fetc%2Fresolv.conf%20%7C%20awk%20%27%20%7Bprint%20%242%7D%27%29%3A0


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

    cout << "argv[0]:" <<  argv[0] << " VERSION: " << TESTMATH_VERSION_MAJOR << "."  << TESTMATH_VERSION_MINOR << endl;

	GLFWwindow *window;

	if( !glfwInit() )
    {
        fprintf( stderr, "Failed to initialize GLFW\n" );
        exit( EXIT_FAILURE );
    }

	window = glfwCreateWindow( 300, 300, "Gears", NULL, NULL );

	if (!window)
    {
        fprintf( stderr, "Failed to open GLFW window\n" );
        glfwTerminate();
        exit( EXIT_FAILURE );
    }

	// Main loop
    while( !glfwWindowShouldClose(window) )
    {   
        // Swap buffers
        glfwSwapBuffers(window);
        glfwPollEvents();
    }

    // Terminate GLFW
    glfwTerminate();

	return 0;
}

