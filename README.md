
# Yocto Project Setup Guide

## Build Host Packages

Ensure that your build host has all the necessary packages installed before starting with Yocto:

```bash
sudo apt install gawk wget git diffstat unzip texinfo gcc build-essential chrpath socat cpio \
python3 python3-pip python3-pexpect xz-utils debianutils iputils-ping python3-git python3-jinja2 \
python3-subunit zstd liblz4-tool file locales libacl1
sudo locale-gen en_US.UTF-8

sudo apt install git make inkscape texlive-latex-extra
```

## Create a Directory for Yocto Images

Set up a dedicated directory for your Yocto project:

```bash
mkdir Yocto_Folder
```

## Clone the Poky Repository

Poky is the reference distribution of the Yocto Project. Clone it into your `Yocto_Folder`:

```bash
git clone git://git.yoctoproject.org/poky
cd poky
```

## Checkout the Kirkstone Branch

Switch to the `kirkstone` branch, which is a specific stable release of the Yocto Project:

```bash
git checkout kirkstone
```

## Initialize the Build Environment

Initialize the build environment by running:

```bash
source oe-init-build-env
```

## Create a New Layer

Navigate to your `Yocto_Folder` and create a new layer for your project:

```bash
bitbake-layers create-layer meta-deviceManagement
```

## Add the Layer to Your Build

Navigate to the `build` directory and add your new layer:

```bash
bitbake-layers add-layer ~/Yocto_Folder/meta-deviceManagement
bitbake-layers add-layer ~/Yocto_Folder/meta-openembedded/meta-oe
bitbake-layers add-layer ~/Yocto_Folder/meta-openembedded/meta-python
```

## Verify the Layer Addition

You can verify that your layer has been added correctly with:

```bash
bitbake-layers show-layers
```

## Create Recipes in Your Layer

In your layer directory under `recipes-example`, create directories for your recipes:

```bash
mkdir deviceManagement grpcio
```

### Add Project Files and Recipes

- **deviceManagement**: Clone your IoT device project files into `deviceManagement/files` and create the `deviceManagement_1.0.bb` recipe file.
- **grpcio**: Add the gRPC recipe in `grpcio/python3-grpcio_1.45.0.bb`.

---
### Build the recipe 
 ```bash
cd ~/Yocto_Folder/poky/build
bitbake deviceManagement
```
