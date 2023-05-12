#include <iostream>

using namespace std;

void insertSort(int a[], int size) {
	int x;
    int j=0;
	for(int i=0; i<size; i++)
	{  // цикл проходов, i - номер прохода
		x=a[i];

		// поиск места элемента в готовой последовательности
		for (j=i-1; j>=0 && a[j]>x; j--)
		{

				a[j+1]=a[j];
		}
		// место найдено, вставить элемент
		a[j+1] = x;
	}
}

int main(){
	int SIZE=10;
	int ar[10] = {7, 8, 9, 5, 3, 9, 2, 0, 11};
	// до сортировки
	for(int i=0;i<SIZE;i++){
		cout<<ar[i];
	}
	insertSort(ar,SIZE);
    cout<<'_';
	// после сортировки
	for(int i=0;i<SIZE;i++){
	    cout<<' ';
		cout<<ar[i];
	}
}