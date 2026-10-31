//202610125119
//周丽淇
#include <stdio.h>
int main(void)
{
    float score;
    printf("请输入一个实数作为成绩\n");
    scanf("%f",&score);
    if (score<0||score>100)
    {
    printf("输入无效\n");
    }
    else if (score>=90)
    {
        printf("等级为A\n");
    }
    else if(score>=80)
{
    printf("等级为B\n");
}
else if(score>=70)
{
    printf("等级为C\n");
}
else if(score>=60)
{
    printf("等级为D\n");
}
else
{
    printf("等级为E\n");
}
return 0;
}