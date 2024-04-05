#include "Slau.h"

#include <cstdio>

Slau::Slau(EnvCase* cs, int firstOrSecond)
{
	int left, right, center;
	bool leftIncl, rightIncl;
	if (firstOrSecond == 1)
	{
		left = cs->xLeft;
		right = cs->xRight;
		// ������� �������
		p = cs->pX();
		// ������ ����������� ��������, �� ������� ������ ���������� �������
		center = cs->centerX();
		leftIncl = cs->LeftXIncluded();
		rightIncl = cs->RightXIncluded();
	}
	else
	{
		left = cs->yLeft;
		right = cs->yRight;
		// ������� �������
		p = cs->pY();
		// ������ ����������� ��������, �� ������� ������ ���������� �������
		center = cs->centerY();
		leftIncl = cs->LeftYIncluded();
		rightIncl = cs->RightYIncluded();
	}

	// ��������� ������
	A = new float*[p];
	B = new Polynom*[p];
	for (int i = 0; i < p; i++)
	{
		A[i] = nullptr;
		B[i] = nullptr;
	}

	int idx = 0;

	// ����� ����-��������
	if (leftIncl)
	{
		Polynom* bcf = new Polynom(p + 1);
		(*bcf)[center] = -1.0f;
		A[idx] = GetTaylorCoeffs(-0.5 - left, p);
		B[idx] = bcf;
		idx++;
	}

	// �������� ��������
	//int offset = -1;
	int initVel = 1 + (leftIncl ? 1 : 0);
	int maxVel = p + (rightIncl ? 0 : 1);
	for (int vel = initVel; vel <= maxVel; vel++)
	{
		if (vel == center)
		{
			continue;
		}

		Polynom* bcf = new Polynom(p + 1);
		(*bcf)[vel] = 1.0f;
		(*bcf)[center] = -1.0f;
		A[idx] = GetTaylorCoeffs(vel - center, p);
		B[idx] = bcf;
		idx++;
	}

	// ������ ����-��������
	if (rightIncl)
	{
		Polynom* bcf = new Polynom(p + 1);
		(*bcf)[center] = -1.0f;
		A[idx] = GetTaylorCoeffs(0.5 + right, p);
		B[idx] = bcf;
	}
}

void Slau::printA()
{
	for (int i = 0; i < p; i++)
	{
		for (int j = 0; j < p; j++)
		{
			printf("%.4f ", A[i][j]);
		}
		printf("\n");
	}
	printf("\n");
}

void Slau::printB()
{
	for (int i = 0; i < p; i++)
	{
		for (int j = 1; j <= p + 1; j++)
		{
			printf("%.4f ", (*B[i])[j]);
		}
		printf("\n");
	}
	printf("\n");
}

void Slau::SwapRows(int a, int b)
{
	if (a == b) { return; }
	if (a >= 0 && a < p && b >= 0 && b < p)
	{
		float* fb = A[a];
		A[a] = A[b];
		A[b] = fb;

		Polynom* pb = B[a];
		B[a] = B[b];
		B[b] = pb;
	}
}

void Slau::AddToRow(int row, int ccol)
{
	if (A[row][ccol] == 0.0f)
	{
		return;
	}

	float mult = -A[row][ccol] / A[ccol][ccol];
	for (int i = ccol; i < p; i++)
	{
		A[row][i] += mult * A[ccol][i];
	}
	(*B[row]).add(B[ccol], mult);

	// Controlieren
	A[row][ccol] = 0.0f;
}

int Slau::SeekRow(int col)
{
	for (int rowIdx = col; rowIdx < p; rowIdx++)
	{
		if (A[rowIdx][col] != 0.0f)
		{
			return rowIdx;
		}
	}

    // return an invalid index if the row could not be found
    return -1;
}

void Slau::Trianglize()
{
	//printA();
	//printB();
	for (int cl = 0; cl < p - 1; cl++)
	{
		int mainrow = SeekRow(cl);
		SwapRows(cl, mainrow);
		for (int row = cl + 1; row < p; row++)
		{
			AddToRow(row, cl);
		}
		//printA();
		//printB();
	}
}

Polynom& Slau::SolveForSecondDerivative()
{
	Trianglize();
	Polynom** sols = new Polynom*[p - 1];
	for (int resIdx = p - 1; resIdx > 0; resIdx--)
	{
		for (int col = resIdx + 1; col < p; col++)
		{
			float mult = -A[resIdx][col];
			(*B[resIdx]).add(sols[col - 1], mult);
		}
		sols[resIdx - 1] = (*B[resIdx]) / A[resIdx][resIdx];
		//for (int i = 1; i <= p + 1; i++)
		//{
		//	printf("%.9f ", (*sols[resIdx - 1])[i]);
		//}
		//printf("\n");
	}
	return *(sols[0]);
}

Slau::~Slau(void)
{
	if (A != nullptr)
	{
		for (int i = 0; i < p; i++)
		{
			if (A[i] != nullptr)
			{
				delete[] A[i];
				A[i] = nullptr;
			}
		}
		delete[] A;
		A  = nullptr;
	}
	if (B != nullptr)
	{
		delete[] B;
		B = nullptr;
	}
}

float* Slau::GetTaylorCoeffs(float d, int maxp)
{
	float* cfs = new float[maxp];
	float nom = 1.0f, den = 1.0f;
	for (int p = 1; p <= maxp; p++)
	{
		nom *= d;
		den *= p;
		cfs[p - 1] = nom / den;
	}
	return cfs;
}
