#include <cuda_runtime.h>
#include <mpi.h>

#include <chrono>
#include <cstdlib>
#include <iostream>
#include <string>
#include <string_view>

#define CHECK_MPI(x)                             \
    if (auto e = x; e != MPI_SUCCESS) {          \
        std::cout << "MPI error: " << e << '\n'; \
        std::exit(1);                            \
    }
#define CHECK_CUDA(x)                             \
    if (auto e = x; e != cudaSuccess) {           \
        std::cout << "CUDA error: " << e << '\n'; \
        std::exit(1);                             \
    }

namespace test {
enum class mem_type {
    host,
    pinned_host,
    device,
};

mem_type parse_mem_type(std::string_view s) {
    if (s == "host") {
        return mem_type::host;
    } else if (s == "pinned_host") {
        return mem_type::pinned_host;
    } else if (s == "device") {
        return mem_type::device;
    } else {
        std::cout << "Memory type must be host, pinned_host, or device; got \""
                  << s << "\"\n";
        std::exit(1);
    }
}

template <typename T>
T* malloc(mem_type t, std::size_t n) {
    switch (t) {
        case mem_type::host:
            return static_cast<T*>(::malloc(n));

        case mem_type::pinned_host: {
            void* p = nullptr;
            CHECK_CUDA(cudaMallocHost(&p, n));
            return static_cast<T*>(p);
        }

        case mem_type::device: {
            void* p = nullptr;
            CHECK_CUDA(cudaMalloc(&p, n));
            return static_cast<T*>(p);
        }

        default:
            std::terminate();
    }
}

void free(mem_type t, void* p) {
    switch (t) {
        case mem_type::host:
            ::free(p);
            break;

        case mem_type::pinned_host:
            CHECK_CUDA(cudaFreeHost(p));
            break;

        case mem_type::device:
            CHECK_CUDA(cudaFree(p));
            break;

        default:
            std::terminate();
    }
}
}  // namespace test

int main(int argc, char** argv) {
    if (argc != 5) {
        std::cout << "Usage: gpudirect_p2p_overalloc <num_iterations> "
                     "<num_sub_iterations> <memory_type> <p2p_size>\n";
        std::exit(1);
    }

    CHECK_MPI(MPI_Init(&argc, &argv));

    int comm_rank;
    CHECK_MPI(MPI_Comm_rank(MPI_COMM_WORLD, &comm_rank));
    int comm_size;
    CHECK_MPI(MPI_Comm_size(MPI_COMM_WORLD, &comm_size));

    const auto rank_recv = comm_size - 1;

    std::size_t const num_iterations = std::stoul(argv[1]);
    std::size_t const num_sub_iterations = std::stoul(argv[2]);
    test::mem_type const t = test::parse_mem_type(argv[3]);
    std::size_t const p2p_size = std::stoul(argv[4]);

    if (comm_rank == 0) {
        std::cout << "mem_type: " << argv[3] << '\n';
        std::cout << "p2p_size: " << p2p_size << '\n';
    }

    // Warmup
    {
        const std::chrono::time_point<std::chrono::steady_clock> start =
            std::chrono::steady_clock::now();

        if (comm_rank == 0) {
            char* mem = test::malloc<char>(t, p2p_size);
            CHECK_MPI(MPI_Send(mem, p2p_size, MPI_CHAR, rank_recv, 0,
                               MPI_COMM_WORLD));
            test::free(t, mem);
        } else if (comm_rank == rank_recv) {
            char* mem = test::malloc<char>(t, p2p_size);
            MPI_Status status;
            CHECK_MPI(MPI_Recv(mem, p2p_size, MPI_CHAR, 0, 0, MPI_COMM_WORLD,
                               &status));
            test::free(t, mem);
        }

        CHECK_MPI(MPI_Barrier(MPI_COMM_WORLD));

        auto const stop = std::chrono::steady_clock::now();
        if (comm_rank == 0) {
            std::cout << "[-1] time: "
                      << std::chrono::duration<double>(stop - start).count()
                      << '\n';
        }
    }

    if (comm_rank == 0) {
        std::cout << "Doing MPI_Send/Recv from rank 0 to rank " << rank_recv
                  << ", of " << p2p_size << " bytes\n";
    }

    for (std::size_t i = 0; i < num_iterations; ++i) {
        char* mem = nullptr;
        if (comm_rank == 0 || comm_rank == rank_recv) {
            mem = test::malloc<char>(t, p2p_size);
        }

        for (std::size_t j = 0; j < num_sub_iterations; ++j) {
            const std::chrono::time_point<std::chrono::steady_clock> start =
                std::chrono::steady_clock::now();

            if (comm_rank == 0) {
                CHECK_MPI(MPI_Send(mem, p2p_size, MPI_CHAR, rank_recv, 0,
                                   MPI_COMM_WORLD));
            } else if (comm_rank == rank_recv) {
                MPI_Status status;
                CHECK_MPI(MPI_Recv(mem, p2p_size, MPI_CHAR, 0, 0,
                                   MPI_COMM_WORLD, &status));
            }

            CHECK_MPI(MPI_Barrier(MPI_COMM_WORLD));

            auto const stop = std::chrono::steady_clock::now();
            if (comm_rank == 0) {
                std::cout << "[" << i << ":" << j << "] time: "
                          << std::chrono::duration<double>(stop - start).count()
                          << '\n';
            }
        }

        test::free(t, mem);
    }

    return EXIT_SUCCESS;
}
