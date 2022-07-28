#include "sm3.h"
#include "md5.h"
#include "sha256.h"
using namespace std;
string hashhanshu(string temp, int i);
int xxhh = 0;
int main()
{
	static const string arr[] = {
		"sdu",
		"shandong",
		"441",
		"20220720",
		"2020",
		"wangan",
		"zhangqinxin",
		"wangjinghan",
		"yuxiaochang",
		"lijinyuan" };
	vector<string> sample_hashes(arr, arr + sizeof(arr) / sizeof(arr[0]));

	cout << "\nMerkle Root: " << merkle(sample_hashes) << endl;
}

string merkle(vector<string> hash_vector)
{
	xxhh += 1;
	if (hash_vector.size() == 1)
	{
		//This is the Merkle Root
		return hash_vector[0];
	}

	//This vector stores the new set of branhces in that level to pass to the next level
	vector<string> new_hash_vector;

	cout << "\nNumber of branches in round " << xxhh << " is " << hash_vector.size() << "\n";

	//Collects two elements from a level in each iteration
	for (int i = 0; i < hash_vector.size() - 1; i = i + 2)
	{
		cout << "Elements to combine: " << hash_vector[i] << " and " << hash_vector[i + 1];
		new_hash_vector.push_back(hashhanshu(hash_vector[i]+hash_vector[i + 1],1));
		cout << " resulting in " << new_hash_vector[new_hash_vector.size() - 1] << "\n";
	}

	//In case there are an odd number of branches, hash the last branch with itself
	if ((hash_vector.size() % 2) == 1)
	{
		cout << "Elements to combine: " << hash_vector[hash_vector.size() - 1] << " with itself resulting in ";
		new_hash_vector.push_back(hashhanshu(hash_vector[hash_vector.size() - 1]+hash_vector[hash_vector.size() - 1],1));
		cout << new_hash_vector[new_hash_vector.size() - 1] << "\n";
	}

	return merkle(new_hash_vector);
}
string hashhanshu(string temp, int i)
{
	if (i == 1)
		return sm3(temp);
	else if (i == 2)
		return md5(temp);
	else if (i == 3)
		return sha256_test(temp);
	else
		return "";
}
