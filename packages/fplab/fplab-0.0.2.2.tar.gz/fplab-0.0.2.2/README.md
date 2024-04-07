This is a python3 package designed for fingerprint. The methods of import part in fingerprint processing procedure, including getting intrinsic images, enhancement and matching, can be found in this package. Some usefull tools for images are also included in this package.

If you want to use this package, you should install all the required library:
pytorch==1.13.1, 
cuda==11.6,
torchvision==0.14.1, 
pillow, 
numpy, 
opencv, 
opencv-contrib, 
scipy,
tqdm, 
matplotlib

The following is the recommended command.

conda create -n fpLAB python=3.10

conda activate fpLAB

conda install pytorch==1.13.1 torchvision==0.14.1 pytorch-cuda=11.6 -c pytorch -c nvidia

conda install pillow

conda install numpy

pip install opencv

pip install opencv-contrib-python

conda install scipy

conda install tqdm

conda install matplotlib
