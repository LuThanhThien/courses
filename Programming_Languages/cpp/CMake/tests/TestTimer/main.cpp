#include <iostream>
#include <Timer.h>


int main(int argc, char *argv[]) {
    timer::Timer timer;
	timer.start();
	timer.stop();
	auto time = timer.elapsed();

    std::cout << "Timer: " << time << "\n";

	return 0;
}
