input="./numbers.dat"

while IFS= read -r line; do num=$line; done < $input

numbers=$(python3 -c "n='$num';new=n.replace(',',' ');print(new)")
cd src
python3 generate_mnist_sub_dataset.py --numbers $numbers

