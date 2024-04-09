# Project Name: UF-Toolkit

## Description

UF-Toolkit is a Python package providing an efficient and robust implementation of the Union Find algorithm, also known as Disjoint Set Union (DSU). This data structure is essential for managing a set of elements divided into several disjoint, non-overlapping subsets. It's particularly useful in computer science for applications like network connectivity, image segmentation, clustering, and more.

Our implementation offers features like path compression and union by rank, ensuring optimal time complexity for both find and union operations. Whether you're dealing with graph algorithms or just need a fast way to handle disjoint sets, UF-Toolkit is designed to offer straightforward, reliable, and efficient performance.

## Features

- **Efficient Union Find Operations:** Implements both path compression and union by rank for fast operation.
- **Easy-to-Use API:** Designed with simplicity in mind, our API makes it easy to integrate into your existing Python projects.
- **Versatile Applications:** Suitable for use cases ranging from network analysis to algorithmic problem solving in competitive programming.
- **Fully Documented:** Each method and class is thoroughly documented, making it easy to get started and understand how the package works.

## Installation

Install UF-Toolkit using pip:

```bash
pip install uf-toolkit
```

## Usage

Here's a quick example of how to use UF-Toolkit:

```python
from uf_toolkit import UnionFind
```

## Create a Union Find instance with 10 elements

```python
uf = UnionFind(10)
```

## Union some sets

```python
uf.union(1, 2)
uf.union(2, 3)
```

## Check if two elements are in the same set

```python
print(uf.connected([1, 3])) # True
```

## Count the number of distinct sets

```python
print(uf.count_sets()) # 3
```

## Check all elements of the set that contains given element

```python
print(uf.get_all_elements_of_set(1)) # [1, 2, 3]
```

## Requirements

Python 3.x

## Contributing

Contributions, issues, and feature requests are welcome! Feel free to check issues page.

## License

Distributed under the MIT License. See LICENSE for more information.

## Contact

Chas Huggins - <hugginsc10@gmail.com>

Project Link: <https://github.com/hugginsc10/uf-toolkit/>
