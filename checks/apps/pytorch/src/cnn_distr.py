import os
import random
import time
import numpy as np
import torch
import torch.distributed as dist
import torch.nn.functional as F
import torch.optim as optim
from torch.nn.parallel import DistributedDataParallel
from torch.utils.data import DataLoader, Dataset, DistributedSampler
from torchvision import models
from pt_distr_env import DistributedEnviron


num_warmup_epochs = 2
num_epochs = 5
batch_size_per_gpu = 512
num_iters = 25
model_name = 'resnet50'

distr_env = DistributedEnviron()
dist.init_process_group(backend="nccl")
world_size = dist.get_world_size()
rank = dist.get_rank()
device = 0  # distr_env.local_rank  # since CUDA_VISIBLE_DEVICES=$SLURM_LOCALID
device_count = torch.cuda.device_count()

model = getattr(models, model_name)()
model.to(device)

optimizer = optim.SGD(model.parameters(), lr=0.01)


class SyntheticDataset(Dataset):
    def __getitem__(self, idx):
        data = torch.randn(3, 224, 224)
        target = random.randint(0, 999)
        return (data, target)

    def __len__(self):
        return batch_size_per_gpu * num_iters * world_size


ddp_model = DistributedDataParallel(model, device_ids=[device])

train_set = SyntheticDataset()
train_sampler = DistributedSampler(
    train_set,
    num_replicas=world_size,
    rank=rank,
    shuffle=False,
    seed=42
)
train_loader = DataLoader(
    train_set,
    batch_size=batch_size_per_gpu,
    shuffle=False,
    sampler=train_sampler,
    pin_memory=True,
    num_workers=2
)


def benchmark_step(model, imgs, labels):
    imgs = imgs.to(device, non_blocking=True)
    labels = labels.to(device, non_blocking=True)
    optimizer.zero_grad()
    output = model(imgs)
    loss = F.cross_entropy(output, labels)
    loss.backward()
    optimizer.step()


# warmup
for epoch in range(num_warmup_epochs):
    for step, (imgs, labels) in enumerate(train_loader):
        benchmark_step(ddp_model, imgs, labels)

# benchmark
imgs_sec = []
for epoch in range(num_epochs):
    t0 = time.time()
    for step, (imgs, labels) in enumerate(train_loader):
        benchmark_step(ddp_model, imgs, labels)

    dt = time.time() - t0
    imgs_sec.append(batch_size_per_gpu * num_iters / dt)

    if rank == 0:
        print(f' * Rank {rank} - Epoch {epoch:2d}: '
              f'{imgs_sec[epoch]:.2f} images/sec per GPU')

imgs_sec_total = np.mean(imgs_sec) * world_size * device_count
if rank == 0:
    print(f' * Total average: {imgs_sec_total:.2f} images/sec')
