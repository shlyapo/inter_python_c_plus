#include <iostream>

using namespace std;

int test (int a)
{
    cout << a;
    return a;
}
int testt (int a)
{
    cout << a;
    return a;
}
void testtt (int b)
{
    cout << b;
}

int main ()
{
    int bb = 5443;
    testt (55);
    testtt (bb);
    return 0;
}