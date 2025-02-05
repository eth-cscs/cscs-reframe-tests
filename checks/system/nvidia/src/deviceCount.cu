#include <stdio.h>
#include <unistd.h>
#include <nvml.h>

#ifndef __USE_POSIX
   #define __USE_POSIX
#endif

#include <limits.h>

int main() {
   char hostname[HOST_NAME_MAX];
   unsigned int nvmlCount = 0;
   int deviceCount = 0;
   int result;
   nvmlReturn_t nvml_return;
   cudaError_t error;

   result = gethostname(hostname, HOST_NAME_MAX);
   if (result != 0) {
       printf("error retriving the hostname\n");
       return -1;
   }

   nvml_return = nvmlInit_v2();
   if (nvml_return != NVML_SUCCESS) {
       printf("%s: error initializing NVML\n", hostname);
       return -1;
   }

   nvml_return = nvmlDeviceGetCount_v2(&nvmlCount);
   if (nvml_return != NVML_SUCCESS) {
       printf("%s: NVML error retrieving the device count:\n", hostname);
       nvml_return = nvmlShutdown();
       return -1;
   }

   error = cudaGetDeviceCount(&deviceCount);
   if (error != cudaSuccess) {
       printf("%s: CUDA error retrieving the device count:\n", hostname);
       nvml_return = nvmlShutdown();
       return -1;
   }

   if (deviceCount != nvmlCount) {
       printf("%s: NVML device count %d != CUDA device count: %d\n", hostname,
              nvmlCount, deviceCount);
       nvml_return = nvmlShutdown();
       return -1;
   }

   nvml_return = nvmlShutdown();
   printf("%s: NVML device count == Cuda device count == %d\n", hostname,
          deviceCount);

   return 0;
}
