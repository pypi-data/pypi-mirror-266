# CROP Images with CLI
Crops images with python using Pillow. Useful for cropping multiple images at the same time.
The dafult resolution is 1920x1080


## How to install
1. Install [pipx](https://github.com/pypa/pipx)
2. Install easycrop
```sh
pipx install easycrop
```

## How to use:
<details>
  <summary>Base Image</summary>

![Base image](https://github.com/moutella/crop/blob/main/examples/kanagawa.jpg?raw=True))

</details>

1. Single file

```sh
crop examples/kanagawa.jpg -height 300 -width 300
```
<details>
  <summary>Output Focused 300x300</summary>

  ![300x300](https://github.com/moutella/crop/blob/main/examples/kanagawa-300x300.jpg?raw=True))

</details>

1. Resize image to keep maximum information possible

```sh
crop examples/kanagawa.jpg -height 450 -width 450 -resize
```
<details>
  <summary>Output: resized then 450x450, </summary>

  ![450x450](https://github.com/moutella/crop/blob/main/examples/kanagawa-450x450.jpg?raw=True))

</details>

1. Using ratio instead of size, will get biggest possible:

```sh
crop examples/kanagawa.jpg -ratio 1:1  
```
<details>
  <summary>Output: 2990x2990</summary>
    
  ![2990x2990](https://github.com/moutella/crop/blob/main/examples/kanagawa-2990x2990.jpg?raw=True))

</details>


1. Make it recursive

```sh
crop -r {folder} -height {height} -width {width}
```