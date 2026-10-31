//202610125119
//周丽淇
#include <stdio.h>
int main(void)
{
    float a,b;
    char op;
    printf("请输入两个数字和运算符\n");
    scanf("%f %c %f",&a,&op,&b);
    if (op=='+')
    {
        printf("%.2f",a+b);
    }
    else if (op=='-')
    {
        printf("%.2f",a-b);
    }
    else if(op=='*')
    {
        printf("%.2f",a*b);
    }
    else if(op=='/')
    {
        if(b==0)
        {
            printf("错误，除数不能为零");
        }
        else
        {
            printf("%.2f",a/b);
        }
    }
    return 0;
}