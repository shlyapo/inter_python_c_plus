#include <iostream>

using namespace std;

void insertSort(int a[], int size) {
	int x;
    int j=0;
	for(int i=0; i<size; i++)
	{
		x=a[i];

		for (j=i-1; j>=0 && a[j]>x; j--)
		{

				a[j+1]=a[j];
		}
		a[j+1] = x;
	}
}

int main()
{
    int X[] = { 1, 2, 4, 2 };
    int Y[] = { 4, 55, 6 };
    X[0]=X[0]-5;
    X[2]=X[2] -111;

    int m = 4;
    int n = 3;

    int arr[7];
    for (int i = 0; i < m + n; i++)
    {
        if (i < m) {
            arr[i] = X[i];
        }
        else {
            arr[i] = Y[i - m];
        }
    }

    int size = 7;
    for (int m = 0; m < size-1; m++) { //
            if (arr[m] == arr[m+1]){
                arr[m+1]=0;
                }
    }

    insertSort(arr, 7);

    for (int i = 0; i < size; i++) {
        if (arr[i] != 0)
        {
        cout << arr[i];
        }
    }

}
return 0;}