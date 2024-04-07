# LingoQA dataset for pytorch

## How to use

```python
from lingoqa_dataset.dataset import LingoQADataset
import torchvision.transforms as transforms
from torch.utils.data import DataLoader

dataset = LingoQADataset(
    DatasetType.EVALUATION, transforms=transforms.Resize((256, 512))
)
dataloader = DataLoader(dataset=dataset, batch_size=3, shuffle=True)
for data, question, answer in dataloader:
    pass
```

### data

- type: torch.Tensor
- size : torch.Size([batch_size, 3 * number_of_images, height, width])
- description : Images in the target sequences.

### question

- type: torch.Tuple(str)
- size: batch_size
- description : Questions in the batch.

### answer

- type: torch.Tuple(str)
- size: batch_size
- description : Answers in the batch.

## Special thanks

[LingoQA](https://github.com/wayveai/LingoQA) project from [wayve.](https://wayve.ai/)