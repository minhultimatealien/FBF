#include <stdio.h>
#define a {{1,2,3,4,5},{6,7,8,9,10},}

void main()
{
    //int a = {1,2,3,4,5};
    typedef struct
    {
        int m;
        int n;
        int r;
        int s;
        int v;
    }b;
    b c[2] = a ;
    printf("%d",sizeof(c));
    //return 0;
}