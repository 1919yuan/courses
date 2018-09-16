mkdir build
cd build
cmake ..
make
cd ..
rm -rf build
cd bin

# Solve the thomson problem with 3 points and 3 dimension
./thomson
# Result in x_alm_3_3_....txt

cd ..
