//202610125119
//周丽淇
#include <stdio.h>
int main(void)
{
    float a;
    printf("请输入一个实数");
    scanf("%f",&a);
    if (a<0)
    {
    printf("a是负数");
    }
    else if (a>0)
    {
        printf("a是正数");
    }
    else
    {
    printf("a是零");
    }
    return 0;
}