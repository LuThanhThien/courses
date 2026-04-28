#pragma once

namespace timer {

class Timer {
public:
    void start();
    void stop();
    double elapsed();
};

} // namespace timer