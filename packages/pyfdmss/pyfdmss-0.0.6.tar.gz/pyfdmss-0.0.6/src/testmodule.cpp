#include "testmodule.h"

int mrun(int count, int arg)
{
    int result{0};
    for(int i = 0; i < count; ++i, ++arg){
        result += arg;
    }
    return result;
}
