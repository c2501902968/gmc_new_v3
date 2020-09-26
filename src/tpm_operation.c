#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <sys/stat.h>  //mkdir
#include <sys/types.h> //mkdir
#include <unistd.h>	   //access
#include <time.h>

#include <tss/tss_error.h>
#include <tss/platform.h>
#include <tss/tss_defines.h>
#include <tss/tss_typedef.h>
#include <tss/tss_structs.h>
#include <tss/tspi.h>
#include <trousers/trousers.h>

#define Debug(message, tResult) printf("%s : %s\n", message, (char *)Trspi_Error_String(result))

void printMenu();
void time1(char *buffer);
void write_pcr_value(BYTE *path, UINT32 ulPcrIndex, UINT32 ulPcrLen, BYTE *rgbPcrValue);
TSS_RESULT getPCR(TSS_HTPM hTPM, UINT32 ulPcrIndex, UINT32 *pulPcrValueLength, BYTE **prgbPcrValue);
TSS_RESULT extendPCR(TSS_HTPM hTPM, UINT32 ulPcrIndex, BYTE *pbPcrData, UINT32 *pulPcrValueLength, BYTE **prgbPcrValue);

int main(int argc, char **argv)
{
	TSS_HCONTEXT hContext;
	TSS_HTPM hTPM;
	TSS_HPCRS hPcrs;
	TSS_HENCDATA hEncData;
	TSS_HENCDATA hRetrieveData;
	TSS_RESULT result;
	TSS_HKEY hSRK = 0;
	TSS_HPOLICY hSRKPolicy = 0;
	TSS_UUID SRK_UUID = TSS_UUID_SRK;

	BYTE wks[20];
	BYTE *pubKey;
	UINT32 pubKeySize;
	BYTE *rgbPcrValue;
	UINT32 ulPcrLen;
	BYTE *encData;
	UINT32 encDataSize;
	BYTE *outstring;
	UINT32 outlength;
	FILE *fout, *fin;
	BYTE path[512];
	int i;
	UINT32 j;
	BYTE valueToExtend[250];
	int count = 0;
	int pcrToExtend = 0;

	memset(wks, 0, 20);
	memset(valueToExtend, 0, 250);

	//Pick the TPM you are talking to.
	//In this case, it is the system TPM(indicated with NULL)
	result = Tspi_Context_Create(&hContext);
	//Debug("Create Context", result);

	result = Tspi_Context_Connect(hContext, NULL);
	//Debug("Context Connect", result);

	//Get the TPM handle
	result = Tspi_Context_GetTpmObject(hContext, &hTPM);
	//Debug("Get TPM Handle", result);

	//Get the SRK handle
	result = Tspi_Context_LoadKeyByUUID(hContext, TSS_PS_TYPE_SYSTEM, SRK_UUID, &hSRK);
	//Debug("Get the SRK handle", result);

	//Get the SRK policy
	result = Tspi_GetPolicyObject(hSRK, TSS_POLICY_USAGE, &hSRKPolicy);
	//Debug("Get the SRK policy", result);

	//Then set the SRK policy to be the well known secret
	result = Tspi_Policy_SetSecret(hSRKPolicy, TSS_SECRET_MODE_SHA1, 20, wks);
	//Examine command line arguments.

	if (argc >= 3)
	{
		if (strcmp(argv[1], "-p") == 0)
		{
			pcrToExtend = atoi(argv[2]);
			if (pcrToExtend < 0 || pcrToExtend > 23)
			{
				printMenu();
				return 0;
			}
			if (argc == 5)
			{
				if (strcmp(argv[3], "-v") == 0)
					memcpy(valueToExtend, argv[4], strlen(argv[4]));
			}
			else
			{
				memcpy(valueToExtend, "abcdefghijklmnopqrst", 20);
			}

			extendPCR(hTPM, pcrToExtend, (BYTE *)valueToExtend, &ulPcrLen, &rgbPcrValue);
			return 0;
		}

		if (strcmp(argv[1], "-g") == 0)
		{
			pcrToExtend = atoi(argv[2]);
			if (pcrToExtend < 0 || pcrToExtend > 23)
			{
				printMenu();
				return 0;
			}
			if (argc == 5)
			{
				if (strcmp(argv[3], "-path") == 0)

					memcpy(path, argv[4], strlen(argv[4]));
			}
			else
			{
				memcpy(path, "/home/c/data/gmc_new_v3/Measure", 512);
				// getcwd(path, sizeof(path));
				// printf(path);
			}
			
			getPCR(hTPM, pcrToExtend, &ulPcrLen, &rgbPcrValue);
			write_pcr_value(path, pcrToExtend, ulPcrLen, rgbPcrValue);
			return 0;
		}
	}
	else
	{
		printMenu();
		return 0;
	}
	//Clean up
	Tspi_Context_FreeMemory(hContext, NULL);
	Tspi_Context_Close(hContext);

	return 0;
}

void printMenu()
{
	printf("\nPCRn operation Help Menu:\n");
	printf("\t -p PCR regiter (0-23)\n");
	printf("\t -v Value to be extended into PCR(abc...)\n");
	printf("\t -g get one PCR value\n");
	printf("\t -path put pcr value to path \n");
	printf("\t Note: -v argument is optional and a default value will be used if no value is provided\n");
	printf("\t          PCRn -p 10 -v abcdef\n");
	printf("\t          PCRn -g 10 -path /home/c/data/gmc_new_v3/Measure\n");
}

//获得指定PCR值
TSS_RESULT getPCR(TSS_HTPM hTPM, UINT32 ulPcrIndex, UINT32 *pulPcrValueLength, BYTE **prgbPcrValue)
{
	TSS_RESULT result = Tspi_TPM_PcrRead(hTPM, ulPcrIndex, pulPcrValueLength, prgbPcrValue);
	return result;
}

TSS_RESULT extendPCR(TSS_HTPM hTPM, UINT32 ulPcrIndex, BYTE *pbPcrData, UINT32 *pulPcrValueLength, BYTE **prgbPcrValue)
{
	TSS_RESULT result = Tspi_TPM_PcrExtend(hTPM, ulPcrIndex, 20, (BYTE *)pbPcrData, NULL, pulPcrValueLength, prgbPcrValue);
	return result;
}

void time1(char *buffer)
{
	time_t rawtime;
	struct tm *info;
	//char buffer[80];

	time(&rawtime);
	info = localtime(&rawtime);

	strftime(buffer, 80, "%Y-%m-%e %H:%M:%S", info); //以年月日_时分秒的形式表示当前时间
}

void write_pcr_value(BYTE *path, UINT32 ulPcrIndex, UINT32 ulPcrLen, BYTE *rgbPcrValue)
{
	time_t timer;
	char buffer[80];
	time1(buffer);
	static char dirpath[512];

	if (access(path, 0) == -1)
	{
		if (mkdir(path, 0777))
			printf("create file bag failed!");
	}
	FILE *fp = NULL;
	strncpy(dirpath, path, 512);
	// dirpath[strlen(dirpath)] = '/';
	strncpy(dirpath + strlen(dirpath), "/history_pcr_value", 512 - strlen(dirpath));
	fp = fopen(dirpath, "a+");

	fprintf(fp, buffer);
	fprintf(fp, " PCR %02d:", ulPcrIndex);
	for (int i = 0; i < ulPcrLen; i++)
	{
		fprintf(fp, "%02x", *(rgbPcrValue + i));
	}
	fprintf(fp, "\n");
	fclose(fp);
}