#include <stdio.h>
int
foo (int i)
{
  int v = 0;
  for (int j = 0; j < i; j++)
    v++;
  printf ("Bla\n");
  return v;
}

int
main (void)
{
  int i = 1;
  if (i == 0)
    {
      for (int j = 0; j < 10; j++)
        {
          i++;
        }
    }
  else
    {
      i = 0;
      foo (i);
    }
  printf ("hello\n");
}
