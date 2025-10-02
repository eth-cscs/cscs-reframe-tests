// MPI version of eatmemory.c from Julio Viera
// 12/2020: add cscs_read_proc_meminfo from jg (cscs)
// 10/2022: simpler code from jg (cscs)
#include <ctype.h>
#include <mpi.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#define PROC_FILE "/proc/meminfo"
#define MEMTOTAL 0
#define MEMFREE 1
#define MEMCACHED 2
#define SWAPTOTAL 3
#define SWAPFREE 4
#define SWAPCACHED 5
#define MEMAVAIL 6

typedef struct {
  char *str;
  uint32_t val;
} meminfo_t;

int cscs_read_proc_meminfo(int);

// {{{ sysconf_mem
size_t getTotalSystemMemory() {
  long pages = sysconf(_SC_PHYS_PAGES);
  long page_size = sysconf(_SC_PAGE_SIZE);
  return pages * page_size / 1073741824;
  // 1073741824 = 1024^3 = 1GB
}

size_t getFreeSystemMemory() {
  long pages = sysconf(_SC_AVPHYS_PAGES);
  long page_size = sysconf(_SC_PAGE_SIZE);
  return pages * page_size / 1073741824;
  // 1073741824 = 1024^3 = 1GB
}
// }}}

// {{{ proc_mem
int cscs_read_proc_meminfo(int i) {
  FILE *fp;
  meminfo_t meminfo[] = {{"MemTotal:", 0},     {"MemFree:", 0},
                         {"Cached:", 0},       {"SwapCached:", 0},
                         {"SwapTotal:", 0},    {"SwapFree:", 0},
                         {"MemAvailable:", 0}, {NULL, 0}};
  fp = fopen(PROC_FILE, "r");
  if (!fp) {
    printf("Cannot read %s", PROC_FILE);
    return -1;
  }
  char buf[80];
  while (fgets(buf, sizeof(buf), fp)) {
    int i;
    for (i = 0; meminfo[i].str; i++) {
      size_t len = strlen(meminfo[i].str);
      if (!strncmp(buf, meminfo[i].str, len)) {
        char *ptr = buf + len + 1;
        while (isspace(*ptr))
          ptr++;
        sscanf(ptr, "%u kB", &meminfo[i].val);
      }
    }
  }
  fclose(fp);

  printf(
      "memory from %s: total: %u GB, free: %u GB, avail: %u GB, using: %u GB\n",
      PROC_FILE, meminfo[MEMTOTAL].val / 1048576,
      meminfo[MEMFREE].val / 1048576, meminfo[MEMAVAIL].val / 1048576,
      (meminfo[MEMTOTAL].val - meminfo[MEMAVAIL].val) / 1048576);
  return 0;
}
// }}}

// {{{ eat_mem
// bool eat(long total, int chunk) {
bool eat(int chunk) {
  long i;
  int rank, mpi_size, total = 100000; // should be large enough
  MPI_Comm_size(MPI_COMM_WORLD, &mpi_size);
  MPI_Comm_rank(MPI_COMM_WORLD, &rank);
  // for (i = 0; i < total; i += chunk) {
  for (i = 0; i < total; i++) {
    if (rank == 0) {
      int mb_mpi = chunk / 1048576;
      printf("Eating %d MB/mpi *%dmpi = -%d MB ", mb_mpi, mpi_size,
             mb_mpi * mpi_size);
      // print memory usage from /proc/meminfo
      cscs_read_proc_meminfo(i);
    }
    short *buffer = malloc(sizeof(char) * chunk);
    if (buffer == NULL) {
      return false;
    }
    memset(buffer, 0, chunk);
  }
  return true;
}
// }}}

// {{{ main
int main(int argc, char *argv[]) {
  int rank, mpi_size;
  MPI_Init(&argc, &argv);
  MPI_Comm_rank(MPI_COMM_WORLD, &rank);
  MPI_Comm_size(MPI_COMM_WORLD, &mpi_size);
  if (rank == 0) {
    printf("memory from sysconf: total: %zd GB avail: %zd GB\n",
           getTotalSystemMemory(), getFreeSystemMemory());
    cscs_read_proc_meminfo(rank);
  }
  // chunk * x cores:
  // int chunk = 16777216; // 16M
  // int chunk =  33554432; //  32M
  // int chunk =  67108864; //  64M
  int chunk = 134217728; // 128M
  // int chunk = 268435456; // = 256M
  // int chunk=536870912; // = 512M
  // int chunk=1073741824; // = 1G
  eat(chunk);

  MPI_Finalize();
  return 0;
}
// }}}
