#include <iostream>
#include "Timer.h"

namespace timer {

void Timer::start() { std::cout << "Start\n"; };
void Timer::stop() { std::cout << "Stop\n"; };
double Timer::elapsed() { return 0; };

} // namespace timer